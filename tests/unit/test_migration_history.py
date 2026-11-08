"""Approved migration amendments must preserve the relocated domain specifications."""

import pytest
from test_repository_layout import _normalise


def test_original_content_guard_ignores_approved_web_delivery_amendments():
    """Req 1.10 still catches any unapproved edit after the delivery amendment."""
    notice = (
        "> **Active architecture decision - 2026-11-07:** The MVP frontend is a dedicated "
        "React/TypeScript web application with Vite, Tailwind and shadcn/ui, backed by FastAPI "
        "and the existing Python services. Streamlit is the legacy prototype. Read "
        "[the web migration contract](09_WEB_FRONTEND_MIGRATION.md) and "
        "[the Stitch design reference](08_MVP_DESIGN_REFERENCE.md) before implementation. "
        "Where historical UI instructions below conflict, Requirement 43 and the migration "
        "contract take precedence.\n\n"
    )
    assert _normalise(notice + "original domain text") == "original domain text"
    assert _normalise(notice + "changed domain text") != "original domain text"
    with pytest.raises(AssertionError):
        _normalise(notice.replace("Python services", "JavaScript calculations") + "text")
