"""Property tests for the calibration outcome and the Calibration_Report builder
(Properties 59 and 60). Oracles are written independently of
`services/calibration_report.py`."""

from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.domain import BenchmarkMetric, BenchmarkRecord, SourceTier
from ai_tco_dss.services import calibration_report as cr

HW = ("hw-a", "hw-b")
MODELS = ("model-a", "model-b")
METRICS = (BenchmarkMetric.DECODE_TPS, BenchmarkMetric.PREFILL_TPS)


@given(
    ape=st.floats(min_value=0.0, max_value=1_000.0),
    tolerance=st.floats(min_value=0.01, max_value=200.0),
    listed=st.booleans(),
)
def test_property_59_calibration_outcome_classification(
    ape: float, tolerance: float, listed: bool
) -> None:
    """Property 59: pass if e ≤ t, xfail with the ledger id if e > t and listed, else fail.

    Validates: Requirements 42.3.
    """
    ledger_id = "C-099" if listed else None
    outcome = cr.classify(ape, tolerance, ledger_id)
    if ape <= tolerance:
        assert outcome.kind == "pass"
    elif listed:
        assert outcome.kind == "xfail"
        assert outcome.reason is not None and "C-099" in outcome.reason
    else:
        assert outcome.kind == "fail"


@st.composite
def items(draw: st.DrawFn) -> tuple[BenchmarkRecord, float | None]:
    record = BenchmarkRecord(
        metric=draw(st.sampled_from(METRICS)),
        value=draw(st.sampled_from([0.0, -1.0]) | st.floats(min_value=0.5, max_value=500.0)),
        model_id=draw(st.sampled_from([*MODELS, "ghost-model"])),
        hardware_id=draw(st.sampled_from([*HW, "ghost-hw", None])),
        context_tokens=8_192,
        source_id=draw(st.sampled_from(["S1", "S2", "S3"])),
        tier=SourceTier.COMMUNITY,
        accessed=date(2026, 11, 7),
    )
    formula = draw(st.none() | st.floats(min_value=0.5, max_value=500.0))
    return record, formula


def _valid(record: BenchmarkRecord, formula: float | None) -> bool:
    return (
        record.hardware_id in HW
        and record.model_id in MODELS
        and record.value > 0
        and formula is not None
    )


@given(entries=st.lists(items(), max_size=12))
def test_property_60_calibration_report_builder(
    entries: list[tuple[BenchmarkRecord, float | None]],
) -> None:
    """Property 60: counts, MAPE and the top list cover only valid records; skipped records
    are counted per metric; the top list holds min(5, n) records by APE descending, then
    model_id, then hardware_id.

    Validates: Requirements 42.4, 42.6.
    """
    report = cr.build_report(entries, HW, MODELS)
    assert [m.metric for m in report.metrics] == list(METRICS)
    for item in report.metrics:
        mine = [(r, f) for r, f in entries if r.metric == item.metric]
        valid = [(r, f) for r, f in mine if _valid(r, f)]
        apes = [abs(f - r.value) / r.value * 100 for r, f in valid if f is not None]
        assert item.count == len(valid)
        assert item.skipped == len(mine) - len(valid)
        if valid:
            assert item.mape is not None
            assert abs(item.mape - sum(apes) / len(apes)) <= 1e-9 * max(1.0, item.mape)
        else:
            assert item.mape is None
        assert len(item.top) == min(5, len(valid))
        expected_keys = sorted(
            ((-ape, r.model_id, r.hardware_id) for (r, _), ape in zip(valid, apes, strict=True)),
        )[: len(item.top)]
        actual_keys = [(-row.ape, row.record.model_id, row.record.hardware_id) for row in item.top]
        for (e_ape, e_model, e_hw), (a_ape, a_model, a_hw) in zip(
            expected_keys, actual_keys, strict=True
        ):
            assert abs(e_ape - a_ape) <= 1e-9 * max(1.0, abs(e_ape))
            assert (e_model, e_hw) == (a_model, a_hw)
