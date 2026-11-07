"""Sizing_Engine: memory fit of one hardware-model pairing (Req 16 to 19).

Steps 1 to 11 of design.md § "Sizing_Engine". All memory values are GB (1 GB = 10^9 bytes).
Aggregate values (usable memory, KV pool, OS reservation) cover all effective nodes.
Pure: the result depends only on the `SizingInput` contract and `EngineParameters`.
"""

import math

from ai_tco_dss.domain import (
    AttentionMechanism,
    DeploymentMode,
    EngineParameters,
    FormulaTrace,
    HardwareSpec,
    InterconnectType,
    LicenseType,
    MemoryArchitecture,
    Metric,
    ModelSpec,
    PrecisionFormat,
    RuntimeFormat,
    SizingInput,
    SizingOptions,
    SizingResult,
    Sourced,
    ValueOrigin,
)
from ai_tco_dss.domain.errors import EngineInputError

POWER_OF_TWO_NODES = (1, 2, 4, 8)
AGENTIC_CONTEXT_FLOOR = 128_000
AGREEMENT_THRESHOLD = 0.90
BYTES_PER_GB = 1e9


def precision_bits(precision: PrecisionFormat) -> int:
    """Bit width of a weight or KV precision (design.md step 4)."""
    match precision:
        case PrecisionFormat.FP16 | PrecisionFormat.BF16:
            return 16
        case PrecisionFormat.FP8 | PrecisionFormat.INT8:
            return 8
        case PrecisionFormat.INT4:
            return 4
        case PrecisionFormat.INT3:
            return 3
        case PrecisionFormat.INT2:
            return 2


def _effective_nodes(inp: SizingInput, warnings: list[str]) -> tuple[int, int]:
    """(requested, effective) node count; rejects invalid counts, snaps 3 to 7 (Req 18.1-18.7)."""
    requested = inp.requested_nodes
    if requested != int(requested) or not 1 <= requested <= 8:
        raise EngineInputError(
            "requested_nodes", f"an integer from 1 to 8, got {requested}", inp.hardware.id
        )
    count = int(requested)
    effective = next(n for n in POWER_OF_TWO_NODES if n >= count)
    if effective != count:
        warnings.append(
            f"{inp.hardware.id}: requested node count {count} snapped to {effective} "
            "(tensor parallelism needs a power of two)"
        )
    return count, effective


def _check_memory_bounds(hardware: HardwareSpec, options: SizingOptions) -> None:
    """Req 16.9: reject out-of-range memory fields, naming the field and the hardware_id."""
    adv = hardware.advertised_memory_gb.value
    ratio = hardware.os_reserved_memory_ratio
    if ratio is not None and not 0.0 <= ratio.value < 1.0:
        raise EngineInputError(
            "os_reserved_memory_ratio", "0.0 (inclusive) to 1.0 (exclusive)", hardware.id
        )
    for name, item in (
        ("tuned_max_usable_memory_gb", hardware.tuned_max_usable_memory_gb),
        ("linux_max_usable_memory_gb", hardware.linux_max_usable_memory_gb),
    ):
        if item is not None and not 0.0 < item.value <= adv:
            raise EngineInputError(name, f"> 0 and <= advertised memory {adv} GB", hardware.id)
    if hardware.memory_architecture == MemoryArchitecture.DISCRETE:
        if not 0.0 < options.gpu_memory_utilization <= 1.0:
            raise EngineInputError(
                "gpu_memory_utilization", "0.0 (exclusive) to 1.0 (inclusive)", hardware.id
            )
    elif ratio is None:
        raise EngineInputError(
            "os_reserved_memory_ratio", "a value in [0.0, 1.0) for unified memory", hardware.id
        )


def _usable_per_node(
    hardware: HardwareSpec, options: SizingOptions, warnings: list[str]
) -> tuple[float, float]:
    """(effective, default) usable memory of one node in GB (Req 16.1 to 16.4, 16.8)."""
    _check_memory_bounds(hardware, options)
    adv = hardware.advertised_memory_gb.value
    if hardware.memory_architecture == MemoryArchitecture.DISCRETE:
        usable = adv * options.gpu_memory_utilization
        return usable, usable
    assert hardware.os_reserved_memory_ratio is not None  # checked above
    default = adv * (1 - hardware.os_reserved_memory_ratio.value)
    if hardware.memory_architecture == MemoryArchitecture.APPLE_UNIFIED:
        enabled, option = options.apply_mac_wired_memory_override, "apply_mac_wired_memory_override"
        override, field = hardware.tuned_max_usable_memory_gb, "tuned_max_usable_memory_gb"
    else:
        enabled, option = options.linux_amd_override, "linux_amd_override"
        override, field = hardware.linux_max_usable_memory_gb, "linux_max_usable_memory_gb"
    if not enabled:
        return default, default
    if override is None:
        warnings.append(
            f"{hardware.id}: {option} is enabled but {field} is missing; "
            f"using the default usable memory {default:.2f} GB"
        )
        return default, default
    return override.value, default


def _weights(
    model: ModelSpec, precision: PrecisionFormat, params: EngineParameters
) -> tuple[Metric, FormulaTrace]:
    """Calibrated footprint (measured), else P_total * bits/8 * 1.05 (formula) (Req 17.1, 17.2)."""
    for entry in model.calibrated_weights_gb:
        if entry.precision == precision:
            value = entry.value.value
            metric = Metric(
                value=value,
                unit="GB",
                origin=ValueOrigin(origin="measured", source_ids=(entry.value.source_id,)),
            )
            trace = FormulaTrace(
                name="weights",
                symbolic="M_weights = calibrated_weights_gb[precision]",
                substituted=f"calibrated_weights_gb[{precision.value}] = {value} GB",
                result=value,
                unit="GB",
            )
            return metric, trace
    total = model.total_parameters_billions
    if total is None or total.value <= 0:
        raise EngineInputError("total_parameters_billions", "> 0 billion parameters", model.id)
    bits = precision_bits(precision)
    factor = params.weight_overhead_factor
    value = total.value * bits / 8 * factor
    metric = Metric(
        value=value, unit="GB", origin=ValueOrigin(origin="formula", source_ids=(total.source_id,))
    )
    trace = FormulaTrace(
        name="weights",
        symbolic="M_weights = P_total * (bits / 8) * 1.05",
        substituted=f"{total.value} * ({bits} / 8) * {factor}",
        result=value,
        unit="GB",
    )
    return metric, trace


def _kv_per_token(
    hardware: HardwareSpec, model: ModelSpec, options: SizingOptions, params: EngineParameters
) -> tuple[float, FormulaTrace]:
    """KV cache bytes per token (Req 17.3, 17.4, 17.12)."""
    if model.attention_mechanism == AttentionMechanism.MULTI_HEAD_LATENT:
        value = params.mla_kv_bytes_per_token
        trace = FormulaTrace(
            name="kv_per_token",
            symbolic="M_kv_per_token = 890 bytes (multi-head latent attention)",
            substituted=f"{value} bytes",
            result=value,
            unit="bytes",
        )
        return value, trace
    hybrid = model.attention_mechanism == AttentionMechanism.HYBRID_SPARSE_LAYER
    required: list[tuple[str, Sourced[int] | Sourced[float] | None]] = [
        ("num_layers", model.num_layers),
        ("num_kv_heads", model.num_kv_heads),
        ("head_dim", model.head_dim),
    ]
    if hybrid:
        required.append(("active_kv_layer_ratio", model.active_kv_layer_ratio))
    invalid = [name for name, item in required if item is None or item.value <= 0]
    ratio_item = model.active_kv_layer_ratio
    if hybrid and ratio_item is not None and ratio_item.value > 1:
        invalid.append("active_kv_layer_ratio")
    if invalid:
        raise EngineInputError(
            ", ".join(invalid), "present and > 0 (active_kv_layer_ratio <= 1)", model.id
        )
    assert model.num_layers and model.num_kv_heads and model.head_dim  # checked above
    layers, heads, dim = model.num_layers.value, model.num_kv_heads.value, model.head_dim.value
    ratio = ratio_item.value if hybrid and ratio_item is not None else 1.0
    runtime = options.runtime_format
    if runtime == RuntimeFormat.AUTO:
        apple = hardware.memory_architecture == MemoryArchitecture.APPLE_UNIFIED
        runtime = RuntimeFormat.MLX if apple else RuntimeFormat.VLLM
    phi = dict(params.phi_format)[runtime]
    kv_bits = precision_bits(options.kv_precision)
    value = 2 * layers * ratio * heads * dim * kv_bits / 8 * phi
    trace = FormulaTrace(
        name="kv_per_token",
        symbolic=(
            "M_kv_per_token = 2 * n_layers * r_kv_active * n_kv_heads * d_head"
            " * (kv_bits / 8) * phi_format"
        ),
        substituted=f"2 * {layers} * {ratio} * {heads} * {dim} * ({kv_bits} / 8) * {phi}",
        result=value,
        unit="bytes",
    )
    return value, trace


def _alpha(hardware: HardwareSpec, nodes: int, params: EngineParameters) -> float:
    """Interconnect scaling efficiency (Req 18.4)."""
    if nodes == 1:
        return 1.0
    alpha = dict(params.alpha_scaling).get(hardware.interconnect)
    if alpha is None:
        raise EngineInputError(
            "interconnect", "an interconnect with an alpha_scaling value", hardware.id
        )
    return alpha


def size_deployment(inp: SizingInput, params: EngineParameters) -> SizingResult:
    """Usable memory, weights, KV pool, concurrency, flags and warnings for one pairing."""
    hardware, model, options = inp.hardware, inp.model, inp.options
    if model.type != "open-weights":
        raise EngineInputError(
            "model type", "an open-weights model (API models are not sized on hardware)", model.id
        )
    warnings: list[str] = []
    reasons: list[str] = []

    # 1. Node count (18.1, 18.2, 18.7, 18.8)
    requested, nodes = _effective_nodes(inp, warnings)
    valid_counts = list(hardware.valid_node_counts.value)
    if nodes not in valid_counts:
        reasons.append(
            f"effective node count {nodes} is not in the valid node counts {valid_counts} "
            f"of {hardware.id}"
        )

    # 2.-3. Usable memory per node and aggregate (16.1 to 16.4, 16.8, 16.9, 18.3)
    usable_node, default_node = _usable_per_node(hardware, options, warnings)
    usable_total = nodes * usable_node
    default_total = nodes * default_node
    advertised_total = nodes * hardware.advertised_memory_gb.value

    # 4.-5. Weights and KV per token (17.1 to 17.4, 17.12)
    weights, weights_trace = _weights(model, inp.precision, params)
    kv_per_token, kv_trace = _kv_per_token(hardware, model, options, params)
    m_kv_single = kv_per_token * options.target_context_length / BYTES_PER_GB
    overhead = options.runtime_overhead_gb

    # 3./6. Tiered offload: the Shelf (system RAM) takes weights first (18.6, 18.9, ledger C-034)
    on_device = weights.value
    if hardware.deployment_mode == DeploymentMode.TIERED_OFFLOAD_APPLIANCE:
        offload = hardware.system_ram_offload_gb
        shelf = nodes * offload.value if offload is not None else 0.0
        capacity = usable_total + shelf
        if weights.value > capacity:
            reasons.append(
                f"weights {weights.value:.1f} GB exceed the weight capacity {capacity:.1f} GB "
                "(usable VRAM + system RAM offload)"
            )
        on_device = max(0.0, weights.value - shelf)
        warnings.append(
            f"{hardware.id}: Strata defaults to an 8,192-token context window; "
            "reconfigure it before running agentic harness prompts"
        )

    # 6. KV pool and U_max (17.5, 17.6)
    pool = usable_total - on_device - overhead
    max_users = 0
    if pool <= 0:
        shortfall = on_device + overhead - usable_total
        reasons.append(
            f"OOM: weights {on_device:.1f} GB + runtime overhead {overhead:.1f} GB exceed "
            f"usable memory {usable_total:.2f} GB by {shortfall:.1f} GB"
        )
    else:
        max_users = math.floor(pool / m_kv_single)
        if max_users < 1:
            max_users = 0
            reasons.append(
                f"OOM: the KV cache of one user ({m_kv_single:.2f} GB) exceeds the KV pool "
                f"({pool:.2f} GB) by {m_kv_single - pool:.1f} GB"
            )

    # 7. Mac default-split trap (16.5, 16.7)
    trap = False
    tuned = hardware.tuned_max_usable_memory_gb
    if hardware.memory_architecture == MemoryArchitecture.APPLE_UNIFIED and tuned is not None:
        required = weights.value + overhead + m_kv_single
        tuned_total = nodes * tuned.value
        trap = default_total < required <= tuned_total
        if trap:
            warnings.append(
                f"{hardware.id}: Mac default-split trap: the model needs {required:.2f} GB, "
                f"default usable memory is {default_total:.2f} GB, tuned usable memory is "
                f"{tuned_total:.2f} GB; run sudo sysctl iogpu.wired_limit_mb="
                f"{math.floor(tuned.value * 1024)}"
            )

    # 8. Agent state and eviction risk (17.7, 17.11)
    agent_state = inp.profile.concurrent_agent_instances * (m_kv_single + options.repo_workspace_gb)
    system_ram: float | None = None
    if hardware.memory_architecture == MemoryArchitecture.DISCRETE:
        installed = hardware.system_ram_total_installed_gb
        system_ram = nodes * installed.value if installed is not None else None
        eviction_ram = system_ram
    else:
        eviction_ram = usable_node  # unified memory: no separate system RAM value
    eviction = eviction_ram is not None and agent_state > eviction_ram

    # 9. Memory breakdown (17.8)
    breakdown = (
        ("weights", weights.value),
        ("kv_cache_active", m_kv_single * min(inp.profile.peak_concurrent_requests, max_users)),
        ("agent_state_parked", agent_state),
        ("os_reserved", max(0.0, advertised_total - usable_total)),
        ("runtime_overhead", overhead),
    )

    # 10. Quality, license and context flags (19.1 to 19.7)
    by_pool = math.floor(pool * BYTES_PER_GB / kv_per_token) if pool > 0 else 0
    max_context = model.max_context_length.value
    max_usable_context = min(max_context, by_pool)
    meets_floor = (
        max_context >= AGENTIC_CONTEXT_FLOOR and max_usable_context >= AGENTIC_CONTEXT_FLOOR
    )
    license_valid = model.license_type != LicenseType.LLAMA_4_EU_RESTRICTED
    if not license_valid:
        alternatives = ", ".join(inp.license_alternatives) or "none in the catalog"
        warnings.append(
            f"{model.name} ({model.id}) has license {model.license_type.value}, which is not "
            f"valid for EU commercial use; Apache-2.0 or MIT alternatives: {alternatives}"
        )
    rate = next(
        (e.value.value for e in model.token_agreement_rates if e.precision == inp.precision), None
    )
    if rate is not None and rate < AGREEMENT_THRESHOLD:
        warnings.append(
            f"agentic schema-break risk: token agreement {rate:.1%} at {inp.precision.value} "
            f"is below the {AGREEMENT_THRESHOLD:.2f} threshold"
        )

    # 11. Interconnect (18.4, 18.5)
    alpha = _alpha(hardware, nodes, params)
    tb5 = hardware.interconnect == InterconnectType.THUNDERBOLT_5_RDMA
    cables = nodes * (nodes - 1) // 2 if tb5 else 0

    traces = (
        FormulaTrace(
            name="usable_memory",
            symbolic="M_usable = N * usable_per_node",
            substituted=f"{nodes} * {usable_node:.4f} GB",
            result=usable_total,
            unit="GB",
        ),
        weights_trace,
        kv_trace,
        FormulaTrace(
            name="kv_pool",
            symbolic="M_kv_pool = M_usable - M_weights_on_device - M_runtime_overhead",
            substituted=f"{usable_total:.4f} - {on_device:.4f} - {overhead}",
            result=pool,
            unit="GB",
        ),
        FormulaTrace(
            name="max_concurrent_users",
            symbolic="U_max = ⌊M_kv_pool / M_kv_single⌋",
            substituted=f"⌊{pool:.4f} / {m_kv_single:.6f}⌋",
            result=float(max_users),
            unit="users",
        ),
    )
    return SizingResult(
        hardware_id=hardware.id,
        model_id=model.id,
        precision=inp.precision,
        requested_nodes=requested,
        nodes_required=nodes,
        alpha_scaling=alpha,
        is_feasible=not reasons,
        oom_reason="; ".join(reasons) or None,
        usable_memory_gb=round(usable_total, 2),
        usable_memory_default_gb=round(default_total, 2),
        usable_system_ram_gb=system_ram,
        weights=weights,
        kv_per_token_bytes=kv_per_token,
        m_kv_single_gb=m_kv_single,
        kv_pool_gb=pool,
        max_concurrent_users=max_users,
        max_usable_context=max_usable_context,
        agent_state_memory_required_gb=agent_state,
        memory_breakdown=breakdown,
        triggered_mac_default_split_trap=trap,
        meets_128k_agentic_context_floor=meets_floor,
        eu_commercial_license_valid=license_valid,
        context_eviction_risk=eviction,
        token_agreement_rate=rate,
        thunderbolt_mesh_cables=cables,
        warnings=tuple(warnings),
        traces=traces,
    )
