"""Dashboard smoke test (Req 6.4)."""

import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[2] / "src" / "ai_tco_dss" / "ui" / "app.py"


def test_app_start_page_renders_within_30_seconds() -> None:
    """Req 6.4: the start page renders within 30 s without any exception."""
    start = time.monotonic()
    at = AppTest.from_file(str(APP_PATH), default_timeout=30)
    at.run()
    elapsed = time.monotonic() - start

    assert not at.exception
    assert not at.error
    assert elapsed < 30
    assert [t.value for t in at.title] == ["AI TCO DSS"]
    assert [c.value for c in at.caption] == ["Catalog not loaded yet"]
