"""Property 52: preset and popularity validation (Req 32.8)."""

import math

from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.catalog import loading

CRITERIA = ("tco_60m", "quality", "effective_tps", "ttft", "risk", "popularity")
DOMINANT = {"cheapest": "tco_60m", "most-capable": "quality", "popular": "popularity"}
PRESET_IDS = st.sampled_from(["cheapest", "best-fit", "most-capable", "popular"])
WEIGHT = st.floats(min_value=-0.5, max_value=1.5, allow_nan=False) | st.sampled_from([0.0, 1.0])


def _normalised(raw: list[float]) -> list[float]:
    total = sum(raw)
    return [w / total for w in raw] if total > 0 else raw


WEIGHT_VECTORS = st.one_of(
    st.lists(WEIGHT, min_size=6, max_size=6),
    st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=6, max_size=6).map(_normalised),
)
KEY_SETS = st.one_of(
    st.just(CRITERIA),
    st.lists(st.sampled_from(CRITERIA), min_size=5, max_size=5, unique=True).map(tuple),
)


def _expected_valid(preset_id: str, weights: dict[str, float]) -> bool:
    if set(weights) != set(CRITERIA):
        return False
    if not all(0.0 <= w <= 1.0 for w in weights.values()):
        return False
    if not math.isclose(sum(weights.values()), 1.0, rel_tol=0.0, abs_tol=1e-6):
        return False
    if preset_id == "best-fit":
        return all(w > 0 for w in weights.values())
    top = DOMINANT[preset_id]
    return all(weights[top] > weights[c] for c in CRITERIA if c != top)


@given(PRESET_IDS, WEIGHT_VECTORS, KEY_SETS)
def test_property_52_preset_check_matches_oracle(
    preset_id: str, vector: list[float], keys: tuple[str, ...]
) -> None:
    """Property 52 (Req 32.8): a preset passes iff it has six weights in [0, 1] summing to
    1 +/- 1e-6 and satisfies its preset-specific rule (Req 32.2 to 32.5)."""
    weights = dict(zip(keys, vector, strict=False))
    violations = loading.preset_violations(preset_id, weights)
    assert (violations == []) == _expected_valid(preset_id, weights), (weights, violations)


ENTRIES = st.lists(
    st.tuples(
        st.sampled_from(["m-a", "m-b", "m-c", "m-d"]),
        st.floats(min_value=-10.0, max_value=1e6, allow_nan=False),
    ),
    max_size=6,
)


@given(ENTRIES)
def test_property_52_popularity_check_matches_oracle(entries: list[tuple[str, float]]) -> None:
    """Property 52 (Req 32.8): a popularity list passes iff all values are >= 0 and the
    `model_id`s are unique; every violation names the offending entry."""
    violations = loading.popularity_violations(entries)
    ids = [model_id for model_id, _ in entries]
    valid = all(v >= 0 for _, v in entries) and len(ids) == len(set(ids))
    assert (violations == []) == valid, (entries, violations)
    for index, message in violations:
        assert 0 <= index < len(entries)
        assert entries[index][0] in message
