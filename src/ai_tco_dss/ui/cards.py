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
    EuEngineeringHub,
    Metric,
    PerformanceResult,
    PrecisionFormat,
    Scenario,
    SizePairings,
    SizeRequest,
    SizeResult,
    SizingOptions,
    TcoRequest,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import DssError
from ai_tco_dss.services import project_tco, size
from ai_tco_dss.ui.charts import memory_fit_figure
from ai_tco_dss.ui.formatting import tco_cost_rows, viability_badge
from ai_tco_dss.ui.state import DISPLAY_CURRENCY, RENDER_COUNTS

MEMORY_FIT = "memory_fit"
TIMELINE = "timeline"
DEFAULT_HARDWARE = "mac-studio-m5-max-128gb"
DEFAULT_MODEL = "qwen-3-8-flash-next"
DEFAULT_CONTEXT = 8_192
NODE_COUNTS = (1, 2, 4, 8)
PRECISIONS = tuple(PrecisionFormat)
TIMELINE_HARDWARE = "rtx-pro-6000-96gb"
TIMELINE_NODES = 4
TIMELINE_MODEL = "gpt-oss-120b"
DEFAULT_HUB = EuEngineeringHub.RO_CLUJ_BUCHAREST.value


def _count_render(card: str) -> None:
    counts = st.session_state[RENDER_COUNTS]
    counts[card] = counts.get(card, 0) + 1


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
    warnings = list(sizing.warnings)
    if result.performance is not None:
        st.table(
            performance_rows(result.performance),
            border="horizontal",
            hide_index=True,
            alt=f"Speed and latency of {title} with the origin of each value",
        )
        warnings.extend(result.performance.warnings)
    if warnings:
        st.markdown("\n".join(f"- {warning}" for warning in warnings))


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


def _index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


@st.fragment
def timeline_card(overview: CatalogOverview, workload: WorkloadProfile) -> None:
    """View 2: cost table of one on-premise candidate against Baselines A to C
    (Req 22, 23, 24, 34.3). The 60-month chart follows in Task 8."""
    _count_render(TIMELINE)
    hardware = {item.id: item.label for item in overview.hardware}
    models = {item.id: item.label for item in overview.models}
    hubs = [item.id for item in overview.hubs]
    with st.container(border=True):
        st.subheader("60-month TCO")
        with st.container(horizontal=True, vertical_alignment="bottom"):
            hardware_id = st.selectbox(
                "Hardware",
                list(hardware),
                index=_index(list(hardware), TIMELINE_HARDWARE),
                format_func=hardware.__getitem__,
                key="timeline_hardware",
            )
            nodes = st.segmented_control(
                "Nodes",
                NODE_COUNTS,
                default=TIMELINE_NODES,
                required=True,
                key="timeline_nodes",
            )
            model_id = st.selectbox(
                "Model",
                list(models),
                index=_index(list(models), TIMELINE_MODEL),
                format_func=models.__getitem__,
                key="timeline_model",
            )
            precision = st.selectbox(
                "Precision",
                PRECISIONS,
                index=PRECISIONS.index(PrecisionFormat.INT4),
                format_func=lambda p: p.value,
                key="timeline_precision",
            )
            hub = st.selectbox(
                "Staffing hub", hubs, index=_index(hubs, DEFAULT_HUB), key="timeline_hub"
            )
        if hardware_id is None or model_id is None or hub is None:
            st.info("Select hardware, a model and a staffing hub.")
            return
        candidate_id = f"onprem:{hardware_id}:{nodes or 1}x:{model_id}:{precision.value}"
        scenario = Scenario(
            workload=workload,
            financials=EnterpriseFinancials(engineering_hub_location=EuEngineeringHub(hub)),
            sizing=SizingOptions(weight_precision=precision),
            decision=DecisionOptions(),
        )
        try:
            projection = project_tco(TcoRequest(scenario=scenario, candidate_id=candidate_id))
        except (DssError, ValidationError) as exc:
            st.warning(str(exc), title="Candidate not evaluated")
            return
        candidate = projection.candidate
        tco = candidate.tco
        st.markdown(f"**{candidate.label}**")
        if candidate.sizing is not None and not candidate.sizing.is_feasible:
            st.warning(candidate.sizing.oom_reason or "infeasible", title="Infeasible deployment")
        st.caption(f"Viability: {viability_badge(tco.utilization if tco else None)}")
        st.table(
            tco_cost_rows(projection),
            border="horizontal",
            hide_index=True,
            alt=f"Cost components, Utilization and Baselines A to C for {candidate.label}",
        )
        if tco is not None and tco.warnings:
            st.markdown("\n".join(f"- {warning}" for warning in tco.warnings))
