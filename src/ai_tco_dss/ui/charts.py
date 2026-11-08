"""Pure Plotly figure factories (Req 35.8): contracts in, figures out, no I/O, no Streamlit."""

import plotly.graph_objects as go  # type: ignore[import-untyped]

from ai_tco_dss.domain import DisplaySettings, SizePairings, SizeResult, TcoProjection
from ai_tco_dss.ui import theme

NO_DATA = "No data available"
EVICTION_BADGE = "EVICTION RISK"
BAR_HALF_HEIGHT = 0.45

TIMELINE_SERIES = (
    ("on_prem_cumulative", "On-premise", None),
    ("eu_dedicated_rental_cumulative", "EU dedicated rental", "Dedicated EU Cloud GPU"),
    (
        "baseline_a_subscription_cumulative",
        "Baseline A · subscription",
        "Baseline A (consumer subscription)",
    ),
    (
        "baseline_b_global_api_cumulative",
        "Baseline B · global API",
        "Baseline B / D (global API / OpenRouter value)",
    ),
    (
        "baseline_c_eu_sovereign_api_cumulative",
        "Baseline C · EU-pinned API",
        "Baseline C (EU-pinned API)",
    ),
    (
        "baseline_d_openrouter_value_cumulative",
        "Baseline D · output market value",
        "Baseline B / D (global API / OpenRouter value)",
    ),
    ("hybrid_split_cumulative", "Hybrid split", "Hybrid Split"),
)


def tco_timeline_figure(projection: TcoProjection, display: DisplaySettings) -> go.Figure:
    """Req 35.4-10: pure cumulative comparison with explicit blocked and OOM labels."""
    timeline = projection.timeline
    if timeline is None or not timeline.points:
        return _empty_figure()
    fig = go.Figure()
    divisor = display.fx_rate if display.currency == "EUR" else 1.0
    months = [p.month for p in timeline.points]
    crossings = dict(timeline.break_even_months)
    for field, label, archetype in TIMELINE_SERIES:
        values = [getattr(p, field) for p in timeline.points]
        if all(v is None for v in values):
            continue
        color, dash, width = theme.ARCHETYPE_STYLE[archetype or projection.candidate.archetype]
        blocked = (
            field == "baseline_a_subscription_cumulative"
            and not projection.baselines.baseline_a_eligible
        )
        if field == "on_prem_cumulative":
            label += " · compliant" if projection.candidate.eu_compliant else " · non-compliant"
            if projection.candidate.sizing and not projection.candidate.sizing.is_feasible:
                label += " · OOM"
        if blocked:
            label += " [NON-COMPLIANT / BLOCKED]"
        elif field == "baseline_a_subscription_cumulative":
            dash = "solid"
        crossing = crossings.get(field)
        if field != "on_prem_cumulative" and crossing is None and not blocked:
            label += " · no break-even within 60 months"
        diamond = field == "baseline_d_openrouter_value_cumulative"
        fig.add_trace(
            go.Scatter(
                x=months,
                y=[v / divisor if v is not None else None for v in values],
                name=label,
                mode="lines+markers" if diamond else "lines",
                line={"color": color, "dash": dash, "width": width},
                marker={"symbol": "diamond" if diamond else "circle", "size": 4, "color": color},
                hovertemplate=f"Month %{{x}}<br>%{{y:,.2f}} {display.currency}"
                f"<extra>{label}</extra>",
            )
        )
        if crossing is not None and not blocked:
            point = timeline.points[crossing - 1]
            fig.add_trace(
                go.Scatter(
                    x=[crossing],
                    y=[point.on_prem_cumulative / divisor],
                    mode="markers",
                    name=f"t* = {crossing} · {label}",
                    marker={"color": color, "size": 9, "symbol": "diamond"},
                    hovertemplate=f"t* = {crossing}<br>%{{y:,.2f}} {display.currency}"
                    f"<extra>{label}</extra>",
                )
            )
    utilization = projection.candidate.utilization
    if utilization is not None and utilization < 0.70:
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0,
            x1=1,
            y0=0,
            y1=1,
            fillcolor=theme.ORANGE,
            opacity=0.06,
            line_width=0,
        )
        fig.add_annotation(
            text="Utilization Danger Zone (<70%)",
            x=0,
            y=0,
            xref="paper",
            yref="paper",
            showarrow=False,
            xanchor="left",
        )
    fig.update_layout(
        height=560,
        hovermode="x unified",
        font={"family": "Inter, sans-serif"},
        margin={"l": 15, "r": 15, "t": 25, "b": 15},
        xaxis={"title": "Month", "range": [1, 60]},
        yaxis={"title": f"Cumulative cost ({display.currency})", "tickformat": ",.0f"},
        legend={"orientation": "h", "y": -0.18, "font": {"size": 11}},
    )
    return fig


def _empty_figure() -> go.Figure:
    """A figure without data traces and a "No data available" annotation (Req 35.11)."""
    fig = go.Figure()
    fig.add_annotation(text=NO_DATA, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False})
    return fig


def pairing_label(position: int, item: SizeResult) -> str:
    """Bar label with the AA v5 score (1 decimal) and the token agreement (Req 35.2, 35.9)."""
    sizing = item.sizing
    aa = "n/a" if item.aa_index_v5 is None else f"{item.aa_index_v5.value:.1f}"
    rate = sizing.token_agreement_rate
    agreement = "n/a" if rate is None else f"{rate:.1%}"
    nodes = f" ({sizing.nodes_required} nodes)" if sizing.nodes_required > 1 else ""
    return (
        f"{position}. {sizing.hardware_id}{nodes} · {sizing.model_id} {sizing.precision.value}"
        f"<br>AA v5 {aa} · agreement {agreement}"
    )


def memory_fit_figure(pairings: SizePairings, display: DisplaySettings) -> go.Figure:
    """View 1: one horizontal stacked bar per pairing with usable-memory lines (Req 35.1 to 35.3).

    `display` is accepted for a uniform factory signature; memory is shown in GB.
    """
    items = pairings.items
    if not items:
        return _empty_figure()
    labels = [pairing_label(index + 1, item) for index, item in enumerate(items)]
    breakdowns = [dict(item.sizing.memory_breakdown) for item in items]
    patterns = [theme.EVICTION_HATCH if item.sizing.context_eviction_risk else "" for item in items]

    fig = go.Figure()
    for segment, color in theme.MEMORY_SEGMENT_COLORS:
        fig.add_trace(
            go.Bar(
                name=segment,
                orientation="h",
                y=labels,
                x=[breakdown.get(segment, 0.0) for breakdown in breakdowns],
                marker={
                    "color": color,
                    "pattern": {"shape": patterns, "fgcolor": theme.EVICTION_COLOR},
                },
                hovertemplate="%{y}<br>" + segment + ": %{x:.2f} GB<extra></extra>",
            )
        )

    for index, item in enumerate(items):
        sizing = item.sizing
        low, high = index - BAR_HALF_HEIGHT, index + BAR_HALF_HEIGHT
        fig.add_shape(
            type="line",
            name=f"usable_vram:{index}",
            x0=sizing.usable_memory_gb,
            x1=sizing.usable_memory_gb,
            y0=low,
            y1=high,
            xref="x",
            yref="y",
            line={"color": theme.THRESHOLD_COLOR, "width": 2},
            label={"text": f"usable {sizing.usable_memory_gb:.2f} GB", "textposition": "end"},
        )
        if sizing.usable_system_ram_gb is not None:
            fig.add_shape(
                type="line",
                name=f"usable_system_ram:{index}",
                x0=sizing.usable_system_ram_gb,
                x1=sizing.usable_system_ram_gb,
                y0=low,
                y1=high,
                xref="x",
                yref="y",
                line={"color": theme.THRESHOLD_COLOR, "width": 2, "dash": "dot"},
                label={
                    "text": f"system RAM {sizing.usable_system_ram_gb:.2f} GB",
                    "textposition": "start",
                },
            )
        if sizing.context_eviction_risk:
            fig.add_annotation(
                text=EVICTION_BADGE,
                x=sum(breakdowns[index].values()),
                y=labels[index],
                xref="x",
                yref="y",
                xanchor="left",
                xshift=6,
                showarrow=False,
                font={"color": theme.EVICTION_COLOR},
            )

    fig.update_layout(
        barmode="stack",
        xaxis={"title": {"text": "GB"}},
        yaxis={"autorange": "reversed"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
        height=180 + 90 * len(items),
        margin={"l": 10, "r": 10, "t": 40, "b": 40},
    )
    return fig
