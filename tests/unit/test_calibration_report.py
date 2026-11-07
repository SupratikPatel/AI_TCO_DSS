"""Calibration_Report CLI and its building blocks (Req 42.1 to 42.7)."""

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from ai_tco_dss.catalog import JsonCatalogRepository, get_default_repository
from ai_tco_dss.domain import BenchmarkMetric, BenchmarkRecord, PrecisionFormat, SizingOptions
from ai_tco_dss.services import calibration_report as cr
from ai_tco_dss.settings import load_engine_parameters

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "catalog_min"
PARAMS = load_engine_parameters()
DECODE = BenchmarkMetric.DECODE_TPS
PREFILL = BenchmarkMetric.PREFILL_TPS
HW = ("hw-a", "hw-b", "hw-c")
MODELS = ("model-a", "model-b")


def _rec(
    value: float,
    *,
    metric: BenchmarkMetric = DECODE,
    model_id: str = "model-a",
    hardware_id: str | None = "hw-a",
    source_id: str = "SRC",
    precision: str | None = "INT4",
    context_tokens: int | None = 8_192,
) -> BenchmarkRecord:
    return BenchmarkRecord.model_validate(
        {
            "metric": metric.value,
            "value": value,
            "model_id": model_id,
            "hardware_id": hardware_id,
            "precision": precision,
            "context_tokens": context_tokens,
            "source_id": source_id,
            "tier": "community",
            "accessed": "2026-11-07",
        }
    )


def _metric(report: cr.CalibrationReport, metric: BenchmarkMetric) -> cr.MetricReport:
    return next(m for m in report.metrics if m.metric == metric)


# --------------------------------------------------------------------------- building blocks


def test_req_42_2_absolute_percentage_error() -> None:
    assert cr.absolute_percentage_error(130.0, 100.0) == pytest.approx(30.0)
    assert cr.absolute_percentage_error(70.0, 100.0) == pytest.approx(30.0)


@pytest.mark.parametrize(
    ("ape", "ledger_id", "kind", "reason"),
    [
        (30.0, None, "pass", None),  # equal to the tolerance passes
        (30.0, "C-099", "pass", None),
        (30.01, "C-099", "xfail", "C-099"),
        (30.01, None, "fail", None),
    ],
)
def test_req_42_3_outcome_classification(
    ape: float, ledger_id: str | None, kind: str, reason: str | None
) -> None:
    outcome = cr.classify(ape, 30.0, ledger_id)
    assert outcome.kind == kind
    if reason is None:
        assert outcome.reason is None or kind == "fail"
    else:
        assert outcome.reason is not None and reason in outcome.reason


@pytest.mark.parametrize(
    ("record", "field"),
    [
        (_rec(10.0, hardware_id=None), "hardware_id"),
        (_rec(10.0, hardware_id="ghost-hw"), "hardware_id"),
        (_rec(10.0, model_id="ghost-model"), "model_id"),
        (_rec(0.0), "value"),
        (_rec(-1.0), "value"),
    ],
)
def test_req_42_6_skip_reason_names_model_source_and_field(
    record: BenchmarkRecord, field: str
) -> None:
    reason = cr.skip_reason(record, HW, MODELS)
    assert reason is not None
    assert record.model_id in reason
    assert record.source_id in reason
    assert field in reason


def test_req_42_6_valid_record_has_no_skip_reason() -> None:
    assert cr.skip_reason(_rec(10.0), HW, MODELS) is None


def test_req_42_1_formula_value_ignores_measured_records() -> None:
    """The formula path runs with measured lookup disabled, so a matching record in the
    catalog does not change the formula value."""
    catalog = get_default_repository().catalog()
    record = next(
        r
        for r in catalog.benchmarks
        if r.metric == DECODE
        and r.hardware_id == "mac-mini-m5-pro-64gb"
        and r.model_id == "qwen-3-8-27b"
    )
    hardware = next(h for h in catalog.hardware if h.id == record.hardware_id)
    model = next(m for m in catalog.models if m.id == record.model_id)
    assert model.active_parameters_billions is not None
    expected = (
        hardware.memory_bandwidth_gbs.value
        / (model.active_parameters_billions.value * 4 / 8 * 1.05)
        * 0.70
    )
    value = cr.formula_value(record, catalog, PARAMS)
    assert value == pytest.approx(expected, rel=1e-9)
    assert value != record.value


def test_req_42_1_formula_value_uses_defaults_for_absent_precision_and_context() -> None:
    catalog = get_default_repository().catalog()
    base = dict(model_id="qwen-3-8-27b", hardware_id="mac-mini-m5-pro-64gb")
    defaults = SizingOptions()
    absent = cr.formula_value(
        _rec(10.0, precision=None, context_tokens=None, **base), catalog, PARAMS
    )
    explicit = cr.formula_value(
        _rec(
            10.0,
            precision=defaults.weight_precision.value,
            context_tokens=defaults.target_context_length,
            **base,
        ),
        catalog,
        PARAMS,
    )
    assert defaults.weight_precision == PrecisionFormat.INT4
    assert absent == pytest.approx(explicit)


def test_req_42_1_prefill_formula_value_is_the_base_prefill() -> None:
    catalog = get_default_repository().catalog()
    hardware = next(h for h in catalog.hardware if h.id == "mac-mini-m5-pro-64gb")
    assert hardware.base_prefill_tps_at_32k is not None
    record = _rec(1000.0, metric=PREFILL, model_id="qwen-3-8-27b", hardware_id=hardware.id)
    assert cr.formula_value(record, catalog, PARAMS) == hardware.base_prefill_tps_at_32k.value


# --------------------------------------------------------------------------- report builder


def _items() -> list[tuple[BenchmarkRecord, float | None]]:
    return [
        (_rec(100.0, model_id="model-b", hardware_id="hw-a", source_id="S1"), 110.0),  # 10
        (_rec(100.0, model_id="model-a", hardware_id="hw-b", source_id="S2"), 150.0),  # 50
        (_rec(100.0, model_id="model-a", hardware_id="hw-a", source_id="S3"), 50.0),  # 50
        (_rec(200.0, model_id="model-a", hardware_id="hw-c", source_id="S4"), 210.0),  # 5
        (_rec(10.0, model_id="model-b", hardware_id="hw-b", source_id="S5"), 12.0),  # 20
        (_rec(10.0, model_id="model-b", hardware_id="hw-c", source_id="S6"), 13.0),  # 30
        (_rec(10.0, model_id="model-b", hardware_id=None, source_id="S7"), None),  # skipped
        (_rec(0.0, model_id="model-a", source_id="S8"), 5.0),  # skipped
        (_rec(500.0, metric=PREFILL, model_id="ghost", source_id="S9"), 400.0),  # skipped
    ]


def test_req_42_4_counts_mape_and_top_five() -> None:
    report = cr.build_report(_items(), HW, MODELS)
    decode = _metric(report, DECODE)
    assert decode.count == 6
    assert decode.skipped == 2
    assert decode.mape == pytest.approx((10 + 50 + 50 + 5 + 20 + 30) / 6)
    assert [row.record.source_id for row in decode.top] == ["S3", "S2", "S6", "S5", "S1"]
    assert [round(row.ape, 6) for row in decode.top] == [50.0, 50.0, 30.0, 20.0, 10.0]
    first = decode.top[0]
    assert (first.record.model_id, first.record.hardware_id) == ("model-a", "hw-a")
    assert first.formula == 50.0
    prefill = _metric(report, PREFILL)
    assert (prefill.count, prefill.skipped, prefill.mape, prefill.top) == (0, 1, None, ())


def test_req_42_4_fewer_than_five_records_lists_all() -> None:
    report = cr.build_report(_items()[:2], HW, MODELS)
    assert len(_metric(report, DECODE).top) == 2


def test_req_42_4_printed_output_lists_counts_mape_and_record_fields() -> None:
    report = cr.build_report(_items(), HW, MODELS)
    text = "\n".join(cr.report_lines(report))
    assert "decode_tps: 6 records compared, 2 skipped, MAPE 27.5 %" in text
    assert "prefill_tps: 0 records compared, 1 skipped, MAPE n/a" in text
    lines = cr.report_lines(report)
    top = [line for line in lines if line.lstrip().startswith("1.")]
    assert top
    for token in ("model-a", "hw-a", "S3", "100.0", "50.0"):
        assert token in top[0]


def test_req_42_5_csv_holds_the_printed_values(tmp_path: Path) -> None:
    report = cr.build_report(_items(), HW, MODELS)
    path = tmp_path / "out" / "calibration.csv"
    cr.write_csv(report, path)
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    text = "\n".join(cr.report_lines(report))
    summaries = {r["metric"]: r for r in rows if r["row"] == "summary"}
    assert summaries["decode_tps"]["count"] == "6"
    assert summaries["decode_tps"]["skipped"] == "2"
    assert summaries["decode_tps"]["mape_pct"] == "27.5"
    assert summaries["prefill_tps"]["count"] == "0"
    assert summaries["prefill_tps"]["mape_pct"] == "n/a"
    top = [r for r in rows if r["metric"] == "decode_tps" and r["row"] != "summary"]
    assert [r["row"] for r in top] == ["1", "2", "3", "4", "5"]
    assert [r["source_id"] for r in top] == ["S3", "S2", "S6", "S5", "S1"]
    for row in top:
        line = next(line for line in text.splitlines() if f"({row['source_id']})" in line)
        for key in ("model_id", "hardware_id", "measured", "formula", "ape_pct"):
            assert row[key] in line, (key, row, line)


def test_req_42_7_zero_records_report_count_0_and_mape_not_available(tmp_path: Path) -> None:
    report = cr.build_report([], HW, MODELS)
    for metric in (DECODE, PREFILL):
        item = _metric(report, metric)
        assert (item.count, item.skipped, item.mape, item.top) == (0, 0, None, ())
    lines = cr.report_lines(report)
    assert "decode_tps: 0 records compared, 0 skipped, MAPE n/a" in lines
    path = tmp_path / "calibration.csv"
    cr.write_csv(report, path)
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert [(r["metric"], r["count"], r["mape_pct"]) for r in rows] == [
        ("decode_tps", "0", "n/a"),
        ("prefill_tps", "0", "n/a"),
    ]


# --------------------------------------------------------------------------- CLI


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    shutil.copytree(FIXTURE, root)
    return root


def _decode_file(root: Path, records: list[dict[str, Any]]) -> None:
    (root / "benchmarks" / "decode.json").write_text(
        json.dumps({"records": records}), encoding="utf-8"
    )


def test_req_42_7_cli_on_a_catalog_without_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "reports" / "calibration.csv"
    code = cr.main(["--root", str(FIXTURE), "--output", str(output)])
    out = capsys.readouterr().out
    assert code == 0
    assert "decode_tps: 0 records compared, 0 skipped, MAPE n/a" in out
    assert "prefill_tps: 0 records compared, 0 skipped, MAPE n/a" in out
    assert output.is_file()


def test_req_42_4_cli_prints_and_writes_the_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _copy_fixture(tmp_path)
    base = {
        "metric": "decode_tps",
        "model_id": "qwen-3-8-27b",
        "hardware_id": "rtx-pro-6000-96gb",
        "precision": "INT4",
        "context_tokens": 8192,
        "tier": "community",
        "accessed": "2026-11-07",
        "note": "single-source",
    }
    _decode_file(
        root,
        [
            {**base, "value": 80.0, "source_id": "YT-02"},
            {**base, "value": 100.0, "source_id": "YT-01"},
            {**base, "value": 0.0, "source_id": "YT-03"},
        ],
    )
    output = tmp_path / "calibration.csv"
    code = cr.main(["--root", str(root), "--output", str(output)])
    out = capsys.readouterr().out
    assert code == 0
    # formula: 1800 / (27 x 0.5 x 1.05) x 0.70 = 88.889; APE 11.1 % and 11.1 %
    assert "decode_tps: 2 records compared, 1 skipped, MAPE 11.1 %" in out
    assert "YT-03" in out  # the skipped record is named with its reason
    repo = JsonCatalogRepository(root)
    assert len(repo.catalog().benchmarks) == 3 + 3
    with output.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert {r["row"] for r in rows if r["metric"] == "decode_tps"} == {"summary", "1", "2"}


# --------------------------------------------------------------------------- ledger table


def test_req_42_3_known_deviations_are_parsed_from_the_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.md"
    ledger.write_text(
        "# Ledger\n\n## Calibration Known Deviations\n"
        "| Entry ID | metric | model_id | hardware_id | source_id | Reason |\n"
        "|---|---|---|---|---|---|\n"
        "| C-099 | decode_tps | model-a | hw-a | S1 | too fast |\n\n"
        "## Assumptions\n| Name | Value |\n|---|---|\n| x | 1 |\n",
        encoding="utf-8",
    )
    assert cr.load_known_deviations(ledger) == {("decode_tps", "model-a", "hw-a", "S1"): "C-099"}


def test_req_42_3_repository_ledger_entries_name_existing_records_and_entries() -> None:
    known = cr.load_known_deviations(cr.LEDGER_PATH)
    catalog = get_default_repository().catalog()
    keys = {
        (r.metric.value, r.model_id, r.hardware_id, r.source_id)
        for r in catalog.benchmarks
        if r.metric in cr.CALIBRATION_METRICS
    }
    ledger = cr.LEDGER_PATH.read_text(encoding="utf-8")
    for key, entry_id in known.items():
        assert key in keys, key
        assert f"| {entry_id} | " in ledger.split("## Contract Deviations")[0], entry_id
