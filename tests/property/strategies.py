"""Hypothesis strategies for every Domain_Contract (Property 1).

Strategies are derived from each contract's field annotations and declared
constraints (ge/gt/le/lt, min/max length), so bounds and boundary values follow
the contracts. A few model-level validators need small fix-ups, listed below.
"""

import inspect
import types
import typing
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from enum import Enum
from functools import cache
from typing import Any

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MinLen
from hypothesis import strategies as st
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ai_tco_dss.domain import (
    CandidateEvaluation,
    Contract,
    LifecycleClocks,
    ModelSpec,
    MonthlyTcoPoint,
    SourceEntry,
)

MODULES = ("base", "catalog", "scenario", "results", "inputs", "requests")
MAX_TUPLE = 2
FLOAT_RANGE = 1e9
INT_RANGE = 10**9


def contract_classes() -> list[type[BaseModel]]:
    """All concrete contract classes of `ai_tco_dss.domain`, sorted by name."""
    found: dict[str, type[BaseModel]] = {}
    for name in MODULES:
        module = __import__(f"ai_tco_dss.domain.{name}", fromlist=["_"])
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, Contract)
                and obj.__module__ == module.__name__
                and not obj.__pydantic_generic_metadata__["parameters"]
            ):
                found[obj.__name__] = obj
    return [found[n] for n in sorted(found)]


def _bounds(metadata: list[Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in metadata:
        if isinstance(item, FieldInfo):
            out.update(_bounds(list(item.metadata)))
        elif isinstance(item, Ge):
            out["min_value"] = item.ge
        elif isinstance(item, Gt):
            out["min_value"], out["exclude_min"] = item.gt, True
        elif isinstance(item, Le):
            out["max_value"] = item.le
        elif isinstance(item, Lt):
            out["max_value"], out["exclude_max"] = item.lt, True
        elif isinstance(item, MinLen):
            out["min_size"] = item.min_length
        elif isinstance(item, MaxLen):
            out["max_size"] = item.max_length
    return out


def _number(kind: type, bounds: dict[str, Any]) -> st.SearchStrategy[Any]:
    if kind is int:
        low = bounds.get("min_value", -INT_RANGE)
        high = bounds.get("max_value", INT_RANGE)
        low += 1 if bounds.get("exclude_min") else 0
        high -= 1 if bounds.get("exclude_max") else 0
        return st.integers(min_value=int(low), max_value=int(high))
    return st.floats(
        min_value=bounds.get("min_value", -FLOAT_RANGE),
        max_value=bounds.get("max_value", FLOAT_RANGE),
        exclude_min=bounds.get("exclude_min", False),
        exclude_max=bounds.get("exclude_max", False),
        allow_nan=False,
        allow_infinity=False,
    )


def for_type(annotation: Any, metadata: list[Any]) -> st.SearchStrategy[Any]:
    """Strategy for one annotation with its constraint metadata."""
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is typing.Annotated:
        return for_type(args[0], [*metadata, *args[1:]])
    if annotation is type(None):
        return st.none()
    if origin in (types.UnionType, typing.Union):
        return st.one_of(*(for_type(a, metadata) for a in args))
    if origin is typing.Literal:
        return st.sampled_from(args)
    bounds = _bounds(metadata)
    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            low = bounds.get("min_size", 0)
            high = bounds.get("max_size", max(low, MAX_TUPLE))
            return st.lists(for_type(args[0], []), min_size=low, max_size=high).map(tuple)
        return st.tuples(*(for_type(a, []) for a in args))
    if isinstance(annotation, type):
        if issubclass(annotation, BaseModel):
            return for_contract(annotation)
        if issubclass(annotation, Enum):
            return st.sampled_from(list(annotation))
        if annotation is bool:
            return st.booleans()
        if annotation in (int, float):
            return _number(annotation, bounds)
        if annotation is str:
            low = bounds.get("min_size", 0)
            return st.text(min_size=low, max_size=max(low, bounds.get("max_size", 8)))
        if annotation is date:
            return st.dates(min_value=date(2000, 1, 1), max_value=date(2100, 12, 31))
    raise NotImplementedError(f"no strategy for {annotation!r}")


def _fix_source_entry(kwargs: dict[str, Any]) -> dict[str, Any]:
    if not (kwargs["url"] or "").strip() and not (kwargs["reference"] or "").strip():
        kwargs["url"] = "https://example.org"
    return kwargs


def _fix_model_spec(kwargs: dict[str, Any]) -> dict[str, Any]:
    if kwargs["type"] == "commercial-api" and kwargs["api_prices"] is None:
        kwargs["type"] = "open-weights"
    if kwargs["type"] == "open-weights":
        kwargs["api_prices"] = None
        kwargs["eu_pinned_endpoint"] = None
    return kwargs


def _fix_lifecycle(kwargs: dict[str, Any]) -> dict[str, Any]:
    retention = kwargs["resale_value_retention_3yr"]
    clamped = min(max(retention.value, 0.0), 1.0)
    kwargs["resale_value_retention_3yr"] = retention.model_copy(update={"value": clamped})
    return kwargs


FIXUPS: dict[type[BaseModel], Callable[[dict[str, Any]], dict[str, Any]]] = {
    SourceEntry: _fix_source_entry,
    ModelSpec: _fix_model_spec,
    LifecycleClocks: _fix_lifecycle,
}

FX_OVERRIDE = st.none() | st.decimals(
    min_value=Decimal("0.5"), max_value=Decimal("2.0"), places=6
).map(float)


def _timeline_points() -> st.SearchStrategy[tuple[MonthlyTcoPoint, ...]]:
    """Exactly 60 points (months 1..60) built from one drawn template point."""
    return for_contract(MonthlyTcoPoint).map(
        lambda p: tuple(p.model_copy(update={"month": m}) for m in range(1, 61))
    )


def _candidate_tree() -> st.SearchStrategy[CandidateEvaluation]:
    """Generate bounded recursive component trees instead of recursing at construction.

    Exercise leaf, hybrid and nested JSON round trips; max_leaves limits example size,
    not the production contract's component depth.
    """
    fields = {
        name: for_type(info.annotation, list(info.metadata))
        for name, info in CandidateEvaluation.model_fields.items()
        if name != "components"
    }
    leaves = st.builds(CandidateEvaluation, components=st.just(()), **fields)
    return st.recursive(
        leaves,
        lambda children: st.builds(
            CandidateEvaluation,
            components=st.lists(children, min_size=1, max_size=2).map(tuple),
            **fields,
        ),
        max_leaves=4,
    )


FIELD_OVERRIDES: dict[tuple[str, str], Callable[[], st.SearchStrategy[Any]]] = {
    ("CandidateEvaluation", "components"): lambda: st.lists(_candidate_tree(), max_size=2).map(
        tuple
    ),
    ("Scenario", "fx_override"): lambda: FX_OVERRIDE,
    ("TimelineResult", "points"): _timeline_points,
}


@cache
def for_contract(cls: type[BaseModel]) -> st.SearchStrategy[Any]:
    """Strategy producing valid instances of `cls`."""
    fields: dict[str, st.SearchStrategy[Any]] = {}
    for name, info in cls.model_fields.items():
        override = FIELD_OVERRIDES.get((cls.__name__, name))
        strategy = override() if override else for_type(info.annotation, list(info.metadata))
        if not info.is_required():
            strategy = st.just(info.default) | strategy
        fields[name] = strategy
    fixup = FIXUPS.get(cls, lambda kwargs: kwargs)
    return st.fixed_dictionaries(fields).map(lambda kwargs: cls(**fixup(dict(kwargs))))
