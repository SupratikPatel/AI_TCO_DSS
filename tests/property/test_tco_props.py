"""Property tests for the TCO_Engine and Utilization (Properties 24 to 28).

Inputs are variations of one valid base input (RTX Pro 6000 * 4 + gpt-oss-120b INT4 from
the repository catalog), changed with `model_copy`. Oracles restate the formulas of
requirements.md independently of `engines/tco.py`.
"""

import math
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    BenchmarkSet,
    DeploymentMode,
    EnterpriseFinancials,
    EuEngineeringHub,
    Metric,
    PerformanceInput,
    PrecisionFormat,
    SizingInput,
    SizingOptions,
    TcoInput,
    ValueOrigin,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines.performance import compute_performance
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.engines.tco import classify_utilization, compute_tco, resale_value
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters
from ai_tco_dss.ui.formatting import viability_badge

PARAMS = load_engine_parameters()
HW_ID = "rtx-pro-6000-96gb"
MODEL_ID = "gpt-oss-120b"
REL = 1e-9


def _base_input() -> TcoInput:
    catalog = get_default_repository().catalog()
    hardware = next(h for h in catalog.hardware if h.id == HW_ID)
    model = next(m for m in catalog.models if m.id == MODEL_ID)
    profile = WorkloadProfile()
    options = SizingOptions()
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), PARAMS
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=PrecisionFormat.INT4,
            requested_nodes=4,
            options=options,
            profile=profile,
            license_alternatives=(),
        ),
        PARAMS,
    )
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
        hardware=hardware,
        nodes=4,
        sizing=sizing,
        performance=performance,
        workload=workload,
        profile=profile,
        financials=EnterpriseFinancials(),
        tariffs=catalog.tariffs,
        hubs=catalog.hubs,
        benchmarks=BenchmarkSet(records=()),
    )


BASE = _base_input()
assert BASE.sizing.is_feasible


def _sourced(item: Any, value: Any) -> Any:
    return item.model_copy(update={"value": value})


@st.composite
def tco_inputs(draw: st.DrawFn) -> dict[str, Any]:
    """Cost inputs within the ranges of Requirement 22."""
    return {
        "per_seat": draw(st.booleans()),
        "nodes": draw(st.sampled_from([1, 2, 4, 8])),
        "users": draw(st.integers(min_value=1, max_value=500)),
        "street": draw(st.floats(min_value=0.0, max_value=500_000.0)),
        "mu": draw(st.floats(min_value=1.0, max_value=2.5)),
        "gpus": draw(st.integers(min_value=1, max_value=8)),
        "load_w": draw(st.floats(min_value=0.0, max_value=10_000.0)),
        "idle_w": draw(st.floats(min_value=0.0, max_value=2_000.0)),
        "hours": draw(st.integers(min_value=1, max_value=730)),
        "pue": draw(st.floats(min_value=1.0, max_value=3.0)),
        "rate": draw(st.floats(min_value=0.0, max_value=1.5)),
        "fte": draw(st.floats(min_value=0.0, max_value=10.0)),
        "hub": draw(st.sampled_from(list(EuEngineeringHub))),
        "nim": draw(st.booleans()),
        "nim_fee": draw(st.floats(min_value=0.0, max_value=20_000.0)),
        "capital": draw(st.floats(min_value=0.0, max_value=1.0)),
        "wait": draw(st.booleans()),
        "dev_rate": draw(st.floats(min_value=0.0, max_value=500.0)),
        "cloud_ttft": draw(st.none() | st.floats(min_value=0.0, max_value=60.0)),
        "eviction": draw(st.booleans()),
        "resale": draw(st.booleans()),
        "retention": draw(st.floats(min_value=0.0, max_value=1.0)),
    }


def _build(v: dict[str, Any]) -> TcoInput:
    hw = BASE.hardware
    mode = DeploymentMode.PER_SEAT_WORKSTATION if v["per_seat"] else hw.deployment_mode
    clocks = hw.lifecycle_clocks.model_copy(
        update={
            "resale_value_retention_3yr": _sourced(
                hw.lifecycle_clocks.resale_value_retention_3yr, v["retention"]
            )
        }
    )
    hardware = hw.model_copy(
        update={
            "deployment_mode": mode,
            "street_price": _sourced(hw.street_price, v["street"]),
            "datacenter_multiplier": _sourced(hw.datacenter_multiplier, v["mu"]),
            "gpus_per_unit": _sourced(hw.gpus_per_unit, v["gpus"]),
            "load_watts": _sourced(hw.load_watts, v["load_w"]),
            "idle_watts": _sourced(hw.idle_watts, v["idle_w"]),
            "lifecycle_clocks": clocks,
        }
    )
    profile = BASE.profile.model_copy(
        update={"active_users": v["users"], "active_hours_per_month": v["hours"]}
    )
    financials = EnterpriseFinancials(
        cooling_pue=v["pue"],
        devops_fte_allocation=v["fte"],
        engineering_hub_location=v["hub"],
        enable_nvidia_nim_licensing=v["nim"],
        nvidia_nim_license_per_gpu_yr_usd=v["nim_fee"],
        capital_opportunity_rate=v["capital"],
        include_wait_time_penalty=v["wait"],
        developer_hourly_opportunity_cost=v["dev_rate"],
        include_resale_value=v["resale"],
    )
    tariffs = tuple(
        t.model_copy(update={"price_per_kwh": _sourced(t.price_per_kwh, v["rate"])})
        for t in BASE.tariffs
    )
    sizing = BASE.sizing.model_copy(update={"context_eviction_risk": v["eviction"]})
    return BASE.model_copy(
        update={
            "hardware": hardware,
            "nodes": v["nodes"],
            "profile": profile,
            "financials": financials,
            "tariffs": tariffs,
            "sizing": sizing,
            "cloud_ttft_s": v["cloud_ttft"],
        }
    )


def _personnel(inp: TcoInput, hub: EuEngineeringHub) -> float:
    entry = next(h for h in inp.hubs if h.id == hub)
    salary, tax = entry.base_salary.value, entry.employer_social_tax_pct.value
    return inp.financials.devops_fte_allocation * salary * (1 + tax / 100) / 12


def _close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=REL, abs_tol=1e-9)


@given(tco_inputs())
def test_property_24_on_premise_cost_components(v: dict[str, Any]) -> None:
    """Property 24 (Req 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.13): CapEx, energy,
    personnel, NIM, opportunity cost and wait penalty follow the formulas; every component is
    reported, and NIM, wait penalty and eviction loss are exactly 0 when switched off."""
    inp = _build(v)
    result = compute_tco(inp, PARAMS)
    units = v["users"] if v["per_seat"] else v["nodes"]
    capex = units * v["street"] * v["mu"]
    h_a = v["hours"]
    energy = units * (h_a * v["load_w"] + (730 - h_a) * v["idle_w"]) / 1000 * v["pue"] * v["rate"]
    nim = v["nim_fee"] / 12 * units * v["gpus"] if v["nim"] else 0.0
    opex = dict(result.monthly_opex)
    assert set(opex) == {
        "energy",
        "personnel",
        "nim_licensing",
        "capital_opportunity",
        "wait_penalty",
        "eviction_loss",
    }
    assert result.units == units
    assert result.gpu_count == units * v["gpus"]
    assert _close(result.capex.value, capex)
    assert _close(opex["energy"], energy)
    assert _close(opex["personnel"], _personnel(inp, v["hub"]))
    assert _close(opex["nim_licensing"], nim)
    assert _close(opex["capital_opportunity"], capex * v["capital"] / 12)
    if v["wait"]:
        ttft = inp.performance.ttft_s
        assert ttft is not None
        requests = inp.workload.monthly_requests
        h_local = requests * ttft.value / 3600
        h_cloud = requests * (v["cloud_ttft"] or 0.0) / 3600
        assert _close(opex["wait_penalty"], max(0.0, h_local - h_cloud) * v["dev_rate"])
    else:
        assert opex["wait_penalty"] == 0.0
    if not v["nim"]:
        assert opex["nim_licensing"] == 0.0
    if not v["eviction"]:
        assert opex["eviction_loss"] == 0.0
    assert _close(result.monthly_opex_total, sum(opex.values()))


@given(
    capex=st.floats(min_value=0.0, max_value=1e7),
    retention=st.floats(min_value=0.0, max_value=1.0),
    month=st.integers(min_value=0, max_value=60),
)
def test_property_25_resale_curve(capex: float, retention: float, month: int) -> None:
    """Property 25 (Req 22.9): resale(m) = CapEx * max(0, 1 - (1 - r) * m / 36), CapEx at
    m = 0, CapEx * r at m = 36, non-negative and non-increasing in m."""
    value = resale_value(capex, retention, month)
    assert _close(value, capex * max(0.0, 1 - (1 - retention) * month / 36))
    assert value >= 0
    assert _close(resale_value(capex, retention, 0), capex)
    assert _close(resale_value(capex, retention, 36), capex * retention)
    if month < 60:
        assert resale_value(capex, retention, month + 1) <= value + 1e-9 * max(capex, 1.0)


@given(
    v=tco_inputs(),
    which=st.sampled_from(["street", "rate", "fte"]),
    factor=st.floats(min_value=1.0, max_value=10.0),
    extra=st.floats(min_value=0.0, max_value=1_000.0),
)
def test_property_26_tco_monotonicity(
    v: dict[str, Any], which: str, factor: float, extra: float
) -> None:
    """Property 26 (Req 22.11): increasing street price, electricity rate or FTE allocation
    with all other inputs equal never lowers the 60-month on-premise TCO."""
    upper = {"street": 1e7, "rate": 5.0, "fte": 10.0}[which]
    raised = dict(v)
    raised[which] = min(upper, v[which] * factor + extra / (100 if which != "street" else 1))
    if raised[which] < v[which]:
        raised[which] = v[which]
    before = compute_tco(_build(v), PARAMS).cost_60m
    after = compute_tco(_build(raised), PARAMS).cost_60m
    assert after >= before - 1e-9 * max(abs(before), 1.0)


@given(
    decode=st.floats(min_value=0.1, max_value=500.0),
    u_max=st.integers(min_value=1, max_value=2_000),
    nodes=st.sampled_from([1, 2, 4, 8]),
    prefill=st.floats(min_value=1.0, max_value=50_000.0),
    hours=st.integers(min_value=1, max_value=730),
    demand=st.floats(min_value=0.0, max_value=1e11),
    per_seat=st.booleans(),
    users=st.integers(min_value=1, max_value=500),
)
def test_property_27_utilization_formula(
    decode: float,
    u_max: int,
    nodes: int,
    prefill: float,
    hours: int,
    demand: float,
    per_seat: bool,
    users: int,
) -> None:
    """Property 27 (Req 23.1, 23.2, 23.4): without an aggregate record, Utilization =
    demand / (min(decode * n * E(n), nodes * prefill_32k) * units_factor * 3600 * H_active),
    n = min(U_max, 64 * nodes), E(n) = 1 / (1 + 0.03 (n - 1)), unrounded and uncapped;
    the aggregate throughput never exceeds the compute cap."""
    hw = BASE.hardware
    assert hw.base_prefill_tps_at_32k is not None
    mode = DeploymentMode.PER_SEAT_WORKSTATION if per_seat else DeploymentMode.CENTRALIZED_SERVER
    hardware = hw.model_copy(
        update={
            "deployment_mode": mode,
            "base_prefill_tps_at_32k": _sourced(hw.base_prefill_tps_at_32k, prefill),
        }
    )
    metric = Metric(
        value=decode, unit="tok/s", origin=ValueOrigin(origin="formula", source_ids=("X",))
    )
    inp = BASE.model_copy(
        update={
            "hardware": hardware,
            "nodes": nodes,
            "sizing": BASE.sizing.model_copy(update={"max_concurrent_users": u_max}),
            "performance": BASE.performance.model_copy(update={"decode_tps": metric}),
            "workload": BASE.workload.model_copy(update={"monthly_output_demand": demand}),
            "profile": BASE.profile.model_copy(
                update={"active_hours_per_month": hours, "active_users": users}
            ),
        }
    )
    result = compute_tco(inp, PARAMS)
    n = min(u_max, 64 * nodes)
    per_unit = min(decode * n / (1 + 0.03 * (n - 1)), nodes * prefill)
    units_factor = users if per_seat else 1
    capacity = per_unit * units_factor * 3600 * hours
    assert result.aggregate_tps is not None
    assert result.aggregate_tps.value <= nodes * prefill * units_factor * (1 + REL)
    assert result.utilization is not None
    assert _close(result.utilization, demand / capacity)


BOUNDARIES = st.sampled_from([0.0, 0.55, 0.70, 1.0])


@given(u=BOUNDARIES | st.floats(min_value=0.0, max_value=5.0))
def test_property_28_utilization_classification_and_badge(u: float) -> None:
    """Property 28 (Req 23.5, 23.6, 23.7, 34.3): threshold = (u ≥ 0.70), idle warning iff
    u < 0.55, capacity-insufficient iff u > 1.0, and the badge follows Req 34.3."""
    capacity = 1e6
    meets, insufficient, warnings = classify_utilization(u, u * capacity, capacity, PARAMS)
    assert meets is (u >= 0.70)
    assert any("idle capacity" in w.lower() for w in warnings) is (u < 0.55)
    assert insufficient is (u > 1.0)
    if u > 1.0:
        expected = "capacity-insufficient"
    elif u < 0.55:
        expected = "idle capacity warning"
    elif u < 0.70:
        expected = "below threshold"
    else:
        expected = "viable"
    assert viability_badge(u) == expected
