"""Streamlit entry point: ``uv run streamlit run src/ai_tco_dss/ui/app.py``.

Start page: catalog counts and FX rate, then the View 1 tab with the memory-fit card and
the View 2 tab with the TCO card. All data comes through the Service_Layer.
"""

import streamlit as st

from ai_tco_dss.domain import CatalogOverview, WorkloadProfile
from ai_tco_dss.domain.errors import DssError
from ai_tco_dss.services import catalog_overview, load_workload
from ai_tco_dss.ui.cards import memory_fit_card, timeline_card
from ai_tco_dss.ui.state import init_state


@st.cache_resource
def _overview() -> CatalogOverview:
    return catalog_overview()


@st.cache_resource
def _default_workload() -> WorkloadProfile:
    return load_workload()


st.set_page_config(
    page_title="AI TCO DSS · Sovereign AI cost advisor",
    page_icon=":material/memory:",
    layout="wide",
)
init_state(st.session_state)
st.title("AI TCO DSS")
st.caption("Sovereign AI cost advisor · compare physical capacity and five-year deployment costs")

try:
    overview = _overview()
    workload = _default_workload()
except DssError as exc:
    st.error(f"The catalog could not be loaded:\n\n{exc.message}")
else:
    counts = dict(overview.counts)
    st.markdown(
        f"Catalog: {counts['hardware']} hardware, {counts['models']} models, "
        f"{counts['rentals']} rentals"
    )
    fx = overview.fx
    st.caption(f"FX rate {fx.rate:.4f} USD/EUR (source {fx.source_id}, rate date {fx.rate_date})")

    view_1, view_2 = st.tabs(["View 1: Memory fit", "View 2: 60-month TCO"])
    with view_1:
        memory_fit_card(overview, workload)
    with view_2:
        timeline_card(overview, workload)
