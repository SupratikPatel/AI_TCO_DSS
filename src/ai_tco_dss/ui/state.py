"""Session-state keys and new-session defaults (design.md § "Dashboard (`ui/`)")."""

from collections.abc import MutableMapping
from typing import Any

MODE = "mode"
USE_CASE = "use_case"
ACTIVE_USERS = "active_users"
LAST_VALID_ACTIVE_USERS = "last_valid_active_users"
PRESET = "preset"
EXPERT = "expert"
WEIGHTS = "weights"
METHOD = "method"
FX_OVERRIDE = "fx_override"
DISPLAY_CURRENCY = "display_currency"
RESULT = "result"
RESULT_ERROR = "result_error"
SELECTED_CANDIDATE_ID = "selected_candidate_id"
RENDER_COUNTS = "render_counts"

DEFAULTS: dict[str, Any] = {
    DISPLAY_CURRENCY: "USD",  # Req 12.1
    RESULT: None,
    RESULT_ERROR: None,
}


def init_state(state: MutableMapping[Any, Any]) -> None:
    """Set the defaults for keys that a new session does not have yet."""
    for key, value in DEFAULTS.items():
        state.setdefault(key, value)
    state.setdefault(RENDER_COUNTS, {})
