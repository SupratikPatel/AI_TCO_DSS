"""Engine settings: defaults, ``AI_TCO_*`` environment loading and ``EngineParameters``.

Defaults follow design.md § "Settings (`settings.py`)". Values labelled *assumption*
there are listed in the ledger's Assumptions table. Bounds live in the
``EngineParameters`` contract; ``load_engine_parameters`` turns a bound violation
into ``ConfigurationError`` (Req 9.10).
"""

from itertools import pairwise

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_tco_dss.domain.enums import (
    BenchmarkMetric,
    InterconnectType,
    RuntimeFormat,
    SpeculativeMode,
    ThinkingEffortPreset,
)
from ai_tco_dss.domain.errors import ConfigurationError
from ai_tco_dss.domain.scenario import EngineParameters

__all__ = ["Settings", "load_engine_parameters"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_TCO_", extra="forbid")

    context_match_tolerance: float = 0.25
    eta_dense: float = 0.70
    eta_moe: float = 0.425
    gamma_spec: tuple[tuple[SpeculativeMode, float], ...] = (
        (SpeculativeMode.NONE, 1.0),
        (SpeculativeMode.APPLE_MTP_DFLASH, 1.425),
        (SpeculativeMode.BUILTIN_MTP, 1.80),
        (SpeculativeMode.EXTERNAL_DRAFT, 2.75),
    )
    delta_ctx_breakpoints: tuple[tuple[int, float], ...] = (
        (8_192, 1.00),
        (32_768, 0.89),
        (131_072, 0.60),
        (262_144, 0.50),
        (1_048_576, 0.40),
    )
    alpha_scaling: tuple[tuple[InterconnectType, float], ...] = (
        (InterconnectType.NVLINK, 0.90),
        (InterconnectType.PCIE_GEN5, 0.75),
        (InterconnectType.DGX_RING_CABLE, 0.72),
        (InterconnectType.THUNDERBOLT_5_RDMA, 0.65),
        (InterconnectType.ROCE_200G, 0.80),
        (InterconnectType.PCIE_GEN4, 0.70),
        (InterconnectType.PCIE_GEN3, 0.60),
        (InterconnectType.WIFI_7_VIRTUAL_GPU, 0.30),
        (InterconnectType.UNIFIED_SINGLE, 1.00),
    )
    weight_overhead_factor: float = 1.05
    mla_kv_bytes_per_token: float = 890.0
    phi_format: tuple[tuple[RuntimeFormat, float], ...] = (
        (RuntimeFormat.GGUF, 1.0),
        (RuntimeFormat.VLLM, 1.0),
        (RuntimeFormat.MLX, 1.08),
    )
    mcp_prune_ratio: float = 0.75
    thinking_multipliers: tuple[tuple[ThinkingEffortPreset, float], ...] = (
        (ThinkingEffortPreset.NONE, 1.0),
        (ThinkingEffortPreset.LOW, 1.5),
        (ThinkingEffortPreset.MEDIUM, 2.5),
        (ThinkingEffortPreset.EXTRA_HIGH, 4.94),
    )
    claude_tokenizer_inflation: float = 1.30
    mega_session_slope: float = 2.8
    batch_streams_cap_per_node: int = 64
    batching_contention: float = 0.03
    hours_per_month: float = 730.0
    utilization_threshold: float = 0.70
    idle_warning_threshold: float = 0.55
    risk_weight_support: float = 0.5
    risk_weight_fidelity: float = 0.5
    risk_support_years_cap: float = 5.0
    risk_rental_lifecycle: float = 0.20
    risk_api_lockin: float = 0.40
    risk_missing_agreement: float = 0.95
    aa_ratio_default: float = 2.0
    calibration_tolerance_pct: tuple[tuple[BenchmarkMetric, float], ...] = (
        (BenchmarkMetric.DECODE_TPS, 30.0),
        (BenchmarkMetric.PREFILL_TPS, 50.0),
    )
    eviction_events_per_month: float = 30.0
    eviction_compute_price_per_1m_usd: float = 0.30


def _configuration_error(exc: ValidationError) -> ConfigurationError:
    error = exc.errors()[0]
    setting = str(error["loc"][0]) if error["loc"] else "settings"
    return ConfigurationError(setting, error.get("input"))


def _check_delta_ctx(breakpoints: tuple[tuple[int, float], ...]) -> None:
    """Req 20.6: at least one breakpoint, contexts increasing, factors not increasing."""
    pairs = list(pairwise(breakpoints))
    if not breakpoints or any(c1 <= c0 or d1 > d0 for (c0, d0), (c1, d1) in pairs):
        raise ConfigurationError("delta_ctx_breakpoints", breakpoints)


def load_engine_parameters() -> EngineParameters:
    """Build `EngineParameters` from defaults and `AI_TCO_*` environment variables."""
    try:
        settings = Settings()
        params = EngineParameters.model_validate(settings.model_dump())
    except ValidationError as exc:
        raise _configuration_error(exc) from exc
    _check_delta_ctx(params.delta_ctx_breakpoints)
    return params
