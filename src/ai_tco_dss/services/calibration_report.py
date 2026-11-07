"""Calibration_Report: ``uv run ai-tco-calibrate [--root DIR] [--output FILE]``
(Req 42.1 to 42.7; design.md § "Service Layer").

Compares the formula value of the Performance_Engine (measured lookup disabled) with the
measured value of every decode/prefill Benchmark_Record, prints the record count, MAPE
and top-5 list per metric and writes the same values to a CSV file for the thesis.
"""

import argparse
import csv
import sys
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ai_tco_dss.catalog import JsonCatalogRepository
from ai_tco_dss.domain import (
    BenchmarkMetric,
    BenchmarkRecord,
    BenchmarkSet,
    Catalog,
    EngineParameters,
    PerformanceInput,
    SizingInput,
    SizingOptions,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines import compute_performance, compute_workload, size_deployment
from ai_tco_dss.settings import load_engine_parameters

CALIBRATION_METRICS = (BenchmarkMetric.DECODE_TPS, BenchmarkMetric.PREFILL_TPS)
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = REPOSITORY_ROOT / "specs" / "07_DATA_CORRECTIONS.md"
LEDGER_SECTION = "## Calibration Known Deviations"
DEFAULT_ROOT = Path("data")
DEFAULT_OUTPUT = Path("reports") / "calibration.csv"
TOP_N = 5
NOT_AVAILABLE = "n/a"
CSV_COLUMNS = (
    "metric",
    "row",
    "model_id",
    "hardware_id",
    "source_id",
    "measured",
    "formula",
    "ape_pct",
    "count",
    "skipped",
    "mape_pct",
)

type DeviationKey = tuple[str, str, str | None, str]


@dataclass(frozen=True)
class Outcome:
    kind: Literal["pass", "xfail", "fail"]
    reason: str | None


@dataclass(frozen=True)
class ComparedRecord:
    record: BenchmarkRecord
    formula: float
    ape: float


@dataclass(frozen=True)
class MetricReport:
    metric: BenchmarkMetric
    count: int
    skipped: int
    mape: float | None
    top: tuple[ComparedRecord, ...]
    skip_reasons: tuple[str, ...]


@dataclass(frozen=True)
class CalibrationReport:
    metrics: tuple[MetricReport, ...]


def absolute_percentage_error(formula: float, measured: float) -> float:
    """|formula - measured| / measured * 100 (Req 42.2)."""
    return abs(formula - measured) / measured * 100


def classify(ape: float, tolerance: float, ledger_id: str | None) -> Outcome:
    """pass if APE ≤ tolerance, else xfail if listed in the ledger, else fail (Req 42.3)."""
    if ape <= tolerance:
        return Outcome("pass", None)
    if ledger_id is not None:
        return Outcome("xfail", f"known calibration deviation {ledger_id}")
    return Outcome("fail", None)


def skip_reason(
    record: BenchmarkRecord, hardware_ids: Collection[str], model_ids: Collection[str]
) -> str | None:
    """Why a record cannot be compared, naming model_id, source_id and the field (Req 42.6)."""
    prefix = f"{record.metric.value} record {record.model_id} ({record.source_id})"
    if record.hardware_id is None:
        return f"{prefix}: hardware_id is missing"
    if record.hardware_id not in hardware_ids:
        return f"{prefix}: hardware_id {record.hardware_id} is not in the catalog"
    if record.model_id not in model_ids:
        return f"{prefix}: model_id {record.model_id} is not in the catalog"
    if record.value <= 0:
        return f"{prefix}: value {record.value} is <= 0"
    return None


def formula_value(
    record: BenchmarkRecord, catalog: Catalog, params: EngineParameters
) -> float | None:
    """The Performance_Engine formula value for the record's hardware, model, precision and
    context (defaults where absent), with measured lookup disabled (Req 42.1). One node."""
    hardware = next(h for h in catalog.hardware if h.id == record.hardware_id)
    model = next(m for m in catalog.models if m.id == record.model_id)
    defaults = SizingOptions()
    precision = record.precision or defaults.weight_precision
    options = SizingOptions(
        weight_precision=precision,
        target_context_length=record.context_tokens or defaults.target_context_length,
    )
    profile = WorkloadProfile()
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), params
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=precision,
            requested_nodes=1,
            options=options,
            profile=profile,
            license_alternatives=(),
        ),
        params,
    )
    performance = compute_performance(
        PerformanceInput(
            hardware=hardware,
            model=model,
            precision=precision,
            sizing=sizing,
            workload=workload,
            profile=profile,
            options=options,
            benchmarks=BenchmarkSet(records=()),
            use_measured=False,
        ),
        params,
    )
    metric = (
        performance.decode_tps
        if record.metric == BenchmarkMetric.DECODE_TPS
        else performance.prefill_tps
    )
    return None if metric is None else metric.value


def build_report(
    items: Iterable[tuple[BenchmarkRecord, float | None]],
    hardware_ids: Collection[str],
    model_ids: Collection[str],
) -> CalibrationReport:
    """Count, skipped count, MAPE and top-5 list per calibration metric (Req 42.4, 42.6)."""
    entries = list(items)
    metrics = []
    for metric in CALIBRATION_METRICS:
        compared: list[ComparedRecord] = []
        reasons: list[str] = []
        for record, formula in entries:
            if record.metric != metric:
                continue
            reason = skip_reason(record, hardware_ids, model_ids)
            if reason is None and formula is None:
                reason = f"{metric.value} record {record.model_id} ({record.source_id}): "
                reason += "formula value is not available"
            if reason is not None:
                reasons.append(reason)
                continue
            assert formula is not None
            ape = absolute_percentage_error(formula, record.value)
            compared.append(ComparedRecord(record, formula, ape))
        mape = sum(c.ape for c in compared) / len(compared) if compared else None
        ranked = sorted(
            compared, key=lambda c: (-c.ape, c.record.model_id, c.record.hardware_id or "")
        )
        metrics.append(
            MetricReport(
                metric=metric,
                count=len(compared),
                skipped=len(reasons),
                mape=mape,
                top=tuple(ranked[:TOP_N]),
                skip_reasons=tuple(reasons),
            )
        )
    return CalibrationReport(metrics=tuple(metrics))


def _mape_text(mape: float | None) -> str:
    return NOT_AVAILABLE if mape is None else f"{mape:.1f}"


def _row_values(row: ComparedRecord) -> dict[str, str]:
    return {
        "model_id": row.record.model_id,
        "hardware_id": row.record.hardware_id or "",
        "source_id": row.record.source_id,
        "measured": f"{row.record.value:.1f}",
        "formula": f"{row.formula:.1f}",
        "ape_pct": f"{row.ape:.1f}",
    }


def report_lines(report: CalibrationReport) -> list[str]:
    """The printed report: one summary line per metric, its top list and skipped records."""
    lines = ["Calibration report: formula vs measured (APE = |formula - measured| / measured)"]
    for item in report.metrics:
        mape = _mape_text(item.mape)
        suffix = "" if item.mape is None else " %"
        lines.append(
            f"{item.metric.value}: {item.count} records compared, {item.skipped} skipped, "
            f"MAPE {mape}{suffix}"
        )
        for rank, row in enumerate(item.top, start=1):
            v = _row_values(row)
            lines.append(
                f"  {rank}. {v['model_id']} on {v['hardware_id']} ({v['source_id']}): "
                f"measured {v['measured']}, formula {v['formula']}, APE {v['ape_pct']} %"
            )
        lines.extend(f"  skipped: {reason}" for reason in item.skip_reasons)
    return lines


def write_csv(report: CalibrationReport, path: Path) -> None:
    """Per metric one summary row and one row per top-list record (Req 42.5)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, restval="")
        writer.writeheader()
        for item in report.metrics:
            writer.writerow(
                {
                    "metric": item.metric.value,
                    "row": "summary",
                    "count": str(item.count),
                    "skipped": str(item.skipped),
                    "mape_pct": _mape_text(item.mape),
                }
            )
            for rank, row in enumerate(item.top, start=1):
                writer.writerow({"metric": item.metric.value, "row": str(rank), **_row_values(row)})


def load_known_deviations(path: Path) -> dict[DeviationKey, str]:
    """(metric, model_id, hardware_id, source_id) → ledger entry id of the table
    "Calibration Known Deviations" in the Corrections_Ledger (Req 42.3)."""
    text = path.read_text(encoding="utf-8")
    start = text.find(LEDGER_SECTION)
    if start < 0:
        return {}
    known: dict[DeviationKey, str] = {}
    for line in text[start + len(LEDGER_SECTION) :].splitlines():
        if line.startswith("## "):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].startswith("C-"):
            continue
        entry_id, metric, model_id, hardware_id, source_id = cells[:5]
        known[(metric, model_id, hardware_id or None, source_id)] = entry_id
    return known


def calibrate(catalog: Catalog, params: EngineParameters) -> CalibrationReport:
    """Formula values for every decode/prefill record of the catalog, then the report."""
    hardware_ids = {h.id for h in catalog.hardware}
    model_ids = {m.id for m in catalog.models}
    items: list[tuple[BenchmarkRecord, float | None]] = []
    for record in catalog.benchmarks:
        if record.metric not in CALIBRATION_METRICS:
            continue
        valid = skip_reason(record, hardware_ids, model_ids) is None
        items.append((record, formula_value(record, catalog, params) if valid else None))
    return build_report(items, hardware_ids, model_ids)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare formula and measured TPS values.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="data directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV file")
    args = parser.parse_args(argv)
    report = calibrate(JsonCatalogRepository(args.root).catalog(), load_engine_parameters())
    for line in report_lines(report):
        print(line)
    write_csv(report, args.output)
    print(f"Wrote {args.output.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
