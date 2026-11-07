"""Simulator_Cards: Dashboard panels that own their input widgets (Req 37.5).

Each card is one function decorated with `@st.fragment`, so a widget change reruns only
that card. Each run increments `render_counts[<card>]` for the fragment test (Req 37.6).
"""

import streamlit as st
from pydantic import ValidationError

from ai_tco_dss.domain import (
    CatalogOverview,
    DecisionOptions,
    DisplaySettings,
    EnterpriseFinancials,
    PrecisionFormat,
    Scenario,
    SizePairings,
    SizeRequest,
    SizeResult,
    SizingOptions,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import DssError
from ai_tco_dss.services import size
from ai_tco_dss.ui.charts import memory_fit_figure
from ai_tco_dss.ui.state import DISPLAY_CURRENCY, RENDER_COUNTS

MEMORY_FIT = "memory_fit"
DEFAULT_HARDWARE = "mac-studio-m5-max-128gb"
DEFAULT_MODEL = "qwen-3-8-flash-next"
DEFAULT_CONTEXT = 8_192
NODE_COUNTS = (1, 2, 4, 8)
PRECISIONS = tuple(PrecisionFormat)


def _count_render(card: str) -> None:
    counts = st.session_state[RENDER_COUNTS]
    counts[card] = counts.get(card, 0) + 1


def _pairing_status(result: SizeResult) -> None:
    sizing = result.sizing
    title = f"{sizing.hardware_id} · {sizing.model_id} {sizing.precision.value}"
    if sizing.is_feasible:
        st.success(
            f"Fits: up to {sizing.max_concurrent_users} concurrent users at the target context "
            f"(usable memory {sizing.usable_memory_gb:.2f} GB).",
            title=f"{title}: feasible",
        )
    else:
        st.warning(sizing.oom_reason or "infeasible", title=f"{title}: infeasible")
    if sizing.warnings:
        st.markdown("\n".join(f"- {warning}" for warning in sizing.warnings))


@st.fragment
def memory_fit_card(overview: CatalogOverview, workload: WorkloadProfile) -> None:
    """View 1: memory fit of the selected hardware-model pairings (Req 35.1 to 35.3)."""
    _count_render(MEMORY_FIT)
    hardware = {item.id: item.label for item in overview.hardware}
    models = {item.id: item.label for item in overview.models}
    with st.container(border=True):
        st.subheader("Memory fit")
        hardware_ids = st.multiselect(
            "Hardware",
            list(hardware),
            default=[DEFAULT_HARDWARE] if DEFAULT_HARDWARE in hardware else None,
            format_func=hardware.__getitem__,
            key="memory_fit_hardware",
        )
        model_ids = st.multiselect(
            "Model",
            list(models),
            default=[DEFAULT_MODEL] if DEFAULT_MODEL in models else None,
            format_func=models.__getitem__,
            key="memory_fit_models",
        )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            precision = st.selectbox(
                "Precision",
                PRECISIONS,
                index=PRECISIONS.index(PrecisionFormat.INT4),
                format_func=lambda p: p.value,
                key="memory_fit_precision",
            )
            context = st.number_input(
                "Target context (tokens)",
                min_value=1,
                max_value=2_000_000,
                value=DEFAULT_CONTEXT,
                step=1_024,
                key="memory_fit_context",
            )
            nodes = st.segmented_control(
                "Nodes", NODE_COUNTS, default=1, required=True, key="memory_fit_nodes"
            )
            mac_override = st.toggle("Mac wired-memory override", key="memory_fit_mac_override")
            amd_override = st.toggle("Linux AMD override", key="memory_fit_amd_override")

        scenario = Scenario(
            workload=workload,
            financials=EnterpriseFinancials(),
            sizing=SizingOptions(
                weight_precision=precision,
                target_context_length=int(context),
                apply_mac_wired_memory_override=mac_override,
                linux_amd_override=amd_override,
            ),
            decision=DecisionOptions(),
        )
        results: list[SizeResult] = []
        errors: list[str] = []
        for hardware_id in hardware_ids:
            for model_id in model_ids:
                request = SizeRequest(
                    scenario=scenario,
                    hardware_id=hardware_id,
                    model_id=model_id,
                    precision=precision,
                    nodes=float(nodes or 1),
                )
                try:
                    results.append(size(request))
                except (DssError, ValidationError) as exc:
                    errors.append(f"{hardware[hardware_id]} · {models[model_id]}: {exc}")

        display = DisplaySettings(
            currency=st.session_state[DISPLAY_CURRENCY], fx_rate=overview.fx.rate
        )
        st.plotly_chart(
            memory_fit_figure(SizePairings(items=tuple(results)), display),
            alt="Memory needed by each hardware and model pairing against its usable memory",
            key="memory_fit_chart",
        )
        for result in results:
            _pairing_status(result)
        for error in errors:
            st.warning(error, title="Pairing not sized")
