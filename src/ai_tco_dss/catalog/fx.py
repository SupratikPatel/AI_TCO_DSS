"""EUR to USD conversion of a Catalog (design D-04, Req 12.3, 12.4)."""

from typing import Any

from pydantic import BaseModel

from ai_tco_dss.domain import Catalog, Money


def _convert_money(money: Money, rate: float, fx_source_id: str) -> Money:
    if money.currency == "EUR":
        original = money.value
    elif money.original_value is not None:
        original = money.original_value  # already converted: re-convert from the EUR amount
    else:
        return money  # USD-denominated at the source
    return money.model_copy(
        update={
            "value": original * rate,
            "currency": "USD",
            "original_value": original,
            "fx_source_id": fx_source_id,
        }
    )


def _convert(obj: Any, rate: float, fx_source_id: str) -> Any:
    if isinstance(obj, Money):
        return _convert_money(obj, rate, fx_source_id)
    if isinstance(obj, BaseModel):
        updates = {}
        for name in type(obj).model_fields:
            value = getattr(obj, name)
            converted = _convert(value, rate, fx_source_id)
            if converted is not value:
                updates[name] = converted
        return obj.model_copy(update=updates) if updates else obj
    if isinstance(obj, tuple):
        items = tuple(_convert(item, rate, fx_source_id) for item in obj)
        return items if any(a is not b for a, b in zip(items, obj, strict=True)) else obj
    return obj


def convert_catalog(catalog: Catalog, rate: float, *, is_override: bool) -> Catalog:
    """Return a copy of `catalog` with every Money in USD at `rate` (USD per EUR)."""
    if rate <= 0:
        raise ValueError(f"FX rate must be positive, got {rate}")
    converted: Catalog = _convert(catalog, rate, catalog.fx.source_id)
    return converted.model_copy(update={"fx_active_rate": rate, "fx_is_override": is_override})
