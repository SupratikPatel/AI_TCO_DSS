"""Streamlit entry point: ``uv run streamlit run src/ai_tco_dss/ui/app.py``.

Start page: catalog counts and FX rate, obtained only through the Service_Layer.
"""

import streamlit as st

from ai_tco_dss.domain import CatalogOverview
from ai_tco_dss.domain.errors import DssError
from ai_tco_dss.services import catalog_overview
from ai_tco_dss.ui.state import init_state


@st.cache_resource
def _overview() -> CatalogOverview:
    return catalog_overview()


init_state(st.session_state)
st.title("AI TCO DSS")

try:
    overview = _overview()
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
