"""Scenario contracts and `EngineParameters` (design.md § "Scenario contracts")."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, field_validator

from ai_tco_dss.domain.base import Contract
from ai_tco_dss.domain.enums import (
    BenchmarkMetric,
    ElectricityTariffTier,
    EuEngineeringHub,
    GatewayType,
    HarnessType,
    InterconnectType,
    PrecisionFormat,
    PresetId,
    RankingMethod,
    RuntimeFormat,
    SpeculativeMode,
    ThinkingEffortPreset,
    UseCaseId,
    WorkScheduleMode,
)

Ratio = Annotated[float, Field(ge=0.0, le=1.0)]
Positive = Annotated[float, Field(gt=0.0)]
NonNegative = Annotated[float, Field(ge=0.0)]


class WorkloadProfile(Contract):
    active_users: int = Field(25, ge=1, le=100_000)
    concurrent_agent_instances: int = Field(8, ge=1)
    daily_requests_per_user: int = Field(40, ge=1, le=10_000)
    working_days_per_month: int = Field(22, ge=1, le=31)
    avg_input_tokens: int = Field(15000, ge=1, le=1_000_000)
    avg_output_tokens: int = Field(1500, ge=1, le=200_000)
    thinking_effort_preset: ThinkingEffortPreset = ThinkingEffortPreset.MEDIUM
    reasoning_token_multiplier: float = Field(2.5, ge=1.0, le=10.0)
    has_verification_agent_layer: bool = False
    context_length_p50: int = Field(32000, ge=1024)
    context_length_p90: int = Field(128000, ge=1024)
    context_length_p99: int = Field(250000, ge=1024, le=1_000_000)
    peak_concurrent_requests: int = Field(5, ge=1)
    harness_type: HarnessType = HarnessType.CLAUDE_CODE
    mcp_code_mode_pruning: bool = False
    custom_scaffolding_tokens: int | None = Field(None, ge=0, le=100_000)
    gateway_type: GatewayType = GatewayType.LITELLM_PYTHON
    prompt_cache_hit_rate: float = Field(0.50, ge=0.0, le=0.95)
    batch_api_eligible_ratio: float = Field(0.20, ge=0.0, le=1.0)
    mega_session_ratio: float = Field(0.35, ge=0.0, le=1.0)
    work_schedule_mode: WorkScheduleMode = WorkScheduleMode.INTERACTIVE_WORKDAY
    active_hours_per_month: int = Field(176, ge=1, le=744)
    min_acceptable_tps: float | None = Field(20.0, ge=1.0)
    max_acceptable_ttft_seconds: float | None = Field(15.0, ge=0.5)


class EnterpriseFinancials(Contract):
    currency: Literal["EUR", "USD"] = "USD"
    max_capex_budget_usd: float | None = Field(100_000.0, ge=0.0)
    electricity_tariff_tier: ElectricityTariffTier = ElectricityTariffTier.DE_INDUSTRIAL_BDEW
    cooling_pue: float = Field(1.20, ge=1.0, le=3.0)
    engineering_hub_location: EuEngineeringHub = EuEngineeringHub.RO_CLUJ_BUCHAREST
    devops_fte_allocation: float = Field(0.5, ge=0.0, le=10.0)
    enable_nvidia_nim_licensing: bool = False
    nvidia_nim_license_per_gpu_yr_usd: float = Field(4500.0, ge=0.0)
    developer_hourly_opportunity_cost: float = Field(72.57, ge=0.0)
    include_wait_time_penalty: bool = False
    capital_opportunity_rate: float = Field(0.045, ge=0.0, le=1.0)
    depreciation_years: int = Field(3, ge=1)
    strict_eu_sovereignty: bool = True
    require_third_party_harness: bool = True
    local_offload_ratio: float = Field(0.70, ge=0.0, le=1.0)
    include_resale_value: bool = False
    subscription_plan_id: str | None = None


class SizingOptions(Contract):
    weight_precision: PrecisionFormat = PrecisionFormat.INT4
    kv_precision: PrecisionFormat = PrecisionFormat.FP16
    target_context_length: int = Field(128000, ge=1)
    apply_mac_wired_memory_override: bool = False
    linux_amd_override: bool = False
    speculative_mode: SpeculativeMode = SpeculativeMode.NONE
    enable_optimized_backend: bool = True
    requested_nodes: int | None = None
    gpu_memory_utilization: float = Field(0.90, gt=0.0, le=1.0)
    runtime_overhead_gb: float = Field(2.0, ge=0.0)
    repo_workspace_gb: float = Field(4.0, ge=2.5, le=6.0)
    runtime_format: RuntimeFormat = RuntimeFormat.AUTO


class CriterionWeights(Contract):
    """Raw weights; non-negativity is checked by the ranking (Req 29.11), not here."""

    tco_60m: float
    quality: float
    effective_tps: float
    ttft: float
    risk: float
    popularity: float


class DecisionOptions(Contract):
    use_case: UseCaseId = UseCaseId.AGENTIC_CODING
    preset: PresetId = PresetId.BEST_FIT
    weights: CriterionWeights | None = None
    method: RankingMethod = RankingMethod.SAW
    reference_api_model_id: str | None = None


class Scenario(Contract):
    workload: WorkloadProfile
    financials: EnterpriseFinancials
    sizing: SizingOptions
    decision: DecisionOptions
    fx_override: float | None = Field(default=None, ge=0.5, le=2.0)

    @field_validator("fx_override")
    @classmethod
    def _at_most_six_decimals(cls, value: float | None) -> float | None:
        if value is not None:
            exponent = Decimal(repr(value)).as_tuple().exponent
            if isinstance(exponent, int) and exponent < -6:
                raise ValueError("fx_override allows at most 6 decimal places")
        return value


class EngineParameters(Contract):
    """Engine tunables; defaults live in `ai_tco_dss.settings` (design D-05)."""

    context_match_tolerance: Ratio
    eta_dense: Annotated[float, Field(gt=0.0, le=1.0)]
    eta_moe: Annotated[float, Field(gt=0.0, le=1.0)]
    gamma_spec: tuple[tuple[SpeculativeMode, Positive], ...]
    delta_ctx_breakpoints: tuple[tuple[Annotated[int, Field(ge=1)], Ratio], ...]
    alpha_scaling: tuple[tuple[InterconnectType, Ratio], ...]
    weight_overhead_factor: Annotated[float, Field(ge=1.0)]
    mla_kv_bytes_per_token: Positive
    phi_format: tuple[tuple[RuntimeFormat, Positive], ...]
    mcp_prune_ratio: Ratio
    thinking_multipliers: tuple[tuple[ThinkingEffortPreset, Annotated[float, Field(ge=1.0)]], ...]
    claude_tokenizer_inflation: Annotated[float, Field(ge=1.0)]
    mega_session_slope: NonNegative
    batch_streams_cap_per_node: Annotated[int, Field(ge=1)]
    batching_contention: NonNegative
    hours_per_month: Annotated[float, Field(gt=0.0, le=744.0)]
    utilization_threshold: Ratio
    idle_warning_threshold: Ratio
    risk_weight_support: Ratio
    risk_weight_fidelity: Ratio
    risk_support_years_cap: Positive
    risk_rental_lifecycle: Ratio
    risk_api_lockin: Ratio
    risk_missing_agreement: Ratio
    aa_ratio_default: Positive
    calibration_tolerance_pct: tuple[tuple[BenchmarkMetric, Positive], ...]
    eviction_events_per_month: NonNegative
    eviction_compute_price_per_1m_usd: NonNegative
