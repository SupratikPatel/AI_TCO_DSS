"""TCO_Engine, Utilization, `project_tco` and the View 2 cost table
(Req 13.7, 22.1 to 22.14, 23.1 to 23.8, 34.3)."""

from typing import Any

import pytest
from tests.benchmark_fixtures import conditions

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    BenchmarkRecord,
    BenchmarkSet,
    DecisionOptions,
    DeploymentMode,
    EnterpriseFinancials,
    EuEngineeringHub,
    PerformanceInput,
    PrecisionFormat,
    Scenario,
    SizingInput,
    SizingOptions,
    TcoInput,
    TcoRequest,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import EngineInputError, UnknownIdentifierError
from ai_tco_dss.engines.performance import compute_performance
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.engines.tco import classify_utilization, compute_tco, resale_value
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.services import project_tco
from ai_tco_dss.settings import load_engine_parameters
from ai_tco_dss.ui.formatting import tco_cost_rows, viability_badge

PARAMS = load_engine_parameters()
HW_ID = "rtx-pro-6000-96gb"
MODEL_ID = "gpt-oss-120b"
NODES = 4
CANDIDATE_ID = f"onprem:{HW_ID}:{NODES}x:{MODEL_ID}:INT4"
OPEX_NAMES = (
    "energy",
    "personnel",
    "nim_licensing",
    "capital_opportunity",
    "wait_penalty",
    "eviction_loss",
)
REL = 1e-9


def _catalog() -> Any:
    return get_default_repository().catalog()


def _base(
    hardware_id: str = HW_ID,
    model_id: str = MODEL_ID,
    nodes: int = NODES,
    *,
    profile: WorkloadProfile | None = None,
    financials: EnterpriseFinancials | None = None,
    records: tuple[BenchmarkRecord, ...] = (),
    context: int = 128_000,
) -> TcoInput:
    catalog = _catalog()
    hardware = next(h for h in catalog.hardware if h.id == hardware_id)
    model = next(m for m in catalog.models if m.id == model_id)
    profile = profile or WorkloadProfile()
    options = SizingOptions(
        target_context_length=context,
        performance_prompt_tokens=context,
        benchmark_conditions=conditions(
            nodes=nodes, accelerator_memory_gb=hardware.advertised_memory_gb.value
        ),
    )
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), PARAMS
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=PrecisionFormat.INT4,
            requested_nodes=nodes,
            options=options,
            profile=profile,
            license_alternatives=(),
        ),
        PARAMS,
    )
    assert sizing.is_feasible, sizing.oom_reason
    performance = compute_performance(
        PerformanceInput(
            hardware=hardware,
            model=model,
            precision=PrecisionFormat.INT4,
            sizing=sizing,
            workload=workload,
            profile=profile,
            options=options,
            benchmarks=BenchmarkSet(records=()),
        ),
        PARAMS,
    )
    return TcoInput(
        options=options,
        hardware=hardware,
        nodes=nodes,
        sizing=sizing,
        performance=performance,
        workload=workload,
        profile=profile,
        financials=financials or EnterpriseFinancials(),
        tariffs=catalog.tariffs,
        hubs=catalog.hubs,
        benchmarks=BenchmarkSet(records=records),
    )


def _opex(result: Any) -> dict[str, float]:
    return dict(result.monthly_opex)


def _hub(inp: TcoInput, hub: EuEngineeringHub) -> Any:
    return next(h for h in inp.hubs if h.id == hub)


def _personnel(inp: TcoInput, hub: EuEngineeringHub) -> float:
    entry = _hub(inp, hub)
    fte = inp.financials.devops_fte_allocation
    return fte * entry.base_salary.value * (1 + entry.employer_social_tax_pct.value / 100) / 12


def _aggregate_record(value: float, context: int = 128_000) -> BenchmarkRecord:
    return BenchmarkRecord.model_validate(
        {
            "metric": "aggregate_tps",
            "value": value,
            "model_id": MODEL_ID,
            "hardware_id": HW_ID,
            "precision": "INT4",
            "context_tokens": context,
            "prompt_tokens": context,
            "conditions": conditions(nodes=NODES, accelerator_memory_gb=96),
            "source_id": "AGG-1",
            "tier": "community",
            "accessed": "2026-11-07",
        }
    )


# --- 22.1 to 22.7, 22.9, 22.13: cost components -------------------------------------------


def test_req_22_1_capex_is_units_times_price_times_multiplier_plus_kit() -> None:
    inp = _base()
    result = compute_tco(inp, PARAMS)
    hw = inp.hardware
    expected = NODES * hw.street_price.value * hw.datacenter_multiplier.value + 0.0  # no kit
    assert result.units == NODES
    assert result.gpu_count == NODES * hw.gpus_per_unit.value
    assert result.capex.value == pytest.approx(expected, rel=REL)
    assert result.capex.unit == "USD"
    assert result.capex.origin.origin == "formula"
    assert hw.street_price.source_id in result.capex.origin.source_ids


def test_req_22_2_per_seat_workstation_units_equal_active_users() -> None:
    profile = WorkloadProfile(active_users=12)
    inp = _base("mac-studio-m5-max-128gb", "qwen-3-8-27b", 1, profile=profile)
    assert inp.hardware.deployment_mode == DeploymentMode.PER_SEAT_WORKSTATION
    result = compute_tco(inp, PARAMS)
    assert result.units == 12
    assert result.capex.value == pytest.approx(
        12 * inp.hardware.street_price.value * inp.hardware.datacenter_multiplier.value, rel=REL
    )


def test_req_22_3_energy_formula() -> None:
    inp = _base()
    result = compute_tco(inp, PARAMS)
    hw, fin = inp.hardware, inp.financials
    rate = next(t for t in inp.tariffs if t.id == fin.electricity_tariff_tier).price_per_kwh.value
    h_a = inp.profile.active_hours_per_month
    expected = (
        NODES
        * (h_a * hw.load_watts.value + (730 - h_a) * hw.idle_watts.value)
        / 1000
        * fin.cooling_pue
        * rate
    )
    assert _opex(result)["energy"] == pytest.approx(expected, rel=REL)


def test_req_22_4_personnel_formula_uses_the_selected_hub() -> None:
    fin = EnterpriseFinancials(engineering_hub_location=EuEngineeringHub.PL_WARSAW_KRAKOW)
    inp = _base(financials=fin)
    result = compute_tco(inp, PARAMS)
    assert _opex(result)["personnel"] == pytest.approx(
        _personnel(inp, EuEngineeringHub.PL_WARSAW_KRAKOW), rel=REL
    )


def test_req_22_5_nim_license_per_gpu() -> None:
    fin = EnterpriseFinancials(enable_nvidia_nim_licensing=True)
    result = compute_tco(_base(financials=fin), PARAMS)
    assert _opex(result)["nim_licensing"] == pytest.approx(4500.0 / 12 * NODES, rel=REL)


def test_req_22_6_capital_opportunity_cost() -> None:
    result = compute_tco(_base(), PARAMS)
    assert _opex(result)["capital_opportunity"] == pytest.approx(
        result.capex.value * 0.045 / 12, rel=REL
    )


def test_req_22_7_wait_time_penalty_when_enabled() -> None:
    fin = EnterpriseFinancials(include_wait_time_penalty=True)
    inp = _base(financials=fin).model_copy(update={"cloud_ttft_s": 1.0})
    result = compute_tco(inp, PARAMS)
    ttft = inp.performance.ttft_s
    assert ttft is not None
    requests = inp.workload.monthly_requests
    h_local = requests * ttft.value / 3600
    h_cloud = requests * 1.0 / 3600
    expected = max(0.0, h_local - h_cloud) * fin.developer_hourly_opportunity_cost
    assert _opex(result)["wait_penalty"] == pytest.approx(expected, rel=REL)


def test_req_22_8_eviction_loss_formula_with_assumption_inputs() -> None:
    """Req 22.8: N_ev * (rebuild / 1e6 * P_compute + wait_h * dev_rate / N_agents)."""
    inp = _base()
    inp = inp.model_copy(
        update={"sizing": inp.sizing.model_copy(update={"context_eviction_risk": True})}
    )
    result = compute_tco(inp, PARAMS)
    prefill = inp.performance.prefill_tps
    assert prefill is not None
    context = 128_000
    wait_h = context / prefill.value / 3600
    expected = PARAMS.eviction_events_per_month * (
        context / 1e6 * PARAMS.eviction_compute_price_per_1m_usd
        + wait_h
        * inp.financials.developer_hourly_opportunity_cost
        / inp.profile.concurrent_agent_instances
    )
    assert _opex(result)["eviction_loss"] == pytest.approx(expected, rel=REL)
    trace = next(t for t in result.traces if t.name == "eviction_loss")
    assert "assumption" in trace.symbolic


def test_req_22_9_resale_curve_endpoints() -> None:
    assert resale_value(1000.0, 0.5, 0) == pytest.approx(1000.0)
    assert resale_value(1000.0, 0.5, 36) == pytest.approx(500.0)
    assert resale_value(1000.0, 0.5, 60) == pytest.approx(1000.0 * (1 - 0.5 * 60 / 36))
    assert resale_value(1000.0, 0.0, 60) == 0.0
    with pytest.raises(EngineInputError) as err:
        resale_value(1000.0, 0.5, 61)
    assert err.value.field == "month"


def test_req_22_10_munich_vs_romania_savings_use_the_same_fte() -> None:
    fin = EnterpriseFinancials(devops_fte_allocation=0.8)
    inp = _base(financials=fin)
    result = compute_tco(inp, PARAMS)
    expected = _personnel(inp, EuEngineeringHub.DE_MUNICH_HQ) - _personnel(
        inp, EuEngineeringHub.RO_CLUJ_BUCHAREST
    )
    assert result.munich_vs_romania_personnel_savings_monthly == pytest.approx(expected, rel=REL)
    assert expected > 0


def test_req_22_11_higher_street_price_never_lowers_the_60_month_tco() -> None:
    inp = _base()
    price = inp.hardware.street_price
    dearer = inp.hardware.model_copy(
        update={"street_price": price.model_copy(update={"value": price.value * 1.5})}
    )
    base = compute_tco(inp, PARAMS).cost_60m
    assert compute_tco(inp.model_copy(update={"hardware": dearer}), PARAMS).cost_60m >= base


def _bad_financials(**changes: Any) -> dict[str, Any]:
    return {"financials": EnterpriseFinancials().model_copy(update=changes)}


def _bad_hardware(**changes: Any) -> dict[str, Any]:
    hw = _base().hardware
    updates = {k: getattr(hw, k).model_copy(update={"value": v}) for k, v in changes.items()}
    return {"hardware": hw.model_copy(update=updates)}


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        (_bad_financials(cooling_pue=0.9), "cooling_pue"),
        (_bad_financials(cooling_pue=3.1), "cooling_pue"),
        (_bad_financials(devops_fte_allocation=10.5), "devops_fte_allocation"),
        (_bad_financials(devops_fte_allocation=-0.1), "devops_fte_allocation"),
        (_bad_financials(capital_opportunity_rate=1.5), "capital_opportunity_rate"),
        (
            _bad_financials(developer_hourly_opportunity_cost=-1.0),
            "developer_hourly_opportunity_cost",
        ),
        (
            _bad_financials(nvidia_nim_license_per_gpu_yr_usd=-1.0),
            "nvidia_nim_license_per_gpu_yr_usd",
        ),
        (_bad_hardware(datacenter_multiplier=2.6), "datacenter_multiplier"),
        (_bad_hardware(datacenter_multiplier=0.9), "datacenter_multiplier"),
        (_bad_hardware(street_price=-1.0), "street_price"),
        (_bad_hardware(load_watts=-1.0), "load_watts"),
        (_bad_hardware(idle_watts=-1.0), "idle_watts"),
        (
            {"profile": WorkloadProfile.model_construct(active_hours_per_month=745)},
            "active_hours_per_month",
        ),
        ({"nodes": 0}, "nodes"),
        ({"cloud_ttft_s": -1.0}, "cloud_ttft_s"),
        ({"tariffs": ()}, "electricity_tariff_tier"),
        ({"hubs": ()}, "engineering_hub_location"),
    ],
)
def test_req_22_12_out_of_range_inputs_raise_naming_the_field(
    updates: dict[str, Any], field: str
) -> None:
    inp = _base().model_copy(update=updates)
    with pytest.raises(EngineInputError) as err:
        compute_tco(inp, PARAMS)
    assert field in err.value.field


def test_req_22_12_resale_retention_out_of_range_raises() -> None:
    inp = _base()
    clocks = inp.hardware.lifecycle_clocks
    bad = clocks.model_copy(
        update={
            "resale_value_retention_3yr": clocks.resale_value_retention_3yr.model_copy(
                update={"value": 1.2}
            )
        }
    )
    hw = inp.hardware.model_copy(update={"lifecycle_clocks": bad})
    with pytest.raises(EngineInputError) as err:
        compute_tco(inp.model_copy(update={"hardware": hw}), PARAMS)
    assert err.value.field == "resale_value_retention_3yr"


def test_req_22_12_missing_munich_or_romania_hub_raises() -> None:
    inp = _base()
    hubs = tuple(h for h in inp.hubs if h.id != EuEngineeringHub.DE_MUNICH_HQ)
    with pytest.raises(EngineInputError) as err:
        compute_tco(inp.model_copy(update={"hubs": hubs}), PARAMS)
    assert "de-munich-hq" in err.value.allowed


def test_req_22_13_disabled_components_are_exactly_zero_and_reported() -> None:
    result = compute_tco(_base(), PARAMS)
    opex = _opex(result)
    assert tuple(name for name, _ in result.monthly_opex) == OPEX_NAMES
    assert opex["nim_licensing"] == 0.0
    assert opex["wait_penalty"] == 0.0
    assert opex["eviction_loss"] == 0.0
    assert result.monthly_opex_total == pytest.approx(sum(opex.values()), rel=REL)


@pytest.mark.parametrize("item", ["street_price", "tariff", "hub"])
def test_req_22_14_non_usd_money_raises(item: str) -> None:
    inp = _base()
    if item == "street_price":
        hw = inp.hardware
        update: dict[str, Any] = {
            "hardware": hw.model_copy(
                update={"street_price": hw.street_price.model_copy(update={"currency": "EUR"})}
            )
        }
    elif item == "tariff":
        update = {
            "tariffs": tuple(
                t.model_copy(
                    update={"price_per_kwh": t.price_per_kwh.model_copy(update={"currency": "EUR"})}
                )
                for t in inp.tariffs
            )
        }
    else:
        update = {
            "hubs": tuple(
                h.model_copy(
                    update={"base_salary": h.base_salary.model_copy(update={"currency": "EUR"})}
                )
                for h in inp.hubs
            )
        }
    with pytest.raises(EngineInputError) as err:
        compute_tco(inp.model_copy(update=update), PARAMS)
    assert "currency" in err.value.field
    assert "USD" in err.value.allowed


# --- 23.1 to 23.8: Utilization -----------------------------------------------------------


def test_req_23_1_23_4_utilization_formula_fallback() -> None:
    inp = _base()
    result = compute_tco(inp, PARAMS)
    decode = inp.performance.decode_tps
    assert decode is not None and inp.hardware.base_prefill_tps_at_32k is not None
    n = min(inp.sizing.max_concurrent_users, 64 * NODES)
    raw = decode.value * n / (1 + 0.03 * (n - 1))
    cap = NODES * inp.hardware.base_prefill_tps_at_32k.value
    aggregate = min(raw, cap)
    capacity = aggregate * 3600 * inp.profile.active_hours_per_month
    assert result.aggregate_tps is not None
    assert result.aggregate_tps.value == pytest.approx(aggregate, rel=REL)
    assert result.aggregate_tps.origin.origin == "formula"
    assert result.capacity_tokens_month == pytest.approx(capacity, rel=REL)
    assert result.utilization == pytest.approx(
        inp.workload.monthly_output_demand / capacity, rel=REL
    )


def test_req_23_3_measured_aggregate_throughput_is_used_and_labelled() -> None:
    inp = _base(records=(_aggregate_record(900.0),))
    result = compute_tco(inp, PARAMS)
    assert result.aggregate_tps is not None
    assert result.aggregate_tps.value == 900.0
    assert result.aggregate_tps.origin.origin == "measured"
    assert result.aggregate_tps.origin.source_ids == ("AGG-1",)
    capacity = 900.0 * 3600 * inp.profile.active_hours_per_month
    assert result.utilization == pytest.approx(
        inp.workload.monthly_output_demand / capacity, rel=REL
    )


def test_req_23_3_aggregate_record_outside_the_context_tolerance_is_ignored() -> None:
    inp = _base(records=(_aggregate_record(900.0, context=8_192),))
    result = compute_tco(inp, PARAMS)
    assert result.aggregate_tps is not None
    assert result.aggregate_tps.origin.origin == "formula"


def test_req_23_2_23_7_utilization_above_one_is_not_clipped_and_flagged() -> None:
    inp = _base(records=(_aggregate_record(1.0),))
    result = compute_tco(inp, PARAMS)
    capacity = 1.0 * 3600 * inp.profile.active_hours_per_month
    demand = inp.workload.monthly_output_demand
    assert result.utilization == pytest.approx(demand / capacity, rel=REL)
    assert result.utilization is not None and result.utilization > 1.0
    assert result.capacity_insufficient is True
    assert result.meets_70_percent_utilization_threshold is True
    shortfall = [w for w in result.warnings if "shortfall" in w]
    assert len(shortfall) == 1
    assert f"{demand - capacity:,.0f}" in shortfall[0]


def test_req_23_6_idle_warning_states_the_utilization() -> None:
    result = compute_tco(_base(), PARAMS)
    assert result.utilization is not None and result.utilization < 0.55
    idle = [w for w in result.warnings if "idle capacity" in w.lower()]
    assert len(idle) == 1
    assert f"{result.utilization:.1%}" in idle[0]
    # C-044: author-approved neutral wording supersedes the old API-cost prediction.
    assert "compare modeled total costs" in idle[0]
    assert "likely to exceed" not in idle[0]


def test_req_23_8_infeasible_deployment_has_undefined_utilization() -> None:
    inp = _base()
    sizing = inp.sizing.model_copy(update={"is_feasible": False, "oom_reason": "OOM"})
    result = compute_tco(inp.model_copy(update={"sizing": sizing}), PARAMS)
    assert result.utilization is None
    assert result.capacity_tokens_month is None
    assert result.meets_70_percent_utilization_threshold is False
    assert result.capacity_insufficient is True
    assert any("capacity could not be determined" in w for w in result.warnings)


def test_req_23_8_zero_capacity_has_undefined_utilization() -> None:
    inp = _base(records=(_aggregate_record(0.0),))
    result = compute_tco(inp, PARAMS)
    assert result.utilization is None
    assert result.meets_70_percent_utilization_threshold is False
    assert result.capacity_insufficient is True
    assert any("capacity could not be determined" in w for w in result.warnings)


@pytest.mark.parametrize(
    ("u", "meets", "insufficient", "idle"),
    [
        (0.5499, False, False, True),
        (0.55, False, False, False),
        (0.6999, False, False, False),
        (0.70, True, False, False),
        (1.0, True, False, False),
        (1.0001, True, True, False),
    ],
)
def test_req_23_5_23_6_23_7_boundaries(
    u: float, meets: bool, insufficient: bool, idle: bool
) -> None:
    capacity = 1_000_000.0
    got_meets, got_insufficient, warnings = classify_utilization(u, u * capacity, capacity, PARAMS)
    assert got_meets is meets
    assert got_insufficient is insufficient
    assert any("idle capacity" in w.lower() for w in warnings) is idle
    assert any("shortfall" in w for w in warnings) is insufficient


@pytest.mark.parametrize(
    ("u", "badge"),
    [
        (None, "capacity-insufficient"),
        (0.0, "idle capacity warning"),
        (0.5499, "idle capacity warning"),
        (0.55, "below threshold"),
        (0.6999, "below threshold"),
        (0.70, "viable"),
        (1.0, "viable"),
        (1.0001, "capacity-insufficient"),
    ],
)
def test_req_34_3_viability_badge(u: float | None, badge: str) -> None:
    assert viability_badge(u) == badge


# --- project_tco and the View 2 cost table (13.7, 34.3) ------------------------------------


def _request(hub: EuEngineeringHub = EuEngineeringHub.RO_CLUJ_BUCHAREST, **ids: str) -> TcoRequest:
    scenario = Scenario(
        workload=get_default_repository().load_workload(),
        financials=EnterpriseFinancials(engineering_hub_location=hub),
        sizing=SizingOptions(),
        decision=DecisionOptions(),
    )
    return TcoRequest(scenario=scenario, candidate_id=ids.get("candidate_id", CANDIDATE_ID))


def test_project_tco_returns_the_candidate_cost_baselines_and_timeline() -> None:
    projection = project_tco(_request())
    candidate = projection.candidate
    assert candidate.candidate_id == CANDIDATE_ID
    assert (candidate.hardware_id, candidate.nodes, candidate.model_id) == (HW_ID, 4, MODEL_ID)
    assert candidate.precision == PrecisionFormat.INT4
    assert candidate.tco is not None
    assert candidate.capex == candidate.tco.capex.value
    assert candidate.cost_60m == candidate.tco.cost_60m
    assert candidate.utilization == candidate.tco.utilization
    assert projection.timeline is not None
    assert len(projection.timeline.points) == 60
    assert projection.timeline.points[-1].on_prem_cumulative == pytest.approx(
        projection.candidate.cost_60m
    )
    assert projection.baselines.reference_model_id == "claude-sonnet-5-5"


def test_project_tco_munich_hub_raises_personnel_opex() -> None:
    romania = project_tco(_request(EuEngineeringHub.RO_CLUJ_BUCHAREST)).candidate.tco
    munich = project_tco(_request(EuEngineeringHub.DE_MUNICH_HQ)).candidate.tco
    assert romania is not None and munich is not None
    assert dict(munich.monthly_opex)["personnel"] > dict(romania.monthly_opex)["personnel"]


@pytest.mark.parametrize(
    ("candidate_id", "error"),
    [
        ("onprem:no-such-hw:4x:gpt-oss-120b:INT4", UnknownIdentifierError),
        ("onprem:rtx-pro-6000-96gb:4x:no-such-model:INT4", UnknownIdentifierError),
        ("onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT9", EngineInputError),
        ("onprem:rtx-pro-6000-96gb:four:gpt-oss-120b:INT4", EngineInputError),
        ("garbage", EngineInputError),
    ],
)
def test_project_tco_rejects_unknown_or_malformed_candidate_ids(
    candidate_id: str, error: type[Exception]
) -> None:
    with pytest.raises(error):
        project_tco(_request(candidate_id=candidate_id))


def test_req_34_3_cost_table_lists_capex_six_opex_utilization_and_baselines() -> None:
    projection = project_tco(_request())
    rows = tco_cost_rows(projection)
    items = rows["Item"]
    assert items[0] == "CapEx"
    for label in (
        "Energy OpEx / month",
        "Personnel OpEx / month",
        "NVIDIA NIM licensing / month",
        "Capital opportunity cost / month",
        "Wait-time penalty / month",
        "Eviction loss / month",
        "Utilization",
        "Baseline A (subscription) / month",
        "Baseline B (global API) / month",
        "Baseline C (EU-pinned API) / month",
        "Compliance tax delta (C - A) / month",
    ):
        assert label in items, label
    tco = projection.candidate.tco
    assert tco is not None
    utilization = rows["Value"][items.index("Utilization")]
    assert viability_badge(tco.utilization) in utilization
    assert len(rows["Value"]) == len(items) == len(rows["Origin"])
