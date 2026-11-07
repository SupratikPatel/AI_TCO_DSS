"""Reference data, default workload, use cases, presets and popularity (Req 13.1 to 13.6,
14.1, 31.2, 31.3, 32.1 to 32.6, 32.8)."""

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from ai_tco_dss.catalog import validate

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
LEDGER = ROOT / "specs" / "07_DATA_CORRECTIONS.md"
CRITERIA = ("tco_60m", "quality", "effective_tps", "ttft", "risk", "popularity")
ERROR_LINE = re.compile(r"^(?P<path>\S+\.json): (?P<field>\S*): (?P<message>.+)$")


def _json(rel: str) -> Any:
    return json.loads((DATA / rel).read_text(encoding="utf-8"))


def _registry() -> dict[str, str]:
    return {s["source_id"]: s["tier"] for s in _json("sources.json")["sources"]}


def _assert_provenance(node: dict[str, Any]) -> None:
    registry = _registry()
    assert node["source_id"] in registry, node
    assert node["tier"] == registry[node["source_id"]], node
    assert date.fromisoformat(node["accessed"]) <= date.today()


# --------------------------------------------------------------------------- 13.1


def test_req_13_1_electricity_tariffs() -> None:
    tariffs = {t["id"]: t["price_per_kwh"] for t in _json("reference/electricity.json")["tariffs"]}
    assert set(tariffs) == {"de-industrial-bdew", "de-office", "eu-nordic"}
    expected = {"de-industrial-bdew": 0.172, "de-office": 0.280, "eu-nordic": 0.095}
    for tariff_id, price in tariffs.items():
        assert price["value"] == pytest.approx(expected[tariff_id])
        assert price["currency"] == "EUR"
        assert 0 < price["value"] <= 1.0
        _assert_provenance(price)


# --------------------------------------------------------------------------- 13.2, 13.6


def _hubs() -> dict[str, Any]:
    return {h["id"]: h for h in _json("reference/staffing_hubs.json")["hubs"]}


def test_req_13_2_staffing_hubs() -> None:
    hubs = _hubs()
    assert set(hubs) == {
        "de-munich-hq",
        "de-berlin-hamburg",
        "ro-cluj-bucharest",
        "pl-warsaw-krakow",
    }
    for hub in hubs.values():
        assert hub["base_salary"]["value"] > 0
        assert hub["base_salary"]["currency"] == "EUR"
        assert 0 <= hub["employer_social_tax_pct"]["value"] <= 100
        delay = hub["recruiting_delay_months"]["value"]
        assert isinstance(delay, int) and 0 <= delay <= 24
        for name in ("base_salary", "employer_social_tax_pct", "recruiting_delay_months"):
            _assert_provenance(hub[name])


def _ledger_row(area_part: str) -> list[str]:
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| C-\d{3} \|", line):
            row = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if area_part in row[2]:
                return row
    raise AssertionError(f"no ledger entry for {area_part}")


def test_req_13_6_romania_tax_matches_ledger_choice() -> None:
    row = _ledger_row("Romania employer tax")
    assert "2.25 %" in row[3] and "4 %" in row[3]
    assert date.fromisoformat(row[1])
    chosen = float(re.search(r"([\d.]+) %", row[4]).group(1))  # type: ignore[union-attr]
    registry = _registry()
    for source_id in (s.strip() for s in row[5].split(",")):
        assert source_id in registry, source_id
    assert _hubs()["ro-cluj-bucharest"]["employer_social_tax_pct"]["value"] == chosen == 2.25


# --------------------------------------------------------------------------- 13.3


def test_req_13_3_harness_scaffolding_tokens() -> None:
    harnesses = {
        h["id"]: h["scaffolding_tokens_per_turn"]
        for h in _json("reference/harnesses.json")["harnesses"]
    }
    expected = {"claude-code": 33000, "codex": 13000, "opencode": 7000, "deepseek-dsh": 4200}
    for harness_id, tokens in expected.items():
        assert harnesses[harness_id]["value"] == tokens
        _assert_provenance(harnesses[harness_id])
    lean = harnesses["custom-lean"]
    assert lean["tier"] == "assumption"
    assert isinstance(lean["value"], int) and 0 <= lean["value"] <= 100_000
    _assert_provenance(lean)


# --------------------------------------------------------------------------- 13.4, 31.2, 31.3


def test_req_13_4_31_2_31_3_use_cases() -> None:
    use_cases = {u["id"]: u for u in _json("reference/use_cases.json")["use_cases"]}
    expected = {
        "writing-email": ("aa_index_v5", None),
        "summarisation-rag": ("aa_index_v5", None),
        "coding-assistant": ("terminal_bench", "swe_bench"),
        "agentic-coding": ("terminal_bench", "swe_bench"),
    }
    assert set(use_cases) == set(expected)
    for use_case_id, (matching, second) in expected.items():
        use_case = use_cases[use_case_id]
        assert use_case["matching_benchmark"] == matching
        assert use_case["second_choice_benchmark"] == second
        floor = use_case["quality_floor"]
        assert 0 <= floor["value"] <= 100
        assert floor["tier"] == "assumption"
        _assert_provenance(floor)


# --------------------------------------------------------------------------- 13.5


def test_req_13_5_rentals() -> None:
    rentals = {r["id"]: r for r in _json("reference/rentals.json")["rentals"]}
    hardware = {p.stem for p in (DATA / "catalog" / "hardware").glob("*.json")}
    expected = {"hetzner-gex63": (1, 999, 999), "hetzner-gex430": (4, 3599, 3599)}
    for rental_id, (gpus, monthly, setup) in expected.items():
        rental = rentals[rental_id]
        assert rental["gpu_hardware_id"] == "rtx-pro-6000-96gb"
        assert rental["gpu_count"]["value"] == gpus
        assert rental["monthly_price"]["value"] == monthly
        assert rental["setup_fee"]["value"] == setup
        assert rental["monthly_price"]["currency"] == rental["setup_fee"]["currency"] == "EUR"
    for rental in rentals.values():
        assert rental["gpu_hardware_id"] in hardware, rental["id"]
        assert isinstance(rental["gpu_count"]["value"], int) and rental["gpu_count"]["value"] >= 1
        assert rental["monthly_price"]["value"] > 0, rental["id"]
        assert "setup_fee" in rental and rental["setup_fee"]["value"] >= 0, rental["id"]
        for name in ("gpu_count", "monthly_price", "setup_fee", "system_ram_total_installed_gb"):
            _assert_provenance(rental[name])


# --------------------------------------------------------------------------- 14.1


def test_req_14_1_default_workload() -> None:
    workload = _json("workloads/default.json")
    assert workload["tier"] == "assumption"
    _assert_provenance(workload)
    profile = workload["profile"]
    assert profile["active_users"] == 25
    assert profile["daily_requests_per_user"] == 40
    assert profile["avg_input_tokens"] == 15000
    assert profile["avg_output_tokens"] == 1500
    assert profile["working_days_per_month"] == 22


# --------------------------------------------------------------------------- 32.1 to 32.5


def _presets() -> dict[str, Any]:
    return {p["id"]: p for p in _json("reference/presets.json")["presets"]}


def test_req_32_1_presets_are_valid_weight_vectors() -> None:
    presets = _presets()
    assert set(presets) == {"cheapest", "best-fit", "most-capable", "popular"}
    for preset in presets.values():
        weights = preset["weights"]
        assert set(weights) == set(CRITERIA)
        assert all(0 <= weights[c] <= 1 for c in CRITERIA)
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-6)
        assert preset["tier"] == "assumption"
        _assert_provenance(preset)


@pytest.mark.parametrize(
    ("preset_id", "criterion"),
    [("cheapest", "tco_60m"), ("most-capable", "quality"), ("popular", "popularity")],
)
def test_req_32_2_to_32_4_dominant_criterion(preset_id: str, criterion: str) -> None:
    weights = _presets()[preset_id]["weights"]
    assert all(weights[criterion] > weights[c] for c in CRITERIA if c != criterion)


def test_req_32_5_best_fit_all_positive() -> None:
    assert all(w > 0 for w in _presets()["best-fit"]["weights"].values())


# --------------------------------------------------------------------------- 32.6


def test_req_32_6_popularity_snapshot() -> None:
    snapshot = _json("reference/popularity.json")
    assert date.fromisoformat(snapshot["snapshot_date"])
    _assert_provenance(snapshot)
    assert snapshot["tier"] != "assumption"
    entries = snapshot["entries"]
    assert entries
    model_ids = [e["model_id"] for e in entries]
    assert len(model_ids) == len(set(model_ids))
    catalog_models = {p.stem for p in (DATA / "catalog" / "models").glob("*.json")}
    for entry in entries:
        assert entry["model_id"] in catalog_models
        assert entry["value"] >= 0


# --------------------------------------------------------------------------- 32.8 wiring


@pytest.fixture
def data_copy(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(DATA, target)
    return target


def _edit(root: Path, rel: str, change: Any) -> None:
    path = root / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def _errors(root: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, list[str]]:
    code = validate.main(["--root", str(root)])
    out = capsys.readouterr()
    lines = [line.replace("\\", "/") for line in (out.out + out.err).splitlines()]
    return code, [line for line in lines if ERROR_LINE.match(line)]


def test_req_32_8_preset_sum_violation(data_copy: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(
        data_copy, "reference/presets.json", lambda d: d["presets"][1]["weights"].update(risk=0.5)
    )
    code, errors = _errors(data_copy, capsys)
    assert code == 1
    assert any("presets.json" in e and "best-fit" in e for e in errors), errors


def test_req_32_8_preset_dominance_violation(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def change(d: Any) -> None:
        cheapest = next(p for p in d["presets"] if p["id"] == "cheapest")
        cheapest["weights"].update(tco_60m=0.15, quality=0.50)

    _edit(data_copy, "reference/presets.json", change)
    code, errors = _errors(data_copy, capsys)
    assert code == 1
    assert any("presets.json" in e and "cheapest" in e for e in errors), errors


def test_req_32_8_negative_preset_weight(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def change(d: Any) -> None:
        popular = next(p for p in d["presets"] if p["id"] == "popular")
        popular["weights"].update(risk=-0.10, popularity=0.60)

    _edit(data_copy, "reference/presets.json", change)
    code, errors = _errors(data_copy, capsys)
    assert code == 1
    assert any("presets.json" in e and "popular" in e for e in errors), errors


def test_req_32_8_duplicate_popularity_model(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(
        data_copy, "reference/popularity.json", lambda d: d["entries"].append(dict(d["entries"][0]))
    )
    code, errors = _errors(data_copy, capsys)
    first = _json("reference/popularity.json")["entries"][0]["model_id"]
    assert code == 1
    assert any("popularity.json" in e and first in e and "duplicate" in e for e in errors), errors


def test_req_32_8_negative_popularity_value(
    data_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(data_copy, "reference/popularity.json", lambda d: d["entries"][0].update(value=-1))
    code, errors = _errors(data_copy, capsys)
    first = _json("reference/popularity.json")["entries"][0]["model_id"]
    assert code == 1
    assert any("popularity.json" in e and first in e for e in errors), errors
