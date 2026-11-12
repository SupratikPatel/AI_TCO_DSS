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
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines import compute_performance, compute_workload, size_deployment
from ai_tco_dss.engines.resolver import evidence_gaps, uses_offload
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
    "status",
    "reason",
    "prompt_tokens",
    "conditions",
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
    outcome: Outcome


@dataclass(frozen=True)
class ExcludedRecord:
    record: BenchmarkRecord
    reason: str


@dataclass(frozen=True)
class MetricReport:
    metric: BenchmarkMetric
    count: int
    skipped: int
    mape: float | None
    top: tuple[ComparedRecord, ...]
    skip_reasons: tuple[str, ...]
    compared: tuple[ComparedRecord, ...]
    excluded: tuple[ExcludedRecord, ...]


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
    unsupported = list(evidence_gaps(record))
    conditions = record.conditions
    if conditions is None:
        return f"{prefix}: " + "; ".join(unsupported)
    if conditions.residency == "offload":
        unsupported.append("offload formula unavailable")
    if conditions.prompt_cache_hit_rate not in (None, 0):
        unsupported.append("calibration requires uncached prompt processing")
    if conditions.concurrency not in (None, 1):
        unsupported.append("formula does not model concurrent decode/prefill")
    if (
        conditions.quantization is not None
        and conditions.quantization != f"uniform-{record.precision}"
    ):
        unsupported.append("exact quantization not represented by uniform-bit formula")
    if conditions.speculative_mode not in (None, "none"):
        unsupported.append("speculative runtime/configuration not calibrated")
    if unsupported:
        return f"{prefix}: " + "; ".join(unsupported)
    return None


def calibration_reason(
    record: BenchmarkRecord, catalog: Catalog, params: EngineParameters | None = None
) -> str | None:
    reason = skip_reason(record, {h.id for h in catalog.hardware}, {m.id for m in catalog.models})
    if reason:
        return reason
    model = next(m for m in catalog.models if m.id == record.model_id)
    if model.type != "open-weights":
        return "local performance formula requires an open-weights model"
    assert record.prompt_tokens is not None
    if record.prompt_tokens > model.max_context_length.value:
        return "actual prompt exceeds catalog model context limit"
    hardware = next(h for h in catalog.hardware if h.id == record.hardware_id)
    conditions = record.conditions
    assert conditions is not None
    ram = hardware.system_ram_total_installed_gb
    if (
        conditions.accelerator_memory_gb != hardware.advertised_memory_gb.value
        or conditions.system_ram_gb != (ram.value if ram else 0)
        or conditions.nodes not in hardware.valid_node_counts.value
    ):
        return "hardware configuration differs from catalog"
    if uses_offload(hardware):
        return "offload formula unavailable (RAM shelf deployment)"
    base = hardware.base_prefill_tps_at_32k
    if (
        record.metric == BenchmarkMetric.PREFILL_TPS
        and base is not None
        and base.source_id == record.source_id
    ):
        return "circular prefill evidence: same source as formula input"
    try:
        inp = _formula_input(record, catalog, params or load_engine_parameters())
    except EngineInputError as exc:
        return f"current sizing/formula inputs unsupported: {exc}"
    if not inp.sizing.is_feasible:
        return f"current sizing model cannot represent resident run: {inp.sizing.oom_reason}"
    return None


def _formula_input(
    record: BenchmarkRecord, catalog: Catalog, params: EngineParameters
) -> PerformanceInput:
    """Construct the formula's deployment after static evidence checks."""
    hardware = next(h for h in catalog.hardware if h.id == record.hardware_id)
    model = next(m for m in catalog.models if m.id == record.model_id)
    assert record.precision is not None and record.prompt_tokens is not None
    assert record.conditions is not None and record.conditions.nodes is not None
    assert record.conditions.kv_precision is not None
    precision = record.precision
    options = SizingOptions(
        weight_precision=precision,
        target_context_length=record.prompt_tokens,
        performance_prompt_tokens=record.prompt_tokens,
        benchmark_conditions=record.conditions,
        kv_precision=record.conditions.kv_precision,
        # Decode and raw prefill formulas do not consume the TTFT beta multiplier.
        # Leave an unknown observation field unknown; this is a formula-only option.
        enable_optimized_backend=True,
    )
    profile = WorkloadProfile(
        active_users=1,
        peak_concurrent_requests=1,
        concurrent_agent_instances=1,
        avg_input_tokens=record.prompt_tokens,
        prompt_cache_hit_rate=0,
    )
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), params
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=precision,
            requested_nodes=record.conditions.nodes,
            options=options,
            profile=profile,
            license_alternatives=(),
        ),
        params,
    )
    return PerformanceInput(
        hardware=hardware,
        model=model,
        precision=precision,
        sizing=sizing,
        workload=workload,
        profile=profile,
        options=options,
        benchmarks=BenchmarkSet(records=()),
        use_measured=False,
    )


def formula_value(
    record: BenchmarkRecord, catalog: Catalog, params: EngineParameters
) -> float | None:
    """Formula prediction only for a representable, documented resident deployment."""
    if calibration_reason(record, catalog, params) is not None:
        return None
    performance = compute_performance(_formula_input(record, catalog, params), params)
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
    exclusion_reasons: dict[BenchmarkRecord, str] | None = None,
    params: EngineParameters | None = None,
) -> CalibrationReport:
    """Count, skipped count, MAPE and top-5 list per calibration metric (Req 42.4, 42.6)."""
    entries = list(items)
    tolerances = dict((params or load_engine_parameters()).calibration_tolerance_pct)
    known = load_known_deviations(LEDGER_PATH)
    metrics = []
    for metric in CALIBRATION_METRICS:
        compared: list[ComparedRecord] = []
        reasons: list[str] = []
        excluded: list[ExcludedRecord] = []
        for record, formula in entries:
            if record.metric != metric:
                continue
            reason = (exclusion_reasons or {}).get(record) or skip_reason(
                record, hardware_ids, model_ids
            )
            if reason is None and formula is None:
                reason = f"{metric.value} record {record.model_id} ({record.source_id}): "
                reason += "formula value is not available"
            if reason is not None:
                reasons.append(reason)
                excluded.append(ExcludedRecord(record, reason))
                continue
            assert formula is not None
            ape = absolute_percentage_error(formula, record.value)
            key = (record.metric.value, record.model_id, record.hardware_id, record.source_id)
            outcome = classify(ape, tolerances[metric], known.get(key))
            compared.append(ComparedRecord(record, formula, ape, outcome))
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
                compared=tuple(ranked),
                excluded=tuple(excluded),
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
        "status": row.outcome.kind,
        "reason": row.outcome.reason or "",
        "prompt_tokens": str(row.record.prompt_tokens),
        "conditions": row.record.conditions.model_dump_json() if row.record.conditions else "",
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
                f"measured {v['measured']}, formula {v['formula']}, "
                f"APE {v['ape_pct']} % [{v['status']}]"
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
            for rank, row in enumerate(item.compared, start=1):
                writer.writerow({"metric": item.metric.value, "row": str(rank), **_row_values(row)})
            for excluded_row in item.excluded:
                r = excluded_row.record
                writer.writerow(
                    {
                        "metric": item.metric.value,
                        "row": "excluded",
                        "model_id": r.model_id,
                        "hardware_id": r.hardware_id,
                        "source_id": r.source_id,
                        "measured": str(r.value),
                        "status": "incomplete/unsupported",
                        "reason": excluded_row.reason,
                        "prompt_tokens": r.prompt_tokens,
                        "conditions": r.conditions.model_dump_json() if r.conditions else "",
                    }
                )


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
    reasons: dict[BenchmarkRecord, str] = {}
    for record in catalog.benchmarks:
        if record.metric not in CALIBRATION_METRICS:
            continue
        reason = calibration_reason(record, catalog, params)
        if reason:
            reasons[record] = reason
        items.append((record, formula_value(record, catalog, params) if reason is None else None))
    return build_report(items, hardware_ids, model_ids, reasons, params)


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
