"""Workload_Engine and workload loading (Req 14.2, 14.3, 14.4, 14.6, 14.7, 15.8)."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from ai_tco_dss.catalog import (
    InMemoryCatalogRepository,
    JsonCatalogRepository,
    get_default_repository,
)
from ai_tco_dss.domain import (
    HarnessEntry,
    HarnessType,
    ModelSpec,
    Sourced,
    SourceTier,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import EngineInputError, WorkloadFileError
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.services import load_workload
from ai_tco_dss.settings import load_engine_parameters

REL = 1e-9
PARAMS = load_engine_parameters()


@pytest.fixture(scope="module")
def repo() -> JsonCatalogRepository:
    return get_default_repository()


def _model(repo: JsonCatalogRepository, model_id: str) -> ModelSpec:
    return next(m for m in repo.catalog().models if m.id == model_id)


def _run(repo: JsonCatalogRepository, model_id: str, profile: WorkloadProfile | None = None) -> Any:
    catalog = repo.catalog()
    inp = WorkloadInput(
        profile=profile or repo.load_workload(),
        model=_model(repo, model_id),
        harnesses=catalog.harnesses,
    )
    return compute_workload(inp, PARAMS)


# --------------------------------------------------------------------------- reference values


def test_req_14_4_default_workload_reference_values_non_claude(repo: JsonCatalogRepository) -> None:
    """Req 14.4, 15.1 to 15.7: Default_Workload_File with a non-Claude model (design.md)."""
    result = _run(repo, "qwen-3-8-27b")
    assert result.monthly_requests == 22_000
    assert result.kappa_mega == pytest.approx(1.98, rel=REL)
    assert result.s_effective == pytest.approx(33_000, rel=REL)
    assert result.tau == 1.0
    assert result.t_in_hat == pytest.approx(48_000, rel=REL)
    assert result.t_out_hat == pytest.approx(1_500, rel=REL)
    assert result.out_think == pytest.approx(3_750, rel=REL)
    assert result.nu_verify == 1.0
    assert result.monthly_tokens == pytest.approx(2_254_230_000, rel=REL)
    assert result.monthly_output_demand == pytest.approx(82_500_000, rel=REL)


def test_req_15_2_default_workload_reference_values_claude(repo: JsonCatalogRepository) -> None:
    """Req 15.2: the Claude tokenizer inflates input and output tokens by 1.30."""
    result = _run(repo, "claude-sonnet-5-5")
    assert result.tau == 1.30
    assert result.t_in_hat == pytest.approx(62_400, rel=REL)
    assert result.out_think == pytest.approx(4_875, rel=REL)
    assert result.monthly_tokens == pytest.approx(2_930_499_000, rel=REL)


def test_req_15_1_mcp_pruning_and_verification(repo: JsonCatalogRepository) -> None:
    """Req 15.1, 15.4: pruning keeps 25 % of the scaffolding; the verifier doubles volume."""
    base = repo.load_workload()
    profile = base.model_copy(
        update={"mcp_code_mode_pruning": True, "has_verification_agent_layer": True}
    )
    result = _run(repo, "qwen-3-8-27b", profile)
    assert result.s_effective == pytest.approx(8_250, rel=REL)
    assert result.nu_verify == 2.0
    expected = 22_000 * (15_000 + 8_250 + 3_750) * 1.98 * 2.0
    assert result.monthly_tokens == pytest.approx(expected, rel=REL)


def test_req_15_1_custom_lean_uses_profile_tokens(repo: JsonCatalogRepository) -> None:
    profile = repo.load_workload().model_copy(
        update={"harness_type": HarnessType.CUSTOM_LEAN, "custom_scaffolding_tokens": 1_234}
    )
    assert _run(repo, "qwen-3-8-27b", profile).s_effective == pytest.approx(1_234, rel=REL)


# --------------------------------------------------------------------------- field bounds


def test_req_14_2_working_days_default_and_bounds() -> None:
    assert WorkloadProfile().working_days_per_month == 22
    assert WorkloadProfile(working_days_per_month=1).working_days_per_month == 1
    assert WorkloadProfile(working_days_per_month=31).working_days_per_month == 31
    for bad in (0, 32):
        with pytest.raises(ValidationError, match="working_days_per_month"):
            WorkloadProfile(working_days_per_month=bad)


@pytest.mark.parametrize(
    ("field", "low", "high"),
    [
        ("active_users", 1, 100_000),
        ("daily_requests_per_user", 1, 10_000),
        ("avg_input_tokens", 1, 1_000_000),
        ("avg_output_tokens", 1, 200_000),
    ],
)
def test_req_14_6_workload_field_bounds(field: str, low: int, high: int) -> None:
    assert getattr(WorkloadProfile(**{field: low}), field) == low
    assert getattr(WorkloadProfile(**{field: high}), field) == high
    for bad in (low - 1, high + 1):
        with pytest.raises(ValidationError, match=field):
            WorkloadProfile(**{field: bad})


def test_req_15_8_invalid_profile_names_each_field() -> None:
    """Req 15.8: mega ratio, negative tokens and unknown thinking preset are rejected."""
    with pytest.raises(ValidationError) as info:
        WorkloadProfile.model_validate(
            {
                "mega_session_ratio": 1.5,
                "avg_input_tokens": -1,
                "avg_output_tokens": -5,
                "thinking_effort_preset": "maximum",
            }
        )
    fields = {str(e["loc"][0]) for e in info.value.errors()}
    assert fields == {
        "mega_session_ratio",
        "avg_input_tokens",
        "avg_output_tokens",
        "thinking_effort_preset",
    }


def test_req_15_8_negative_scaffolding_tokens_rejected(repo: JsonCatalogRepository) -> None:
    """Req 15.8: a negative S_harness from the harness table raises an engine error."""
    harnesses = tuple(
        HarnessEntry(
            id=h.id,
            scaffolding_tokens_per_turn=Sourced[int](
                value=-1, source_id="T", tier=SourceTier.ASSUMPTION, accessed="2026-11-07"
            ),
        )
        for h in repo.catalog().harnesses
    )
    inp = WorkloadInput(
        profile=repo.load_workload(), model=_model(repo, "qwen-3-8-27b"), harnesses=harnesses
    )
    with pytest.raises(EngineInputError, match="S_harness"):
        compute_workload(inp, PARAMS)


def test_req_15_8_negative_custom_scaffolding_rejected() -> None:
    with pytest.raises(ValidationError, match="custom_scaffolding_tokens"):
        WorkloadProfile(custom_scaffolding_tokens=-1)


# --------------------------------------------------------------------------- loading


def _write(path: Path, data: Any) -> Path:
    path.write_text(json.dumps(data) if not isinstance(data, str) else data, encoding="utf-8")
    return path


def _file(profile: dict[str, Any]) -> dict[str, Any]:
    return {"source_id": "T", "tier": "assumption", "accessed": "2026-11-07", "profile": profile}


def test_req_14_3_other_file_uses_only_its_values_plus_defaults(tmp_path: Path) -> None:
    path = _write(tmp_path / "w.json", _file({"active_users": 3, "daily_requests_per_user": 10}))
    profile = load_workload(path)
    assert profile.active_users == 3
    assert profile.daily_requests_per_user == 10
    defaults = WorkloadProfile()
    for name in WorkloadProfile.model_fields:
        if name not in {"active_users", "daily_requests_per_user"}:
            assert getattr(profile, name) == getattr(defaults, name), name


def test_req_14_3_default_path_returns_the_default_file() -> None:
    profile = load_workload()
    assert (profile.active_users, profile.daily_requests_per_user) == (25, 40)


def test_req_14_3_in_memory_repository_loads_other_files(
    repo: JsonCatalogRepository, tmp_path: Path
) -> None:
    path = _write(tmp_path / "w.json", _file({"active_users": 9}))
    memory = InMemoryCatalogRepository(repo.catalog(), repo.load_workload())
    assert memory.load_workload(path).active_users == 9
    assert memory.load_workload().active_users == 25


def test_req_14_7_missing_file_names_path(tmp_path: Path) -> None:
    path = tmp_path / "absent.json"
    with pytest.raises(WorkloadFileError) as info:
        load_workload(path)
    assert info.value.path == path
    assert str(path) in info.value.message


def test_req_14_7_invalid_json_names_path(tmp_path: Path) -> None:
    path = _write(tmp_path / "bad.json", "{not json")
    with pytest.raises(WorkloadFileError) as info:
        load_workload(path)
    assert str(path) in info.value.message


def test_req_14_7_out_of_range_fields_are_named(
    repo: JsonCatalogRepository, tmp_path: Path
) -> None:
    path = _write(
        tmp_path / "range.json",
        _file({"active_users": 0, "working_days_per_month": 32, "avg_output_tokens": 200_001}),
    )
    with pytest.raises(WorkloadFileError) as info:
        repo.load_workload(path)
    assert set(info.value.fields) == {
        "profile.active_users",
        "profile.working_days_per_month",
        "profile.avg_output_tokens",
    }
    for name in info.value.fields:
        assert name in info.value.message
    assert str(path) in info.value.message
