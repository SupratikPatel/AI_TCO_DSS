"""Property tests for the Sizing_Engine (Properties 11 to 18).

Generators build valid hardware, model and option contracts within the bounds of
Requirements 16 to 19. Oracles restate the formulas of requirements.md independently
of `engines/sizing.py`.
"""

import math
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from ai_tco_dss.domain import (
    AttentionMechanism,
    DeploymentMode,
    HardwareSpec,
    InterconnectType,
    LicenseType,
    MemoryArchitecture,
    ModelSpec,
    PrecisionFormat,
    RuntimeFormat,
    SizingInput,
    SizingOptions,
    SizingResult,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
BITS = {"FP16": 16, "BF16": 16, "FP8": 8, "INT8": 8, "INT4": 4, "INT3": 3, "INT2": 2}
ALPHA = {
    "NVLink": 0.90,
    "PCIe-Gen5": 0.75,
    "DGX-Ring-Cable": 0.72,
    "Thunderbolt-5-RDMA": 0.65,
}
KEYS = ("weights", "kv_cache_active", "agent_state_parked", "os_reserved", "runtime_overhead")
ALTERNATIVES = ("Gemma 4 12B",)


def _s(value: Any) -> dict[str, Any]:
    return {"value": value, "source_id": "T", "tier": "assumption", "accessed": "2026-11-07"}


def _money(value: float) -> dict[str, Any]:
    return {**_s(value), "currency": "USD"}


# --------------------------------------------------------------------------- generators

MEMORY = st.floats(min_value=1.0, max_value=2048.0, allow_nan=False)
NODE_SETS = st.sets(st.sampled_from([1, 2, 4, 8]), min_size=1).map(sorted)


@st.composite
def hardware_specs(draw: st.DrawFn, architecture: MemoryArchitecture | None = None) -> HardwareSpec:
    arch = architecture or draw(st.sampled_from(list(MemoryArchitecture)))
    adv = draw(MEMORY)
    data: dict[str, Any] = {
        "id": draw(st.sampled_from(["hw-a", "hw-b"])),
        "name": "HW",
        "vendor": "V",
        "memory_architecture": arch.value,
        "interconnect": draw(st.sampled_from(list(InterconnectType))).value,
        "supported_native_precisions": ["INT4"],
        "valid_node_counts": _s(draw(NODE_SETS)),
        "gpus_per_unit": _s(1),
        "advertised_memory_gb": _s(adv),
        "memory_bandwidth_gbs": _s(500.0),
        "idle_watts": _s(10.0),
        "load_watts": _s(100.0),
        "street_price": _money(1000.0),
        "datacenter_multiplier": _s(1.0),
        "lifecycle_clocks": {
            "software_support_years": _s(5.0),
            "resale_value_retention_3yr": _s(0.5),
            "cuda_or_rocm_status": "supported",
        },
    }
    if arch == MemoryArchitecture.DISCRETE:
        mode = draw(st.sampled_from(list(DeploymentMode)))
        if mode == DeploymentMode.TIERED_OFFLOAD_APPLIANCE:
            data["system_ram_offload_gb"] = _s(draw(MEMORY))
        if draw(st.booleans()):
            data["system_ram_total_installed_gb"] = _s(draw(MEMORY))
    else:
        mode = DeploymentMode.PER_SEAT_WORKSTATION
        data["os_reserved_memory_ratio"] = _s(draw(st.floats(min_value=0.0, max_value=0.99)))
        override = draw(st.none() | st.floats(min_value=0.01, max_value=1.0))
        if override is not None:
            field = (
                "tuned_max_usable_memory_gb"
                if arch == MemoryArchitecture.APPLE_UNIFIED
                else "linux_max_usable_memory_gb"
            )
            data[field] = _s(override * adv)
    data["deployment_mode"] = mode.value
    return HardwareSpec.model_validate(data)


@st.composite
def model_specs(draw: st.DrawFn) -> ModelSpec:
    attention = draw(st.sampled_from(list(AttentionMechanism)))
    calibrated = draw(
        st.dictionaries(
            st.sampled_from(sorted(BITS)), st.floats(min_value=0.1, max_value=2000.0), max_size=3
        )
    )
    agreement = draw(
        st.dictionaries(
            st.sampled_from(sorted(BITS)), st.floats(min_value=0.0, max_value=1.0), max_size=3
        )
    )
    data: dict[str, Any] = {
        "id": "model-x",
        "name": "Model X",
        "family": "Test",
        "type": "open-weights",
        "license_type": draw(st.sampled_from(list(LicenseType))).value,
        "architecture": draw(st.sampled_from(["dense", "moe"])),
        "attention_mechanism": attention.value,
        "total_parameters_billions": _s(draw(st.floats(min_value=0.1, max_value=3000.0))),
        "calibrated_weights_gb": [{"precision": p, "value": _s(v)} for p, v in calibrated.items()],
        "token_agreement_rates": [{"precision": p, "value": _s(v)} for p, v in agreement.items()],
        "num_layers": _s(draw(st.integers(min_value=1, max_value=128))),
        "num_kv_heads": _s(draw(st.integers(min_value=1, max_value=64))),
        "head_dim": _s(draw(st.sampled_from([64, 128, 256]))),
        "max_context_length": _s(draw(st.integers(min_value=1024, max_value=2_000_000))),
    }
    if attention == AttentionMechanism.HYBRID_SPARSE_LAYER:
        ratio = draw(st.floats(min_value=0.01, max_value=1.0))
        data["active_kv_layer_ratio"] = _s(ratio)
    return ModelSpec.model_validate(data)


OPTIONS = st.builds(
    SizingOptions,
    kv_precision=st.sampled_from(list(PrecisionFormat)),
    target_context_length=st.integers(min_value=1, max_value=2_000_000),
    apply_mac_wired_memory_override=st.booleans(),
    linux_amd_override=st.booleans(),
    gpu_memory_utilization=st.floats(min_value=0.01, max_value=1.0),
    runtime_overhead_gb=st.floats(min_value=0.0, max_value=8.0),
    repo_workspace_gb=st.floats(min_value=2.5, max_value=6.0),
    runtime_format=st.sampled_from(list(RuntimeFormat)),
)
PROFILES = st.builds(
    WorkloadProfile,
    concurrent_agent_instances=st.integers(min_value=1, max_value=32),
    peak_concurrent_requests=st.integers(min_value=1, max_value=64),
)
PRECISIONS = st.sampled_from(list(PrecisionFormat))


def _input(
    hardware: HardwareSpec,
    model: ModelSpec,
    precision: PrecisionFormat,
    options: SizingOptions,
    profile: WorkloadProfile,
    nodes: float | None = None,
) -> SizingInput:
    return SizingInput(
        hardware=hardware,
        model=model,
        precision=precision,
        requested_nodes=float(hardware.valid_node_counts.value[0]) if nodes is None else nodes,
        options=options,
        profile=profile,
        license_alternatives=ALTERNATIVES,
    )


def _run(inp: SizingInput) -> SizingResult:
    return size_deployment(inp, PARAMS)


# --------------------------------------------------------------------------- oracles


def _value(item: Any) -> Any:
    return None if item is None else item.value


def _usable_per_node(hardware: HardwareSpec, options: SizingOptions) -> tuple[float, float]:
    """(effective usable, default usable) per node in GB (Req 16.1 to 16.4, 16.8)."""
    adv = hardware.advertised_memory_gb.value
    if hardware.memory_architecture == MemoryArchitecture.DISCRETE:
        usable = adv * options.gpu_memory_utilization
        return usable, usable
    default = adv * (1 - hardware.os_reserved_memory_ratio.value)  # type: ignore[union-attr]
    tuned = _value(hardware.tuned_max_usable_memory_gb)
    linux = _value(hardware.linux_max_usable_memory_gb)
    if hardware.memory_architecture == MemoryArchitecture.APPLE_UNIFIED:
        if options.apply_mac_wired_memory_override and tuned is not None:
            return tuned, default
    elif options.linux_amd_override and linux is not None:
        return linux, default
    return default, default


def _weights(model: ModelSpec, precision: PrecisionFormat) -> tuple[float, str]:
    for entry in model.calibrated_weights_gb:
        if entry.precision == precision:
            return entry.value.value, "measured"
    return model.total_parameters_billions.value * BITS[precision] / 8 * 1.05, "formula"  # type: ignore[union-attr]


def _kv_per_token(hardware: HardwareSpec, model: ModelSpec, options: SizingOptions) -> float:
    if model.attention_mechanism == AttentionMechanism.MULTI_HEAD_LATENT:
        return 890.0
    fmt = options.runtime_format
    if fmt == RuntimeFormat.AUTO:
        apple = hardware.memory_architecture == MemoryArchitecture.APPLE_UNIFIED
        fmt = RuntimeFormat.MLX if apple else RuntimeFormat.VLLM
    phi = 1.08 if fmt == RuntimeFormat.MLX else 1.0
    ratio = 1.0
    if model.attention_mechanism == AttentionMechanism.HYBRID_SPARSE_LAYER:
        ratio = model.active_kv_layer_ratio.value  # type: ignore[union-attr]
    return (
        2
        * model.num_layers.value  # type: ignore[union-attr]
        * ratio
        * model.num_kv_heads.value  # type: ignore[union-attr]
        * model.head_dim.value  # type: ignore[union-attr]
        * BITS[options.kv_precision]
        / 8
        * phi
    )


def _pool(inp: SizingInput, nodes: int) -> tuple[float, float, float]:
    """(KV pool GB, M_kv_single GB, weights on device GB) (Req 17.5, 18.3, 18.6)."""
    usable, _ = _usable_per_node(inp.hardware, inp.options)
    weights, _ = _weights(inp.model, inp.precision)
    on_device = weights
    if inp.hardware.deployment_mode == DeploymentMode.TIERED_OFFLOAD_APPLIANCE:
        shelf = nodes * inp.hardware.system_ram_offload_gb.value  # type: ignore[union-attr]
        on_device = max(0.0, weights - shelf)
    m_kv = _kv_per_token(inp.hardware, inp.model, inp.options) * inp.options.target_context_length
    pool = nodes * usable - on_device - inp.options.runtime_overhead_gb
    return pool, m_kv / 1e9, on_device


# --------------------------------------------------------------------------- properties


# Feature: ai-tco-dss-mvp, Property 11: Usable memory by architecture
@given(hardware=hardware_specs(), model=model_specs(), options=OPTIONS, profile=PROFILES)
def test_property_11_usable_memory_by_architecture(
    hardware: HardwareSpec, model: ModelSpec, options: SizingOptions, profile: WorkloadProfile
) -> None:
    """Property 11 (Req 16.1, 16.2, 16.3, 16.4): usable memory per architecture, 0.01 GB."""
    inp = _input(hardware, model, PrecisionFormat.INT4, options, profile, nodes=1.0)
    result = _run(inp)
    usable, default = _usable_per_node(hardware, options)
    assert result.usable_memory_gb == pytest.approx(round(usable, 2), abs=1e-9)
    assert result.usable_memory_default_gb == pytest.approx(round(default, 2), abs=1e-9)
    assert result.usable_memory_gb == round(result.usable_memory_gb, 2)


# Feature: ai-tco-dss-mvp, Property 12: Mac default-split trap
@given(
    hardware=hardware_specs(MemoryArchitecture.APPLE_UNIFIED),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
)
def test_property_12_mac_default_split_trap(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
) -> None:
    """Property 12 (Req 16.5, 16.7): trap iff default < required ≤ tuned, any override."""
    assume(hardware.tuned_max_usable_memory_gb is not None)
    assert hardware.tuned_max_usable_memory_gb is not None
    inp = _input(hardware, model, precision, options, profile, nodes=1.0)
    result = _run(inp)
    flipped = not options.apply_mac_wired_memory_override
    other_options = options.model_copy(update={"apply_mac_wired_memory_override": flipped})
    other = _run(inp.model_copy(update={"options": other_options}))
    _, default = _usable_per_node(
        hardware, options.model_copy(update={"linux_amd_override": False})
    )
    tuned = hardware.tuned_max_usable_memory_gb.value
    _, m_kv, _ = _pool(inp, 1)
    required = _weights(model, precision)[0] + options.runtime_overhead_gb + m_kv
    expected = default < required <= tuned
    assert result.triggered_mac_default_split_trap is expected
    assert other.triggered_mac_default_split_trap is expected
    trap = [w for w in result.warnings if "iogpu.wired_limit_mb" in w]
    assert len(trap) == (1 if expected else 0)
    if expected:
        assert hardware.id in trap[0]
        assert f"sudo sysctl iogpu.wired_limit_mb={math.floor(tuned * 1024)}" in trap[0]
        assert f"{required:.2f} GB" in trap[0]
        assert f"{default:.2f} GB" in trap[0] and f"{tuned:.2f} GB" in trap[0]


# Feature: ai-tco-dss-mvp, Property 13: Weight and KV-per-token formulas
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
)
def test_property_13_weight_and_kv_per_token_formulas(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
) -> None:
    """Property 13 (Req 17.1, 17.2, 17.3, 17.4): calibrated or formula weights; KV/token."""
    result = _run(_input(hardware, model, precision, options, profile))
    weights, origin = _weights(model, precision)
    assert result.weights.value == pytest.approx(weights, rel=1e-9)
    assert result.weights.origin.origin == origin
    assert result.kv_per_token_bytes == pytest.approx(
        _kv_per_token(hardware, model, options), rel=1e-9
    )


# Feature: ai-tco-dss-mvp, Property 14: KV pool, concurrency and OOM
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
    node_index=st.integers(min_value=0, max_value=3),
)
def test_property_14_kv_pool_concurrency_and_oom(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
    node_index: int,
) -> None:
    """Property 14 (Req 17.5, 17.6, 18.3, 18.6): U_max = floor(pool / M_kv); OOM iff pool <= 0
    or U_max < 1."""
    nodes = [1, 2, 4, 8][node_index]
    inp = _input(hardware, model, precision, options, profile, nodes=float(nodes))
    result = _run(inp)
    pool, m_kv, on_device = _pool(inp, nodes)
    users = math.floor(pool / m_kv) if pool > 0 else 0
    oom = pool <= 0 or users < 1
    valid_nodes = nodes in hardware.valid_node_counts.value
    assert result.kv_pool_gb == pytest.approx(pool, rel=1e-9, abs=1e-9)
    assert result.m_kv_single_gb == pytest.approx(m_kv, rel=1e-9)
    assert result.max_concurrent_users == (0 if oom else users)
    assert result.is_feasible is (not oom and valid_nodes)
    if oom:
        assert result.oom_reason is not None
        usable, _ = _usable_per_node(hardware, options)
        shortfall = (
            on_device + options.runtime_overhead_gb - nodes * usable if pool <= 0 else m_kv - pool
        )
        assert f"{shortfall:.1f} GB" in result.oom_reason
    elif valid_nodes:
        assert result.oom_reason is None


# Feature: ai-tco-dss-mvp, Property 15: Memory breakdown and eviction flag
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
)
def test_property_15_memory_breakdown_and_eviction_flag(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
) -> None:
    """Property 15 (Req 17.7, 17.8, 17.11): breakdown keys and values, eviction flag."""
    inp = _input(hardware, model, precision, options, profile)
    nodes = int(inp.requested_nodes)
    result = _run(inp)
    breakdown = dict(result.memory_breakdown)
    assert tuple(k for k, _ in result.memory_breakdown) == KEYS
    assert all(v >= 0 for v in breakdown.values())
    _, m_kv, _ = _pool(inp, nodes)
    agent_state = profile.concurrent_agent_instances * (m_kv + options.repo_workspace_gb)
    assert breakdown["agent_state_parked"] == pytest.approx(agent_state, rel=1e-9)
    assert result.agent_state_memory_required_gb == pytest.approx(agent_state, rel=1e-9)
    assert breakdown["kv_cache_active"] == pytest.approx(
        m_kv * min(profile.peak_concurrent_requests, result.max_concurrent_users), rel=1e-9
    )
    assert breakdown["weights"] == pytest.approx(_weights(model, precision)[0], rel=1e-9)
    assert breakdown["runtime_overhead"] == options.runtime_overhead_gb
    if hardware.memory_architecture == MemoryArchitecture.DISCRETE:
        ram = _value(hardware.system_ram_total_installed_gb)
        system = None if ram is None else ram * nodes
    else:
        system = _usable_per_node(hardware, options)[0]
    assert result.context_eviction_risk is (system is not None and agent_state > system)


# Feature: ai-tco-dss-mvp, Property 16: More memory never hurts
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
    factor=st.floats(min_value=1.0, max_value=8.0),
)
def test_property_16_more_memory_never_hurts(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
    factor: float,
) -> None:
    """Property 16 (Req 17.9): more advertised memory keeps feasibility and never lowers U_max."""
    adv = hardware.advertised_memory_gb
    bigger = hardware.model_copy(
        update={"advertised_memory_gb": adv.model_copy(update={"value": adv.value * factor})}
    )
    small = _run(_input(hardware, model, precision, options, profile))
    large = _run(_input(bigger, model, precision, options, profile))
    if small.is_feasible:
        assert large.is_feasible
    assert large.max_concurrent_users >= small.max_concurrent_users


NODE_VALUES = st.one_of(
    st.integers(min_value=1, max_value=8).map(float),
    st.integers(min_value=-5, max_value=0).map(float),
    st.integers(min_value=9, max_value=64).map(float),
    st.floats(min_value=-10, max_value=20, allow_nan=False).filter(lambda v: v != int(v)),
)


# Feature: ai-tco-dss-mvp, Property 17: Node-count handling
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    requested=NODE_VALUES,
)
def test_property_17_node_count_handling(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    requested: float,
) -> None:
    """Property 17 (Req 18.1, 18.2, 18.7, 18.8): unchanged, snapped, rejected or infeasible."""
    inp = _input(hardware, model, PrecisionFormat.INT4, options, profile, nodes=requested)
    if requested != int(requested) or not 1 <= requested <= 8:
        with pytest.raises(EngineInputError) as info:
            _run(inp)
        assert str(requested) in info.value.message and "1 to 8" in info.value.message
        return
    result = _run(inp)
    expected = {1: 1, 2: 2, 3: 4, 4: 4, 5: 8, 6: 8, 7: 8, 8: 8}[int(requested)]
    node_warnings = [w for w in result.warnings if "snapped" in w]
    assert result.requested_nodes == int(requested)
    assert result.nodes_required == expected
    assert len(node_warnings) == (0 if expected == requested else 1)
    if node_warnings:
        assert str(int(requested)) in node_warnings[0] and str(expected) in node_warnings[0]
    valid = expected in hardware.valid_node_counts.value
    if not valid:
        assert result.is_feasible is False
        assert result.oom_reason is not None
        assert str(list(hardware.valid_node_counts.value)) in result.oom_reason
    expected_alpha = 1.0 if expected == 1 else dict(PARAMS.alpha_scaling)[hardware.interconnect]
    assert result.alpha_scaling == expected_alpha
    if hardware.interconnect.value in ALPHA and expected > 1:
        assert result.alpha_scaling == ALPHA[hardware.interconnect.value]
    cables = expected * (expected - 1) // 2
    tb5 = hardware.interconnect == InterconnectType.THUNDERBOLT_5_RDMA
    assert result.thunderbolt_mesh_cables == (cables if tb5 else 0)


# Feature: ai-tco-dss-mvp, Property 18: Quality, license and context flags never change feasibility
@given(
    hardware=hardware_specs(),
    model=model_specs(),
    options=OPTIONS,
    profile=PROFILES,
    precision=PRECISIONS,
    license_type=st.sampled_from(list(LicenseType)),
    max_context=st.integers(min_value=1024, max_value=2_000_000),
    rate=st.none() | st.floats(min_value=0.0, max_value=1.0),
)
def test_property_18_flags_never_change_feasibility(
    hardware: HardwareSpec,
    model: ModelSpec,
    options: SizingOptions,
    profile: WorkloadProfile,
    precision: PrecisionFormat,
    license_type: LicenseType,
    max_context: int,
    rate: float | None,
) -> None:
    """Property 18 (Req 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7): flags only add warnings."""
    rates = () if rate is None else ({"precision": precision.value, "value": _s(rate)},)
    variant = ModelSpec.model_validate(
        {
            **model.model_dump(),
            "license_type": license_type.value,
            "max_context_length": _s(max_context),
            "token_agreement_rates": list(rates),
        }
    )
    base = _run(_input(hardware, model, precision, options, profile))
    result = _run(_input(hardware, variant, precision, options, profile))
    assert result.is_feasible == base.is_feasible

    inp = _input(hardware, variant, precision, options, profile)
    pool, _, _ = _pool(inp, int(inp.requested_nodes))
    per_token = _kv_per_token(hardware, variant, options)
    by_pool = math.floor(pool * 1e9 / per_token) if pool > 0 else 0
    usable_context = min(max_context, by_pool)
    assert result.max_usable_context == usable_context
    assert result.meets_128k_agentic_context_floor is (
        max_context >= 128_000 and usable_context >= 128_000
    )
    banned = license_type == LicenseType.LLAMA_4_EU_RESTRICTED
    assert result.eu_commercial_license_valid is (not banned)
    license_warnings = [w for w in result.warnings if "Llama-4-EU-Ban" in w]
    assert len(license_warnings) == (1 if banned else 0)
    if banned:
        assert ALTERNATIVES[0] in license_warnings[0]
    assert result.token_agreement_rate == rate
    schema = [w for w in result.warnings if "schema-break" in w]
    assert len(schema) == (1 if rate is not None and rate < 0.90 else 0)
