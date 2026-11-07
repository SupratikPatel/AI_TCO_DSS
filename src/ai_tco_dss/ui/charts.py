"""Pure Plotly figure factories (Req 35.8): contracts in, figures out, no I/O, no Streamlit."""

import plotly.graph_objects as go  # type: ignore[import-untyped]

from ai_tco_dss.domain import DisplaySettings, SizePairings, SizeResult
from ai_tco_dss.ui import theme

NO_DATA = "No data available"
EVICTION_BADGE = "EVICTION RISK"
BAR_HALF_HEIGHT = 0.45


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
