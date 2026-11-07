"""Baseline_Engine: Baselines A to D and the compliance tax delta (Req 24.1 to 24.11, 41.3,
41.4). Reference values are recomputed from the catalog inputs, so verified prices
recompute the expectation (design.md § "Baseline_Engine")."""

from typing import Any

import pytest

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    ApiCostInput,
    BaselineDInput,
    BaselineInput,
    EnterpriseFinancials,
    Metric,
    ModelSpec,
    PerformanceResult,
    SubscriptionPlan,
    ValueOrigin,
    WorkloadInput,
    WorkloadProfile,
    WorkloadResult,
)
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines.baselines import api_monthly_cost, compute_baseline_d, compute_baselines
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
REF_MODEL = "claude-sonnet-5-5"
OPEN_MODEL = "gpt-oss-120b"
BASELINE_REL = 0.01  # Req 41.4: at most 1 % relative tolerance for Baseline formula outputs
SOVEREIGNTY = "no EU data residency or enterprise DPA"
HARNESS = "third-party harnesses blocked on consumer plans"


def _catalog() -> Any:
    return get_default_repository().catalog()


def _model(model_id: str = REF_MODEL) -> ModelSpec:
    return next(m for m in _catalog().models if m.id == model_id)


def _plan() -> SubscriptionPlan:
    defaults = _catalog().baseline_defaults
    return next(p for p in defaults.plans if p.id == defaults.default_plan_id)


def _gateway() -> float:
    fee: float = _catalog().baseline_defaults.gateway_fee_per_month.value
    return fee


def _workload(profile: WorkloadProfile, model: ModelSpec | None = None) -> WorkloadResult:
    return compute_workload(
        WorkloadInput(profile=profile, model=model or _model(), harnesses=_catalog().harnesses),
        PARAMS,
    )


def _input(
    profile: WorkloadProfile | None = None,
    financials: EnterpriseFinancials | None = None,
    **updates: Any,
) -> BaselineInput:
    profile = profile or get_default_repository().load_workload()
    inp = BaselineInput(
        workload_ref=_workload(profile),
        profile=profile,
        ref_model=_model(),
        plan=_plan(),
        gateway_fee_usd=_gateway(),
        financials=financials or EnterpriseFinancials(),
    )
    return inp.model_copy(update=updates) if updates else inp


def _hand_b(workload: WorkloadResult, profile: WorkloadProfile, model: ModelSpec) -> float:
    assert model.api_prices is not None
    p = model.api_prices
    r_cache = profile.prompt_cache_hit_rate
    per_req = (
        workload.t_in_hat * (1 - r_cache) * p.input_per_1m.value
        + workload.t_in_hat * r_cache * p.cache_read_per_1m.value
        + workload.out_think * p.output_per_1m.value
    ) / 1e6
    return (
        workload.monthly_requests
        * per_req
        * workload.kappa_mega
        * workload.nu_verify
        * (1 - 0.5 * profile.batch_api_eligible_ratio)
    )


def test_req_24_4_baseline_b_reference() -> None:
    """Req 24.4, 41.3: Baseline B of the Default_Workload_File with Claude Sonnet 5.5.

    design.md: per_req = 0.0624 + 0.00312 + 0.04875 = 0.11427; B = 22 000 * 0.11427 * 1.98
    * 1 * 0.9 = 4 479.84108 USD with the spec 03 prices $2 / $0.10 / $10. The expectation is
    recomputed from the catalog prices; the literal holds while those prices are unchanged.
    """
    inp = _input()
    result = compute_baselines(inp, PARAMS)
    expected = _hand_b(inp.workload_ref, inp.profile, inp.ref_model)
    assert result.b_monthly.value == pytest.approx(expected, rel=BASELINE_REL)
    assert abs(result.b_monthly.value - expected) <= 0.01
    prices = inp.ref_model.api_prices
    assert prices is not None
    if (prices.input_per_1m.value, prices.cache_read_per_1m.value, prices.output_per_1m.value) == (
        2.0,
        0.1,
        10.0,
    ):
        assert result.b_monthly.value == pytest.approx(4_479.84108, rel=BASELINE_REL)


def test_req_24_5_baseline_c_reference() -> None:
    """Req 24.5, 41.3: C = B * 1.10 + gateway fee (design.md: 5 427.825 USD at 500 USD)."""
    result = compute_baselines(_input(), PARAMS)
    expected = result.b_monthly.value * 1.10 + _gateway()
    assert result.c_monthly.value == pytest.approx(expected, rel=BASELINE_REL)
    assert abs(result.c_monthly.value - expected) <= 0.01
    if result.b_monthly.value == pytest.approx(4_479.84108, rel=1e-9) and _gateway() == 500:
        assert result.c_monthly.value == pytest.approx(5_427.825, rel=BASELINE_REL)


def test_req_24_1_baseline_a_reference() -> None:
    """Req 24.1, 41.3: A = active users * plan price (design.md: 25 * 200 = 5 000 USD)."""
    inp = _input()
    result = compute_baselines(inp, PARAMS)
    expected = inp.profile.active_users * inp.plan.price_per_seat_month.value
    assert abs(result.a_monthly.value - expected) <= 0.01
    assert result.a_monthly.value == pytest.approx(expected, rel=BASELINE_REL)
    if inp.plan.price_per_seat_month.value == 200 and inp.profile.active_users == 25:
        assert result.a_monthly.value == pytest.approx(5_000.0, rel=BASELINE_REL)


def test_req_24_7_compliance_tax_delta_reference() -> None:
    """Req 24.7, 41.3: delta = C - A (design.md: 427.825 USD)."""
    result = compute_baselines(_input(), PARAMS)
    expected = result.c_monthly.value - result.a_monthly.value
    assert result.compliance_tax_delta_monthly == pytest.approx(expected, rel=BASELINE_REL)
    if result.c_monthly.value == pytest.approx(5_427.825, rel=1e-9):
        assert result.compliance_tax_delta_monthly == pytest.approx(427.825, rel=BASELINE_REL)


def test_req_24_7_compliance_tax_delta_may_be_negative() -> None:
    inp = _input()
    plan = inp.plan.model_copy(
        update={
            "price_per_seat_month": inp.plan.price_per_seat_month.model_copy(
                update={"value": 10_000.0}
            )
        }
    )
    result = compute_baselines(inp.model_copy(update={"plan": plan}), PARAMS)
    assert result.compliance_tax_delta_monthly < 0
    assert result.compliance_tax_delta_monthly == pytest.approx(
        result.c_monthly.value - result.a_monthly.value, rel=1e-9
    )


@pytest.mark.parametrize(
    ("strict", "harness", "reasons"),
    [
        (False, False, ()),
        (True, False, (SOVEREIGNTY,)),
        (False, True, (HARNESS,)),
        (True, True, (SOVEREIGNTY, HARNESS)),
    ],
)
def test_req_24_2_24_3_baseline_a_eligibility(
    strict: bool, harness: bool, reasons: tuple[str, ...]
) -> None:
    fin = EnterpriseFinancials(strict_eu_sovereignty=strict, require_third_party_harness=harness)
    inp = _input(financials=fin)
    result = compute_baselines(inp, PARAMS)
    assert result.baseline_a_eligible is (not reasons)
    assert result.baseline_a_ineligibility_reasons == reasons
    expected = inp.profile.active_users * inp.plan.price_per_seat_month.value
    assert result.a_monthly.value == pytest.approx(expected, rel=1e-9)


def test_api_monthly_cost_global_and_eu_pinned() -> None:
    inp = _input()
    prices = inp.ref_model.api_prices
    assert prices is not None
    common: dict[str, Any] = {
        "model_id": REF_MODEL,
        "workload": inp.workload_ref,
        "profile": inp.profile,
        "prices": prices,
        "gateway_fee_usd": 500.0,
    }
    b = api_monthly_cost(ApiCostInput(eu_pinned=False, **common), PARAMS)
    c = api_monthly_cost(ApiCostInput(eu_pinned=True, **common), PARAMS)
    expected_b = _hand_b(inp.workload_ref, inp.profile, inp.ref_model)
    assert b.monthly.value == pytest.approx(expected_b, rel=1e-9)
    assert c.monthly.value == pytest.approx(expected_b * 1.10 + 500.0, rel=1e-9)
    assert b.per_request_usd == c.per_request_usd
    assert (b.eu_pinned, c.eu_pinned) == (False, True)


def _performance(effective: float | None) -> PerformanceResult:
    metric = (
        None
        if effective is None
        else Metric(
            value=effective, unit="tok/s", origin=ValueOrigin(origin="formula", source_ids=("X",))
        )
    )
    return PerformanceResult(
        decode_tps=metric,
        prefill_tps=None,
        ttft_s=None,
        effective_tps=metric,
        warnings=(),
        traces=(),
    )


def test_req_24_6_baseline_d_formula() -> None:
    model = _model(OPEN_MODEL)
    profile = WorkloadProfile()
    price = model.open_weights_output_price_per_1m
    assert price is not None
    for utilization in (0.4, 1.7):
        result = compute_baseline_d(
            BaselineDInput(
                performance=_performance(30.0),
                utilization=utilization,
                profile=profile,
                model=model,
                infeasible_reason=None,
            ),
            PARAMS,
        )
        expected = 176 * 3600 * 30.0 * min(utilization, 1.0) / 1e6 * price.value
        assert result.monthly is not None
        assert result.monthly.value == pytest.approx(expected, rel=BASELINE_REL)
        assert abs(result.monthly.value - expected) <= 0.01
        assert result.unavailable_reason is None
        assert result.monthly.unit == "USD"
        assert result.monthly.origin.origin == "formula"
        assert price.source_id in result.monthly.origin.source_ids


def test_req_24_6_baseline_d_unavailable_for_infeasible_candidate() -> None:
    result = compute_baseline_d(
        BaselineDInput(
            performance=None,
            utilization=None,
            profile=WorkloadProfile(),
            model=_model(OPEN_MODEL),
            infeasible_reason="OOM: weights exceed usable memory",
        ),
        PARAMS,
    )
    assert result.monthly is None
    assert result.unavailable_reason is not None
    assert "infeasible" in result.unavailable_reason
    assert "OOM: weights exceed usable memory" in result.unavailable_reason


@pytest.mark.parametrize(
    ("effective", "utilization", "drop_price", "phrase"),
    [
        (None, 0.5, False, "effective TPS"),
        (30.0, None, False, "Utilization"),
        (30.0, 0.5, True, "open-weights output price"),
    ],
)
def test_req_24_6_baseline_d_unavailable_reasons(
    effective: float | None, utilization: float | None, drop_price: bool, phrase: str
) -> None:
    model = _model(OPEN_MODEL)
    if drop_price:
        model = model.model_copy(update={"open_weights_output_price_per_1m": None})
    result = compute_baseline_d(
        BaselineDInput(
            performance=_performance(effective),
            utilization=utilization,
            profile=WorkloadProfile(),
            model=model,
            infeasible_reason=None,
        ),
        PARAMS,
    )
    assert result.monthly is None
    assert result.unavailable_reason is not None and phrase in result.unavailable_reason


def _price_update(inp: BaselineInput, name: str, value: float) -> dict[str, Any]:
    prices = inp.ref_model.api_prices
    assert prices is not None
    money = getattr(prices, name).model_copy(update={"value": value})
    model = inp.ref_model.model_copy(update={"api_prices": prices.model_copy(update={name: money})})
    return {"ref_model": model}


def _profile_update(**changes: Any) -> dict[str, Any]:
    return {"profile": WorkloadProfile().model_copy(update=changes)}


def _workload_update(inp: BaselineInput, **changes: Any) -> dict[str, Any]:
    return {"workload_ref": inp.workload_ref.model_copy(update=changes)}


BASE = _input()


@pytest.mark.parametrize(
    ("updates", "fields"),
    [
        (_price_update(BASE, "input_per_1m", -1.0), ("input_per_1m",)),
        (_price_update(BASE, "output_per_1m", -0.5), ("output_per_1m",)),
        (_price_update(BASE, "cache_read_per_1m", -0.1), ("cache_read_per_1m",)),
        ({"gateway_fee_usd": -1.0}, ("gateway_fee_usd",)),
        (_profile_update(prompt_cache_hit_rate=1.2), ("r_cache",)),
        (_profile_update(batch_api_eligible_ratio=-0.1), ("r_batch",)),
        (_profile_update(active_hours_per_month=0), ("active_hours_per_month",)),
        (_profile_update(active_hours_per_month=745), ("active_hours_per_month",)),
        (_workload_update(BASE, kappa_mega=0.9), ("kappa_mega",)),
        (_workload_update(BASE, nu_verify=0.5), ("nu_verify",)),
        (_workload_update(BASE, out_think=BASE.workload_ref.t_out_hat * 0.5), ("thinking",)),
        (
            {
                **_profile_update(prompt_cache_hit_rate=1.5, batch_api_eligible_ratio=2.0),
                "gateway_fee_usd": -5.0,
            },
            ("r_cache", "r_batch", "gateway_fee_usd"),
        ),
    ],
)
def test_req_24_10_invalid_inputs_are_rejected_naming_each_field(
    updates: dict[str, Any], fields: tuple[str, ...]
) -> None:
    with pytest.raises(EngineInputError) as err:
        compute_baselines(BASE.model_copy(update=updates), PARAMS)
    for field in fields:
        assert field in err.value.field


def test_req_24_10_baseline_d_rejects_invalid_active_hours() -> None:
    with pytest.raises(EngineInputError) as err:
        compute_baseline_d(
            BaselineDInput(
                performance=_performance(30.0),
                utilization=0.5,
                profile=WorkloadProfile().model_copy(update={"active_hours_per_month": 800}),
                model=_model(OPEN_MODEL),
                infeasible_reason=None,
            ),
            PARAMS,
        )
    assert "active_hours_per_month" in err.value.field


def test_req_24_11_values_are_usd_with_formula_origin_and_sources() -> None:
    inp = _input()
    result = compute_baselines(inp, PARAMS)
    assert result.currency == "USD"
    prices = inp.ref_model.api_prices
    assert prices is not None
    for metric in (result.a_monthly, result.b_monthly, result.c_monthly):
        assert metric.unit == "USD"
        assert metric.origin.origin == "formula"
    assert inp.plan.price_per_seat_month.source_id in result.a_monthly.origin.source_ids
    for money in (prices.input_per_1m, prices.output_per_1m, prices.cache_read_per_1m):
        assert money.source_id in result.b_monthly.origin.source_ids
        assert money.source_id in result.c_monthly.origin.source_ids
