"""U-01: metric semantics, rather than universal metadata completeness."""

import pytest
from tests.unit.test_benchmark_eligibility import complete_record
from tests.unit.test_performance import _inp, _perf, _query, _rec

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import BenchmarkMetric, BenchmarkSet
from ai_tco_dss.engines.resolver import evidence_gaps, select_benchmark
from ai_tco_dss.services import calibration_report as cr


@pytest.mark.parametrize(
    "field",
    [
        "nodes",
        "accelerator_memory_gb",
        "system_ram_gb",
        "runtime",
        "runtime_version",
        "model_revision",
        "quantization",
        "kv_precision",
        "prompt_cache_hit_rate",
        "speculative_mode",
        "concurrency",
        "protocol",
        "cache_state",
        "residency",
    ],
)
@pytest.mark.parametrize("metric", [BenchmarkMetric.DECODE_TPS, BenchmarkMetric.PREFILL_TPS])
def test_missing_physical_execution_facts_still_exclude_observations(field, metric):
    record = complete_record(metric=metric)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={field: None})}
    )
    assert f"conditions.{field} missing" in evidence_gaps(record)
    assert select_benchmark(_query((record,), metric=metric, conditions=record.conditions)) is None
    assert cr.skip_reason(record, (record.hardware_id,), (record.model_id,)) is not None


@pytest.mark.parametrize("metric", [BenchmarkMetric.PREFILL_TPS, BenchmarkMetric.TTFT_S])
def test_input_phase_metrics_do_not_require_output_length(metric):
    record = complete_record(metric=metric)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"output_tokens": None})}
    )
    query = _query((record,), metric=metric, conditions=record.conditions)
    assert evidence_gaps(record) == ()
    assert select_benchmark(query) == record


@pytest.mark.parametrize("metric", [BenchmarkMetric.DECODE_TPS, BenchmarkMetric.AGGREGATE_TPS])
def test_generation_metrics_still_require_output_length(metric):
    record = complete_record(metric=metric)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"output_tokens": None})}
    )
    assert "conditions.output_tokens missing" in evidence_gaps(record)
    assert select_benchmark(_query((record,), metric=metric, conditions=record.conditions)) is None


def test_disabled_speculation_has_no_required_drafter_configuration():
    record = complete_record()
    query = _query((record,), conditions=record.conditions)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"speculative_config": None})}
    )
    assert (
        select_benchmark(query.model_copy(update={"records": BenchmarkSet(records=(record,))}))
        == record
    )
    enabled = record.model_copy(
        update={
            "conditions": record.conditions.model_copy(update={"speculative_mode": "built-in-mtp"})
        }
    )
    assert "conditions.speculative_config missing" in evidence_gaps(enabled)


@pytest.mark.parametrize(
    "metric",
    [
        BenchmarkMetric.DECODE_TPS,
        BenchmarkMetric.PREFILL_TPS,
        BenchmarkMetric.TTFT_S,
        BenchmarkMetric.AGGREGATE_TPS,
    ],
)
def test_app_backend_multiplier_is_not_a_runtime_measurement_fact(metric):
    record = complete_record(metric=metric)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"optimized_backend": None})}
    )
    query = _query(
        (record,),
        metric=metric,
        conditions=record.conditions.model_copy(update={"optimized_backend": False}),
    )
    assert select_benchmark(query) == record
    if metric in cr.CALIBRATION_METRICS:
        assert cr.skip_reason(record, (record.hardware_id,), (record.model_id,)) is None


def test_measured_prefill_is_not_penalized_again_by_formula_backend_multiplier():
    repo = get_default_repository()
    record = _rec(BenchmarkMetric.PREFILL_TPS, 1000)
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"optimized_backend": False})}
    )
    inp = _inp(repo, records=(record,), enable_optimized_backend=False)
    result = _perf(inp)
    assert result.prefill_tps.origin.origin == "measured"
    expected = inp.workload.t_in_hat * (1 - inp.profile.prompt_cache_hit_rate) / 1000
    assert result.ttft_s.value == pytest.approx(expected)


def test_measured_prefill_is_not_penalized_again_in_eviction_cost():
    from tests.unit.test_tco import PARAMS, _base

    from ai_tco_dss.domain import ValueOrigin
    from ai_tco_dss.engines.tco import compute_tco

    inp = _base()
    prefill = inp.performance.prefill_tps.model_copy(
        update={"origin": ValueOrigin(origin="measured", source_ids=("synthetic-prefill",))}
    )
    inp = inp.model_copy(
        update={
            "sizing": inp.sizing.model_copy(update={"context_eviction_risk": True}),
            "performance": inp.performance.model_copy(update={"prefill_tps": prefill}),
        }
    )
    fast = dict(compute_tco(inp, PARAMS).monthly_opex)["eviction_loss"]
    inp = inp.model_copy(
        update={"options": inp.options.model_copy(update={"enable_optimized_backend": False})}
    )
    slow = dict(compute_tco(inp, PARAMS).monthly_opex)["eviction_loss"]
    assert slow == pytest.approx(fast)


def test_ttft_matches_workload_prompt_instead_of_decode_context():
    repo = get_default_repository()
    inp = _inp(repo)
    assert abs(inp.workload.t_in_hat - 8192) > 8192 * 0.25
    wrong = _rec(BenchmarkMetric.TTFT_S, 0.123, context_tokens=8192)
    actual = _rec(BenchmarkMetric.TTFT_S, 4.2, context_tokens=round(inp.workload.t_in_hat))
    result = _perf(inp.model_copy(update={"benchmarks": BenchmarkSet(records=(wrong, actual))}))
    assert result.ttft_s.origin.origin == "measured"
    assert result.ttft_s.value == 4.2


def test_eviction_does_not_reuse_a_ttft_record_without_rebuild_measurement():
    repo = get_default_repository()
    inp = _inp(repo)
    records = tuple(
        _rec(BenchmarkMetric.TTFT_S, 0.123, context_tokens=tokens)
        for tokens in (8192, round(inp.workload.t_in_hat))
    )
    inp = inp.model_copy(
        update={
            "sizing": inp.sizing.model_copy(update={"context_eviction_risk": True}),
            "benchmarks": BenchmarkSet(records=records),
        }
    )
    result = _perf(inp)
    assert result.ttft_s.origin.origin == "formula"


def test_prompt_beyond_documented_capacity_is_not_eligible():
    record = complete_record(configured_context_tokens=4096)
    assert any("configured" in gap for gap in evidence_gaps(record))
    assert select_benchmark(_query((record,), conditions=record.conditions)) is None


def test_calibration_without_app_backend_flag_preserves_unknown_fact():
    record = complete_record()
    record = record.model_copy(
        update={"conditions": record.conditions.model_copy(update={"optimized_backend": None})}
    )
    assert (
        cr.formula_value(record, get_default_repository().catalog(), cr.load_engine_parameters())
        is not None
    )
    assert record.conditions.optimized_backend is None


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"concurrency": 2}, "concurrent"),
        ({"prompt_cache_hit_rate": 0.5}, "uncached"),
        ({"speculative_mode": "built-in-mtp", "speculative_config": "depth=3"}, "speculative"),
        ({"residency": "offload"}, "offload"),
        ({"quantization": "oQ4e"}, "uniform"),
    ],
)
def test_measurement_match_does_not_imply_formula_support(changes, reason):
    record = complete_record()
    record = record.model_copy(update={"conditions": record.conditions.model_copy(update=changes)})
    assert select_benchmark(_query((record,), conditions=record.conditions)) == record
    assert reason in cr.skip_reason(record, (record.hardware_id,), (record.model_id,))


def test_capacity_is_separate_from_actual_prompt_and_does_not_supply_it():
    record = complete_record(configured_context_tokens=131072)
    assert select_benchmark(_query((record,), conditions=record.conditions)) == record
    report = cr.calibrate(get_default_repository().catalog(), cr.load_engine_parameters())
    assert [(item.count, item.skipped, item.mape) for item in report.metrics] == [
        (0, 12, None),
        (0, 1, None),
    ]
