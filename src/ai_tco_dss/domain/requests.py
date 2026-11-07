"""Service_Layer request and output contracts (design.md § "Result contracts")."""

from typing import Literal

from pydantic import Field

from ai_tco_dss.domain.base import Contract, IsoDate
from ai_tco_dss.domain.enums import PrecisionFormat
from ai_tco_dss.domain.results import (
    BaselineResult,
    CandidateEvaluation,
    PerformanceResult,
    QualityScore,
    SizingResult,
    TimelineResult,
    WorkloadResult,
)
from ai_tco_dss.domain.scenario import Scenario


class ScenarioRequest(Contract):
    scenario: Scenario


class RecommendRequest(Contract):
    scenario: Scenario


class SizeRequest(Contract):
    scenario: Scenario
    hardware_id: str
    model_id: str
    precision: PrecisionFormat
    nodes: float = 1.0  # float so that non-integers reach the engine check (Req 18.7)


class SizeResult(Contract):
    sizing: SizingResult
    performance: PerformanceResult | None
    workload: WorkloadResult
    aa_index_v5: QualityScore | None


class SizePairings(Contract):
    items: tuple[SizeResult, ...]


class TcoRequest(Contract):
    scenario: Scenario
    candidate_id: str


class TcoProjection(Contract):
    candidate: CandidateEvaluation
    timeline: TimelineResult | None
    baselines: BaselineResult


class CatalogItem(Contract):
    id: str
    label: str


class FxInfo(Contract):
    rate: float = Field(gt=0)
    source_id: str
    rate_date: IsoDate
    is_override: bool


class CatalogOverview(Contract):
    counts: tuple[tuple[str, int], ...]
    hardware: tuple[CatalogItem, ...]
    models: tuple[CatalogItem, ...]
    use_cases: tuple[CatalogItem, ...]
    presets: tuple[CatalogItem, ...]
    hubs: tuple[CatalogItem, ...]
    tariffs: tuple[CatalogItem, ...]
    default_active_users: int
    fx: FxInfo


class DisplaySettings(Contract):
    currency: Literal["USD", "EUR"] = "USD"
    fx_rate: float = Field(gt=0)
