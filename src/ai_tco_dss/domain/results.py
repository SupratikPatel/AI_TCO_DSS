"""Engine and decision result contracts (design.md § "Result contracts")."""

from typing import Literal

from pydantic import Field

from ai_tco_dss.domain.base import Contract, FormulaTrace, IsoDate, Metric, ValueOrigin
from ai_tco_dss.domain.catalog import SourceEntry
from ai_tco_dss.domain.enums import (
    BenchmarkMetric,
    CandidateKind,
    Criterion,
    PrecisionFormat,
    RankingMethod,
    UseCaseId,
)
from ai_tco_dss.domain.scenario import CriterionWeights, Scenario


class WorkloadResult(Contract):
    monthly_requests: int
    s_effective: float
    t_in_hat: float
    t_out_hat: float
    out_think: float
    kappa_mega: float
    nu_verify: float
    tau: float
    monthly_tokens: float
    monthly_output_demand: float


class SizingResult(Contract):
    hardware_id: str
    model_id: str
    precision: PrecisionFormat
    requested_nodes: int
    nodes_required: int
    alpha_scaling: float
    is_feasible: bool
    oom_reason: str | None = None
    usable_memory_gb: float
    usable_memory_default_gb: float
    usable_system_ram_gb: float | None
    weights: Metric
    kv_per_token_bytes: float
    m_kv_single_gb: float
    kv_pool_gb: float
    max_concurrent_users: int
    max_usable_context: int
    agent_state_memory_required_gb: float
    memory_breakdown: tuple[tuple[str, float], ...]
    triggered_mac_default_split_trap: bool = False
    meets_128k_agentic_context_floor: bool = True
    eu_commercial_license_valid: bool = True
    context_eviction_risk: bool = False
    token_agreement_rate: float | None = None
    thunderbolt_mesh_cables: int = 0
    warnings: tuple[str, ...]
    traces: tuple[FormulaTrace, ...]


class PerformanceResult(Contract):
    decode_tps: Metric | None
    prefill_tps: Metric | None
    ttft_s: Metric | None
    effective_tps: Metric | None
    prefill_1m_minutes: Metric | None = None
    warnings: tuple[str, ...]
    traces: tuple[FormulaTrace, ...]


class TcoResult(Contract):
    units: int
    gpu_count: int
    capex: Metric
    monthly_opex: tuple[tuple[str, float], ...]
    monthly_opex_total: float
    munich_vs_romania_personnel_savings_monthly: float
    aggregate_tps: Metric | None
    capacity_tokens_month: float | None
    utilization: float | None
    meets_70_percent_utilization_threshold: bool
    capacity_insufficient: bool
    resale_retention_3yr: float
    cost_60m: float
    warnings: tuple[str, ...]
    traces: tuple[FormulaTrace, ...]


class MonthlyTcoPoint(Contract):
    month: int = Field(ge=1, le=60)
    on_prem_cumulative: float
    eu_dedicated_rental_cumulative: float
    baseline_a_subscription_cumulative: float
    baseline_b_global_api_cumulative: float
    baseline_c_eu_sovereign_api_cumulative: float
    baseline_d_openrouter_value_cumulative: float | None
    hybrid_split_cumulative: float


class TimelineResult(Contract):
    anchor_candidate_id: str
    rental_id: str
    hybrid_api_model_id: str
    points: tuple[MonthlyTcoPoint, ...] = Field(min_length=60, max_length=60)
    break_even_months: tuple[tuple[str, int | None], ...]
    single_stream_break_even_years: Metric | None = None
    include_resale: bool


class BaselineResult(Contract):
    reference_model_id: str
    a_monthly: Metric
    b_monthly: Metric
    c_monthly: Metric
    baseline_a_eligible: bool
    baseline_a_ineligibility_reasons: tuple[str, ...]
    compliance_tax_delta_monthly: float
    currency: Literal["USD"] = "USD"


class ApiCost(Contract):
    """Monthly cost of one API model priced as Baseline B (global) or C (EU-pinned)."""

    model_id: str
    eu_pinned: bool
    per_request_usd: float
    monthly: Metric


class BaselineD(Contract):
    monthly: Metric | None
    unavailable_reason: str | None


class RentalCost(Contract):
    rental_id: str
    setup_fee_usd: float
    monthly_usd: float
    personnel_monthly_usd: float
    cost_60m: float
    origin: ValueOrigin


class HybridCost(Contract):
    local_offload_ratio: float
    capex_usd: float
    monthly_usd: float
    cost_60m: float
    origin: ValueOrigin


class FilterFailure(Contract):
    name: str
    measured: str
    threshold: str


class CriterionScore(Contract):
    criterion: Criterion
    raw: float | None
    missing: bool
    normalised: float
    weight: float
    contribution: float


class QualityScore(Contract):
    value: float
    benchmark: BenchmarkMetric
    origin: ValueOrigin
    fallback_note: str | None


class CandidateEvaluation(Contract):
    candidate_id: str
    kind: CandidateKind
    label: str
    archetype: str
    hardware_id: str | None
    nodes: int | None
    model_id: str
    precision: PrecisionFormat | None
    rental_id: str | None
    api_model_id: str | None
    local_candidate_id: str | None
    sizing: SizingResult | None
    performance: PerformanceResult | None
    tco: TcoResult | None
    capex: float
    monthly_cost: float
    cost_60m: float
    price_origin: ValueOrigin
    quality: QualityScore | None
    risk: float
    popularity: float
    utilization: float | None
    eu_compliant: bool
    failures: tuple[FilterFailure, ...]
    notes: tuple[str, ...]
    # Filter facts travel with the evaluation; hybrid averages cannot establish feasibility.
    model_max_context_tokens: int | None = None
    api_has_eu_endpoint: bool = False
    components: tuple["CandidateEvaluation", ...] = ()


class CandidateSet(Contract):
    candidates: tuple[CandidateEvaluation, ...]
    warnings: tuple[str, ...]


class FilteredCandidates(Contract):
    feasible: tuple[CandidateEvaluation, ...]
    rejected: tuple[CandidateEvaluation, ...]


class RankedCandidate(Contract):
    rank: int
    evaluation: CandidateEvaluation
    saw_score: float
    saw_rank: int
    criteria: tuple[CriterionScore, ...]
    topsis_closeness: float | None
    d_plus: float | None
    d_minus: float | None
    topsis_rank: int | None


class RankingResult(Contract):
    method: RankingMethod
    weights_normalised: CriterionWeights | None
    ranked: tuple[RankedCandidate, ...]
    explanation: str | None
    ranking_error: str | None


class Recommendation(Contract):
    use_case: UseCaseId
    method: RankingMethod
    weights_normalised: CriterionWeights | None
    ranked: tuple[RankedCandidate, ...]
    rejected: tuple[CandidateEvaluation, ...]
    explanation: str | None
    ranking_error: str | None
    warnings: tuple[str, ...]


class ScenarioResult(Contract):
    scenario: Scenario
    recommendation: Recommendation
    baselines: BaselineResult
    timeline: TimelineResult | None
    fx_rate: float
    fx_source_id: str
    fx_rate_date: IsoDate
    fx_is_override: bool
    sources: tuple[SourceEntry, ...]
    warnings: tuple[str, ...]
