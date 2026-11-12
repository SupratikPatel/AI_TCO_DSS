"""C-054: incomplete observations must not masquerade as matched measurements."""

import pytest
from tests.unit.test_performance import _inp, _perf, _query, _rec

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import BenchmarkRecord, RecommendRequest
from ai_tco_dss.engines.resolver import select_benchmark
from ai_tco_dss.services import calibration_report as cr
from ai_tco_dss.services import recommend

CONDITIONS = dict(
    nodes=1,
    accelerator_memory_gb=64,
    system_ram_gb=0,
    runtime="test-runtime",
    runtime_version="1",
    model_revision="test-revision",
    kv_precision="FP16",
    optimized_backend=True,
    prompt_cache_hit_rate=0,
    quantization="uniform-INT4",
    speculative_mode="none",
    speculative_config="disabled",
    concurrency=1,
    protocol="single-request-decode",
    cache_state="cold",
    residency="resident",
    output_tokens=512,
)


def complete_record(**changes):
    return BenchmarkRecord.model_validate(
        {**_rec().model_dump(), "prompt_tokens": 8192, "conditions": CONDITIONS, **changes}
    )


def test_legacy_context_is_not_evidence_of_prompt_length():
    legacy = _rec().model_copy(update={"prompt_tokens": None, "conditions": None})
    assert select_benchmark(_query((legacy,))) is None
    assert "prompt_tokens" in cr.skip_reason(legacy, (_rec().hardware_id,), (_rec().model_id,))


@pytest.mark.parametrize(
    "field,value",
    [
        ("nodes", 2),
        ("accelerator_memory_gb", 128),
        ("system_ram_gb", 64),
        ("runtime", "different"),
        ("runtime_version", "2"),
        ("model_revision", "different"),
        ("kv_precision", "INT8"),
        ("prompt_cache_hit_rate", 0.5),
        ("quantization", "oQ4e"),
        ("speculative_mode", "built-in-mtp"),
        ("concurrency", 2),
        ("protocol", "aggregate"),
        ("cache_state", "warm"),
        ("residency", "offload"),
        ("output_tokens", 1024),
    ],
)
def test_every_execution_condition_must_match(field, value):
    r = complete_record()
    q = _query((r,)).model_copy(update={"conditions": r.conditions})
    assert select_benchmark(q) == r
    changed = r.conditions.model_copy(update={field: value})
    assert select_benchmark(q.model_copy(update={"conditions": changed})) is None


def test_capacity_does_not_substitute_for_prompt():
    r = complete_record(prompt_tokens=None, configured_context_tokens=8192)
    assert select_benchmark(_query((r,)).model_copy(update={"conditions": r.conditions})) is None


def test_unknown_query_conditions_and_prompt_do_not_match_complete_record():
    r = complete_record()
    query = _query((r,)).model_copy(update={"conditions": r.conditions})
    assert select_benchmark(query.model_copy(update={"conditions": None})) is None
    assert select_benchmark(query.model_copy(update={"target_context": None})) is None


def test_ineligible_observation_export_keeps_value_and_reasons(tmp_path):
    import csv

    r = complete_record(prompt_tokens=None, configured_context_tokens=131072)
    report = cr.build_report([(r, 999)], (r.hardware_id,), (r.model_id,))
    path = tmp_path / "report.csv"
    cr.write_csv(report, path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    excluded = next(row for row in rows if row["row"] == "excluded")
    assert float(excluded["measured"]) == r.value
    assert excluded["formula"] == ""
    assert "prompt_tokens" in excluded["reason"]
    assert report.metrics[0].mape is None


def test_calibration_rejects_circular_prefill_and_hardware_mismatch():
    from tests.benchmark_fixtures import conditions

    catalog = get_default_repository().catalog()
    hw = next(h for h in catalog.hardware if h.id == _rec().hardware_id)
    r = complete_record(metric="prefill_tps", source_id=hw.base_prefill_tps_at_32k.source_id)
    assert "circular" in cr.calibration_reason(r, catalog)
    r = r.model_copy(
        update={
            "conditions": conditions(
                prompt_cache_hit_rate=0, concurrency=1, accelerator_memory_gb=128
            )
        }
    )
    assert "hardware configuration" in cr.calibration_reason(r, catalog)


def test_calibration_keeps_successes_and_numerical_failures_separate():
    good = complete_record(value=100)
    bad = complete_record(value=10, source_id="independent-test")
    report = cr.build_report([(good, 110), (bad, 110)], (good.hardware_id,), (good.model_id,))
    assert report.metrics[0].count == 2
    assert {row.outcome.kind for row in report.metrics[0].compared} == {"pass", "fail"}


def test_offload_has_no_vram_only_performance_fallback():
    repo = get_default_repository()
    hw = next(h for h in repo.catalog().hardware if h.id == "rtx-5070-strata-64gb")
    p = _perf(_inp(repo, hardware=hw))
    assert p.decode_tps is None
    assert p.effective_tps is None
    assert any("offload" in w.lower() for w in p.warnings)


def test_cheapest_selects_minimum_admissible_cost():
    s = default_scenario()
    s = s.model_copy(
        update={
            "workload": s.workload.model_copy(update={"active_users": 1}),
            "decision": s.decision.model_copy(update={"preset": "cheapest"}),
        }
    )
    r = recommend(RecommendRequest(scenario=s))
    assert r.ranked[0].evaluation.cost_60m == min(c.evaluation.cost_60m for c in r.ranked)


def test_self_managed_mac_cost_is_purchase_once_plus_power():
    from tests.unit.test_tco import PARAMS, _base

    from ai_tco_dss.domain import EnterpriseFinancials
    from ai_tco_dss.engines.tco import compute_tco

    inp = _base(
        hardware_id="mac-studio-m5-ultra-256gb",
        nodes=1,
        profile=default_scenario().workload.model_copy(update={"active_users": 1}),
        financials=EnterpriseFinancials.model_validate({"cost_model": "self-managed"}),
    )
    result = compute_tco(inp, PARAMS)
    assert result.units == 1
    assert result.cost_60m == pytest.approx(
        result.capex.value + 60 * dict(result.monthly_opex)["energy"]
    )
