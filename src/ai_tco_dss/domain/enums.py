"""Enumerations: spec 04 enums (without `ElectricityTariffTier.CUSTOM`) plus new ones."""

from enum import StrEnum


class PrecisionFormat(StrEnum):
    FP16 = "FP16"
    BF16 = "BF16"
    FP8 = "FP8"
    INT8 = "INT8"
    INT4 = "INT4"
    INT3 = "INT3"
    INT2 = "INT2"


class AttentionMechanism(StrEnum):
    STANDARD_MHA_GQA = "standard-mha-gqa"
    MULTI_HEAD_LATENT = "multi-head-latent"
    HYBRID_SPARSE_LAYER = "hybrid-sparse"


class LicenseType(StrEnum):
    APACHE_2 = "Apache-2.0"
    MIT = "MIT"
    LLAMA_4_EU_RESTRICTED = "Llama-4-EU-Ban"
    COMMERCIAL_PROPRIETARY = "Proprietary-API"


class HarnessType(StrEnum):
    CLAUDE_CODE = "claude-code"
    CODEX = "codex"
    OPENCODE = "opencode"
    DEEPSEEK_HARNESS_DSH = "deepseek-dsh"
    CUSTOM_LEAN = "custom-lean"


class GatewayType(StrEnum):
    LITELLM_PYTHON = "litellm-python"
    BIFROST_COMPILED = "bifrost-compiled"


class DeploymentMode(StrEnum):
    PER_SEAT_WORKSTATION = "per-seat-workstation"
    CENTRALIZED_SERVER = "centralized-server"
    DISAGGREGATED_PREFILL_DECODE = "disaggregated-pd"
    TIERED_OFFLOAD_APPLIANCE = "tiered-offload-appliance"
    HETEROGENEOUS_ROUTED_APPLIANCE = "heterogeneous-routed"
    WIRELESS_EGPU_APPLIANCE = "wireless-egpu-appliance"
    CLOUD_RENTAL = "cloud-rental"


class InterconnectType(StrEnum):
    NVLINK = "NVLink"
    ROCE_200G = "RoCE-200Gbps"
    PCIE_GEN5 = "PCIe-Gen5"
    PCIE_GEN4 = "PCIe-Gen4"
    PCIE_GEN3 = "PCIe-Gen3"
    THUNDERBOLT_5_RDMA = "Thunderbolt-5-RDMA"
    DGX_RING_CABLE = "DGX-Ring-Cable"
    WIFI_7_VIRTUAL_GPU = "WiFi-7-Virtual-GPU"
    UNIFIED_SINGLE = "Unified-Single"


class WorkScheduleMode(StrEnum):
    INTERACTIVE_WORKDAY = "interactive-workday"
    UNATTENDED_BACKGROUND_LOOP = "unattended-background-loop"


class ThinkingEffortPreset(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    EXTRA_HIGH = "extra-high"


class SpeculativeMode(StrEnum):
    NONE = "none"
    APPLE_MTP_DFLASH = "apple-mtp-dflash"
    BUILTIN_MTP = "built-in-mtp"
    EXTERNAL_DRAFT = "external-draft"


class EuEngineeringHub(StrEnum):
    DE_MUNICH_HQ = "de-munich-hq"
    DE_BERLIN_HAMBURG = "de-berlin-hamburg"
    RO_CLUJ_BUCHAREST = "ro-cluj-bucharest"
    PL_WARSAW_KRAKOW = "pl-warsaw-krakow"


class ElectricityTariffTier(StrEnum):
    DE_INDUSTRIAL_BDEW = "de-industrial-bdew"
    DE_COMMERCIAL_OFFICE = "de-office"
    EU_NORDIC_GREEN = "eu-nordic"


class BenchmarkMetric(StrEnum):
    DECODE_TPS = "decode_tps"
    PREFILL_TPS = "prefill_tps"
    AGGREGATE_TPS = "aggregate_tps"
    TTFT_S = "ttft_s"
    AA_INDEX_V5 = "aa_index_v5"
    TERMINAL_BENCH = "terminal_bench"
    SWE_BENCH = "swe_bench"


class MemoryArchitecture(StrEnum):
    APPLE_UNIFIED = "apple-unified"
    AMD_UNIFIED = "amd-unified"
    DISCRETE = "discrete"


class RuntimeFormat(StrEnum):
    AUTO = "auto"
    GGUF = "gguf"
    VLLM = "vllm"
    MLX = "mlx"


class CandidateKind(StrEnum):
    ONPREM = "onprem"
    API = "api"
    RENTAL = "rental"
    HYBRID = "hybrid"


class UseCaseId(StrEnum):
    WRITING_EMAIL = "writing-email"
    SUMMARISATION_RAG = "summarisation-rag"
    CODING_ASSISTANT = "coding-assistant"
    AGENTIC_CODING = "agentic-coding"


class PresetId(StrEnum):
    CHEAPEST = "cheapest"
    BEST_FIT = "best-fit"
    MOST_CAPABLE = "most-capable"
    POPULAR = "popular"


class RankingMethod(StrEnum):
    SAW = "saw"
    TOPSIS = "topsis"


class Criterion(StrEnum):
    TCO_60M = "tco_60m"
    QUALITY = "quality"
    EFFECTIVE_TPS = "effective_tps"
    TTFT = "ttft"
    RISK = "risk"
    POPULARITY = "popularity"
