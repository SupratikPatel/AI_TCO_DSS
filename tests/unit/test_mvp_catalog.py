"""Curated MVP catalog (Req 8.2, 10.1 to 10.11)."""

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from ai_tco_dss.catalog import loading, validate
from ai_tco_dss.domain import LicenseType

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
LEDGER = ROOT / "specs" / "07_DATA_CORRECTIONS.md"

OPEN_MODELS = {
    "gemma-4-12b",
    "qwen-3-8-27b",
    "qwen-3-6-35b-a3b",
    "gpt-oss-120b",
    "qwen-3-8-flash-next",
    "glm-5-3-flash",
    "deepseek-v4-1-flash",
    "kimi-k3-1-pro",
}
API_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5", "gpt-6-1", "gemini-3-1-pro"}
NODE_COUNTS = {
    "rtx-5060-ti-16gb": [1],
    "rtx-5070-strata-64gb": [1],
    "mac-mini-m5-pro-64gb": [1],
    "mac-studio-m5-max-128gb": [1],
    "mac-studio-m5-ultra-256gb": [1],
    "amd-strix-halo-128gb": [1],
    "dgx-spark-128gb": [1, 2, 4],
    "rtx-pro-6000-96gb": [1, 4, 8],
    "h100-80gb-sxm": [8],
}
QUALITY_METRICS = {"aa_index_v5", "terminal_bench", "swe_bench"}
ERROR_LINE = re.compile(r"^(?P<path>\S+\.json): (?P<field>\S*): (?P<message>.+)$")


def _json(rel: str) -> Any:
    return json.loads((DATA / rel).read_text(encoding="utf-8"))


def _registry() -> dict[str, str]:
    return {s["source_id"]: s["tier"] for s in _json("sources.json")["sources"]}


def _model(model_id: str) -> Any:
    return _json(f"catalog/models/{model_id}.json")


def _ledger_rows() -> list[list[str]]:
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| C-\d{3} \|", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def _assert_provenance(node: dict[str, Any], registry: dict[str, str]) -> None:
    assert node["source_id"] in registry, node
    assert node["tier"] == registry[node["source_id"]], node
    assert date.fromisoformat(node["accessed"]) <= date.today()


# --------------------------------------------------------------------------- item sets


def test_req_10_1_10_3_exactly_the_mvp_model_files() -> None:
    stems = {p.stem for p in (DATA / "catalog" / "models").glob("*.json")}
    assert stems == OPEN_MODELS | API_MODELS
    for model_id in OPEN_MODELS:
        assert _model(model_id)["type"] == "open-weights", model_id
    for model_id in API_MODELS:
        assert _model(model_id)["type"] == "commercial-api", model_id


def test_req_10_4_exactly_the_mvp_hardware_files() -> None:
    stems = {p.stem for p in (DATA / "catalog" / "hardware").glob("*.json")}
    assert stems == set(NODE_COUNTS)


def test_req_10_5_valid_node_counts() -> None:
    for hardware_id, expected in NODE_COUNTS.items():
        item = _json(f"catalog/hardware/{hardware_id}.json")
        assert sorted(item["valid_node_counts"]["value"]) == expected, hardware_id


def test_data_root_loads_without_errors() -> None:
    report = loading.load_catalog(DATA, mvp=True)
    assert report.errors == [], report.errors
    assert report.catalog is not None


# --------------------------------------------------------------------------- models


def test_req_10_2_gpt_oss_is_moe_117b_total_5_1b_active() -> None:
    registry = _registry()
    model = _model("gpt-oss-120b")
    assert model["architecture"] == "moe"
    assert model["total_parameters_billions"]["value"] == 117
    assert model["active_parameters_billions"]["value"] == 5.1
    _assert_provenance(model["total_parameters_billions"], registry)
    _assert_provenance(model["active_parameters_billions"], registry)


def test_open_models_have_parameter_counts_with_provenance() -> None:
    registry = _registry()
    for model_id in OPEN_MODELS:
        model = _model(model_id)
        for name in ("total_parameters_billions", "active_parameters_billions"):
            assert model[name]["value"] > 0, (model_id, name)
            _assert_provenance(model[name], registry)
        assert (
            model["active_parameters_billions"]["value"]
            <= (model["total_parameters_billions"]["value"])
        )


def test_req_10_3_api_prices_positive_usd_official() -> None:
    registry = _registry()
    for model_id in API_MODELS:
        prices = _model(model_id)["api_prices"]
        for name in ("input_per_1m", "output_per_1m", "cache_read_per_1m"):
            price = prices[name]
            assert price["value"] > 0, (model_id, name)
            assert price["currency"] == "USD", (model_id, name)
            assert price["tier"] == "official", (model_id, name)
            _assert_provenance(price, registry)


def test_req_10_7_license_types_non_empty_and_known() -> None:
    """The `eu_commercial_license_valid` flag itself is set by the Sizing_Engine (Req 19.2,
    19.6) from `license_type`; the catalog must carry a known, non-empty license type."""
    allowed = {member.value for member in LicenseType}
    for model_id in OPEN_MODELS | API_MODELS:
        license_type = _model(model_id).get("license_type")
        assert license_type, model_id
        assert license_type in allowed, (model_id, license_type)
    for model_id in API_MODELS:
        assert _model(model_id)["license_type"] == LicenseType.COMMERCIAL_PROPRIETARY.value


def test_req_10_8_quality_scores_in_range_registered_and_never_zero() -> None:
    registry = _registry()
    records = _json("benchmarks/quality.json")["records"]
    seen: set[tuple[str, str]] = set()
    for record in records:
        assert record["metric"] in QUALITY_METRICS, record
        assert record["model_id"] in OPEN_MODELS | API_MODELS, record
        assert 0 < record["value"] <= 100, record
        _assert_provenance(record, registry)
        key = (record["metric"], record["model_id"])
        assert key not in seen, f"duplicate quality record {key}"
        seen.add(key)
    by_key = {(r["metric"], r["model_id"]): r["value"] for r in records}
    assert by_key[("aa_index_v5", "qwen-3-8-27b")] == pytest.approx(20.1)
    assert by_key[("terminal_bench", "qwen-3-8-27b")] == pytest.approx(73.0)
    assert by_key[("aa_index_v5", "claude-opus-5-5")] > by_key[("aa_index_v5", "kimi-k3-1-pro")]


# --------------------------------------------------------------------------- rentals


@pytest.mark.parametrize(
    ("rental_id", "gpus", "monthly", "setup"),
    [("hetzner-gex63", 1, 999, 999), ("hetzner-gex430", 4, 3599, 3599)],
)
def test_req_10_6_hetzner_rentals(rental_id: str, gpus: int, monthly: float, setup: float) -> None:
    registry = _registry()
    rentals = {r["id"]: r for r in _json("reference/rentals.json")["rentals"]}
    rental = rentals[rental_id]
    assert rental["gpu_hardware_id"] == "rtx-pro-6000-96gb"
    assert rental["gpu_count"]["value"] == gpus
    for name, expected in (("monthly_price", monthly), ("setup_fee", setup)):
        assert rental[name]["value"] == expected
        assert rental[name]["currency"] == "EUR"
        _assert_provenance(rental[name], registry)


# --------------------------------------------------------------------------- ledger


def _row(area_part: str) -> list[str]:
    for row in _ledger_rows():
        if area_part in row[2]:
            return row
    raise AssertionError(f"no ledger entry for {area_part}")


def _assert_sources_registered(cell: str) -> None:
    registry = _registry()
    ids = [part.strip() for part in cell.split(",") if part.strip()]
    assert ids
    for source_id in ids:
        assert source_id in registry, source_id


def test_req_10_9_ledger_entry_gpt_oss() -> None:
    row = _row("gpt-oss-120b architecture")
    assert date.fromisoformat(row[1])
    assert row[3] == "dense"
    assert "mixture-of-experts (117B total, 5.1B active)" in row[4]
    _assert_sources_registered(row[5])


def test_req_10_10_ledger_entry_gex63() -> None:
    row = _row("Hetzner GEX63 monthly price")
    assert date.fromisoformat(row[1])
    assert "€1,197" in row[3]
    assert "€999" in row[4]
    _assert_sources_registered(row[5])


# --------------------------------------------------------------------------- registry tiers


def test_req_8_2_youtube_and_industry_source_tiers() -> None:
    registry = _registry()
    for number in (*range(1, 13), *range(16, 23)):
        assert registry[f"YT-{number:02d}"] == "community"
    expected = {
        "IND-01": "third_party",
        "IND-02": "third_party",
        "IND-03": "official",
        "IND-04": "official",
        "IND-05": "third_party",
        "IND-06": "official",
        "IND-07": "official",
        "IND-08": "official",
        "IND-09": "official",
        "IND-10": "community",
    }
    for source_id, tier in expected.items():
        assert registry[source_id] == tier, source_id


# --------------------------------------------------------------------------- validator


@pytest.fixture
def data_copy(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(DATA, target)
    return target


def _run(root: Path, capsys: pytest.CaptureFixture[str], *flags: str) -> tuple[int, list[str]]:
    code = validate.main(["--root", str(root), *flags])
    out = capsys.readouterr()
    return code, (out.out + out.err).strip().splitlines()


def _has_error(lines: list[str], *parts: str) -> bool:
    for line in lines:
        if ERROR_LINE.match(line.replace("\\", "/")) and all(p in line for p in parts):
            return True
    return False


def test_req_10_11_repository_data_root_validates(capsys: pytest.CaptureFixture[str]) -> None:
    code, lines = _run(DATA, capsys)
    assert code == 0, lines


def test_req_10_11_missing_mvp_model_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (data_copy / "catalog" / "models" / "gpt-oss-120b.json").unlink()
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "gpt-oss-120b", "missing MVP item"), lines


def test_req_10_11_missing_mvp_hardware_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (data_copy / "catalog" / "hardware" / "h100-80gb-sxm.json").unlink()
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "h100-80gb-sxm", "missing MVP item"), lines


def test_req_10_11_mvp_rules_do_not_run_for_other_roots(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (data_copy / "catalog" / "models" / "gpt-oss-120b.json").unlink()
    code, lines = _run(data_copy, capsys)
    assert code == 0, lines


def test_req_10_11_missing_parameter_count_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = data_copy / "catalog" / "models" / "gpt-oss-120b.json"
    model = json.loads(path.read_text(encoding="utf-8"))
    model.pop("active_parameters_billions")
    path.write_text(json.dumps(model), encoding="utf-8")
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "gpt-oss-120b", "active_parameters_billions"), lines


def test_req_10_11_non_official_api_price_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = data_copy / "catalog" / "models" / "gpt-6-1.json"
    model = json.loads(path.read_text(encoding="utf-8"))
    model["api_prices"]["output_per_1m"].update(
        source_id="ASSUMPTION-MVP", tier="assumption", accessed="2026-11-07"
    )
    path.write_text(json.dumps(model), encoding="utf-8")
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "gpt-6-1", "api_prices.output_per_1m", "official"), lines


def test_req_10_11_wrong_node_counts_are_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = data_copy / "catalog" / "hardware" / "dgx-spark-128gb.json"
    item = json.loads(path.read_text(encoding="utf-8"))
    item["valid_node_counts"]["value"] = [1, 2, 4, 8]
    path.write_text(json.dumps(item), encoding="utf-8")
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "dgx-spark-128gb", "valid_node_counts"), lines


def test_req_10_8_zero_quality_score_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = data_copy / "benchmarks" / "quality.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"][0]["value"] = 0
    path.write_text(json.dumps(data), encoding="utf-8")
    code, lines = _run(data_copy, capsys, "--mvp")
    assert code == 1
    assert _has_error(lines, "quality.json", "records[0].value"), lines


def test_req_10_8_quality_score_above_100_is_reported(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = data_copy / "benchmarks" / "quality.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["records"][0]["value"] = 101
    path.write_text(json.dumps(data), encoding="utf-8")
    code, lines = _run(data_copy, capsys)
    assert code == 1
    assert _has_error(lines, "quality.json", "records[0].value"), lines
