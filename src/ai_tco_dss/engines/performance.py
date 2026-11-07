"""Performance_Engine: decode, prefill, TTFT, effective TPS and 1M-token prefill time
(Req 20.1 to 20.7, 21.1 to 21.9; design.md § "Performance_Engine").

Measured Benchmark_Records win over formula values (Req 9.4, Project Rule 4) unless
`use_measured` is False (calibration path, Req 42.1).
Pure: the result depends only on the input contract and `EngineParameters`.
"""

import math
from itertools import pairwise
from typing import Literal

from ai_tco_dss.domain import (
    ApiPerformanceInput,
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkRecord,
    EngineParameters,
    FormulaTrace,
    Metric,
    PerformanceInput,
    PerformanceResult,
    PrecisionFormat,
    Sourced,
    ValueOrigin,
    WorkloadResult,
)
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines.resolver import select_benchmark
from ai_tco_dss.engines.sizing import precision_bits

PREFILL_1M_TOKENS = 1_000_000
BETA_UNOPTIMIZED = 0.035
TPS = "tok/s"
SPECULATIVE_MODES = "none, apple-mtp-dflash, built-in-mtp or external-draft"


def delta_ctx(context: float, breakpoints: tuple[tuple[int, float], ...]) -> float:
    """Context degradation factor: linear in log2(context) between the breakpoints,
    the first factor below the first breakpoint, the last factor above the last (Req 20.6)."""
    if context <= breakpoints[0][0]:
        return breakpoints[0][1]
    for (c0, d0), (c1, d1) in pairwise(breakpoints):
        if context == c1:
            return d1
        if context < c1:
            t = (math.log2(context) - math.log2(c0)) / (math.log2(c1) - math.log2(c0))
            return d0 + t * (d1 - d0)
    return breakpoints[-1][1]


def _origin(origin: Literal["measured", "formula"], *source_ids: str) -> ValueOrigin:
    return ValueOrigin(origin=origin, source_ids=tuple(dict.fromkeys(source_ids)))


def _measured(record: BenchmarkRecord, name: str, unit: str) -> tuple[Metric, FormulaTrace]:
    if record.value <= 0:
        raise EngineInputError(name, f"> 0 {unit} (measured value)", record.source_id)
    metric = Metric(value=record.value, unit=unit, origin=_origin("measured", record.source_id))
    trace = FormulaTrace(
        name=name,
        symbolic=f"{name} = Benchmark_Record value",
        substituted=f"{record.source_id} at {record.context_tokens} tokens = {record.value}",
        result=record.value,
        unit=unit,
    )
    return metric, trace


def _formula_decode(inp: PerformanceInput, params: EngineParameters) -> tuple[Metric, FormulaTrace]:
    """BW / (P_active * bits/8 * 1.05) * eta * gamma * delta_ctx * alpha (Req 20.1 to 20.7)."""
    hardware, model, options = inp.hardware, inp.model, inp.options
    bandwidth = hardware.memory_bandwidth_gbs
    if bandwidth.value <= 0:
        raise EngineInputError("memory_bandwidth_gbs", "> 0 GB/s", hardware.id)
    p_active = model.active_parameters_billions
    if p_active is None or p_active.value <= 0:
        raise EngineInputError("active_parameters_billions", "> 0 billion parameters", model.id)
    try:
        bits = precision_bits(PrecisionFormat(inp.precision))
    except ValueError:
        bits = 0
    if bits <= 0:
        raise EngineInputError("bits", "> 0 (a supported precision)", model.id)
    gamma = dict(params.gamma_spec).get(options.speculative_mode)
    if gamma is None:
        raise EngineInputError("speculative_mode", SPECULATIVE_MODES, model.id)
    eta = params.eta_dense if model.architecture == "dense" else params.eta_moe
    delta = delta_ctx(options.target_context_length, params.delta_ctx_breakpoints)
    alpha = inp.sizing.alpha_scaling
    factor = params.weight_overhead_factor
    m_active = p_active.value * bits / 8 * factor
    value = bandwidth.value / m_active * eta * gamma * delta * alpha
    metric = Metric(
        value=value,
        unit=TPS,
        origin=_origin("formula", bandwidth.source_id, p_active.source_id),
    )
    trace = FormulaTrace(
        name="decode_tps",
        symbolic=(
            "TPS_decode = BW / (P_active * bits / 8 * 1.05) * eta_engine * gamma_spec"
            " * delta_ctx * alpha_scaling"
        ),
        substituted=(
            f"{bandwidth.value} / ({p_active.value} * {bits} / 8 * {factor}) * {eta} * {gamma}"
            f" * {delta:.4f} * {alpha}"
        ),
        result=value,
        unit=TPS,
    )
    return metric, trace


def _catalog_value(
    name: str,
    item: Sourced[float],
    unit: str,
    origin: Literal["measured", "formula"] = "formula",
) -> tuple[Metric, FormulaTrace]:
    metric = Metric(value=item.value, unit=unit, origin=_origin(origin, item.source_id))
    trace = FormulaTrace(
        name=name,
        symbolic=f"{name} = catalog value",
        substituted=f"{item.value}",
        result=item.value,
        unit=unit,
    )
    return metric, trace


def _effective(
    decode: Metric, ttft: Metric, workload: WorkloadResult
) -> tuple[Metric, FormulaTrace]:
    """T_out * mu / (TTFT + T_out * mu / TPS_decode); 0 if T_out * mu = 0 (Req 21.4, 21.8)."""
    out = workload.out_think / workload.tau  # T_out * mu_thinking, without tau (Req 21.4)
    value = 0.0 if out == 0 else min(decode.value, out / (ttft.value + out / decode.value))
    metric = Metric(
        value=value,
        unit=TPS,
        origin=_origin("formula", *decode.origin.source_ids, *ttft.origin.source_ids),
    )
    trace = FormulaTrace(
        name="effective_tps",
        symbolic="TPS_eff = T_out * mu / (TTFT + T_out * mu / TPS_decode)",
        substituted=f"{out} / ({ttft.value:.4f} + {out} / {decode.value:.4f})",
        result=value,
        unit=TPS,
    )
    return metric, trace


def compute_performance(inp: PerformanceInput, params: EngineParameters) -> PerformanceResult:
    """Speed and latency of one open-weights deployment."""
    hardware, model, options = inp.hardware, inp.model, inp.options
    r_cache = inp.profile.prompt_cache_hit_rate
    if not 0.0 <= r_cache <= 1.0:
        raise EngineInputError("r_cache", f"[0.0, 1.0], got {r_cache}", model.id)
    context = options.target_context_length
    warnings: list[str] = []
    traces: list[FormulaTrace] = []

    def lookup(metric: BenchmarkMetric, target: int) -> BenchmarkRecord | None:
        if not inp.use_measured:
            return None
        query = BenchmarkQuery(
            records=inp.benchmarks,
            metric=metric,
            model_id=model.id,
            hardware_id=hardware.id,
            precision=inp.precision,
            target_context=target,
            tolerance=params.context_match_tolerance,
        )
        return select_benchmark(query)

    # Decode (20.1 to 20.7): formula inputs are checked even when a record matches.
    decode, trace = _formula_decode(inp, params)
    record = lookup(BenchmarkMetric.DECODE_TPS, context)
    if record is not None:
        decode, trace = _measured(record, "decode_tps", TPS)
    traces.append(trace)

    # Prefill (21.1, 21.7)
    prefill: Metric | None = None
    record = lookup(BenchmarkMetric.PREFILL_TPS, context)
    base = hardware.base_prefill_tps_at_32k
    if record is not None:
        prefill, trace = _measured(record, "prefill_tps", TPS)
    elif base is not None:
        if base.value <= 0:
            raise EngineInputError("base_prefill_tps_at_32k", "> 0 tok/s", hardware.id)
        prefill, trace = _catalog_value("prefill_tps", base, TPS)
    else:
        warnings.append(
            f"{hardware.id} with {model.id} lacks prefill data (no prefill Benchmark_Record, "
            "no base_prefill_tps_at_32k): TTFT, effective TPS and the 1M-token prefill time "
            "are not available"
        )
    if prefill is not None:
        traces.append(trace)

    # TTFT (21.2, 21.3, 21.9): a measured TTFT record wins (9.4).
    ttft: Metric | None = None
    record = lookup(BenchmarkMetric.TTFT_S, context)
    if record is not None:
        ttft, trace = _measured(record, "ttft_s", "s")
        traces.append(trace)
    elif prefill is not None:
        beta = 1.0 if options.enable_optimized_backend else BETA_UNOPTIMIZED
        rate = prefill.value * beta
        value = inp.workload.t_in_hat * (1 - r_cache) / rate
        symbolic = "TTFT = T_in_hat * (1 - r_cache) / (prefill_TPS * beta_backend)"
        substituted = f"{inp.workload.t_in_hat} * (1 - {r_cache}) / ({prefill.value} * {beta})"
        if inp.sizing.context_eviction_risk:
            value += context / rate
            symbolic += " + target_context / (prefill_TPS * beta_backend)"
            substituted += f" + {context} / ({prefill.value} * {beta})"
        ttft = Metric(value=value, unit="s", origin=prefill.origin)
        traces.append(
            FormulaTrace(
                name="ttft_s", symbolic=symbolic, substituted=substituted, result=value, unit="s"
            )
        )

    # Effective TPS (21.4, 21.8)
    effective: Metric | None = None
    if ttft is not None:
        effective, trace = _effective(decode, ttft, inp.workload)
        traces.append(trace)

    # 1M-token prefill time (21.5)
    prefill_1m: Metric | None = None
    if prefill is not None:
        record = lookup(BenchmarkMetric.PREFILL_TPS, PREFILL_1M_TOKENS)
        catalog_1m = hardware.prefill_tps_at_1m
        if record is not None:
            rate_1m, origin = record.value, _origin("measured", record.source_id)
        elif catalog_1m is not None:
            rate_1m, origin = catalog_1m.value, _origin("formula", catalog_1m.source_id)
        else:
            rate_1m, origin = prefill.value, _origin("formula", *prefill.origin.source_ids)
            warnings.append(
                f"{hardware.id}: the 1,000,000-token prefill time uses the prefill rate at "
                f"{context} tokens; long-context prefill speed is likely overestimated"
            )
        if rate_1m <= 0:
            raise EngineInputError("prefill_tps_1m", "> 0 tok/s", hardware.id)
        minutes = PREFILL_1M_TOKENS / rate_1m / 60
        prefill_1m = Metric(value=minutes, unit="min", origin=origin)
        traces.append(
            FormulaTrace(
                name="prefill_1m_minutes",
                symbolic="t_1M = 1,000,000 / prefill_TPS_1M / 60",
                substituted=f"1000000 / {rate_1m} / 60",
                result=minutes,
                unit="min",
            )
        )

    return PerformanceResult(
        decode_tps=decode,
        prefill_tps=prefill,
        ttft_s=ttft,
        effective_tps=effective,
        prefill_1m_minutes=prefill_1m,
        warnings=tuple(warnings),
        traces=tuple(traces),
    )


def compute_api_performance(
    inp: ApiPerformanceInput, params: EngineParameters
) -> PerformanceResult:
    """Speed of a commercial API model from its catalog values; missing values stay None."""
    model = inp.model
    traces: list[FormulaTrace] = []
    decode: Metric | None = None
    ttft: Metric | None = None
    effective: Metric | None = None
    if model.api_decode_tps is not None:
        decode, trace = _catalog_value("decode_tps", model.api_decode_tps, TPS, "measured")
        traces.append(trace)
    if model.api_ttft_s is not None:
        ttft, trace = _catalog_value("ttft_s", model.api_ttft_s, "s", "measured")
        traces.append(trace)
    if decode is not None and ttft is not None:
        effective, trace = _effective(decode, ttft, inp.workload)
        traces.append(trace)
    return PerformanceResult(
        decode_tps=decode,
        prefill_tps=None,
        ttft_s=ttft,
        effective_tps=effective,
        warnings=(),
        traces=tuple(traces),
    )
