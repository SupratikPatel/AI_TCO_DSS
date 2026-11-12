"""U-05 author policy: resident slots must cover simultaneous peak requests (Req 28)."""

import pytest

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.decision import apply_hard_filters, generate_candidates
from ai_tco_dss.decision.candidates import precisions
from ai_tco_dss.domain import (
    CandidateInput,
    CandidateKind,
    DeploymentMode,
    FilterInput,
    RecommendRequest,
    SizingInput,
)
from ai_tco_dss.engines import size_deployment
from ai_tco_dss.services import recommend
from ai_tco_dss.settings import load_engine_parameters


@pytest.fixture(scope="module")
def peak_setup():
    catalog = get_default_repository().catalog()
    scenario = default_scenario()
    params = load_engine_parameters()
    candidates = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    use_case = next(u for u in catalog.use_cases if u.id == scenario.decision.use_case)
    feasible = apply_hard_filters(
        FilterInput(candidates=candidates.candidates, scenario=scenario, use_case=use_case), params
    ).feasible
    candidate = next(c for c in feasible if c.kind == CandidateKind.ONPREM)
    return catalog, scenario, params, use_case, candidate


def check(candidate, setup, scenario=None):
    _, default, params, use_case, _ = setup
    return apply_hard_filters(
        FilterInput(candidates=(candidate,), scenario=scenario or default, use_case=use_case),
        params,
    )


@pytest.mark.parametrize("slots", [0, 3, 4, 5, 6])
def test_peak_slots_boundary_independent_of_monthly_utilization(peak_setup, slots):
    _, scenario, _, _, base = peak_setup
    assert scenario.workload.peak_concurrent_requests == 5
    candidate = base.model_copy(
        update={
            "sizing": base.sizing.model_copy(update={"max_concurrent_users": slots}),
            "utilization": 0.01,
        }
    )
    result = check(candidate, peak_setup)
    if slots >= 5:
        assert result.feasible
    else:
        assert not result.feasible
        failure = next(f for f in result.rejected[0].failures if f.name == "peak_capacity")
        assert failure.measured == f"{slots} resident request slots"
        assert failure.threshold == ">= 5 simultaneous requests at target context"


def test_peak_capacity_missing_sizing_and_monthly_capacity_are_separate(peak_setup):
    base = peak_setup[-1]
    missing = base.model_copy(update={"sizing": None, "utilization": 2.0})
    failures = {f.name: f for f in check(missing, peak_setup).rejected[0].failures}
    assert {"peak_capacity", "users_served", "memory_fit"} <= failures.keys()
    assert failures["peak_capacity"].measured == "not available"


def test_peak_capacity_applies_to_rental_and_hybrid_local_but_not_api(peak_setup):
    base = peak_setup[-1]
    local = base.model_copy(
        update={"sizing": base.sizing.model_copy(update={"max_concurrent_users": 3})}
    )
    rental = local.model_copy(update={"kind": CandidateKind.RENTAL})
    assert any(f.name == "peak_capacity" for f in check(rental, peak_setup).rejected[0].failures)
    api = base.model_copy(
        update={"kind": CandidateKind.API, "sizing": None, "api_has_eu_endpoint": True}
    )
    assert check(api, peak_setup).feasible
    hybrid = base.model_copy(update={"kind": CandidateKind.HYBRID, "components": (local, api)})
    failure = next(
        f for f in check(hybrid, peak_setup).rejected[0].failures if f.name == "peak_capacity"
    )
    assert local.candidate_id in failure.measured


def test_average_hybrid_share_and_unset_latency_do_not_reduce_peak_requirement(peak_setup):
    _, scenario, _, _, base = peak_setup
    scenario = scenario.model_copy(
        update={
            "financials": scenario.financials.model_copy(update={"local_offload_ratio": 0.1}),
            "workload": scenario.workload.model_copy(
                update={"min_acceptable_tps": None, "max_acceptable_ttft_seconds": None}
            ),
        }
    )
    local = base.model_copy(
        update={"sizing": base.sizing.model_copy(update={"max_concurrent_users": 3})}
    )
    hybrid = base.model_copy(update={"kind": CandidateKind.HYBRID, "components": (local,)})
    assert any(
        f.name == "peak_capacity" for f in check(hybrid, peak_setup, scenario).rejected[0].failures
    )


def test_one_user_max_int3_cannot_qualify_for_five_simultaneous_requests():
    scenario = default_scenario()
    scenario = scenario.model_copy(
        update={
            "workload": scenario.workload.model_copy(update={"active_users": 1}),
            "financials": scenario.financials.model_copy(update={"cost_model": "self-managed"}),
            "decision": scenario.decision.model_copy(update={"preset": "cheapest"}),
        }
    )
    result = recommend(RecommendRequest(scenario=scenario))
    candidate_id = "onprem:mac-studio-m5-max-128gb:1x:qwen-3-8-flash-next:INT3"
    rejected = next(c for c in result.rejected if c.candidate_id == candidate_id)
    assert rejected.sizing.max_concurrent_users == 3
    assert any(f.name == "peak_capacity" for f in rejected.failures)
    assert all(
        c.evaluation.sizing.max_concurrent_users >= 5
        for c in result.ranked
        if c.evaluation.kind in (CandidateKind.ONPREM, CandidateKind.RENTAL)
    )


def test_rental_selection_keeps_a_precision_that_can_cover_peak(peak_setup):
    catalog, scenario, params, _, _ = peak_setup
    generated = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    for rental in catalog.rentals:
        original = next(h for h in catalog.hardware if h.id == rental.gpu_hardware_id)
        hardware = original.model_copy(
            update={
                "deployment_mode": DeploymentMode.CLOUD_RENTAL,
                "system_ram_total_installed_gb": rental.system_ram_total_installed_gb.model_copy(
                    update={
                        "value": rental.system_ram_total_installed_gb.value / rental.gpu_count.value
                    }
                ),
            }
        )
        for model in (m for m in catalog.models if m.type == "open-weights"):
            sizes = [
                size_deployment(
                    SizingInput(
                        hardware=hardware,
                        model=model,
                        precision=p,
                        requested_nodes=rental.gpu_count.value,
                        options=scenario.sizing,
                        profile=scenario.workload,
                        license_alternatives=(),
                    ),
                    params,
                )
                for p in precisions(hardware, model)
            ]
            if any(s.is_feasible and s.max_concurrent_users >= 5 for s in sizes):
                chosen = next(
                    c
                    for c in generated.candidates
                    if c.candidate_id == f"rental:{rental.id}:{model.id}"
                )
                assert chosen.sizing.max_concurrent_users >= 5, chosen.candidate_id
