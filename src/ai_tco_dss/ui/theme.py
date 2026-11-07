"""Okabe-Ito colour constants and chart styles (Req 37.1; ledger C-004).

Every trace colour in a Dashboard figure comes from these constants.
"""

ORANGE = "#E69F00"
SKY_BLUE = "#56B4E9"
BLUISH_GREEN = "#009E73"
YELLOW = "#F0E442"
BLUE = "#0072B2"
VERMILLION = "#D55E00"
REDDISH_PURPLE = "#CC79A7"
BLACK = "#000000"

OKABE_ITO = (ORANGE, SKY_BLUE, BLUISH_GREEN, YELLOW, BLUE, VERMILLION, REDDISH_PURPLE, BLACK)

# OOM / Thermal / Eviction Warning archetype (ledger C-004): vermillion diagonal hatch.
EVICTION_COLOR = VERMILLION
EVICTION_HATCH = "/"

# View 1 memory segments in the fixed order of Req 35.1, one colour each.
MEMORY_SEGMENT_COLORS = (
    ("weights", BLUE),
    ("kv_cache_active", SKY_BLUE),
    ("agent_state_parked", BLUISH_GREEN),
    ("os_reserved", YELLOW),
    ("runtime_overhead", REDDISH_PURPLE),
)
THRESHOLD_COLOR = BLACK
