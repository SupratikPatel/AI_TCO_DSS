"""Property tests for catalog loading, validation and FX conversion."""

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

from ai_tco_dss.catalog import JsonCatalogRepository, loading
from ai_tco_dss.domain import Catalog, Money

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "catalog_min"
TRIPLE = {"source_id": "S", "tier": "official", "accessed": "2026-01-01"}

# --------------------------------------------------------------------------- Property 2

KEYS = st.sampled_from(["a", "b", "c", "value", "x"])
LEAVES = (
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(max_size=3)
)


def _with_triple(obj: dict[str, Any], add: bool) -> dict[str, Any]:
    return {**obj, **TRIPLE} if add else obj


TREES = st.recursive(
    LEAVES,
    lambda children: (
        st.lists(children, max_size=3)
        | st.builds(_with_triple, st.dictionaries(KEYS, children, max_size=3), st.booleans())
    ),
    max_leaves=20,
)


def _oracle(node: Any, path: str = "", covered: bool = False) -> list[str]:
    """Independent reference walk: a number is covered by any ancestor object with a triple."""
    if isinstance(node, bool) or node is None or isinstance(node, str):
        return []
    if isinstance(node, int | float):
        return [] if covered else [path]
    if isinstance(node, list):
        return [p for i, child in enumerate(node) for p in _oracle(child, f"{path}[{i}]", covered)]
    here = covered or TRIPLE.keys() <= node.keys()
    return [
        p
        for key, child in node.items()
        for p in _oracle(child, f"{path}.{key}" if path else key, here)
    ]


# Feature: ai-tco-dss-mvp, Property 2: Provenance coverage
@given(tree=TREES)
def test_property_2_provenance_coverage(tree: Any) -> None:
    """Property 2 (Req 8.3, 8.5): exactly the uncovered number paths are reported."""
    assert loading.uncovered_number_paths(tree) == _oracle(tree)


# --------------------------------------------------------------------------- Property 3


def _edit(rel: str, change: Callable[[Any], None]) -> Callable[[Path], str]:
    def inject(root: Path) -> str:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
        change(data)
        (root / rel).write_text(json.dumps(data), encoding="utf-8")
        return rel

    return inject


def _unparseable(root: Path) -> str:
    rel = "catalog/models/claude-sonnet-5-5.json"
    (root / rel).write_text('{"id": ', encoding="utf-8")
    return rel


def _duplicate_id(root: Path) -> str:
    data = json.loads((root / "catalog/models/qwen-3-8-27b.json").read_text(encoding="utf-8"))
    data["id"] = "mac-studio-m5-max-128gb"
    rel = "catalog/models/mac-studio-m5-max-128gb.json"
    (root / rel).write_text(json.dumps(data), encoding="utf-8")
    return "catalog/hardware/mac-studio-m5-max-128gb.json"


def _filename_mismatch(root: Path) -> str:
    rel = "catalog/models/qwen-renamed.json"
    (root / "catalog/models/qwen-3-8-27b.json").rename(root / rel)
    return rel


def _missing_context(root: Path) -> str:
    rel = "benchmarks/decode.json"
    record = {
        "metric": "decode_tps",
        "value": 10.0,
        "model_id": "qwen-3-8-27b",
        "source_id": "ASSUMPTION-MVP",
        "tier": "assumption",
        "accessed": "2026-01-01",
    }
    (root / rel).write_text(json.dumps({"records": [record]}), encoding="utf-8")
    return rel


INJECTORS: dict[str, Callable[[Path], str]] = {
    "unparseable": _unparseable,
    "missing_provenance": _edit(
        "catalog/hardware/mac-studio-m5-max-128gb.json", lambda d: d.update(idle_watts=10)
    ),
    "unknown_source": _edit(
        "catalog/hardware/rtx-pro-6000-96gb.json",
        lambda d: d["load_watts"].update(source_id="NOPE"),
    ),
    "duplicate_id": _duplicate_id,
    "filename_mismatch": _filename_mismatch,
    "dangling_model": _edit(
        "benchmarks/quality.json", lambda d: d["records"][0].update(model_id="ghost")
    ),
    "invalid_tier": _edit(
        "reference/electricity.json",
        lambda d: d["tariffs"][0]["price_per_kwh"].update(tier="rumour"),
    ),
    "future_date": _edit(
        "reference/staffing_hubs.json",
        lambda d: d["hubs"][0]["base_salary"].update(accessed="2999-01-01"),
    ),
    "missing_context_tokens": _missing_context,
}


# Feature: ai-tco-dss-mvp, Property 3: Validator reports every injected fault in one run
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(faults=st.sets(st.sampled_from(sorted(INJECTORS))))
def test_property_3_validator_reports_every_injected_fault(faults: set[str]) -> None:
    """Property 3 (Req 8.10, 11.3): one run names every injected fault's file."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "data"
        shutil.copytree(FIXTURE, root)
        expected = {INJECTORS[name](root) for name in sorted(faults)}
        report = loading.load_catalog(root)
    reported = {error.file for error in report.errors}
    assert expected <= reported, (faults, report.errors)
    assert (not report.errors) == (not faults)


# --------------------------------------------------------------------------- Property 5

EUR_CATALOG = loading.load_catalog(FIXTURE).catalog
REPOSITORY = JsonCatalogRepository(FIXTURE)


def _money(model: BaseModel) -> list[Money]:
    """Every Money in `model`, in field order (same order for equal structures)."""
    found: list[Money] = []
    for name in type(model).model_fields:
        value = getattr(model, name)
        for item in value if isinstance(value, tuple) else (value,):
            if isinstance(item, Money):
                found.append(item)
            elif isinstance(item, BaseModel):
                found.extend(_money(item))
    return found


def _snapshot() -> dict[str, bytes]:
    return {str(p): p.read_bytes() for p in sorted(FIXTURE.rglob("*.json"))}


# Feature: ai-tco-dss-mvp, Property 5: Repository FX conversion
@given(rate=st.floats(min_value=0.5, max_value=2.0, allow_nan=False))
def test_property_5_repository_fx_conversion(rate: float) -> None:
    """Property 5 (Req 12.3, 12.4): every Money is USD = EUR * rate; files unchanged."""
    assert isinstance(EUR_CATALOG, Catalog)
    before = _snapshot()
    converted = REPOSITORY.catalog(rate)
    originals = _money(EUR_CATALOG)
    results = _money(converted)
    assert len(results) == len(originals) > 0
    for original, result in zip(originals, results, strict=True):
        assert result.currency == "USD"
        expected = original.value * rate if original.currency == "EUR" else original.value
        assert abs(result.value - expected) <= 1e-9 * max(1.0, abs(expected))
    assert converted.fx_active_rate == rate
    assert _snapshot() == before
