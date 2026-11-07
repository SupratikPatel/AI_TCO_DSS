"""Contract base configuration, provenance wrappers and value origins (design D-01)."""

import re
from datetime import date
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _iso_date(value: object) -> object:
    """Accept `date` objects and `YYYY-MM-DD` strings only (no timestamps, no datetimes)."""
    if isinstance(value, date):
        return value
    if isinstance(value, str) and ISO_DATE.match(value):
        return value
    raise ValueError("date must be an ISO 8601 date in the format YYYY-MM-DD")


IsoDate = Annotated[date, BeforeValidator(_iso_date)]


class Contract(BaseModel):
    """Base class of every Domain_Contract: immutable, no undeclared fields."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
        validate_default=True,
        use_enum_values=False,
    )


class SourceTier(StrEnum):
    OFFICIAL = "official"
    THIRD_PARTY = "third_party"
    COMMUNITY = "community"
    FORMULA = "formula"
    ASSUMPTION = "assumption"


TIER_RANK: dict[SourceTier, int] = {
    SourceTier.OFFICIAL: 4,
    SourceTier.THIRD_PARTY: 3,
    SourceTier.COMMUNITY: 2,
    SourceTier.ASSUMPTION: 1,
    SourceTier.FORMULA: 0,
}


class Sourced[T](Contract):
    """A catalog value with its Provenance_Record."""

    value: T
    source_id: str = Field(min_length=1)
    tier: SourceTier
    accessed: IsoDate
    note: str | None = None


class Money(Sourced[float]):
    """A non-negative monetary amount; EUR amounts are converted to USD by the repository."""

    value: float = Field(ge=0)
    currency: Literal["EUR", "USD"]
    fx_source_id: str | None = None
    original_value: float | None = None


class ValueOrigin(Contract):
    origin: Literal["measured", "formula"]
    source_ids: tuple[str, ...] = Field(min_length=1)


class Metric(Contract):
    """A computed number with its Value_Origin."""

    value: float
    unit: str
    origin: ValueOrigin


class FormulaTrace(Contract):
    """Symbolic and substituted formula for the audit drawer (Req 36.1)."""

    name: str
    symbolic: str
    substituted: str
    result: float
    unit: str
