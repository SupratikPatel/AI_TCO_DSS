"""Pure display helpers: viability badge and the View 2 cost table (Req 23.5 to 23.7, 34.3).

Monetary values are shown in USD; display-currency conversion follows in Task 11.
"""

from ai_tco_dss.domain import Metric, PerformanceResult, TcoProjection, ValueOrigin

UTILIZATION_THRESHOLD = 0.70  # spec 02 §2.3, Req 23.5
IDLE_WARNING_THRESHOLD = 0.55  # spec 02 §2.3, Req 23.6
NON_COMPLIANT = "[NON-COMPLIANT / BLOCKED]"
OPEX_LABELS = (
    ("energy", "Energy OpEx / month"),
    ("personnel", "Personnel OpEx / month"),
    ("nim_licensing", "NVIDIA NIM licensing / month"),
    ("capital_opportunity", "Capital opportunity cost / month"),
    ("wait_penalty", "Wait-time penalty / month"),
    ("eviction_loss", "Eviction loss / month"),
)


def viability_badge(utilization: float | None) -> str:
    """Badge text of Req 34.3; undefined Utilization is capacity-insufficient (Req 23.8)."""
    if utilization is None or utilization > 1.0:
        return "capacity-insufficient"
    if utilization < IDLE_WARNING_THRESHOLD:
        return "idle capacity warning"
    if utilization < UTILIZATION_THRESHOLD:
        return "below threshold"
    return "viable"


def usd(value: float) -> str:
    return f"{value:,.2f} USD"


def origin_label(origin: ValueOrigin) -> str:
    return f"{origin.origin} ({', '.join(origin.source_ids)})"


def _metric_origin(metric: Metric | None) -> str:
    return "n/a" if metric is None else origin_label(metric.origin)


def tco_cost_rows(projection: TcoProjection) -> dict[str, list[str]]:
    """Columns Item, Value and Origin of the View 2 cost table (Req 22, 23, 24, 34.3)."""
    rows: list[tuple[str, str, str]] = []
    tco = projection.candidate.tco
    if tco is not None:
        opex = dict(tco.monthly_opex)
        rows.append(("CapEx", usd(tco.capex.value), origin_label(tco.capex.origin)))
        rows.extend((label, usd(opex[name]), "formula") for name, label in OPEX_LABELS)
        rows.append(("Monthly OpEx total", usd(tco.monthly_opex_total), "formula"))
        rows.append(
            (
                "Munich vs Romania personnel savings / month",
                usd(tco.munich_vs_romania_personnel_savings_monthly),
                "formula",
            )
        )
        utilization = "not defined" if tco.utilization is None else f"{tco.utilization:.1%}"
        rows.append(
            (
                "Utilization",
                f"{utilization} · {viability_badge(tco.utilization)}",
                _metric_origin(tco.aggregate_tps),
            )
        )
        rows.append(("60-month TCO", usd(tco.cost_60m), "formula"))
    baselines = projection.baselines
    a_value = usd(baselines.a_monthly.value)
    if not baselines.baseline_a_eligible:
        reasons = "; ".join(baselines.baseline_a_ineligibility_reasons)
        a_value = f"{a_value} · {NON_COMPLIANT}: {reasons}"
    rows.append(
        ("Baseline A (subscription) / month", a_value, origin_label(baselines.a_monthly.origin))
    )
    rows.append(
        (
            "Baseline B (global API) / month",
            usd(baselines.b_monthly.value),
            origin_label(baselines.b_monthly.origin),
        )
    )
    rows.append(
        (
            "Baseline C (EU-pinned API) / month",
            usd(baselines.c_monthly.value),
            origin_label(baselines.c_monthly.origin),
        )
    )
    rows.append(
        (
            "Compliance tax delta (C - A) / month",
            usd(baselines.compliance_tax_delta_monthly),
            "formula",
        )
    )
    return {
        "Item": [item for item, _, _ in rows],
        "Value": [value for _, value, _ in rows],
        "Origin": [origin for _, _, origin in rows],
    }


def _origin_label(metric: Metric | None) -> str:
    if metric is None:
        return "n/a"
    return f"{metric.origin.origin} ({', '.join(metric.origin.source_ids)})"


def performance_rows(performance: PerformanceResult) -> dict[str, list[str]]:
    """Columns of the performance table: value with unit and Value_Origin with sources."""
    metrics = (
        ("Decode TPS", performance.decode_tps),
        ("Prefill TPS", performance.prefill_tps),
        ("TTFT", performance.ttft_s),
        ("Effective TPS", performance.effective_tps),
        ("1M-token prefill", performance.prefill_1m_minutes),
    )
    return {
        "Metric": [name for name, _ in metrics],
        "Value": ["n/a" if m is None else f"{m.value:,.1f} {m.unit}" for _, m in metrics],
        "Origin": [_origin_label(m) for _, m in metrics],
    }
