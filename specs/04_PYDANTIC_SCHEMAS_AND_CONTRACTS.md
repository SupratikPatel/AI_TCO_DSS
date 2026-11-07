<!-- ===================================================================== -->
<!-- SPLIT FILE: specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md               -->
<!-- PURPOSE: Strict Type-Safe Data Contracts (src/core/schemas.py)        -->
<!-- ===================================================================== -->

# Strict Data Contracts (`src/core/schemas.py` — Pydantic v2)

All calculation engines, FastAPI endpoints, Streamlit state stores, and LLM tool calls must strictly validate against these Pydantic v2 schemas:

```python
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PrecisionFormat(str, Enum):
    FP16 = "FP16"
    BF16 = "BF16"
    FP8 = "FP8"
    INT8 = "INT8"
    INT4 = "INT4"
    INT3 = "INT3"
    INT2 = "INT2"


class AttentionMechanism(str, Enum):
    STANDARD_MHA_GQA = "standard-mha-gqa"      # ~120-163.8 KB/token FP16 (~41 KB INT4)
    MULTI_HEAD_LATENT = "multi-head-latent"    # ~890 bytes/token (<0.9 GB @ 1M ctx - DeepSeek MLA)
    HYBRID_SPARSE_LAYER = "hybrid-sparse"      # 16/64 growing KV layers (Qwen 3.8-27B)


class LicenseType(str, Enum):
    APACHE_2 = "Apache-2.0"                    # EU commercial safe (Qwen, gpt-oss, Mistral Small)
    MIT = "MIT"                                # EU commercial safe (DeepSeek V4/V4.1)
    LLAMA_4_EU_RESTRICTED = "Llama-4-EU-Ban"   # Prohibited for companies domiciled in the EU
    COMMERCIAL_PROPRIETARY = "Proprietary-API"


class HarnessType(str, Enum):
    CLAUDE_CODE = "claude-code"                # ~33,000 scaffolding tokens/turn ($18.34/task)
    CODEX = "codex"                            # ~13,000 scaffolding tokens/turn (100k init)
    OPENCODE = "opencode"                      # ~7,000 scaffolding tokens/turn
    DEEPSEEK_HARNESS_DSH = "deepseek-dsh"      # ~4,200 scaffolding tokens/turn ($3.28/task)
    CUSTOM_LEAN = "custom-lean"


class GatewayType(str, Enum):
    LITELLM_PYTHON = "litellm-python"          # 100-500 ms P99 overhead at scale
    BIFROST_COMPILED = "bifrost-compiled"      # 11-840 µs overhead


class DeploymentMode(str, Enum):
    PER_SEAT_WORKSTATION = "per-seat-workstation"
    CENTRALIZED_SERVER = "centralized-server"
    DISAGGREGATED_PREFILL_DECODE = "disaggregated-pd"
    TIERED_OFFLOAD_APPLIANCE = "tiered-offload-appliance"
    HETEROGENEOUS_ROUTED_APPLIANCE = "heterogeneous-routed"
    WIRELESS_EGPU_APPLIANCE = "wireless-egpu-appliance"
    CLOUD_RENTAL = "cloud-rental"


class InterconnectType(str, Enum):
    NVLINK = "NVLink"
    ROCE_200G = "RoCE-200Gbps"
    PCIE_GEN5 = "PCIe-Gen5"
    PCIE_GEN4 = "PCIe-Gen4"
    PCIE_GEN3 = "PCIe-Gen3"
    THUNDERBOLT_5_RDMA = "Thunderbolt-5-RDMA"
    DGX_RING_CABLE = "DGX-Ring-Cable"
    WIFI_7_VIRTUAL_GPU = "WiFi-7-Virtual-GPU"
    UNIFIED_SINGLE = "Unified-Single"


class WorkScheduleMode(str, Enum):
    INTERACTIVE_WORKDAY = "interactive-workday"            # 176 hrs/mo (22d * 8h)
    UNATTENDED_BACKGROUND_LOOP = "unattended-background-loop"  # 360-720 hrs/mo


class ThinkingEffortPreset(str, Enum):
    NONE = "none"              # 1.0x output multiplier
    LOW = "low"                # 1.5x output multiplier
    MEDIUM = "medium"          # 2.5x output multiplier
    EXTRA_HIGH = "extra-high"  # 4.9x - 8.0x (13k thinking + 3.3k visible output)


class SpeculativeMode(str, Enum):
    NONE = "none"
    APPLE_MTP_DFLASH = "apple-mtp-dflash"    # 1.35x - 1.50x speedup on MLX
    BUILTIN_MTP = "built-in-mtp"             # 1.40x - 2.20x speedup on CUDA/vLLM
    EXTERNAL_DRAFT = "external-draft"        # 2.40x - 3.10x speedup


class EuEngineeringHub(str, Enum):
    DE_MUNICH_HQ = "de-munich-hq"            # ~€120k base + 21% Lohnnebenkosten = €145.2k/yr
    DE_BERLIN_HAMBURG = "de-berlin-hamburg"  # ~€100k base + 21% Lohnnebenkosten = €121.0k/yr
    RO_CLUJ_BUCHAREST = "ro-cluj-bucharest"  # ~€75k base + 2.25% CAM (~4% w/ perks) = €78.0k/yr
    PL_WARSAW_KRAKOW = "pl-warsaw-krakow"    # ~€82k base + employer cost = ~€91.8k/yr


class ElectricityTariffTier(str, Enum):
    DE_INDUSTRIAL_BDEW = "de-industrial-bdew"  # €0.172 / kWh (2026 German SME industrial rate)
    DE_COMMERCIAL_OFFICE = "de-office"         # €0.280 / kWh
    EU_NORDIC_GREEN = "eu-nordic"              # €0.095 / kWh
    CUSTOM = "custom"


class WorkloadProfile(BaseModel):
    active_users: int = Field(25, ge=1, description="Active developer/enterprise seats")
    concurrent_agent_instances: int = Field(8, ge=1, description="Simultaneous agent loops")
    daily_requests_per_user: int = Field(40, ge=1)
    avg_input_tokens: int = Field(15000, ge=1)
    avg_output_tokens: int = Field(1500, ge=1)
    thinking_effort_preset: ThinkingEffortPreset = ThinkingEffortPreset.MEDIUM
    reasoning_token_multiplier: float = Field(2.5, ge=1.0, le=10.0)
    has_verification_agent_layer: bool = Field(False, description="Layer 4 verifier.md 2.0x multiplier")
    context_length_p50: int = Field(32000, ge=1024)
    context_length_p90: int = Field(128000, ge=1024)
    context_length_p99: int = Field(250000, ge=1024, le=1000000)
    peak_concurrent_requests: int = Field(5, ge=1)
    harness_type: HarnessType = HarnessType.CLAUDE_CODE
    mcp_code_mode_pruning: bool = Field(False, description="Prunes 58-92% MCP tool schema tokens")
    custom_scaffolding_tokens: Optional[int] = None
    gateway_type: GatewayType = GatewayType.LITELLM_PYTHON
    prompt_cache_hit_rate: float = Field(0.50, ge=0.0, le=0.95)
    batch_api_eligible_ratio: float = Field(0.20, ge=0.0, le=1.0, description="Share eligible for 50% Batch API discount")
    mega_session_ratio: float = Field(0.35, ge=0.0, le=1.0, description="Share of 80+ turn sessions")
    work_schedule_mode: WorkScheduleMode = WorkScheduleMode.INTERACTIVE_WORKDAY
    active_hours_per_month: int = Field(176, ge=1, le=744)
    min_acceptable_tps: float = Field(20.0, ge=1.0)
    max_acceptable_ttft_seconds: float = Field(15.0, ge=0.5)


class ModelSpec(BaseModel):
    id: str
    name: str
    family: str
    type: str = Field(..., pattern="^(open-weights|commercial-api)$")
    license_type: LicenseType = LicenseType.APACHE_2
    architecture: str = Field(..., pattern="^(dense|moe)$")
    attention_mechanism: AttentionMechanism = AttentionMechanism.STANDARD_MHA_GQA
    tokenizer_inflation_factor: float = Field(1.0, description="1.30 for Claude 4.7+/5.5, 1.00 baseline")
    total_parameters_billions: Optional[float] = None
    active_parameters_billions: Optional[float] = None
    calibrated_weights_gb: Optional[Dict[PrecisionFormat, float]] = None
    token_agreement_rates: Optional[Dict[PrecisionFormat, float]] = None
    ssd_streaming_lookup_gb: float = Field(0.0, description="196 GB for DeepSeek V4.1 Engram")
    num_layers: Optional[int] = None
    active_kv_layer_ratio: float = Field(1.0, description="0.25 for Qwen 3.8-27B")
    num_kv_heads: Optional[int] = None
    head_dim: Optional[int] = None
    max_context_length: int
    supports_builtin_mtp: bool = False
    aa_v5_score: float = Field(..., description="Artificial Analysis v5 Intelligence Index")
    terminal_bench_score: Optional[float] = None
    openrouter_output_price_per_1m: Optional[float] = None
    avg_benchmark_task_cost_usd: Optional[float] = None
    api_input_price_per_1m: Optional[float] = None
    api_output_price_per_1m: Optional[float] = None
    api_cache_read_multiplier: float = Field(0.10, description="0.05 for Sonnet 5.5, 0.10 standard")
    eu_compliant: bool = True


class LifecycleClocks(BaseModel):
    software_support_years: float
    resale_value_retention_3yr: float = Field(..., ge=0.0, le=1.0)
    cuda_or_rocm_status: str = Field(..., pattern="^(active-flagship|supported|deprecated-legacy)$")
    requires_nvidia_nim_license: bool = False
    warning_notes: Optional[str] = None


class HardwareSpec(BaseModel):
    id: str
    name: str
    vendor: str
    deployment_mode: DeploymentMode
    advertised_memory_gb: float
    system_ram_offload_gb: float = 0.0
    system_ram_total_installed_gb: float = Field(64.0, description="Host system DDR4/DDR5 capacity")
    nvme_ssd_offload_gb: float = 0.0
    os_reserved_memory_ratio: float = 0.25
    tuned_max_usable_memory_gb: Optional[float] = None
    linux_max_usable_memory_gb: Optional[float] = None
    memory_bandwidth_gbs: float
    gpu_cores: Optional[int] = None
    per_core_prefill_score: Optional[float] = None  # 151 (M1-M4), 531 (M5/M6)
    base_prefill_tps_at_32k: float
    prefill_tps_at_1m: Optional[float] = None
    host_cpu_cores: Optional[int] = None
    has_igpu_vision_offload: bool = False
    has_npu_audio_security_offload: bool = False
    supported_native_precisions: List[PrecisionFormat]
    interconnect: InterconnectType
    valid_node_counts: List[int] = Field(default=[1, 2, 4, 8])
    idle_watts: float
    load_watts: float
    msrp_eur: float
    street_price_eur: float
    monthly_cloud_rental_eur: Optional[float] = None
    lifecycle_clocks: LifecycleClocks


class EnterpriseFinancials(BaseModel):
    currency: str = Field("EUR", pattern="^(EUR|USD)$")
    max_capex_budget: float = 100000.0
    electricity_tariff_tier: ElectricityTariffTier = ElectricityTariffTier.DE_INDUSTRIAL_BDEW
    electricity_cost_per_kwh: float = 0.172
    cooling_pue: float = Field(1.20, ge=1.0, le=2.0)
    datacenter_infrastructure_multiplier: float = Field(1.0, ge=1.0, le=3.0)
    engineering_hub_location: EuEngineeringHub = EuEngineeringHub.RO_CLUJ_BUCHAREST
    devops_fte_allocation: float = Field(0.5, ge=0.0, le=5.0)
    devops_annual_base_salary_eur: float = 75000.0
    employer_social_tax_multiplier: float = Field(0.04, description="0.21 Munich vs 0.0225-0.04 Romania")
    enable_nvidia_nim_licensing: bool = False
    nvidia_nim_license_per_gpu_yr_eur: float = 4150.0
    developer_hourly_opportunity_cost: float = 65.0
    include_wait_time_penalty: bool = False
    capital_opportunity_rate: float = 0.045
    depreciation_years: int = 3
    strict_eu_sovereignty: bool = True
    require_third_party_harness: bool = True
    local_offload_ratio: float = Field(0.70, ge=0.0, le=1.0)


class SizingOptions(BaseModel):
    weight_precision: PrecisionFormat = PrecisionFormat.INT4
    kv_precision: PrecisionFormat = PrecisionFormat.FP16
    target_context_length: int = 128000
    apply_mac_wired_memory_override: bool = False
    linux_amd_override: bool = False
    speculative_mode: SpeculativeMode = SpeculativeMode.NONE
    enable_optimized_backend: bool = True
    requested_nodes: Optional[int] = None


class HardwareSizingResult(BaseModel):
    hardware_id: str
    model_id: str
    nodes_required: int
    is_feasible: bool
    oom_reason: Optional[str] = None
    triggered_mac_default_split_trap: bool = False
    meets_128k_agentic_context_floor: bool = True
    eu_commercial_license_valid: bool = True
    memory_breakdown: Dict[str, float]
    max_concurrent_users: int
    max_retained_agent_instances: int
    agent_state_memory_required_gb: float
    context_eviction_risk: bool = False
    token_agreement_rate: Optional[float] = None
    decode_tps: float
    ttft_seconds: float
    prefill_1m_minutes: Optional[float] = None
    effective_tps: float
    thunderbolt_mesh_cables: int = 0
    warnings: List[str]


class MonthlyTcoPoint(BaseModel):
    month: int
    on_prem_cumulative: float
    eu_dedicated_rental_cumulative: float
    baseline_a_subscription_cumulative: float
    baseline_b_global_api_cumulative: float
    baseline_c_eu_sovereign_api_cumulative: float
    baseline_d_openrouter_value_cumulative: float
    hybrid_split_cumulative: float


class TcoProjectionResult(BaseModel):
    hardware_id: str
    nodes_count: int
    capex_total: float
    sustained_gpu_utilization: float
    meets_70_percent_utilization_threshold: bool
    monthly_on_prem_opex: Dict[str, float]
    monthly_eviction_loss_eur: float = 0.0
    munich_vs_romania_personnel_savings_monthly: float
    monthly_cloud_baselines: Dict[str, float]
    baseline_a_eligible: bool
    baseline_a_ineligibility_reasons: List[str]
    compliance_tax_delta_monthly: float
    three_clocks_scorecard: Dict[str, float | str]
    break_even_months: Dict[str, Optional[int]]
    single_stream_break_even_years: Optional[float] = None
    timeline_60_months: List[MonthlyTcoPoint]
```