"""Dashboard smoke test (Req 6.1, 6.4)."""

import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

from ai_tco_dss.services import catalog_overview

APP_PATH = Path(__file__).resolve().parents[2] / "src" / "ai_tco_dss" / "ui" / "app.py"


def _run_app() -> tuple[AppTest, float]:
    start = time.monotonic()
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    return at, time.monotonic() - start


def test_req_6_4_start_page_renders_within_30_seconds() -> None:
    """Req 6.4: the start page renders within 30 s without any exception or error."""
    at, elapsed = _run_app()
    assert not at.exception
    assert not at.error
    assert elapsed < 30
    assert [t.value for t in at.title] == ["AI TCO DSS"]


def test_req_6_1_start_page_shows_catalog_counts_from_the_service() -> None:
    """Req 6.1: hardware and model counts come from `catalog_overview`."""
    overview = catalog_overview()
    counts = dict(overview.counts)
    at, _ = _run_app()
    texts = [m.value for m in at.markdown] + [c.value for c in at.caption]
    expected = (
        f"Catalog: {counts['hardware']} hardware, {counts['models']} models, "
        f"{counts['rentals']} rentals"
    )
    assert expected in texts, texts
    fx = overview.fx
    assert any(f"{fx.rate:.4f} USD/EUR" in t and fx.source_id in t for t in texts), texts
