"""Baseline_Engine: cloud Baselines A to D and the compliance tax delta (Req 24.1 to 24.11;
design.md § "Baseline_Engine").

All values are USD with Value_Origin `formula` (Req 24.11).
Pure: results depend only on the input contract and `EngineParameters`.
"""

from ai_tco_dss.domain import (
    ApiCost,
    ApiCostInput,
    ApiPrices,
    BaselineD,
    BaselineDInput,
    BaselineInput,
    BaselineResult,
    EngineParameters,
    Metric,
    ValueOrigin,
    WorkloadProfile,
    WorkloadResult,
)
from ai_tco_dss.domain.errors import EngineInputError

USD = "USD"
EU_RESIDENCY_SURCHARGE = 1.10
BATCH_DISCOUNT = 0.50
MAX_ACTIVE_HOURS = 744
REASON_SOVEREIGNTY = "no EU data residency or enterprise DPA"
REASON_HARNESS = "third-party harnesses blocked on consumer plans"


def _usd(value: float, *source_ids: str) -> Metric:
    return Metric(
        value=value,
        unit=USD,
        origin=ValueOrigin(origin="formula", source_ids=tuple(dict.fromkeys(source_ids))),
    )


def _raise_if(invalid: list[str], allowed: str, item_id: str | None = None) -> None:
    """Req 24.10: one error naming every offending field."""
    if invalid:
        raise EngineInputError(", ".join(invalid), allowed, item_id)


def _hours_invalid(profile: WorkloadProfile) -> list[str]:
    hours = profile.active_hours_per_month
    return [] if 1 <= hours <= MAX_ACTIVE_HOURS else ["active_hours_per_month"]


def _api_invalid(
    workload: WorkloadResult, profile: WorkloadProfile, prices: ApiPrices, gateway_fee: float
) -> list[str]:
    invalid = [
        name
        for name in ("input_per_1m", "output_per_1m", "cache_read_per_1m")
        if getattr(prices, name).value < 0 or getattr(prices, name).currency != USD
    ]
    if gateway_fee < 0:
        invalid.append("gateway_fee_usd")
    if not 0.0 <= profile.prompt_cache_hit_rate <= 1.0:
        invalid.append("r_cache")
    if not 0.0 <= profile.batch_api_eligible_ratio <= 1.0:
        invalid.append("r_batch")
    if workload.t_out_hat > 0 and workload.out_think / workload.t_out_hat < 1.0:
        invalid.append("thinking_multiplier")
    if workload.kappa_mega < 1.0:
        invalid.append("kappa_mega")
    if workload.nu_verify < 1.0:
        invalid.append("nu_verify")
    return invalid + _hours_invalid(profile)


API_ALLOWED = (
    "token prices >= 0 USD, gateway fee >= 0, r_cache and r_batch in [0, 1], thinking "
    "multiplier, kappa_mega and nu_verify >= 1, active hours per month in [1, 744]"
)


def _per_request(workload: WorkloadResult, profile: WorkloadProfile, prices: ApiPrices) -> float:
    """[T̂_in (1 - r_cache) P_in + T̂_in r_cache P_cache + out_think P_out] / 1e6 (Req 24.4)."""
    r_cache, t_in = profile.prompt_cache_hit_rate, workload.t_in_hat
    return (
        t_in * (1 - r_cache) * prices.input_per_1m.value
        + t_in * r_cache * prices.cache_read_per_1m.value
        + workload.out_think * prices.output_per_1m.value
    ) / 1e6


def _global_monthly(
    workload: WorkloadResult, profile: WorkloadProfile, per_request: float
) -> float:
    """B = requests * per_req * kappa_mega * nu_verify * (1 - 0.5 r_batch) (Req 24.4)."""
    return (
        workload.monthly_requests
        * per_request
        * workload.kappa_mega
        * workload.nu_verify
        * (1 - BATCH_DISCOUNT * profile.batch_api_eligible_ratio)
    )


def _price_sources(prices: ApiPrices) -> tuple[str, ...]:
    return (
        prices.input_per_1m.source_id,
        prices.cache_read_per_1m.source_id,
        prices.output_per_1m.source_id,
    )


def api_monthly_cost(inp: ApiCostInput, params: EngineParameters) -> ApiCost:
    """Monthly cost of one API model: global (Baseline B) or EU-pinned (Baseline C)."""
    _raise_if(
        _api_invalid(inp.workload, inp.profile, inp.prices, inp.gateway_fee_usd),
        API_ALLOWED,
        inp.model_id,
    )
    per_request = _per_request(inp.workload, inp.profile, inp.prices)
    monthly = _global_monthly(inp.workload, inp.profile, per_request)
    if inp.eu_pinned:
        monthly = monthly * EU_RESIDENCY_SURCHARGE + inp.gateway_fee_usd
    return ApiCost(
        model_id=inp.model_id,
        eu_pinned=inp.eu_pinned,
        per_request_usd=per_request,
        monthly=_usd(monthly, *_price_sources(inp.prices)),
    )


def compute_baselines(inp: BaselineInput, params: EngineParameters) -> BaselineResult:
    """Baselines A, B and C for the reference API model, plus the compliance tax delta."""
    model, plan, profile = inp.ref_model, inp.plan, inp.profile
    prices = model.api_prices
    if prices is None:
        raise EngineInputError("api_prices", "a commercial API model with prices", model.id)
    invalid = _api_invalid(inp.workload_ref, profile, prices, inp.gateway_fee_usd)
    seat = plan.price_per_seat_month
    if seat.value < 0 or seat.currency != USD:
        invalid.append("price_per_seat_month")
    _raise_if(invalid, API_ALLOWED + ", plan price >= 0 USD", model.id)

    # Baseline A (24.1 to 24.3): the cost is returned even when ineligible.
    a = profile.active_users * seat.value
    reasons: list[str] = []
    if inp.financials.strict_eu_sovereignty:
        reasons.append(REASON_SOVEREIGNTY)
    if inp.financials.require_third_party_harness:
        reasons.append(REASON_HARNESS)

    # Baselines B and C (24.4, 24.5)
    per_request = _per_request(inp.workload_ref, profile, prices)
    b = _global_monthly(inp.workload_ref, profile, per_request)
    c = b * EU_RESIDENCY_SURCHARGE + inp.gateway_fee_usd
    sources = _price_sources(prices)
    return BaselineResult(
        reference_model_id=model.id,
        a_monthly=_usd(a, seat.source_id),
        b_monthly=_usd(b, *sources),
        c_monthly=_usd(c, *sources),
        baseline_a_eligible=not reasons,
        baseline_a_ineligibility_reasons=tuple(reasons),
        compliance_tax_delta_monthly=c - a,  # 24.7: independent of eligibility, may be < 0
    )


def compute_baseline_d(inp: BaselineDInput, params: EngineParameters) -> BaselineD:
    """Open-weights market value of the tokens a candidate produces (Req 24.6)."""
    price = inp.model.open_weights_output_price_per_1m
    invalid = _hours_invalid(inp.profile)
    if price is not None and (price.value < 0 or price.currency != USD):
        invalid.append("open_weights_output_price_per_1m")
    if inp.utilization is not None and inp.utilization < 0:
        invalid.append("utilization")
    _raise_if(invalid, "active hours per month in [1, 744], price >= 0 USD, Utilization >= 0")

    if inp.infeasible_reason is not None:
        return BaselineD(monthly=None, unavailable_reason=f"infeasible: {inp.infeasible_reason}")
    effective = inp.performance.effective_tps if inp.performance is not None else None
    if effective is None:
        return BaselineD(monthly=None, unavailable_reason="no effective TPS for the candidate")
    if inp.utilization is None:
        return BaselineD(monthly=None, unavailable_reason="Utilization is undefined")
    if price is None:
        return BaselineD(
            monthly=None,
            unavailable_reason=f"no open-weights output price for {inp.model.id}",
        )
    produced = (
        inp.profile.active_hours_per_month * 3600 * effective.value * min(inp.utilization, 1.0)
    )
    value = produced / 1e6 * price.value
    return BaselineD(
        monthly=_usd(value, *effective.origin.source_ids, price.source_id),
        unavailable_reason=None,
    )
