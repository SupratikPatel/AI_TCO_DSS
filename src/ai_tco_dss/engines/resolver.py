"""Measured-first resolver (Req 9.3 to 9.6, 9.9, 9.10; design.md § "Measured-first resolver").

Pure: the result depends only on the `BenchmarkQuery` contract.
"""

from ai_tco_dss.domain import (
    TIER_RANK,
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkRecord,
    HardwareSpec,
    SizingOptions,
)
from ai_tco_dss.domain.benchmark_conditions import BenchmarkConditions
from ai_tco_dss.domain.errors import ConfigurationError

PERFORMANCE_METRICS = frozenset(
    (
        BenchmarkMetric.DECODE_TPS,
        BenchmarkMetric.PREFILL_TPS,
        BenchmarkMetric.TTFT_S,
        BenchmarkMetric.AGGREGATE_TPS,
    )
)


def matching_fields(metric: BenchmarkMetric, conditions: BenchmarkConditions) -> tuple[str, ...]:
    """Physical execution facts relevant to this metric (docs/BENCHMARK_MATCHING_POLICY.md).

    optimized_backend is the application's formula multiplier, not a runtime identifier.
    Actual kernel settings must be captured in the runtime/protocol identity.
    """
    omitted = {"optimized_backend"}
    if metric in (BenchmarkMetric.PREFILL_TPS, BenchmarkMetric.TTFT_S):
        omitted.add("output_tokens")
    if conditions.speculative_mode == "none":
        omitted.add("speculative_config")
    return tuple(name for name in type(conditions).model_fields if name not in omitted)


def uses_offload(hardware: HardwareSpec) -> bool:
    """The sizing engine places weights on the RAM shelf first for these deployments."""
    shelf = hardware.system_ram_offload_gb
    return hardware.memory_architecture == "discrete" and shelf is not None and shelf.value > 0


def deployment_conditions(
    hardware: HardwareSpec,
    nodes: int,
    options: SizingOptions,
    concurrency: int,
    prompt_cache_hit_rate: float,
    output_tokens: int,
) -> BenchmarkConditions | None:
    conditions = options.benchmark_conditions
    if conditions is None:
        return None
    ram = hardware.system_ram_total_installed_gb
    return conditions.model_copy(
        update={
            "nodes": nodes,
            "accelerator_memory_gb": hardware.advertised_memory_gb.value,
            "system_ram_gb": ram.value if ram is not None else 0,
            "speculative_mode": options.speculative_mode,
            "kv_precision": options.kv_precision,
            "optimized_backend": options.enable_optimized_backend,
            "prompt_cache_hit_rate": prompt_cache_hit_rate,
            "concurrency": concurrency,
            "output_tokens": output_tokens,
            "residency": "offload" if uses_offload(hardware) else "resident",
        }
    )


def evidence_gaps(record: BenchmarkRecord) -> tuple[str, ...]:
    """Missing/uncertain conditions, independent of any candidate's desired settings."""
    gaps = list(record.uncertainty_reasons)
    if record.prompt_tokens is None:
        gaps.append("actual prompt_tokens missing; legacy/configured context is not a prompt")
    elif (
        record.configured_context_tokens is not None
        and record.prompt_tokens > record.configured_context_tokens
    ):
        gaps.append("actual prompt_tokens exceeds configured_context_tokens")
    if record.precision is None:
        gaps.append("precision missing")
    if record.conditions is None:
        gaps.append("execution conditions missing")
    else:
        gaps.extend(
            f"conditions.{name} missing"
            for name in matching_fields(record.metric, record.conditions)
            if getattr(record.conditions, name) is None
        )
    return tuple(gaps)


def _matches(record: BenchmarkRecord, query: BenchmarkQuery) -> bool:
    if (record.metric, record.model_id, record.hardware_id, record.precision) != (
        query.metric,
        query.model_id,
        query.hardware_id,
        query.precision,
    ):
        return False
    if query.metric in PERFORMANCE_METRICS:
        if evidence_gaps(record) or query.conditions is None or query.target_context is None:
            return False
        assert record.conditions is not None
        if any(
            getattr(query.conditions, name) is None
            or getattr(record.conditions, name) != getattr(query.conditions, name)
            for name in matching_fields(query.metric, record.conditions)
        ):
            return False
    target = query.target_context
    if target is None:
        return True
    tokens = record.prompt_tokens if query.metric in PERFORMANCE_METRICS else record.context_tokens
    return tokens is not None and abs(tokens - target) <= query.tolerance * target


def select_benchmark(query: BenchmarkQuery) -> BenchmarkRecord | None:
    """The one matching record (highest tier, latest access, closest context, lowest
    source_id), or None if no record matches metric, model, hardware, precision and
    the context-match tolerance. Quality queries pass `target_context=None`."""
    if not 0.0 <= query.tolerance <= 1.0:
        raise ConfigurationError("context_match_tolerance", query.tolerance)
    target = query.target_context

    def key(record: BenchmarkRecord) -> tuple[int, int, int, str]:
        tokens = (
            record.prompt_tokens if query.metric in PERFORMANCE_METRICS else record.context_tokens
        )
        distance = abs(tokens - target) if target and tokens else 0
        return (-TIER_RANK[record.tier], -record.accessed.toordinal(), distance, record.source_id)

    candidates = [r for r in query.records.records if _matches(r, query)]
    return min(candidates, key=key) if candidates else None
