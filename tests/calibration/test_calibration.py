"""Calibration tests: formula against measured decode/prefill records (Req 42.1, 42.3, 42.6).

One test case per `decode_tps` / `prefill_tps` Benchmark_Record of the repository catalog.
The formula value comes from the Performance_Engine with measured lookup disabled.
Records listed in the ledger table "Calibration Known Deviations" become expected
failures with the ledger entry id as reason.
"""

import pytest

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import BenchmarkMetric, BenchmarkRecord
from ai_tco_dss.services import calibration_report as cr
from ai_tco_dss.settings import load_engine_parameters

CATALOG = get_default_repository().catalog()
PARAMS = load_engine_parameters()
TOLERANCES = dict(PARAMS.calibration_tolerance_pct)
KNOWN = cr.load_known_deviations(cr.LEDGER_PATH)
HARDWARE_IDS = {h.id for h in CATALOG.hardware}
MODEL_IDS = {m.id for m in CATALOG.models}
RECORDS = [r for r in CATALOG.benchmarks if r.metric in cr.CALIBRATION_METRICS]


def _case_id(record: BenchmarkRecord) -> str:
    return (
        f"{record.metric.value}-{record.model_id}-{record.hardware_id}-"
        f"{record.precision.value if record.precision else 'default'}-"
        f"{record.context_tokens}-{record.source_id}"
    )


def test_req_42_1_catalog_has_decode_and_prefill_records() -> None:
    metrics = {r.metric for r in RECORDS}
    assert metrics == {BenchmarkMetric.DECODE_TPS, BenchmarkMetric.PREFILL_TPS}


@pytest.mark.parametrize("record", RECORDS, ids=_case_id)
def test_req_42_1_formula_within_tolerance_of_measured(record: BenchmarkRecord) -> None:
    reason = cr.skip_reason(record, HARDWARE_IDS, MODEL_IDS)
    if reason is not None:
        pytest.skip(reason)
    formula = cr.formula_value(record, CATALOG, PARAMS)
    if formula is None:
        pytest.skip(f"{record.model_id} ({record.source_id}): no formula value")
    ape = cr.absolute_percentage_error(formula, record.value)
    tolerance = TOLERANCES[record.metric]
    key = (record.metric.value, record.model_id, record.hardware_id, record.source_id)
    outcome = cr.classify(ape, tolerance, KNOWN.get(key))
    if outcome.kind == "xfail":
        pytest.xfail(outcome.reason or "")
    assert outcome.kind == "pass", (
        f"APE {ape:.1f} % exceeds the {tolerance:.0f} % tolerance: measured {record.value}, "
        f"formula {formula:.2f}"
    )
