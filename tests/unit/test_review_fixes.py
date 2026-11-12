"""Post-MVP review regressions: context, cost parity, coverage and provenance."""

import pytest

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import InMemoryCatalogRepository, get_default_repository
from ai_tco_dss.domain import RecommendRequest, ScenarioRequest, Sourced
from ai_tco_dss.services import evaluate_scenario, recommend


def test_requested_context_rejects_unsupported_models():
    s = default_scenario()
    s = s.model_copy(
        update={"sizing": s.sizing.model_copy(update={"target_context_length": 1000000})}
    )
    r = recommend(RecommendRequest(scenario=s))
    assert r.ranked
    assert all(c.evaluation.model_max_context_tokens >= 1000000 for c in r.ranked)


def test_reference_latency_ranking_timeline_parity():
    repo = get_default_repository()
    cat = repo.catalog()
    models = tuple(
        m.model_copy(
            update={
                "api_ttft_s": Sourced[float](
                    value=2, source_id="ASSUMPTION-MVP", tier="assumption", accessed="2026-11-07"
                )
            }
        )
        if m.id == cat.baseline_defaults.reference_api_model_id
        else m
        for m in cat.models
    )
    memory = InMemoryCatalogRepository(
        cat.model_copy(update={"models": models}), repo.load_workload()
    )
    s = default_scenario()
    s = s.model_copy(
        update={"financials": s.financials.model_copy(update={"include_wait_time_penalty": True})}
    )
    r = evaluate_scenario(ScenarioRequest(scenario=s), repo=memory)
    c = next(
        c.evaluation
        for c in r.recommendation.ranked
        if c.evaluation.candidate_id == r.timeline.anchor_candidate_id
    )
    assert c.cost_60m == pytest.approx(r.timeline.points[-1].on_prem_cumulative)


def test_missing_api_evidence_is_visible():
    r = recommend(RecommendRequest(scenario=default_scenario()))
    assert any("API" in w and "missing" in w for w in r.warnings)


def test_744_hours_produces_local_costs():
    s = default_scenario()
    s = s.model_copy(
        update={"workload": s.workload.model_copy(update={"active_hours_per_month": 744})}
    )
    r = recommend(RecommendRequest(scenario=s))
    assert any(c.evaluation.kind == "onprem" for c in r.ranked)


def test_derived_latency_is_formula():
    from tests.unit.test_performance import PREFILL, _inp, _perf, _rec

    result = _perf(_inp(get_default_repository(), records=(_rec(metric=PREFILL, value=1200),)))
    assert result.ttft_s.origin.origin == "formula"


def test_hybrid_anchor_meets_quality_floor():
    r = recommend(RecommendRequest(scenario=default_scenario()))
    hybrids = [c for c in r.rejected if c.kind == "hybrid"]
    assert hybrids
    assert all(c.components[0].quality.value >= 55 for c in hybrids)


def test_total_budget_excludes_expensive_rentals():
    s = default_scenario()
    s = s.model_copy(
        update={
            "decision": s.decision.model_copy(update={"use_case": "writing-email"}),
            "financials": s.financials.model_copy(update={"max_tco_budget_usd": 400000}),
        }
    )
    r = recommend(RecommendRequest(scenario=s))
    assert r.ranked
    assert all(c.evaluation.cost_60m <= 400000 for c in r.ranked)
    assert any(f.name == "tco_budget" for c in r.rejected for f in c.failures)


def test_audit_rejects_changed_catalog():
    from ai_tco_dss.domain.errors import EngineInputError
    from ai_tco_dss.services.audit_export import AuditRequest, candidate_audit

    repo = get_default_repository()
    r = evaluate_scenario(ScenarioRequest(scenario=default_scenario()))
    cat = repo.catalog()
    hw = cat.hardware[0]
    changed = hw.model_copy(update={"name": hw.name + " changed"})
    memory = InMemoryCatalogRepository(
        cat.model_copy(update={"hardware": (changed, *cat.hardware[1:])}), repo.load_workload()
    )
    with pytest.raises(EngineInputError, match="snapshot"):
        candidate_audit(
            AuditRequest(result=r, candidate_id=r.recommendation.ranked[0].evaluation.candidate_id),
            repo=memory,
        )


def test_writing_does_not_pay_for_excess_performance_by_default():
    s = default_scenario()
    s = s.model_copy(
        update={"decision": s.decision.model_copy(update={"use_case": "writing-email"})}
    )
    r = recommend(RecommendRequest(scenario=s))
    assert r.ranked[0].evaluation.cost_60m < 400000


def test_excess_performance_is_an_explicit_preference():
    s = default_scenario()
    s = s.model_copy(
        update={
            "decision": s.decision.model_copy(
                update={"use_case": "writing-email", "reward_excess_performance": True}
            )
        }
    )
    r = recommend(RecommendRequest(scenario=s))
    assert r.ranked[0].evaluation.kind == "rental"
    assert r.ranked[0].evaluation.cost_60m > 1000000


def test_backend_factor_changes_eviction_wait_component():
    from tests.unit.test_tco import PARAMS, _base

    from ai_tco_dss.engines.tco import compute_tco

    inp = _base()
    inp = inp.model_copy(
        update={"sizing": inp.sizing.model_copy(update={"context_eviction_risk": True})}
    )
    fast = compute_tco(inp, PARAMS)
    slow = compute_tco(
        inp.model_copy(
            update={"options": inp.options.model_copy(update={"enable_optimized_backend": False})}
        ),
        PARAMS,
    )
    assert dict(slow.monthly_opex)["eviction_loss"] > dict(fast.monthly_opex)["eviction_loss"]
