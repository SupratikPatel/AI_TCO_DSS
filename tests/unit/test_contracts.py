"""Domain contracts (Requirement 7, 12.7, 40.4, 40.5)."""

import ast
import inspect
import re
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

import ai_tco_dss.domain as domain
from ai_tco_dss.domain import (
    BenchmarkRecord,
    Contract,
    DecisionOptions,
    EnterpriseFinancials,
    LifecycleClocks,
    ModelSpec,
    Money,
    PresetId,
    RankingMethod,
    Scenario,
    SizingOptions,
    SourceEntry,
    TimelineResult,
    UseCaseId,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import ConfigurationError, DssError, EngineInputError
from ai_tco_dss.domain.money import eur_to_usd, round_display, usd_to_eur
from ai_tco_dss.settings import Settings, load_engine_parameters

ROOT = Path(__file__).resolve().parents[2]
SPEC_04 = ROOT / "specs" / "04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md"
LEDGER = ROOT / "specs" / "07_DATA_CORRECTIONS.md"

# spec 04 contracts whose fields moved into differently named domain contracts.
SPEC_TO_DOMAIN = {
    "HardwareSizingResult": ("SizingResult", "PerformanceResult"),
    "TcoProjectionResult": ("TcoResult", "BaselineResult", "TimelineResult"),
}
REQUIRED = "<required>"


def _sourced(value: Any, tier: str = "official") -> dict[str, Any]:
    return {"value": value, "source_id": "SRC-1", "tier": tier, "accessed": "2026-11-06"}


def _money(value: float, currency: str = "EUR") -> dict[str, Any]:
    return {**_sourced(value), "currency": currency}


def _model(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": "m",
        "name": "M",
        "family": "Qwen",
        "type": "open-weights",
        "architecture": "dense",
        "max_context_length": _sourced(131072),
    }
    return {**data, **overrides}


def _api_prices() -> dict[str, Any]:
    return {
        "input_per_1m": _money(2.0, "USD"),
        "output_per_1m": _money(10.0, "USD"),
        "cache_read_per_1m": _money(0.1, "USD"),
    }


def _errors(exc: pytest.ExceptionInfo[ValidationError]) -> list[dict[str, Any]]:
    return list(exc.value.errors())  # type: ignore[arg-type]


def _all_contract_classes() -> list[type[BaseModel]]:
    classes: dict[str, type[BaseModel]] = {}
    for module_name in ("base", "enums", "catalog", "scenario", "results", "inputs", "requests"):
        module = __import__(f"ai_tco_dss.domain.{module_name}", fromlist=["_"])
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseModel) and obj.__module__ == module.__name__:
                classes[obj.__name__] = obj
    return [classes[name] for name in sorted(classes)]


# --------------------------------------------------------------------------- 7.2 to 7.6


def test_req_7_2_every_contract_is_frozen_and_forbids_extra() -> None:
    classes = _all_contract_classes()
    assert len(classes) > 40
    for cls in classes:
        assert issubclass(cls, Contract), cls.__name__
        assert cls.model_config.get("frozen") is True, cls.__name__
        assert cls.model_config.get("extra") == "forbid", cls.__name__


def test_req_7_3_assignment_raises_naming_field_and_keeps_value() -> None:
    profile = WorkloadProfile()
    with pytest.raises(ValidationError) as exc:
        profile.active_users = 3  # type: ignore[misc]
    error = _errors(exc)[0]
    assert error["loc"] == ("active_users",)
    assert error["type"] == "frozen_instance"
    assert profile.active_users == 25


def test_req_7_4_unknown_field_raises_naming_field() -> None:
    with pytest.raises(ValidationError) as exc:
        WorkloadProfile(unknown_field=1)  # type: ignore[call-arg]
    error = _errors(exc)[0]
    assert error["loc"] == ("unknown_field",)
    assert error["type"] == "extra_forbidden"


@pytest.mark.parametrize(
    ("cls", "kwargs", "field", "error_type", "message_part"),
    [
        (WorkloadProfile, {"active_users": 0}, "active_users", "greater_than_equal", "1"),
        (WorkloadProfile, {"active_users": 100_001}, "active_users", "less_than_equal", "100000"),
        (
            WorkloadProfile,
            {"mega_session_ratio": 1.5},
            "mega_session_ratio",
            "less_than_equal",
            "1",
        ),
        (
            WorkloadProfile,
            {"working_days_per_month": 32},
            "working_days_per_month",
            "less_than_equal",
            "31",
        ),
        (
            WorkloadProfile,
            {"thinking_effort_preset": "ultra"},
            "thinking_effort_preset",
            "enum",
            "medium",
        ),
        (
            SourceEntry,
            {"source_id": "", "title": "t", "url": "u", "publisher": "p", "tier": "official"},
            "source_id",
            "string_too_short",
            "1 character",
        ),
    ],
)
def test_req_7_5_constraint_violation_names_field_and_constraint(
    cls: type[BaseModel], kwargs: dict[str, Any], field: str, error_type: str, message_part: str
) -> None:
    with pytest.raises(ValidationError) as exc:
        cls(**kwargs)
    errors = [e for e in _errors(exc) if e["loc"] == (field,)]
    assert errors, _errors(exc)
    assert errors[0]["type"] == error_type
    assert message_part in errors[0]["msg"]


def test_req_7_5_tuple_length_constraint() -> None:
    with pytest.raises(ValidationError) as exc:
        TimelineResult(
            anchor_candidate_id="a",
            rental_id="r",
            hybrid_api_model_id="m",
            points=(),
            break_even_months=(),
            single_stream_break_even_years=None,
            include_resale=False,
        )
    error = next(e for e in _errors(exc) if e["loc"] == ("points",))
    assert error["type"] == "too_short"
    assert "60" in error["msg"]


def test_req_7_6_missing_fields_are_each_named() -> None:
    with pytest.raises(ValidationError) as exc:
        SourceEntry()  # type: ignore[call-arg]
    missing = {e["loc"][0] for e in _errors(exc) if e["type"] == "missing"}
    assert missing == {"source_id", "title", "publisher", "tier"}


def test_req_7_6_wrong_type_names_field() -> None:
    with pytest.raises(ValidationError) as exc:
        WorkloadProfile(active_users="abc")  # type: ignore[arg-type]
    error = _errors(exc)[0]
    assert error["loc"] == ("active_users",)
    assert error["type"] == "int_parsing"


# --------------------------------------------------------------------------- 40.4, 40.5


def _benchmark(**overrides: Any) -> dict[str, Any]:
    data = {
        "metric": "decode_tps",
        "value": 14.7,
        "model_id": "qwen-3-8-27b",
        "source_id": "YT-21",
        "tier": "community",
        "accessed": "2026-11-06",
    }
    return {**data, **overrides}


def test_req_40_4_minimal_benchmark_record_validates() -> None:
    record = BenchmarkRecord.model_validate(_benchmark())
    assert record.hardware_id is None
    assert record.precision is None
    assert record.context_tokens is None
    assert record.accessed == date(2026, 11, 6)


def test_req_40_5_missing_provenance_fields_are_each_named() -> None:
    data = _benchmark()
    for key in ("source_id", "tier", "accessed"):
        del data[key]
    with pytest.raises(ValidationError) as exc:
        BenchmarkRecord.model_validate(data)
    assert {e["loc"][0] for e in _errors(exc)} == {"source_id", "tier", "accessed"}


def test_req_40_5_invalid_tier_named() -> None:
    with pytest.raises(ValidationError) as exc:
        BenchmarkRecord.model_validate(_benchmark(tier="blog"))
    assert _errors(exc)[0]["loc"] == ("tier",)


@pytest.mark.parametrize("accessed", ["2026-13-01", "06.11.2026", "2026-11-06T10:00:00", 20261106])
def test_req_40_5_invalid_accessed_date_named(accessed: object) -> None:
    with pytest.raises(ValidationError) as exc:
        BenchmarkRecord.model_validate(_benchmark(accessed=accessed))
    assert _errors(exc)[0]["loc"] == ("accessed",)


def test_sourced_accessed_rejects_non_iso_dates() -> None:
    with pytest.raises(ValidationError) as exc:
        Money.model_validate({**_money(1.0), "accessed": "2026/11/06"})
    assert _errors(exc)[0]["loc"] == ("accessed",)


# --------------------------------------------------------------------------- contract validators


def test_source_entry_requires_url_or_reference() -> None:
    base = {"source_id": "S", "title": "t", "publisher": "p", "tier": "official"}
    with pytest.raises(ValidationError, match="url or reference"):
        SourceEntry.model_validate({**base, "url": None, "reference": ""})
    assert SourceEntry.model_validate({**base, "reference": "book, p. 3"}).url is None


def test_money_currency_and_non_negative_value() -> None:
    with pytest.raises(ValidationError) as exc:
        Money.model_validate(_money(1.0, "GBP"))
    assert _errors(exc)[0]["loc"] == ("currency",)
    with pytest.raises(ValidationError) as exc:
        Money.model_validate(_money(-1.0))
    assert _errors(exc)[0]["loc"] == ("value",)


def test_model_spec_commercial_api_requires_prices() -> None:
    with pytest.raises(ValidationError, match="api_prices"):
        ModelSpec.model_validate(_model(type="commercial-api", license_type="Proprietary-API"))
    model = ModelSpec.model_validate(
        _model(type="commercial-api", license_type="Proprietary-API", api_prices=_api_prices())
    )
    assert model.api_prices is not None


def test_model_spec_open_weights_rejects_api_fields() -> None:
    with pytest.raises(ValidationError, match="eu_pinned_endpoint"):
        ModelSpec.model_validate(_model(eu_pinned_endpoint=_sourced(True)))


def test_lifecycle_resale_retention_range() -> None:
    data = {
        "software_support_years": _sourced(5.0),
        "resale_value_retention_3yr": _sourced(1.2),
        "cuda_or_rocm_status": "supported",
    }
    with pytest.raises(ValidationError) as exc:
        LifecycleClocks.model_validate(data)
    assert _errors(exc)[0]["loc"][0] == "resale_value_retention_3yr"


def _scenario(**overrides: Any) -> Scenario:
    return Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(),
        decision=DecisionOptions(),
        **overrides,
    )


def test_scenario_fx_override_bounds_and_decimals() -> None:
    assert _scenario(fx_override=1.123456).fx_override == 1.123456
    assert _scenario().fx_override is None
    for bad in (0.49, 2.01, 1.1234567):
        with pytest.raises(ValidationError) as exc:
            _scenario(fx_override=bad)
        assert _errors(exc)[0]["loc"] == ("fx_override",)


def test_financials_defaults_are_usd() -> None:
    financials = EnterpriseFinancials()
    assert financials.currency == "USD"
    assert financials.max_capex_budget_usd == 100_000.0
    assert financials.nvidia_nim_license_per_gpu_yr_usd == 4500.0
    assert financials.include_resale_value is False


def test_decision_defaults() -> None:
    decision = DecisionOptions()
    assert decision.use_case == UseCaseId.AGENTIC_CODING
    assert decision.preset == PresetId.BEST_FIT
    assert decision.method == RankingMethod.SAW


# ------------------------------------------------------------- money, errors, settings


def test_req_12_7_money_helpers() -> None:
    assert eur_to_usd(100.0, 1.1165) == pytest.approx(111.65)
    assert usd_to_eur(111.65, 1.1165) == pytest.approx(100.0)
    assert round_display(1.005) in (1.0, 1.01)
    for bad_rate in (0.0, -1.0, float("nan")):
        with pytest.raises(ValueError, match="rate"):
            usd_to_eur(1.0, bad_rate)


def test_error_hierarchy() -> None:
    error = EngineInputError("local_offload_ratio", "[0.0, 1.0]")
    assert isinstance(error, DssError)
    assert isinstance(error, ValueError)
    assert "local_offload_ratio" in str(error)
    assert "[0.0, 1.0]" in str(error)


def test_settings_and_engine_parameters_have_the_same_fields() -> None:
    assert set(Settings.model_fields) == set(domain.EngineParameters.model_fields)


def test_load_engine_parameters_defaults() -> None:
    params = load_engine_parameters()
    assert params.context_match_tolerance == 0.25
    assert params.eta_dense == 0.70
    assert params.eta_moe == 0.425
    assert dict(params.thinking_multipliers)[domain.ThinkingEffortPreset.EXTRA_HIGH] == 4.94


def test_load_engine_parameters_out_of_range_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_TCO_CONTEXT_MATCH_TOLERANCE", "1.5")
    with pytest.raises(ConfigurationError) as exc:
        load_engine_parameters()
    assert exc.value.setting == "context_match_tolerance"
    assert "1.5" in str(exc.value)


# --------------------------------------------------------------------------- 7.7 ledger


def _spec_04_classes() -> dict[str, dict[str, object]]:
    """spec 04 class name -> {field or member name: default literal or REQUIRED}."""
    text = SPEC_04.read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)```", text, re.S)
    assert code is not None
    result: dict[str, dict[str, object]] = {}
    for node in ast.parse(code.group(1)).body:
        if not isinstance(node, ast.ClassDef):
            continue
        is_enum = any(isinstance(b, ast.Name) and b.id == "Enum" for b in node.bases)
        entries: dict[str, object] = {}
        for stmt in node.body:
            if is_enum and isinstance(stmt, ast.Assign):
                name = stmt.targets[0]
                assert isinstance(name, ast.Name)
                entries[name.id] = ast.literal_eval(stmt.value)
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                entries[stmt.target.id] = _spec_default(stmt.value)
        result[node.name] = entries
    return result


def _spec_default(value: ast.expr | None) -> object:
    if value is None:
        return REQUIRED
    if isinstance(value, ast.Call):
        default: ast.expr | None = value.args[0] if value.args else None
        for kw in value.keywords:
            if kw.arg == "default":
                default = kw.value
        return _spec_default(default)
    if isinstance(value, ast.Constant) and value.value is Ellipsis:
        return REQUIRED
    if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
        return f"{value.value.id}.{value.attr}"
    return ast.literal_eval(value)


def _domain_default(cls: type[BaseModel], name: str) -> object:
    field = cls.model_fields[name]
    if field.is_required():
        return REQUIRED
    default = field.default
    if isinstance(default, Enum):
        return f"{type(default).__name__}.{default.name}"
    if isinstance(default, tuple):
        return list(default)
    return default


def _required_deviations() -> set[tuple[str, str]]:
    deviations: set[tuple[str, str]] = set()
    for spec_name, spec_entries in _spec_04_classes().items():
        targets = [getattr(domain, n) for n in SPEC_TO_DOMAIN.get(spec_name, (spec_name,))]
        if issubclass(targets[0], Enum):
            members = {m.name: m.value for m in targets[0]}
            for name in spec_entries.keys() | members.keys():
                if spec_entries.get(name) != members.get(name):
                    deviations.add((spec_name, name))
            continue
        for name, spec_default in spec_entries.items():
            owner = next((t for t in targets if name in t.model_fields), None)
            if owner is None or _domain_default(owner, name) != spec_default:
                deviations.add((spec_name, name))
        for target in targets:
            for name in target.model_fields.keys() - spec_entries.keys():
                deviations.add((target.__name__, name))
    return deviations


def _ledger_deviation_rows() -> list[list[str]]:
    lines = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("## Contract Deviations"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    rows = [line.strip() for line in lines[start + 1 : end] if line.strip().startswith("|")]
    body = [row for row in rows[1:] if not re.match(r"^\|[\s:|-]+\|$", row)]
    return [[cell.strip().strip("`") for cell in row.strip("|").split("|")] for row in body]


def test_req_7_7_every_spec_04_deviation_has_a_ledger_row() -> None:
    rows = _ledger_deviation_rows()
    for row in rows:
        assert len(row) == 6, row
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[5]), row
        assert row[4], row
    recorded = set()
    for row in rows:
        recorded.add((row[0], row[1]))
        for spec_name, domain_names in SPEC_TO_DOMAIN.items():
            if row[0] == spec_name:
                recorded.update((d, row[1]) for d in domain_names)
    missing = sorted(_required_deviations() - recorded)
    assert missing == []
