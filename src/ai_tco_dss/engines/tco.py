"""TCO_Engine: on-premise CapEx, six monthly OpEx components, resale, Munich-vs-Romania
personnel savings and Utilization (Req 22.1 to 22.14, 23.1 to 23.8; design.md § "TCO_Engine").

Every monetary input must already be USD (Req 22.14, design D-04).
Pure: the result depends only on the `TcoInput` contract and `EngineParameters`.
"""

from ai_tco_dss.domain import (
    BenchmarkMetric,
    BenchmarkQuery,
    DeploymentMode,
    EngineParameters,
    EuEngineeringHub,
    FormulaTrace,
    Metric,
    Money,
    SizingResult,
    StaffingHub,
    TcoInput,
    TcoResult,
    ValueOrigin,
)
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines.resolver import deployment_conditions, select_benchmark

USD = "USD"
TPS = "tok/s"
HORIZON_MONTHS = 60
RESALE_REFERENCE_MONTH = 36
DATACENTER_MULTIPLIER_RANGE = (1.0, 2.5)
PUE_RANGE = (1.0, 3.0)
FTE_RANGE = (0.0, 10.0)
BYTES_PER_GB = 1e9
MUNICH = EuEngineeringHub.DE_MUNICH_HQ
ROMANIA = EuEngineeringHub.RO_CLUJ_BUCHAREST


def resale_value(capex: float, retention_3yr: float, month: int) -> float:
    """CapEx * max(0, 1 - (1 - r_resale_3yr) * m / 36) for m in [0, 60] (Req 22.9)."""
    if month != int(month) or not 0 <= month <= HORIZON_MONTHS:
        raise EngineInputError("month", f"an integer from 0 to {HORIZON_MONTHS}, got {month}")
    if not 0.0 <= retention_3yr <= 1.0:
        raise EngineInputError("resale_value_retention_3yr", f"[0.0, 1.0], got {retention_3yr}")
    return capex * max(0.0, 1 - (1 - retention_3yr) * month / RESALE_REFERENCE_MONTH)


def classify_utilization(
    utilization: float, demand: float, capacity: float, params: EngineParameters
) -> tuple[bool, bool, tuple[str, ...]]:
    """(meets_70_percent_utilization_threshold, capacity_insufficient, warnings) of a defined
    Utilization (Req 23.5 to 23.7). Exactly 0.70 meets the threshold, exactly 0.55 gives no
    idle warning and exactly 1.0 is not capacity-insufficient."""
    warnings: list[str] = []
    if utilization < params.idle_warning_threshold:
        warnings.append(
            f"Idle capacity financial warning: Utilization {utilization:.1%} is below "
            f"{params.idle_warning_threshold:.0%}. Low utilization spreads fixed costs over less "
            "work; compare modeled total costs before choosing local or API deployment."
        )
    insufficient = utilization > 1.0
    if insufficient:
        warnings.append(
            f"Capacity insufficient: Utilization {utilization:.3f} is above 1.0; monthly token "
            f"shortfall {demand - capacity:,.0f} tokens"
        )
    return utilization >= params.utilization_threshold, insufficient, tuple(warnings)


def _check(ok: bool, field: str, allowed: str, item_id: str | None = None) -> None:
    if not ok:
        raise EngineInputError(field, allowed, item_id)


def _check_usd(money: Money, field: str, item_id: str) -> None:
    _check(
        money.currency == USD,
        f"{field}.currency",
        f"USD (converted by the Catalog_Repository), got {money.currency}",
        item_id,
    )


def _in_range(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def _hub(hubs: tuple[StaffingHub, ...], hub_id: EuEngineeringHub, field: str) -> StaffingHub:
    found = next((h for h in hubs if h.id == hub_id), None)
    _check(found is not None, field, f"a hub in staffing_hubs.json, got {hub_id.value}")
    assert found is not None
    _check_usd(found.base_salary, "base_salary", hub_id.value)
    _check(found.base_salary.value >= 0, "base_salary", ">= 0", hub_id.value)
    tax = found.employer_social_tax_pct.value
    _check(_in_range(tax, 0.0, 100.0), "employer_social_tax_pct", "[0, 100]", hub_id.value)
    return found


def _target_context(sizing: SizingResult) -> int:
    """Target context of the sizing run: M_kv_single = kv_per_token * context / 1e9."""
    return round(sizing.m_kv_single_gb * BYTES_PER_GB / sizing.kv_per_token_bytes)


def _validate(inp: TcoInput, params: EngineParameters) -> None:
    """Req 22.12 and 22.14: ranges of criteria 1 to 9 and USD money, before any result."""
    hw, fin, profile = inp.hardware, inp.financials, inp.profile
    _check(inp.nodes >= 1, "nodes", f"an integer >= 1, got {inp.nodes}", hw.id)
    _check(profile.active_users >= 1, "active_users", ">= 1")
    _check_usd(hw.street_price, "street_price", hw.id)
    _check(hw.street_price.value >= 0, "street_price", ">= 0", hw.id)
    for kit in hw.cabling_kits:
        _check_usd(kit.price, "cabling_kit", hw.id)
        _check(kit.price.value >= 0, "cabling_kit", ">= 0", hw.id)
    low, high = DATACENTER_MULTIPLIER_RANGE
    mu = hw.datacenter_multiplier.value
    _check(_in_range(mu, low, high), "datacenter_multiplier", f"[{low}, {high}], got {mu}", hw.id)
    hours = profile.active_hours_per_month
    _check(
        _in_range(hours, 1, 744),
        "active_hours_per_month",
        f"[1, 744] hours per month, got {hours}",
    )
    _check(hw.load_watts.value >= 0, "load_watts", ">= 0 W", hw.id)
    _check(hw.idle_watts.value >= 0, "idle_watts", ">= 0 W", hw.id)
    _check(_in_range(fin.cooling_pue, *PUE_RANGE), "cooling_pue", "[1.0, 3.0]")
    _check(_in_range(fin.devops_fte_allocation, *FTE_RANGE), "devops_fte_allocation", "[0.0, 10.0]")
    _check(fin.nvidia_nim_license_per_gpu_yr_usd >= 0, "nvidia_nim_license_per_gpu_yr_usd", ">= 0")
    _check(
        _in_range(fin.capital_opportunity_rate, 0.0, 1.0), "capital_opportunity_rate", "[0.0, 1.0]"
    )
    _check(fin.developer_hourly_opportunity_cost >= 0, "developer_hourly_opportunity_cost", ">= 0")
    _check(inp.cloud_ttft_s is None or inp.cloud_ttft_s >= 0, "cloud_ttft_s", ">= 0 s")
    _check(_in_range(inp.demand_share, 0.0, 1.0), "demand_share", "[0.0, 1.0]")
    retention = hw.lifecycle_clocks.resale_value_retention_3yr.value
    _check(_in_range(retention, 0.0, 1.0), "resale_value_retention_3yr", "[0.0, 1.0]", hw.id)


def _trace(name: str, symbolic: str, substituted: str, result: float, unit: str) -> FormulaTrace:
    return FormulaTrace(
        name=name, symbolic=symbolic, substituted=substituted, result=result, unit=unit
    )


def compute_tco(inp: TcoInput, params: EngineParameters) -> TcoResult:
    """Cost components, 60-month TCO and Utilization of one on-premise deployment."""
    hw, fin, profile, sizing, perf = (
        inp.hardware,
        inp.financials.effective_costs(),
        inp.profile,
        inp.sizing,
        inp.performance,
    )
    _validate(inp, params)
    tariff = next((t for t in inp.tariffs if t.id == fin.electricity_tariff_tier), None)
    _check(
        tariff is not None,
        "electricity_tariff_tier",
        f"a tariff in electricity.json, got {fin.electricity_tariff_tier.value}",
    )
    assert tariff is not None
    _check_usd(tariff.price_per_kwh, "price_per_kwh", tariff.id.value)
    rate = tariff.price_per_kwh.value
    _check(rate >= 0, "price_per_kwh", ">= 0 per kWh", tariff.id.value)
    hub = _hub(inp.hubs, fin.engineering_hub_location, "engineering_hub_location")
    munich = _hub(inp.hubs, MUNICH, "hubs")
    romania = _hub(inp.hubs, ROMANIA, "hubs")

    warnings: list[str] = []
    traces: list[FormulaTrace] = []
    per_seat = hw.deployment_mode == DeploymentMode.PER_SEAT_WORKSTATION
    units = profile.active_users if per_seat else inp.nodes
    gpu_count = units * hw.gpus_per_unit.value

    # CapEx (22.1, 22.2)
    street, mu = hw.street_price.value, hw.datacenter_multiplier.value
    kit = next((k for k in hw.cabling_kits if k.nodes == inp.nodes), None)
    kit_price = kit.price.value if kit is not None else 0.0
    if inp.nodes > 1 and kit is None:
        warnings.append(
            "Networking cost unknown: no cabling/switch quote; modeled allowance is 0 USD."
        )
    capex = units * street * mu + kit_price
    capex_sources = [hw.street_price.source_id, hw.datacenter_multiplier.source_id]
    if kit is not None:
        capex_sources.append(kit.price.source_id)
    traces.append(
        _trace(
            "capex",
            "CapEx = (units * street_price) * μ_datacenter + cabling_and_switch_kit",
            f"({units} * {street:.2f}) * {mu} + {kit_price:.2f}",
            capex,
            USD,
        )
    )

    # Energy (22.3)
    h_active = profile.active_hours_per_month
    h_idle = max(0.0, params.hours_per_month - h_active)
    w_load, w_idle, pue = hw.load_watts.value, hw.idle_watts.value, fin.cooling_pue
    energy = units * (h_active * w_load + h_idle * w_idle) / 1000 * pue * rate
    traces.append(
        _trace(
            "energy",
            "Energy = units * (H_active * W_load + H_idle * W_idle) / 1000 * PUE * rate",
            f"{units} * ({h_active} * {w_load} + {h_idle:g} * {w_idle}) / 1000"
            f" * {pue} * {rate:.4f}",
            energy,
            USD,
        )
    )

    # Personnel (22.4, 22.10)
    fte = fin.devops_fte_allocation

    def personnel_of(entry: StaffingHub) -> float:
        tax = entry.employer_social_tax_pct.value
        return fte * entry.base_salary.value * (1 + tax / 100) / 12

    personnel = personnel_of(hub)
    savings = personnel_of(munich) - personnel_of(romania)
    traces.append(
        _trace(
            "personnel",
            "Personnel = FTE * annual_base_salary * (1 + τ_employer) / 12",
            f"{fte} * {hub.base_salary.value:.2f} * (1 + {hub.employer_social_tax_pct.value}%)"
            " / 12",
            personnel,
            USD,
        )
    )
    traces.append(
        _trace(
            "munich_vs_romania_personnel_savings",
            "Savings = Personnel(de-munich-hq) - Personnel(ro-cluj-bucharest)",
            f"{personnel_of(munich):.2f} - {personnel_of(romania):.2f}",
            savings,
            USD,
        )
    )

    # NIM licensing (22.5, 22.13)
    fee = fin.nvidia_nim_license_per_gpu_yr_usd
    nim = fee / 12 * gpu_count if fin.enable_nvidia_nim_licensing else 0.0
    traces.append(
        _trace(
            "nim_licensing",
            "NIM = license_per_gpu_yr / 12 * GPU count (0 if disabled)",
            f"{fee} / 12 * {gpu_count}" if fin.enable_nvidia_nim_licensing else "disabled",
            nim,
            USD,
        )
    )

    # Capital opportunity cost (22.6)
    capital = fin.capital_opportunity_rate
    opportunity = capex * capital / 12
    traces.append(
        _trace(
            "capital_opportunity",
            "Opportunity = CapEx * capital_opportunity_rate / 12 (rate: assumption)",
            f"{capex:.2f} * {capital} / 12",
            opportunity,
            USD,
        )
    )

    # Wait-time penalty (22.7, 22.13)
    dev_rate = fin.developer_hourly_opportunity_cost
    requests = inp.workload.monthly_requests
    wait = 0.0
    wait_text = "disabled"
    if fin.include_wait_time_penalty:
        if perf.ttft_s is None:
            wait_text = "TTFT not available"
            warnings.append("wait-time penalty set to 0: the local TTFT is not available")
        else:
            h_local = requests * perf.ttft_s.value / 3600
            h_cloud = requests * (inp.cloud_ttft_s or 0.0) / 3600
            wait = max(0.0, h_local - h_cloud) * dev_rate
            wait_text = f"max(0, {h_local:.4f} - {h_cloud:.4f}) * {dev_rate}"
    traces.append(
        _trace(
            "wait_penalty",
            "Wait = max(0, H_local_wait - H_cloud_wait) * dev_rate, H = requests * TTFT / 3600",
            wait_text,
            wait,
            USD,
        )
    )

    # Eviction loss (22.8, 22.13)
    target_context = _target_context(sizing)
    eviction = 0.0
    eviction_text = (
        "excluded by self-managed cost assumptions"
        if fin.cost_model == "self-managed"
        else "no context eviction risk"
    )
    if sizing.context_eviction_risk and fin.cost_model == "enterprise":
        n_ev, p_compute = params.eviction_events_per_month, params.eviction_compute_price_per_1m_usd
        agents = profile.concurrent_agent_instances
        wait_h = 0.0
        if perf.prefill_tps is None or perf.prefill_tps.value <= 0:
            warnings.append(
                "eviction loss excludes the developer wait time: the prefill rate is not available"
            )
        else:
            beta = (
                1.0
                if perf.prefill_tps.origin.origin == "measured"
                or inp.options.enable_optimized_backend
                else 0.035
            )
            wait_h = target_context / (perf.prefill_tps.value * beta) / 3600
        eviction = n_ev * (target_context / 1e6 * p_compute + wait_h * dev_rate / agents)
        eviction_text = (
            f"{n_ev:g} * ({target_context} / 1e6 * {p_compute} + {wait_h:.6f} * {dev_rate}"
            f" / {agents})"
        )
    traces.append(
        _trace(
            "eviction_loss",
            "Eviction = N_ev * (rebuild_tokens / 1e6 * P_compute + wait_h * dev_rate / N_agents)"
            "; N_ev and P_compute: assumption",
            eviction_text,
            eviction,
            USD,
        )
    )

    monthly_opex = (
        ("energy", energy),
        ("personnel", personnel),
        ("nim_licensing", nim),
        ("capital_opportunity", opportunity),
        ("wait_penalty", wait),
        ("eviction_loss", eviction),
    )
    opex_total = sum(value for _, value in monthly_opex)

    # Utilization (23.1 to 23.8)
    units_factor = units if per_seat else 1
    demand = inp.workload.monthly_output_demand * inp.demand_share
    aggregate: Metric | None = None
    capacity: float | None = None
    undefined_reason: str | None = None
    if not sizing.is_feasible:
        undefined_reason = "the Sizing_Engine marked the deployment infeasible"
    else:
        aggregate, aggregate_trace = _aggregate_tps(inp, params, target_context, units_factor)
        if aggregate is None:
            undefined_reason = "no decode TPS is available"
        else:
            traces.append(aggregate_trace)
            capacity = aggregate.value * 3600 * h_active
            if capacity <= 0:
                undefined_reason = "monthly capacity tokens are 0"
    utilization: float | None = None
    if undefined_reason is not None:
        meets, insufficient = False, True
        warnings.append(
            f"Utilization undefined: capacity could not be determined ({undefined_reason})"
        )
    else:
        assert capacity is not None
        utilization = demand / capacity
        meets, insufficient, flags = classify_utilization(utilization, demand, capacity, params)
        warnings.extend(flags)
        traces.append(
            _trace(
                "utilization",
                "Utilization = demanded output tokens / (aggregate TPS * 3600 * H_active)",
                f"{demand:.0f} / ({aggregate.value if aggregate else 0:.4f} * 3600 * {h_active})",
                utilization,
                "ratio",
            )
        )

    # 60-month TCO (22.9, 22.11, spec 02 §2.7)
    retention = hw.lifecycle_clocks.resale_value_retention_3yr.value
    resale = resale_value(capex, retention, HORIZON_MONTHS) if fin.include_resale_value else 0.0
    cost_60m = capex + HORIZON_MONTHS * opex_total - resale
    traces.append(
        _trace(
            "cost_60m",
            "TCO(60) = CapEx + 60 * monthly OpEx - resale(60) (resale only if included)",
            f"{capex:.2f} + 60 * {opex_total:.2f} - {resale:.2f}",
            cost_60m,
            USD,
        )
    )

    return TcoResult(
        units=units,
        gpu_count=gpu_count,
        capex=Metric(
            value=capex,
            unit=USD,
            origin=ValueOrigin(origin="formula", source_ids=tuple(dict.fromkeys(capex_sources))),
        ),
        monthly_opex=monthly_opex,
        monthly_opex_total=opex_total,
        munich_vs_romania_personnel_savings_monthly=savings,
        aggregate_tps=aggregate,
        capacity_tokens_month=capacity,
        utilization=utilization,
        meets_70_percent_utilization_threshold=meets,
        capacity_insufficient=insufficient,
        resale_retention_3yr=retention,
        cost_60m=cost_60m,
        warnings=tuple(warnings),
        traces=tuple(traces),
    )


def _aggregate_tps(
    inp: TcoInput, params: EngineParameters, target_context: int, units_factor: int
) -> tuple[Metric | None, FormulaTrace]:
    """Measured aggregate_tps record (23.3) or the saturating batching fallback (23.4, D-07)."""
    hw, sizing = inp.hardware, inp.sizing
    record = select_benchmark(
        BenchmarkQuery(
            conditions=deployment_conditions(
                hw,
                inp.nodes,
                inp.options,
                inp.profile.peak_concurrent_requests,
                inp.profile.prompt_cache_hit_rate,
                round(inp.workload.out_think),
            ),
            records=inp.benchmarks,
            metric=BenchmarkMetric.AGGREGATE_TPS,
            model_id=sizing.model_id,
            hardware_id=hw.id,
            precision=sizing.precision,
            target_context=inp.options.performance_prompt_tokens,
            tolerance=params.context_match_tolerance,
        )
    )
    if record is not None and inp.options.performance_prompt_tokens is not None:
        value = record.value * units_factor
        trace = _trace(
            "aggregate_tps",
            "aggregate TPS = Benchmark_Record value * units_factor",
            f"{record.source_id} at {record.prompt_tokens} prompt tokens = {record.value}"
            f" * {units_factor}",
            value,
            TPS,
        )
        origin = ValueOrigin(origin="measured", source_ids=(record.source_id,))
        return Metric(value=value, unit=TPS, origin=origin), trace
    decode = inp.performance.decode_tps
    empty = _trace("aggregate_tps", "not available", "no decode TPS", 0.0, TPS)
    if decode is None:
        return None, empty
    nodes = inp.nodes
    n = min(sizing.max_concurrent_users, params.batch_streams_cap_per_node * nodes)
    c = params.batching_contention
    efficiency = 1 / (1 + c * (n - 1)) if n > 0 else 0.0
    raw = decode.value * n * efficiency
    prefill = hw.base_prefill_tps_at_32k
    per_unit = raw if prefill is None else min(raw, nodes * prefill.value)
    value = units_factor * per_unit
    prefill_sources = [prefill.source_id] if prefill is not None else []
    sources = [*decode.origin.source_ids, *prefill_sources, hw.advertised_memory_gb.source_id]
    cap_text = f"{nodes} * {prefill.value}" if prefill is not None else "no compute cap"
    trace = _trace(
        "aggregate_tps",
        "aggregate = units_factor * min(decode * n * 1/(1 + c(n - 1)), nodes * prefill_32k),"
        " n = min(U_max, batch_cap * nodes)",
        f"{units_factor} * min({decode.value:.4f} * {n} * {efficiency:.6f}, {cap_text})",
        value,
        TPS,
    )
    origin = ValueOrigin(origin="formula", source_ids=tuple(dict.fromkeys(sources)))
    return Metric(value=value, unit=TPS, origin=origin), trace
