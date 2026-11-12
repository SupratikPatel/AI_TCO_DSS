"""Task 9 acceptance: Req 27-29, 31 and 32; independent arithmetic/filter oracles."""

import pytest

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.decision import apply_hard_filters, generate_candidates, rank_candidates
from ai_tco_dss.decision.quality import quality_ratios, resolve_quality
from ai_tco_dss.domain import (
    BenchmarkMetric,
    CandidateInput,
    CandidateKind,
    CriterionWeights,
    FilterInput,
    RankingInput,
    RankingMethod,
)
from ai_tco_dss.settings import load_engine_parameters


@pytest.fixture(scope="module")
def setup():
    catalog = get_default_repository().catalog()
    scenario = default_scenario()
    params = load_engine_parameters()
    candidates = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    return catalog, scenario, params, candidates


def test_req_27_enumeration_order_and_determinism(setup):
    catalog, scenario, params, result = setup
    expected = [
        f"onprem:{h.id}:{n}x:{m.id}:{p.value}"
        for h in sorted(catalog.hardware, key=lambda h: h.id)
        for n in sorted(set(h.valid_node_counts.value) & {1, 2, 4, 8})
        for m in sorted(catalog.models, key=lambda m: m.id)
        if m.type == "open-weights"
        for p in sorted(
            set(h.supported_native_precisions) | {v.precision for v in m.calibrated_weights_gb}
        )
    ]
    assert [c.candidate_id for c in result.candidates if c.kind == CandidateKind.ONPREM] == expected
    assert (
        len([c for c in result.candidates if c.kind == CandidateKind.RENTAL])
        == len(catalog.rentals) * 8
    )
    assert len([c for c in result.candidates if c.kind == CandidateKind.API]) == 4
    assert len([c for c in result.candidates if c.kind == CandidateKind.HYBRID]) == 4
    assert any(c.sizing and not c.sizing.is_feasible for c in result.candidates)
    assert generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params) == result
    hybrids = [c for c in result.candidates if c.kind == CandidateKind.HYBRID]
    assert all(c.components[0].quality.value >= 55 for c in hybrids)


def test_req_27_no_feasible_local_no_hybrids(setup):
    catalog, scenario, params, _ = setup
    tiny = tuple(
        h.model_copy(
            update={
                "advertised_memory_gb": h.advertised_memory_gb.model_copy(update={"value": 0.01}),
                "tuned_max_usable_memory_gb": None,
                "linux_max_usable_memory_gb": None,
                "system_ram_offload_gb": None,
            }
        )
        for h in catalog.hardware
    )
    result = generate_candidates(
        CandidateInput(catalog=catalog.model_copy(update={"hardware": tiny}), scenario=scenario),
        params,
    )
    assert not any(c.kind == CandidateKind.HYBRID for c in result.candidates)
    assert any("no feasible on-premise" in w for w in result.warnings)


def test_rental_ram_total_and_precision_selection(setup):
    catalog, _, _, result = setup
    for c in result.candidates:
        if c.kind != CandidateKind.RENTAL:
            continue
        rental = next(r for r in catalog.rentals if r.id == c.rental_id)
        assert c.sizing.usable_system_ram_gb == rental.system_ram_total_installed_gb.value
        assert c.nodes == rental.gpu_count.value


def test_req_31_quality_matching_second_scaled_missing(setup):
    catalog, _, params, _ = setup
    use_case = next(u for u in catalog.use_cases if u.id == "agentic-coding")
    aa = next(b for b in catalog.benchmarks if b.metric == BenchmarkMetric.AA_INDEX_V5)
    records = tuple(
        aa.model_copy(update={"model_id": model, "metric": metric, "value": value})
        for model, metric, value in [
            ("a", BenchmarkMetric.AA_INDEX_V5, 20),
            ("a", BenchmarkMetric.TERMINAL_BENCH, 40),
            ("b", BenchmarkMetric.AA_INDEX_V5, 10),
            ("b", BenchmarkMetric.TERMINAL_BENCH, 30),
            ("c", BenchmarkMetric.AA_INDEX_V5, 50),
            ("d", BenchmarkMetric.SWE_BENCH, 60),
        ]
    )
    cat = catalog.model_copy(update={"benchmarks": records})
    ratios = quality_ratios(cat, params)
    assert ratios[BenchmarkMetric.TERMINAL_BENCH] == 2.5
    assert resolve_quality(cat, "a", use_case, ratios, params).value == 40
    second = resolve_quality(cat, "d", use_case, ratios, params)
    assert second.value == 60 and "swe_bench" in second.fallback_note
    fallback = resolve_quality(cat, "c", use_case, ratios, params)
    assert fallback.value == 100
    assert all(s in fallback.fallback_note for s in ["aa_index_v5", "50", "2.5", "100"])
    assert resolve_quality(cat, "missing", use_case, ratios, params) is None
    assert (
        quality_ratios(cat.model_copy(update={"benchmarks": (aa,)}), params)[
            BenchmarkMetric.TERMINAL_BENCH
        ]
        == 2
    )


def valid_candidate(setup):
    _, _, _, result = setup
    c = next(c for c in result.candidates if c.kind == CandidateKind.ONPREM and c.performance)
    metric = c.performance.effective_tps.model_copy(update={"value": 100.0})
    return c.model_copy(
        update={
            "sizing": c.sizing.model_copy(
                update={
                    "is_feasible": True,
                    "eu_commercial_license_valid": True,
                    "meets_128k_agentic_context_floor": True,
                }
            ),
            "performance": c.performance.model_copy(
                update={"effective_tps": metric, "ttft_s": metric.model_copy(update={"value": 1})}
            ),
            "quality": next(x.quality for x in result.candidates if x.quality).model_copy(
                update={"value": 100}
            ),
            "utilization": 0.5,
            "capex": 100,
            "model_max_context_tokens": 128000,
            "api_has_eu_endpoint": True,
        }
    )


def filtered(c, setup, scenario=None):
    catalog, default, params, _ = setup
    use_case = next(u for u in catalog.use_cases if u.id == default.decision.use_case)
    return apply_hard_filters(
        FilterInput(candidates=(c,), scenario=scenario or default, use_case=use_case), params
    )


@pytest.mark.parametrize(
    "name",
    [
        "memory_fit",
        "eu_license",
        "eu_sovereignty",
        "min_tps",
        "max_ttft",
        "users_served",
        "context_128k",
        "quality_floor",
        "capex_budget",
    ],
)
def test_req_28_each_filter_including_hybrid_components(name, setup):
    c = valid_candidate(setup)
    assert filtered(c, setup).feasible
    if name in ("memory_fit", "eu_license", "context_128k"):
        field = {
            "memory_fit": "is_feasible",
            "eu_license": "eu_commercial_license_valid",
            "context_128k": "meets_128k_agentic_context_floor",
        }[name]
        bad = c.model_copy(update={"sizing": c.sizing.model_copy(update={field: False})})
    elif name == "eu_sovereignty":
        bad = c.model_copy(update={"kind": CandidateKind.API, "api_has_eu_endpoint": False})
    elif name in ("min_tps", "max_ttft"):
        field = "effective_tps" if name == "min_tps" else "ttft_s"
        bad = c.model_copy(update={"performance": c.performance.model_copy(update={field: None})})
    else:
        field = {
            "users_served": "utilization",
            "quality_floor": "quality",
            "capex_budget": "capex",
        }[name]
        value = {"users_served": 2, "quality_floor": None, "capex_budget": 200000}[name]
        bad = c.model_copy(update={field: value})
    result = filtered(bad, setup)
    assert [f.name for f in result.rejected[0].failures] == [name]
    assert all(f.measured and f.threshold for f in result.rejected[0].failures)
    hybrid = c.model_copy(update={"kind": CandidateKind.HYBRID, "components": (bad, c)})
    failure = filtered(hybrid, setup).rejected[0].failures
    assert [f.name for f in failure] == [name]
    assert bad.candidate_id in failure[0].measured


def test_req_28_complete_reasons_skips_non_applicable_and_rejected_order(setup):
    c = valid_candidate(setup)
    bad = c.model_copy(
        update={"quality": None, "utilization": None, "performance": None, "capex": 1e9}
    )
    assert {f.name for f in filtered(bad, setup).rejected[0].failures} == {
        "quality_floor",
        "users_served",
        "min_tps",
        "max_ttft",
        "capex_budget",
    }
    _, s, _, _ = setup
    s = s.model_copy(
        update={
            "workload": s.workload.model_copy(
                update={"min_acceptable_tps": None, "max_acceptable_ttft_seconds": None}
            ),
            "financials": s.financials.model_copy(update={"max_capex_budget_usd": None}),
        }
    )
    api = bad.model_copy(update={"kind": CandidateKind.API, "quality": c.quality})
    assert filtered(api, setup, s).feasible
    rental = c.model_copy(update={"kind": CandidateKind.RENTAL, "capex": 1e9})
    assert filtered(rental, setup).feasible


def test_req_29_saw_normalization_missing_contributions_explanation_ties(setup):
    c = valid_candidate(setup)
    a = c.model_copy(update={"candidate_id": "a", "cost_60m": 100, "risk": 0.1})
    b = c.model_copy(
        update={"candidate_id": "b", "cost_60m": 200, "risk": 0.5, "performance": None}
    )
    weights = CriterionWeights(tco_60m=2, quality=2, effective_tps=1, ttft=1, risk=1, popularity=1)
    inp = RankingInput(feasible=(b, a), weights=weights, method=RankingMethod.SAW)
    result = rank_candidates(inp, setup[2])
    assert [r.evaluation.candidate_id for r in result.ranked] == ["a", "b"]
    for row in result.ranked:
        assert len(row.criteria) == 6
        assert sum(v.contribution for v in row.criteria) == pytest.approx(row.saw_score)
        assert sum(v.weight for v in row.criteria) == 1
    assert result.ranked[0].criteria[0].normalised == 1
    assert result.ranked[1].criteria[0].normalised == 0
    assert result.ranked[1].criteria[2].missing
    assert result.ranked[1].criteria[2].normalised == 0
    assert "tco_60m 0.250" in result.explanation and "quality 0.250" in result.explanation
    assert rank_candidates(inp, setup[2]) == result
    tied = rank_candidates(
        inp.model_copy(update={"feasible": (a.model_copy(update={"candidate_id": "z"}), a)}),
        setup[2],
    )
    assert [r.evaluation.candidate_id for r in tied.ranked] == ["a", "z"]


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), 0])
def test_req_29_invalid_weights_return_error_without_mutation(value, setup):
    c = valid_candidate(setup)
    weights = CriterionWeights.model_construct(
        **dict.fromkeys(
            ["tco_60m", "quality", "effective_tps", "ttft", "risk", "popularity"], value
        )
    )
    result = rank_candidates(
        RankingInput(feasible=(c,), weights=weights, method=RankingMethod.SAW), setup[2]
    )
    assert not result.ranked and "weight" in result.ranking_error


def test_req_27_api_cost_and_risk_oracles(setup):
    catalog, scenario, params, result = setup
    global_result = generate_candidates(
        CandidateInput(
            catalog=catalog,
            scenario=scenario.model_copy(
                update={
                    "financials": scenario.financials.model_copy(
                        update={"strict_eu_sovereignty": False}
                    )
                }
            ),
        ),
        params,
    )
    global_api = {c.model_id: c for c in global_result.candidates if c.kind == CandidateKind.API}
    for c in result.candidates:
        assert 0 <= c.risk <= 1
        if c.kind == CandidateKind.API:
            expected = global_api[c.model_id].monthly_cost
            if c.api_has_eu_endpoint:
                expected = expected * 1.1 + catalog.baseline_defaults.gateway_fee_per_month.value
            assert c.monthly_cost == pytest.approx(expected)
            assert c.cost_60m == 60 * c.monthly_cost
            assert c.risk == 0.2


def test_req_28_rejected_sort_all_filters_and_context_api(setup):
    c = valid_candidate(setup)
    _, s, params, _ = setup
    catalog = setup[0]
    a = c.model_copy(update={"candidate_id": "a", "quality": None})
    b = a.model_copy(update={"candidate_id": "b"})
    worse = b.model_copy(update={"candidate_id": "0", "utilization": 2})
    result = apply_hard_filters(
        FilterInput(
            candidates=(worse, b, a),
            scenario=s,
            use_case=next(u for u in catalog.use_cases if u.id == s.decision.use_case),
        ),
        params,
    )
    assert [c.candidate_id for c in result.rejected] == ["a", "b", "0"]
    api = c.model_copy(update={"kind": CandidateKind.API, "model_max_context_tokens": 127999})
    assert [f.name for f in filtered(api, setup).rejected[0].failures] == ["context_128k"]


def test_hybrid_local_utilization_and_result_consistency(setup):
    _, scenario, _, result = setup
    onprem = {c.candidate_id: c for c in result.candidates if c.kind == CandidateKind.ONPREM}
    for c in result.candidates:
        if c.kind != CandidateKind.HYBRID:
            continue
        local, remote = c.components
        assert local.utilization == local.tco.utilization
        assert local.utilization == pytest.approx(
            onprem[c.local_candidate_id].utilization * scenario.financials.local_offload_ratio
        )
        assert c.monthly_cost == pytest.approx(
            local.monthly_cost + (1 - scenario.financials.local_offload_ratio) * remote.monthly_cost
        )


def test_missing_quality_has_explicit_note_and_unavailable_measurement(setup):
    c = valid_candidate(setup).model_copy(update={"quality": None})
    failure = filtered(c, setup).rejected[0].failures[0]
    assert failure.measured == "not available"
    assert any(
        "no quality score available" in note for note in filtered(c, setup).rejected[0].notes
    )


def test_rental_highest_bit_feasible_and_smallest_footprint_fallback(setup):
    from ai_tco_dss.decision.candidates import BITS, precisions
    from ai_tco_dss.domain import SizingInput
    from ai_tco_dss.engines import size_deployment

    catalog, scenario, params, result = setup
    for c in result.candidates:
        if c.kind != CandidateKind.RENTAL:
            continue
        rental = next(r for r in catalog.rentals if r.id == c.rental_id)
        hw = next(h for h in catalog.hardware if h.id == c.hardware_id)
        model = next(m for m in catalog.models if m.id == c.model_id)
        hw = hw.model_copy(
            update={
                "system_ram_total_installed_gb": rental.system_ram_total_installed_gb.model_copy(
                    update={"value": rental.system_ram_total_installed_gb.value / c.nodes}
                )
            }
        )
        choices = [
            size_deployment(
                SizingInput(
                    hardware=hw,
                    model=model,
                    precision=p,
                    requested_nodes=c.nodes,
                    options=scenario.sizing,
                    profile=scenario.workload,
                    license_alternatives=(),
                ),
                params,
            )
            for p in precisions(hw, model)
        ]
        feasible = [s for s in choices if s.is_feasible]
        peak_feasible = [
            s
            for s in feasible
            if s.max_concurrent_users >= scenario.workload.peak_concurrent_requests
        ]
        if feasible:
            assert dict(BITS)[c.precision] == max(
                dict(BITS)[s.precision] for s in (peak_feasible or feasible)
            )
        else:
            assert c.sizing.weights.value == min(s.weights.value for s in choices)


@pytest.mark.parametrize("kind", ["api", "rental", "onprem"])
def test_per_candidate_engine_error_is_rejected_not_a_partial_success_or_abort(kind, setup):
    catalog, scenario, params, _ = setup
    if kind == "api":
        model = next(m for m in catalog.models if m.type == "commercial-api")
        bad = model.model_copy(
            update={
                "api_prices": model.api_prices.model_copy(
                    update={
                        "input_per_1m": model.api_prices.input_per_1m.model_copy(
                            update={"value": -1}
                        )
                    }
                )
            }
        )
        catalog = catalog.model_copy(
            update={"models": tuple(bad if m.id == bad.id else m for m in catalog.models)}
        )
    elif kind == "rental":
        rental = catalog.rentals[0]
        bad = rental.model_copy(
            update={"monthly_price": rental.monthly_price.model_copy(update={"value": -1})}
        )
        catalog = catalog.model_copy(update={"rentals": (bad, *catalog.rentals[1:])})
    else:
        hw = catalog.hardware[0]
        bad = hw.model_copy(
            update={"street_price": hw.street_price.model_copy(update={"value": -1})}
        )
        catalog = catalog.model_copy(update={"hardware": (bad, *catalog.hardware[1:])})
    result = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    errors = [
        c
        for c in result.candidates
        if c.kind == kind and any(f.name == "engine_input" for f in c.failures)
    ]
    assert errors
    use_case = next(u for u in catalog.use_cases if u.id == scenario.decision.use_case)
    filtered_result = apply_hard_filters(
        FilterInput(candidates=result.candidates, scenario=scenario, use_case=use_case), params
    )
    assert {c.candidate_id for c in errors} <= {c.candidate_id for c in filtered_result.rejected}


def test_decision_pipeline_is_pure_and_no_io(setup, monkeypatch):
    import builtins
    import socket
    from pathlib import Path

    def blocked(*args, **kwargs):
        raise AssertionError("decision engine attempted I/O")

    catalog, scenario, params, expected = setup
    monkeypatch.setattr(builtins, "open", blocked)
    monkeypatch.setattr(Path, "open", blocked)
    monkeypatch.setattr(socket, "socket", blocked)
    result = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    assert result == expected
    use_case = next(u for u in catalog.use_cases if u.id == scenario.decision.use_case)
    filtered_result = apply_hard_filters(
        FilterInput(candidates=result.candidates, scenario=scenario, use_case=use_case), params
    )
    ranked = rank_candidates(
        RankingInput(
            feasible=filtered_result.feasible,
            weights=catalog.presets[0].weights,
            method=RankingMethod.SAW,
        ),
        params,
    )
    assert ranked.ranked


def test_risk_monotonic_support_and_agreement_and_missing_popularity_note(setup):
    catalog, scenario, params, _ = setup
    hw = next(h for h in catalog.hardware if h.id == "rtx-pro-6000-96gb")
    model = next(m for m in catalog.models if m.id == "qwen-3-8-27b")
    risks = []
    for years, agreement in ((1, 0.8), (5, 0.8), (5, 1.0)):
        support = hw.lifecycle_clocks.software_support_years.model_copy(update={"value": years})
        changed_hw = hw.model_copy(
            update={
                "lifecycle_clocks": hw.lifecycle_clocks.model_copy(
                    update={"software_support_years": support}
                )
            }
        )
        changed_model = model.model_copy(
            update={
                "token_agreement_rates": (
                    model.calibrated_weights_gb[0].model_copy(
                        update={
                            "precision": "INT4",
                            "value": model.calibrated_weights_gb[0].value.model_copy(
                                update={"value": agreement}
                            ),
                        }
                    ),
                )
            }
        )
        cat = catalog.model_copy(
            update={
                "hardware": (changed_hw,),
                "models": (changed_model,),
                "rentals": (),
                "popularity": catalog.popularity.model_copy(update={"entries": ()}),
            }
        )
        c = next(
            c
            for c in generate_candidates(
                CandidateInput(catalog=cat, scenario=scenario), params
            ).candidates
            if c.precision == "INT4"
        )
        risks.append(c.risk)
        assert c.popularity == 0 and any("Popularity not available" in n for n in c.notes)
    assert risks[0] > risks[1] > risks[2]


def test_scaled_quality_provenance_includes_ratio_contributors(setup):
    catalog, _, params, _ = setup
    template = next(b for b in catalog.benchmarks if b.metric == BenchmarkMetric.AA_INDEX_V5)
    records = tuple(
        template.model_copy(
            update={"model_id": model, "metric": metric, "value": value, "source_id": source}
        )
        for model, metric, value, source in (
            ("a", BenchmarkMetric.AA_INDEX_V5, 10, "aa-a"),
            ("a", BenchmarkMetric.TERMINAL_BENCH, 20, "tb-a"),
            ("b", BenchmarkMetric.AA_INDEX_V5, 20, "aa-b"),
            ("b", BenchmarkMetric.TERMINAL_BENCH, 60, "tb-b"),
            ("c", BenchmarkMetric.AA_INDEX_V5, 30, "aa-c"),
        )
    )
    cat = catalog.model_copy(update={"benchmarks": records})
    use_case = next(u for u in catalog.use_cases if u.id == "agentic-coding")
    score = resolve_quality(cat, "c", use_case, quality_ratios(cat, params), params)
    assert set(score.origin.source_ids) == {"aa-a", "aa-b", "tb-a", "tb-b", "aa-c"}


def test_hybrid_cannot_pass_filters_without_component_evidence(setup):
    candidate = valid_candidate(setup).model_copy(update={"kind": CandidateKind.HYBRID})
    assert filtered(candidate, setup).rejected
