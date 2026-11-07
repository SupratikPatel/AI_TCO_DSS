"""Sizing_Engine and the `size` service (Req 16 to 19, 41.3, 41.4).

Tolerances follow Req 41.4: exact equality for flags, at most 5 % relative for values
the specification marks as approximate, a strict `<` for the 0.9 GB bound.
"""

import math
from typing import Any

import pytest
from pydantic import BaseModel

from ai_tco_dss.catalog import JsonCatalogRepository, get_default_repository
from ai_tco_dss.domain import (
    DecisionOptions,
    EnterpriseFinancials,
    HardwareSpec,
    LicenseType,
    ModelSpec,
    PrecisionFormat,
    Scenario,
    SizeRequest,
    SizingInput,
    SizingOptions,
    SizingResult,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import EngineInputError, UnknownIdentifierError
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.services import size
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
MAC = "mac-studio-m5-max-128gb"
FLASH_NEXT = "qwen-3-8-flash-next"
BREAKDOWN_KEYS = (
    "weights",
    "kv_cache_active",
    "agent_state_parked",
    "os_reserved",
    "runtime_overhead",
)


@pytest.fixture(scope="module")
def repo() -> JsonCatalogRepository:
    return get_default_repository()


def _s(value: Any) -> dict[str, Any]:
    return {"value": value, "source_id": "T", "tier": "assumption", "accessed": "2026-11-07"}


def _with[M: BaseModel](item: M, **changes: Any) -> M:
    return type(item).model_validate({**item.model_dump(), **changes})


def _hw(repo: JsonCatalogRepository, hardware_id: str) -> HardwareSpec:
    return next(h for h in repo.catalog().hardware if h.id == hardware_id)


def _model(repo: JsonCatalogRepository, model_id: str) -> ModelSpec:
    return next(m for m in repo.catalog().models if m.id == model_id)


def _size(
    hardware: HardwareSpec,
    model: ModelSpec,
    precision: PrecisionFormat = PrecisionFormat.INT4,
    nodes: float = 1,
    options: SizingOptions | None = None,
    **opts: Any,
) -> SizingResult:
    inp = SizingInput(
        hardware=hardware,
        model=model,
        precision=precision,
        requested_nodes=nodes,
        options=options or SizingOptions(**opts),
        profile=WorkloadProfile(),
        license_alternatives=("Gemma 4 12B",),
    )
    return size_deployment(inp, PARAMS)


# --------------------------------------------------------------------------- reference cases


def test_req_16_6_mac_128gb_trap(repo: JsonCatalogRepository) -> None:
    """Req 16.6, 41.3: Flash Next INT4 on Mac Studio M5 Max 128 GB (reference 103 / 115 GB)."""
    hardware, model = _hw(repo, MAC), _model(repo, FLASH_NEXT)
    default = _size(hardware, model, target_context_length=8_192)
    tuned = _size(
        hardware, model, target_context_length=8_192, apply_mac_wired_memory_override=True
    )
    # Reference values; a deviation above 1.0 GB would need a ledger entry (none exists).
    assert default.usable_memory_gb == pytest.approx(103.0, abs=1.0)
    assert tuned.usable_memory_gb == pytest.approx(115.0, abs=1.0)
    assert default.weights.value == pytest.approx(111.0, rel=0.05)
    assert default.usable_memory_gb < 111.0 <= tuned.usable_memory_gb
    assert default.is_feasible is False
    assert tuned.is_feasible is True
    assert default.triggered_mac_default_split_trap is True
    assert tuned.triggered_mac_default_split_trap is True
    assert any("sudo sysctl iogpu.wired_limit_mb=117760" in w for w in default.warnings)


def test_req_17_10_deepseek_mla_1m(repo: JsonCatalogRepository) -> None:
    """Req 17.10, 41.3: MLA KV cache of DeepSeek V4.1 Flash at 1M tokens is 0.89 GB, < 0.9."""
    result = _size(
        _hw(repo, "mac-studio-m5-ultra-256gb"),
        _model(repo, "deepseek-v4-1-flash"),
        PrecisionFormat.INT3,
        target_context_length=1_000_000,
    )
    assert result.kv_per_token_bytes == 890.0
    assert result.m_kv_single_gb == pytest.approx(0.89, rel=0.05)
    assert result.m_kv_single_gb < 0.9


# --------------------------------------------------------------------------- usable memory


def test_req_16_8_missing_mac_override_falls_back_with_warning(repo: JsonCatalogRepository) -> None:
    hardware = _with(_hw(repo, MAC), tuned_max_usable_memory_gb=None)
    result = _size(hardware, _model(repo, "qwen-3-8-27b"), apply_mac_wired_memory_override=True)
    assert result.usable_memory_gb == pytest.approx(103.04, abs=0.005)
    assert any(MAC in w and "tuned_max_usable_memory_gb" in w for w in result.warnings)


def test_req_16_8_missing_linux_override_falls_back_with_warning(
    repo: JsonCatalogRepository,
) -> None:
    hardware = _with(_hw(repo, "amd-strix-halo-128gb"), linux_max_usable_memory_gb=None)
    result = _size(hardware, _model(repo, "qwen-3-8-27b"), linux_amd_override=True)
    assert result.usable_memory_gb == pytest.approx(96.0, abs=0.005)
    assert any(
        "amd-strix-halo-128gb" in w and "linux_max_usable_memory_gb" in w for w in result.warnings
    )


def test_req_16_3_linux_override_applies(repo: JsonCatalogRepository) -> None:
    result = _size(
        _hw(repo, "amd-strix-halo-128gb"), _model(repo, "qwen-3-8-27b"), linux_amd_override=True
    )
    assert result.usable_memory_gb == pytest.approx(118.0, abs=0.005)
    assert not any("linux_max_usable_memory_gb" in w for w in result.warnings)


def test_req_16_4_discrete_default_utilization(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"))
    assert result.usable_memory_gb == pytest.approx(86.4, abs=0.005)
    assert result.usable_memory_gb == round(result.usable_memory_gb, 2)


@pytest.mark.parametrize(
    ("hardware_id", "field", "value"),
    [
        (MAC, "os_reserved_memory_ratio", 1.0),
        (MAC, "os_reserved_memory_ratio", -0.1),
        (MAC, "tuned_max_usable_memory_gb", 0.0),
        (MAC, "tuned_max_usable_memory_gb", 128.5),
        ("amd-strix-halo-128gb", "linux_max_usable_memory_gb", 0.0),
        ("amd-strix-halo-128gb", "linux_max_usable_memory_gb", 130.0),
    ],
)
def test_req_16_9_bound_violations_name_field_and_hardware(
    repo: JsonCatalogRepository, hardware_id: str, field: str, value: float
) -> None:
    hardware = _with(_hw(repo, hardware_id), **{field: _s(value)})
    with pytest.raises(EngineInputError) as info:
        _size(hardware, _model(repo, "qwen-3-8-27b"))
    assert field in info.value.message
    assert hardware_id in info.value.message


@pytest.mark.parametrize("value", [0.0, 1.5])
def test_req_16_9_gpu_memory_utilization_bounds(repo: JsonCatalogRepository, value: float) -> None:
    options = SizingOptions.model_construct(gpu_memory_utilization=value)
    with pytest.raises(EngineInputError) as info:
        _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), options=options)
    assert "gpu_memory_utilization" in info.value.message
    assert "rtx-pro-6000-96gb" in info.value.message


# --------------------------------------------------------------------------- weights and KV


def test_req_17_1_calibrated_weights_are_measured(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, MAC), _model(repo, FLASH_NEXT), target_context_length=8_192)
    assert result.weights.value == 111.3
    assert result.weights.origin.origin == "measured"
    assert result.weights.origin.source_ids == ("UNSLOTH-GGUF",)


def test_req_17_2_formula_weights_without_calibration(repo: JsonCatalogRepository) -> None:
    result = _size(
        _hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), PrecisionFormat.FP8
    )
    assert result.weights.value == pytest.approx(27 * 1.0 * 1.05, rel=1e-9)
    assert result.weights.origin.origin == "formula"


def test_req_17_4_hybrid_kv_per_token_mlx_and_vllm(repo: JsonCatalogRepository) -> None:
    model = _model(repo, FLASH_NEXT)
    expected = 2 * 48 * 0.25 * 2 * 256 * (16 / 8)
    mac = _size(_hw(repo, MAC), model, target_context_length=8_192)
    gpu = _size(_hw(repo, "rtx-pro-6000-96gb"), model, target_context_length=8_192)
    assert mac.kv_per_token_bytes == pytest.approx(expected * 1.08, rel=1e-9)
    assert gpu.kv_per_token_bytes == pytest.approx(expected, rel=1e-9)


def test_req_17_12_missing_kv_parameters_name_model_and_parameters(
    repo: JsonCatalogRepository,
) -> None:
    model = _with(_model(repo, "qwen-3-8-27b"), num_layers=None, head_dim=_s(0))
    with pytest.raises(EngineInputError) as info:
        _size(_hw(repo, "rtx-pro-6000-96gb"), model)
    message = info.value.message
    assert "qwen-3-8-27b" in message
    assert "num_layers" in message and "head_dim" in message
    assert "num_kv_heads" not in message


def test_req_17_12_hybrid_needs_kv_layer_ratio(repo: JsonCatalogRepository) -> None:
    model = _with(_model(repo, "qwen-3-8-27b"), active_kv_layer_ratio=None)
    with pytest.raises(EngineInputError, match="active_kv_layer_ratio"):
        _size(_hw(repo, "rtx-pro-6000-96gb"), model)


def test_req_17_6_oom_reason_names_shortfall(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, MAC), _model(repo, FLASH_NEXT), target_context_length=8_192)
    shortfall = 111.3 + 2.0 - 128 * (1 - 0.195)
    assert result.max_concurrent_users == 0
    assert result.oom_reason is not None
    assert f"{shortfall:.1f} GB" in result.oom_reason


def test_req_17_8_breakdown_keys_and_values(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"))
    breakdown = dict(result.memory_breakdown)
    assert tuple(k for k, _ in result.memory_breakdown) == BREAKDOWN_KEYS
    assert breakdown["runtime_overhead"] == 2.0
    assert breakdown["os_reserved"] == pytest.approx(96 - 86.4, rel=1e-9)
    peak = min(WorkloadProfile().peak_concurrent_requests, result.max_concurrent_users)
    assert breakdown["kv_cache_active"] == pytest.approx(result.m_kv_single_gb * peak, rel=1e-9)
    assert breakdown["agent_state_parked"] == pytest.approx(
        8 * (result.m_kv_single_gb + 4.0), rel=1e-9
    )


# --------------------------------------------------------------------------- nodes


@pytest.mark.parametrize(
    ("hardware_id", "nodes", "alpha"),
    [
        ("rtx-pro-6000-96gb", 1, 1.0),
        ("rtx-pro-6000-96gb", 4, 0.75),
        ("h100-80gb-sxm", 8, 0.90),
        ("dgx-spark-128gb", 2, 0.72),
        (MAC, 2, 0.65),
    ],
)
def test_req_18_4_alpha_scaling(
    repo: JsonCatalogRepository, hardware_id: str, nodes: int, alpha: float
) -> None:
    result = _size(_hw(repo, hardware_id), _model(repo, "qwen-3-8-27b"), nodes=nodes)
    assert result.alpha_scaling == alpha


@pytest.mark.parametrize(("nodes", "cables"), [(1, 0), (2, 1), (4, 6), (8, 28)])
def test_req_18_5_thunderbolt_cables(repo: JsonCatalogRepository, nodes: int, cables: int) -> None:
    hardware = _with(_hw(repo, MAC), valid_node_counts=_s([1, 2, 4, 8]))
    result = _size(hardware, _model(repo, "qwen-3-8-27b"), nodes=nodes)
    assert result.thunderbolt_mesh_cables == cables
    assert result.nodes_required == nodes


def test_req_18_3_aggregate_usable_memory(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), nodes=4)
    assert result.usable_memory_gb == pytest.approx(4 * 86.4, abs=0.005)


def test_req_18_2_snaps_three_to_four_with_warning(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), nodes=3)
    assert (result.requested_nodes, result.nodes_required) == (3, 4)
    assert sum("3" in w and "4" in w and "node" in w for w in result.warnings) == 1


def test_req_18_1_valid_node_count_has_no_node_warning(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), nodes=4)
    assert not any("node" in w for w in result.warnings)


@pytest.mark.parametrize("nodes", [2.5, 0, 9, -1])
def test_req_18_7_invalid_node_count_rejected(repo: JsonCatalogRepository, nodes: float) -> None:
    with pytest.raises(EngineInputError) as info:
        _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), nodes=nodes)
    assert str(nodes) in info.value.message
    assert "1 to 8" in info.value.message


def test_req_18_8_node_count_outside_valid_counts_is_infeasible(
    repo: JsonCatalogRepository,
) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), nodes=2)
    assert result.is_feasible is False
    assert result.oom_reason is not None
    assert "2" in result.oom_reason and "[1, 4, 8]" in result.oom_reason


def test_req_18_9_exactly_one_strata_warning(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-5070-strata-64gb"), _model(repo, "qwen-3-8-27b"))
    assert sum("Strata" in w and "8,192" in w for w in result.warnings) == 1


def test_req_18_6_tiered_offload_weight_capacity(repo: JsonCatalogRepository) -> None:
    strata = _hw(repo, "rtx-5070-strata-64gb")
    fits = _size(strata, _model(repo, "qwen-3-8-27b"), target_context_length=8_192)
    too_big = _size(strata, _model(repo, FLASH_NEXT), PrecisionFormat.INT2)
    assert fits.is_feasible is True  # 27B INT4 exceeds 10.8 GB VRAM but fits VRAM + Shelf
    assert too_big.is_feasible is False  # 79.6 GB > 10.8 + 64 GB


# --------------------------------------------------------------------------- flags


def test_req_19_1_context_floor_does_not_change_feasibility(repo: JsonCatalogRepository) -> None:
    hardware, model = _hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b")
    base = _size(hardware, model)
    short = _size(hardware, _with(model, max_context_length=_s(100_000)))
    assert base.meets_128k_agentic_context_floor is True
    assert short.meets_128k_agentic_context_floor is False
    assert short.is_feasible == base.is_feasible
    assert short.max_usable_context == 100_000


def test_req_19_2_llama_license_warning(repo: JsonCatalogRepository) -> None:
    hardware, model = _hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b")
    base = _size(hardware, model)
    banned = _size(hardware, _with(model, license_type=LicenseType.LLAMA_4_EU_RESTRICTED))
    assert base.eu_commercial_license_valid is True
    assert banned.eu_commercial_license_valid is False
    assert banned.is_feasible == base.is_feasible
    license_warnings = [w for w in banned.warnings if "Llama-4-EU-Ban" in w]
    assert len(license_warnings) == 1
    assert model.name in license_warnings[0] and "Gemma 4 12B" in license_warnings[0]
    assert not any("Llama-4-EU-Ban" in w for w in base.warnings)


@pytest.mark.parametrize(("rate", "warned"), [(0.90, False), (0.899, True), (0.978, False)])
def test_req_19_4_agreement_threshold(
    repo: JsonCatalogRepository, rate: float, warned: bool
) -> None:
    model = _with(
        _model(repo, FLASH_NEXT),
        token_agreement_rates=[{"precision": "INT4", "value": _s(rate)}],
    )
    result = _size(_hw(repo, MAC), model, target_context_length=8_192)
    assert result.token_agreement_rate == rate
    schema = [w for w in result.warnings if "schema-break" in w]
    assert len(schema) == (1 if warned else 0)
    if warned:
        assert "89.9%" in schema[0] and "INT4" in schema[0] and "0.90" in schema[0]


def test_req_19_7_no_agreement_entry_gives_null(repo: JsonCatalogRepository) -> None:
    result = _size(
        _hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"), PrecisionFormat.FP8
    )
    assert result.token_agreement_rate is None
    assert not any("schema-break" in w for w in result.warnings)


def test_req_19_1_max_usable_context_from_kv_pool(repo: JsonCatalogRepository) -> None:
    result = _size(_hw(repo, "rtx-pro-6000-96gb"), _model(repo, "qwen-3-8-27b"))
    by_pool = math.floor(result.kv_pool_gb * 1e9 / result.kv_per_token_bytes)
    assert result.max_usable_context == min(262_144, by_pool)


# --------------------------------------------------------------------------- size service


def _scenario(**sizing: Any) -> Scenario:
    return Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(**sizing),
        decision=DecisionOptions(),
    )


def test_size_service_returns_sizing_and_workload() -> None:
    request = SizeRequest(
        scenario=_scenario(target_context_length=8_192),
        hardware_id=MAC,
        model_id=FLASH_NEXT,
        precision=PrecisionFormat.INT4,
    )
    result = size(request)
    assert result.sizing.hardware_id == MAC
    assert result.sizing.is_feasible is False
    assert result.workload.monthly_requests == 22_000
    assert result.performance is None
    assert result.aa_index_v5 is None


@pytest.mark.parametrize(
    ("hardware_id", "model_id", "item_type"),
    [("no-such-hw", FLASH_NEXT, "hardware"), (MAC, "no-such-model", "model")],
)
def test_size_service_unknown_ids(hardware_id: str, model_id: str, item_type: str) -> None:
    request = SizeRequest(
        scenario=_scenario(), hardware_id=hardware_id, model_id=model_id, precision="INT4"
    )
    with pytest.raises(UnknownIdentifierError) as info:
        size(request)
    assert info.value.item_type == item_type


def test_size_service_rejects_commercial_api_models() -> None:
    request = SizeRequest(
        scenario=_scenario(), hardware_id=MAC, model_id="claude-sonnet-5-5", precision="INT4"
    )
    with pytest.raises(EngineInputError, match="claude-sonnet-5-5"):
        size(request)
