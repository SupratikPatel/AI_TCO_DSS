"""Property tests for the Baseline_Engine (Properties 29 to 31).

Workloads are drawn within the `WorkloadProfile` bounds and run through the Workload_Engine
with the reference API model of the repository catalog; prices, plan price and gateway fee
are drawn as non-negative USD amounts. Oracles restate Requirement 24 independently of
`engines/baselines.py`.
"""

import math
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    ApiPrices,
    BaselineDInput,
    BaselineInput,
    EnterpriseFinancials,
    HarnessType,
    Metric,
    PerformanceResult,
    SubscriptionPlan,
    ThinkingEffortPreset,
    ValueOrigin,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines.baselines import compute_baseline_d, compute_baselines
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
CATALOG = get_default_repository().catalog()
REF_MODEL = next(m for m in CATALOG.models if m.id == "claude-sonnet-5-5")
OPEN_MODEL = next(m for m in CATALOG.models if m.id == "gpt-oss-120b")
assert REF_MODEL.api_prices is not None
PRICES = REF_MODEL.api_prices
PLAN = CATALOG.baseline_defaults.plans[0]
ABS = 0.01  # Req 24.1, 24.4: within 0.01 USD


def _price(money: Any, value: float) -> Any:
    return money.model_copy(update={"value": value})


@st.composite
def profiles(draw: st.DrawFn) -> WorkloadProfile:
    return WorkloadProfile(
        active_users=draw(st.integers(min_value=1, max_value=5_000)),
        daily_requests_per_user=draw(st.integers(min_value=1, max_value=500)),
        working_days_per_month=draw(st.integers(min_value=1, max_value=31)),
        avg_input_tokens=draw(st.integers(min_value=1, max_value=200_000)),
        avg_output_tokens=draw(st.integers(min_value=1, max_value=20_000)),
        thinking_effort_preset=draw(st.sampled_from(list(ThinkingEffortPreset))),
        has_verification_agent_layer=draw(st.booleans()),
        harness_type=draw(st.sampled_from(list(HarnessType))),
        mcp_code_mode_pruning=draw(st.booleans()),
        prompt_cache_hit_rate=draw(st.floats(min_value=0.0, max_value=0.95)),
        batch_api_eligible_ratio=draw(st.floats(min_value=0.0, max_value=1.0)),
        mega_session_ratio=draw(st.floats(min_value=0.0, max_value=1.0)),
        active_hours_per_month=draw(st.integers(min_value=1, max_value=744)),
    )


@st.composite
def money_inputs(draw: st.DrawFn) -> dict[str, float]:
    amount = st.floats(min_value=0.0, max_value=200.0)
    return {
        "p_in": draw(amount),
        "p_out": draw(amount),
        "p_cache": draw(amount),
        "plan": draw(st.floats(min_value=0.0, max_value=5_000.0)),
        "gateway": draw(st.floats(min_value=0.0, max_value=100_000.0)),
    }


def _input(profile: WorkloadProfile, m: dict[str, float]) -> BaselineInput:
    prices = ApiPrices(
        input_per_1m=_price(PRICES.input_per_1m, m["p_in"]),
        output_per_1m=_price(PRICES.output_per_1m, m["p_out"]),
        cache_read_per_1m=_price(PRICES.cache_read_per_1m, m["p_cache"]),
    )
    plan = SubscriptionPlan(
        id=PLAN.id,
        name=PLAN.name,
        price_per_seat_month=_price(PLAN.price_per_seat_month, m["plan"]),
    )
    workload = compute_workload(
        WorkloadInput(profile=profile, model=REF_MODEL, harnesses=CATALOG.harnesses), PARAMS
    )
    return BaselineInput(
        workload_ref=workload,
        profile=profile,
        ref_model=REF_MODEL.model_copy(update={"api_prices": prices}),
        plan=plan,
        gateway_fee_usd=m["gateway"],
        financials=EnterpriseFinancials(),
    )


def _close(actual: float, expected: float) -> bool:
    return abs(actual - expected) <= max(ABS, 1e-9 * abs(expected))


@given(
    profile=profiles(),
    m=money_inputs(),
    effective=st.floats(min_value=0.0, max_value=5_000.0),
    utilization=st.floats(min_value=0.0, max_value=5.0),
    open_price=st.floats(min_value=0.0, max_value=50.0),
)
def test_property_29_baseline_formulas(
    profile: WorkloadProfile,
    m: dict[str, float],
    effective: float,
    utilization: float,
    open_price: float,
) -> None:
    """Property 29 (Req 24.1, 24.4, 24.5, 24.6, 24.7, 24.11): A = users * plan price,
    B = Req 24.4 formula, C = B * 1.10 + gateway fee, D = H_a * 3600 * eff_tps * min(U, 1)
    / 10^6 * P_open_out, delta = C - A, each within 0.01 USD, USD with origin `formula`."""
    inp = _input(profile, m)
    result = compute_baselines(inp, PARAMS)
    w, r_cache = inp.workload_ref, profile.prompt_cache_hit_rate
    per_req = (
        w.t_in_hat * (1 - r_cache) * m["p_in"]
        + w.t_in_hat * r_cache * m["p_cache"]
        + w.out_think * m["p_out"]
    ) / 1e6
    b = (
        w.monthly_requests
        * per_req
        * w.kappa_mega
        * w.nu_verify
        * (1 - 0.5 * profile.batch_api_eligible_ratio)
    )
    a = profile.active_users * m["plan"]
    c = b * 1.10 + m["gateway"]
    assert _close(result.a_monthly.value, a)
    assert _close(result.b_monthly.value, b)
    assert _close(result.c_monthly.value, c)
    assert _close(result.compliance_tax_delta_monthly, c - a)
    for metric in (result.a_monthly, result.b_monthly, result.c_monthly):
        assert metric.unit == "USD" and metric.origin.origin == "formula"
    assert result.currency == "USD"

    model = OPEN_MODEL.model_copy(
        update={
            "open_weights_output_price_per_1m": _price(
                OPEN_MODEL.open_weights_output_price_per_1m, open_price
            )
        }
    )
    metric = Metric(
        value=effective, unit="tok/s", origin=ValueOrigin(origin="formula", source_ids=("X",))
    )
    performance = PerformanceResult(
        decode_tps=metric,
        prefill_tps=None,
        ttft_s=None,
        effective_tps=metric,
        warnings=(),
        traces=(),
    )
    d = compute_baseline_d(
        BaselineDInput(
            performance=performance,
            utilization=utilization,
            profile=profile,
            model=model,
            infeasible_reason=None,
        ),
        PARAMS,
    )
    expected_d = (
        profile.active_hours_per_month * 3600 * effective * min(utilization, 1.0) / 1e6 * open_price
    )
    assert d.monthly is not None
    assert _close(d.monthly.value, expected_d)
    assert d.monthly.unit == "USD" and d.monthly.origin.origin == "formula"


@given(profile=profiles(), m=money_inputs())
def test_property_30_eu_pinned_api_is_never_cheaper_than_global(
    profile: WorkloadProfile, m: dict[str, float]
) -> None:
    """Property 30 (Req 24.8): for all valid Workload_Profiles and gateway fees ≥ 0,
    Baseline C ≥ Baseline B."""
    result = compute_baselines(_input(profile, m), PARAMS)
    assert result.c_monthly.value >= result.b_monthly.value


@given(profile=profiles(), m=money_inputs(), more=st.integers(min_value=1, max_value=10_000))
def test_property_31_baselines_grow_with_users(
    profile: WorkloadProfile, m: dict[str, float], more: int
) -> None:
    """Property 31 (Req 24.9): for all valid Workload_Profiles, adding one or more active
    users with all other inputs equal leaves Baselines A, B and C equal or higher."""
    larger = profile.model_copy(update={"active_users": min(100_000, profile.active_users + more)})
    before = compute_baselines(_input(profile, m), PARAMS)
    after = compute_baselines(_input(larger, m), PARAMS)
    for name in ("a_monthly", "b_monthly", "c_monthly"):
        old, new = getattr(before, name).value, getattr(after, name).value
        assert new >= old or math.isclose(new, old, rel_tol=1e-12)
