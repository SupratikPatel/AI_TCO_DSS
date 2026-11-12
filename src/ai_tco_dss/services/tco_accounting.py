"""Presentation-only accounting explanations for the exact TCO simulator projection.

All amounts remain USD. Engine results and ranking are unchanged.
"""

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import FormulaTrace, TcoProjection, TcoRequest
from ai_tco_dss.domain.base import Contract
from ai_tco_dss.domain.requests import FxInfo
from ai_tco_dss.services.audit_export import AuditProvenance, AuditSource


class AccountingRow(Contract):
    key: str
    label: str
    value: float
    note: str
    trace: FormulaTrace
    sources: tuple[AuditSource, ...] = ()


class TcoAccounting(Contract):
    candidate_id: str
    rows: tuple[AccountingRow, ...]
    fx: FxInfo
    includes_resale: bool
    break_even_month: int | None
    utilization_text: str


class TcoResponse(TcoProjection):
    accounting: TcoAccounting | None


def explain_tco(request: TcoRequest, projection: TcoProjection) -> TcoResponse:
    candidate = projection.candidate
    cost = candidate.tco
    if candidate.kind != "onprem" or cost is None:
        return TcoResponse(**projection.model_dump(), accounting=None)
    catalog = get_default_repository().catalog(request.scenario.fx_override)
    financials = request.scenario.financials.effective_costs()
    hardware = next(h for h in catalog.hardware if h.id == candidate.hardware_id)
    hub = next(h for h in catalog.hubs if h.id == financials.engineering_hub_location)
    tariff = next(t for t in catalog.tariffs if t.id == financials.electricity_tariff_tier)

    def sources(*inputs: object) -> tuple[AuditSource, ...]:
        records: dict[str, list[AuditProvenance]] = {}

        def collect(value: object, path: str) -> None:
            if isinstance(value, Contract):
                collect(value.model_dump(mode="json"), path)
            elif isinstance(value, dict):
                if {"source_id", "tier", "accessed"} <= value.keys():
                    records.setdefault(str(value["source_id"]), []).append(
                        AuditProvenance(
                            path=path,
                            tier=value["tier"],
                            accessed=value["accessed"],
                            value=str(value.get("value", "")),
                            unit=value.get("currency"),
                        )
                    )
                else:
                    for key, child in value.items():
                        collect(child, f"{path}.{key}")
            elif isinstance(value, (tuple, list)):
                for index, child in enumerate(value):
                    collect(child, f"{path}[{index}]")

        for item in inputs:
            # Named fields keep source provenance understandable in the UI.
            collect(item, "input")
        return tuple(
            AuditSource(**s.model_dump(), provenance=tuple(records[s.source_id]))
            for s in catalog.sources
            if s.source_id in records
        )

    traces = {t.name: t for t in cost.traces}
    rows: list[AccountingRow] = []

    def row(
        key: str,
        label: str,
        value: float,
        note: str,
        trace: FormulaTrace,
        refs: tuple[AuditSource, ...] = (),
    ) -> None:
        rows.append(
            AccountingRow(key=key, label=label, value=value, note=note, trace=trace, sources=refs)
        )

    def derived(
        name: str, symbolic: str, substituted: str, value: float, unit: str = "USD/month"
    ) -> FormulaTrace:
        return FormulaTrace(
            name=name, symbolic=symbolic, substituted=substituted, result=value, unit=unit
        )

    row(
        "capex",
        "Hardware CapEx",
        cost.capex.value,
        "Street price is a catalog assumption, not a verified vendor quotation."
        if hardware.street_price.tier == "assumption"
        else "Upfront purchase using the cited catalog inputs.",
        traces["capex"],
        sources(
            {
                "street_price": hardware.street_price,
                "datacenter_multiplier": hardware.datacenter_multiplier,
                "cabling": tuple(k for k in hardware.cabling_kits if k.nodes == candidate.nodes),
            }
        ),
    )
    labels = {
        "energy": "Energy",
        "personnel": "Personnel",
        "nim_licensing": "NIM licensing",
        "capital_opportunity": "Capital opportunity cost",
        "wait_penalty": "Wait-time penalty",
        "eviction_loss": "Context eviction loss",
    }
    notes = {
        "energy": "Monthly cash expense; active/idle power, PUE and tariff assumptions.",
        "personnel": "Monthly cash expense; allocated FTE, salary and employer costs.",
        "nim_licensing": "Disabled in this projection."
        if not financials.enable_nvidia_nim_licensing
        else "Enabled; annual fee per GPU is a scenario assumption (zero fee is allowed).",
        "capital_opportunity": (
            "Monthly economic cost, not an invoice; capital rate is a scenario assumption."
        ),
        "wait_penalty": "Disabled in this projection."
        if not financials.include_wait_time_penalty
        else (
            "Enabled; modeled productivity cost. Zero can mean no excess wait; "
            "unavailable TTFT is flagged in warnings."
        ),
        "eviction_loss": "No context eviction risk detected."
        if not candidate.sizing or not candidate.sizing.context_eviction_risk
        else (
            "Modeled rebuild and developer-wait cost; "
            "eviction frequency and compute price are assumptions."
        ),
    }
    if financials.cost_model == "self-managed":
        for key in (
            "personnel",
            "nim_licensing",
            "capital_opportunity",
            "wait_penalty",
            "eviction_loss",
        ):
            notes[key] = "Excluded by self-managed purchase-and-electricity assumptions."
    refs = {
        "energy": sources(
            {
                "load_watts": hardware.load_watts,
                "idle_watts": hardware.idle_watts,
                "tariff": tariff.price_per_kwh,
            }
        ),
        "personnel": sources(
            {"annual_salary": hub.base_salary, "employer_tax": hub.employer_social_tax_pct}
        ),
    }
    components = dict(cost.monthly_opex)
    for key, value in cost.monthly_opex:
        row(key, labels[key], value, notes[key], traces[key], refs.get(key, ()))
    cash = sum(components[k] for k in ("energy", "personnel", "nim_licensing"))
    economic = sum(components[k] for k in ("capital_opportunity", "wait_penalty", "eviction_loss"))
    for key, label, value, symbolic in (
        (
            "cash_monthly",
            "Monthly cash operating costs",
            cash,
            "energy + personnel + NIM licensing",
        ),
        (
            "economic_monthly",
            "Monthly modeled economic costs",
            economic,
            "capital opportunity + wait penalty + eviction loss",
        ),
        (
            "monthly_total",
            "Monthly modeled cost",
            cost.monthly_opex_total,
            "cash operating costs + modeled economic costs",
        ),
    ):
        row(
            key,
            label,
            value,
            "Subtotal; components above are counted once.",
            derived(
                key,
                symbolic,
                " + ".join(repr(v) for _, v in cost.monthly_opex)
                if key == "monthly_total"
                else " + ".join(
                    repr(components[k])
                    for k in (
                        ("energy", "personnel", "nim_licensing")
                        if key == "cash_monthly"
                        else ("capital_opportunity", "wait_penalty", "eviction_loss")
                    )
                ),
                value,
            ),
        )
    resale = cost.capex.value + 60 * cost.monthly_opex_total - cost.cost_60m
    row(
        "resale",
        "Resale deduction at month 60",
        resale,
        "Included in this projection."
        if financials.include_resale_value
        else "Disabled in this projection.",
        derived(
            "resale",
            "resale = CapEx * max(0, 1 - (1-retention_3yr)*60/36) if enabled; otherwise 0",
            f"CapEx {cost.capex.value}; retention at 36 months {cost.resale_retention_3yr}; "
            f"enabled {financials.include_resale_value}",
            resale,
            "USD",
        ),
        sources({"retention_3yr": hardware.lifecycle_clocks.resale_value_retention_3yr}),
    )
    row(
        "cost_60m",
        "60-month modeled TCO",
        cost.cost_60m,
        "after resale deduction"
        if financials.include_resale_value
        else "before resale; resale disabled",
        traces["cost_60m"].model_copy(
            update={
                "substituted": f"{cost.capex.value} + 60 * {cost.monthly_opex_total!r} - {resale!r}"
            }
        ),
    )
    baseline = projection.baselines
    gateway = catalog.baseline_defaults.gateway_fee_per_month
    model = next(m for m in catalog.models if m.id == baseline.reference_model_id)
    row(
        "baseline_c",
        "Baseline C monthly",
        baseline.c_monthly.value,
        f"EU-pinned API: {model.name}; 10% residency surcharge plus gateway fee. "
        "Baseline B is the token-usage cost with cache/batch and workload adjustments.",
        derived(
            "baseline_c",
            "Baseline C = Baseline B * 1.10 + gateway fee",
            f"{baseline.b_monthly.value!r} * 1.10 + {gateway.value!r}",
            baseline.c_monthly.value,
        ),
        sources({"api_prices": model.api_prices, "gateway_fee": gateway}),
    )
    c_total = 60 * baseline.c_monthly.value
    row(
        "baseline_c_60m",
        "Baseline C over 60 months",
        c_total,
        "Same workload and horizon as the local comparison.",
        derived(
            "baseline_c_60m",
            "60 * Baseline C monthly",
            f"60 * {baseline.c_monthly.value!r}",
            c_total,
            "USD",
        ),
    )
    savings = c_total - cost.cost_60m
    row(
        "savings_60m",
        "60-month savings vs Baseline C",
        savings,
        "Positive favors local; negative favors the API. Modeled economic costs included.",
        derived(
            "savings_60m",
            "Baseline C 60-month cost - local 60-month TCO",
            f"{c_total!r} - {cost.cost_60m!r}",
            savings,
            "USD",
        ),
    )
    utilization = "Not available" if cost.utilization is None else f"{cost.utilization:.1%}"
    return TcoResponse(
        **projection.model_dump(),
        accounting=TcoAccounting(
            candidate_id=candidate.candidate_id,
            rows=tuple(rows),
            fx=FxInfo(
                rate=catalog.fx_active_rate,
                source_id=catalog.fx.source_id,
                rate_date=catalog.fx.rate_date,
                is_override=catalog.fx_is_override,
            ),
            includes_resale=financials.include_resale_value,
            break_even_month=dict(projection.timeline.break_even_months).get(
                "baseline_c_eu_sovereign_api_cumulative"
            )
            if projection.timeline
            else None,
            utilization_text=utilization,
        ),
    )
