"""One `*Input` contract per public engine and decision function (design.md § "Engine call
convention"). Every engine takes one input contract plus `EngineParameters`."""

from pydantic import Field

from ai_tco_dss.domain.base import Contract, Metric, Money
from ai_tco_dss.domain.benchmark_conditions import BenchmarkConditions
from ai_tco_dss.domain.catalog import (
    ApiPrices,
    BenchmarkRecord,
    Catalog,
    ElectricityTariff,
    HardwareSpec,
    HarnessEntry,
    ModelSpec,
    RentalSpec,
    StaffingHub,
    SubscriptionPlan,
    UseCaseSpec,
)
from ai_tco_dss.domain.enums import BenchmarkMetric, PrecisionFormat, RankingMethod
from ai_tco_dss.domain.results import (
    BaselineD,
    BaselineResult,
    CandidateEvaluation,
    HybridCost,
    PerformanceResult,
    RentalCost,
    SizingResult,
    TcoResult,
    WorkloadResult,
)
from ai_tco_dss.domain.scenario import (
    CriterionWeights,
    EnterpriseFinancials,
    Scenario,
    SizingOptions,
    WorkloadProfile,
)


class BenchmarkSet(Contract):
    """Benchmark_Records pre-filtered for one (model_id, hardware_id) pair."""

    records: tuple[BenchmarkRecord, ...]


class WorkloadInput(Contract):
    profile: WorkloadProfile
    model: ModelSpec
    harnesses: tuple[HarnessEntry, ...]


class SizingInput(Contract):
    hardware: HardwareSpec
    model: ModelSpec
    precision: PrecisionFormat
    requested_nodes: float  # float so that non-integers reach the engine check (Req 18.7)
    options: SizingOptions
    profile: WorkloadProfile
    license_alternatives: tuple[str, ...]


class BenchmarkQuery(Contract):
    conditions: BenchmarkConditions | None = None
    records: BenchmarkSet
    metric: BenchmarkMetric
    model_id: str
    hardware_id: str | None
    precision: PrecisionFormat | None
    target_context: int | None
    tolerance: float


class PerformanceInput(Contract):
    hardware: HardwareSpec
    model: ModelSpec
    precision: PrecisionFormat
    sizing: SizingResult
    workload: WorkloadResult
    profile: WorkloadProfile
    options: SizingOptions
    benchmarks: BenchmarkSet
    use_measured: bool = True


class ApiPerformanceInput(Contract):
    model: ModelSpec
    workload: WorkloadResult
    profile: WorkloadProfile


class TcoInput(Contract):
    options: SizingOptions = Field(default_factory=SizingOptions)
    hardware: HardwareSpec
    nodes: int
    sizing: SizingResult
    performance: PerformanceResult
    workload: WorkloadResult
    profile: WorkloadProfile
    financials: EnterpriseFinancials
    tariffs: tuple[ElectricityTariff, ...]
    hubs: tuple[StaffingHub, ...]
    benchmarks: BenchmarkSet
    demand_share: float = Field(1.0, ge=0.0, le=1.0)
    cloud_ttft_s: float | None = None


class ApiCostInput(Contract):
    model_id: str
    workload: WorkloadResult
    profile: WorkloadProfile
    prices: ApiPrices
    eu_pinned: bool
    gateway_fee_usd: float


class BaselineInput(Contract):
    workload_ref: WorkloadResult
    profile: WorkloadProfile
    ref_model: ModelSpec
    plan: SubscriptionPlan
    gateway_fee_usd: float
    financials: EnterpriseFinancials


class BaselineDInput(Contract):
    performance: PerformanceResult | None
    utilization: float | None
    profile: WorkloadProfile
    model: ModelSpec
    infeasible_reason: str | None


class RentalCostInput(Contract):
    rental: RentalSpec
    personnel_monthly_usd: float


class HybridCostInput(Contract):
    local: TcoResult
    api_c_monthly_usd: float
    local_offload_ratio: float  # no bound here: the engine raises the Req 25.6 error


class TimelineInput(Contract):
    anchor_candidate_id: str
    onprem: TcoResult
    include_resale: bool
    baselines: BaselineResult
    baseline_d: BaselineD
    rental: RentalCost
    hybrid: HybridCost
    hybrid_api_model_id: str
    decode_tps: Metric | None
    open_output_price: Money | None


class CandidateInput(Contract):
    catalog: Catalog
    scenario: Scenario


class FilterInput(Contract):
    candidates: tuple[CandidateEvaluation, ...]
    scenario: Scenario
    use_case: UseCaseSpec


class RankingInput(Contract):
    tps_target: float | None = Field(None, gt=0)
    ttft_target: float | None = Field(None, gt=0)
    feasible: tuple[CandidateEvaluation, ...]
    weights: CriterionWeights
    method: RankingMethod
