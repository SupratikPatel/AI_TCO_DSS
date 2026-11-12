"""Property tests for the measured-first resolver and the Performance_Engine
(Properties 4 and 19 to 23).

Inputs are variations of one valid base input (Mac mini M5 Pro + Qwen 3.8-27B from the
repository catalog), changed with `model_copy`. Oracles restate the formulas of
requirements.md independently of `engines/performance.py` and `engines/resolver.py`.
"""

import math
from datetime import date
from itertools import pairwise
from typing import Any

from hypothesis import given
from hypothesis import strategies as st
from tests.benchmark_fixtures import conditions

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkRecord,
    BenchmarkSet,
    PerformanceInput,
    PrecisionFormat,
    SizingInput,
    SizingOptions,
    SourceTier,
    SpeculativeMode,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines.performance import compute_performance, delta_ctx
from ai_tco_dss.engines.resolver import select_benchmark
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
HW_ID = "mac-mini-m5-pro-64gb"
MODEL_ID = "qwen-3-8-27b"
BITS = {"FP16": 16, "BF16": 16, "FP8": 8, "INT8": 8, "INT4": 4, "INT3": 3, "INT2": 2}
ETA = {"dense": 0.70, "moe": 0.425}
GAMMA = {"none": 1.0, "apple-mtp-dflash": 1.425, "built-in-mtp": 1.80, "external-draft": 2.75}
BREAKPOINTS = ((8_192, 1.00), (32_768, 0.89), (131_072, 0.60), (262_144, 0.50), (1_048_576, 0.40))
TIER_ORDER = {"official": 0, "third_party": 1, "community": 2}
REL = 1e-9


def _base_input() -> PerformanceInput:
    catalog = get_default_repository().catalog()
    hardware = next(h for h in catalog.hardware if h.id == HW_ID)
    model = next(m for m in catalog.models if m.id == MODEL_ID)
    profile = WorkloadProfile()
    options = SizingOptions(
        target_context_length=8_192,
        performance_prompt_tokens=8192,
        benchmark_conditions=conditions(),
    )
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), PARAMS
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=PrecisionFormat.INT4,
            requested_nodes=1,
            options=options,
            profile=profile,
            license_alternatives=(),
        ),
        PARAMS,
    )
    return PerformanceInput(
        hardware=hardware,
        model=model,
        precision=PrecisionFormat.INT4,
        sizing=sizing,
        workload=workload,
        profile=profile,
        options=options,
        benchmarks=BenchmarkSet(records=()),
    )


BASE = _base_input()
assert BASE.hardware.base_prefill_tps_at_32k is not None
assert BASE.model.active_parameters_billions is not None
PREFILL_32K = BASE.hardware.base_prefill_tps_at_32k
P_ACTIVE = BASE.model.active_parameters_billions


def _oracle_delta(context: float) -> float:
    """Linear interpolation in log2(context) between the design.md breakpoints."""
    if context <= BREAKPOINTS[0][0]:
        return BREAKPOINTS[0][1]
    for (c0, d0), (c1, d1) in pairwise(BREAKPOINTS):
        if context <= c1:
            t = (math.log2(context) - math.log2(c0)) / (math.log2(c1) - math.log2(c0))
            return d0 + t * (d1 - d0)
    return BREAKPOINTS[-1][1]


@st.composite
def scenarios(draw: st.DrawFn) -> dict[str, Any]:
    """Formula inputs within the bounds of Requirements 20 and 21."""
    return {
        "bandwidth": draw(st.floats(min_value=1.0, max_value=20_000.0)),
        "p_active": draw(st.floats(min_value=0.1, max_value=2_000.0)),
        "architecture": draw(st.sampled_from(["dense", "moe"])),
        "precision": draw(st.sampled_from(list(PrecisionFormat))),
        "mode": draw(st.sampled_from(list(SpeculativeMode))),
        "context": draw(st.integers(min_value=1, max_value=2_000_000)),
        "alpha": draw(st.floats(min_value=0.3, max_value=1.0)),
        "prefill": draw(st.floats(min_value=1.0, max_value=50_000.0)),
        "r_cache": draw(st.floats(min_value=0.0, max_value=1.0)),
        "optimized": draw(st.booleans()),
        "eviction": draw(st.booleans()),
        "t_in_hat": draw(st.floats(min_value=1.0, max_value=2_000_000.0)),
        "out_think": draw(st.just(0.0) | st.floats(min_value=1.0, max_value=1_000_000.0)),
        "tau": draw(st.sampled_from([1.0, 1.3])),
    }


def _input(s: dict[str, Any], records: tuple[BenchmarkRecord, ...] = ()) -> PerformanceInput:
    hw, model = BASE.hardware, BASE.model
    hardware = hw.model_copy(
        update={
            "memory_bandwidth_gbs": hw.memory_bandwidth_gbs.model_copy(
                update={"value": s["bandwidth"]}
            ),
            "base_prefill_tps_at_32k": PREFILL_32K.model_copy(update={"value": s["prefill"]}),
        }
    )
    model = model.model_copy(
        update={
            "architecture": s["architecture"],
            "active_parameters_billions": P_ACTIVE.model_copy(update={"value": s["p_active"]}),
        }
    )
    return BASE.model_copy(
        update={
            "hardware": hardware,
            "model": model,
            "precision": s["precision"],
            "options": BASE.options.model_copy(
                update={
                    "weight_precision": s["precision"],
                    "speculative_mode": s["mode"],
                    "target_context_length": s["context"],
                    "enable_optimized_backend": s["optimized"],
                }
            ),
            "profile": BASE.profile.model_copy(update={"prompt_cache_hit_rate": s["r_cache"]}),
            "workload": BASE.workload.model_copy(
                update={"t_in_hat": s["t_in_hat"], "out_think": s["out_think"], "tau": s["tau"]}
            ),
            "sizing": BASE.sizing.model_copy(
                update={"alpha_scaling": s["alpha"], "context_eviction_risk": s["eviction"]}
            ),
            "benchmarks": BenchmarkSet(records=records),
        }
    )


def _decode(s: dict[str, Any]) -> float:
    result = compute_performance(_input(s), PARAMS)
    assert result.decode_tps is not None
    return result.decode_tps.value


# --------------------------------------------------------------------------- Property 4

CONTEXTS = [None, 4_096, 6_144, 8_192, 10_240, 32_768]
DATES = [date(2026, 1, 1), date(2026, 10, 1), date(2026, 11, 7)]


@st.composite
def records(draw: st.DrawFn) -> BenchmarkRecord:
    prompt = draw(st.sampled_from(CONTEXTS))
    return BenchmarkRecord(
        metric=draw(
            st.sampled_from(
                [
                    BenchmarkMetric.DECODE_TPS,
                    BenchmarkMetric.PREFILL_TPS,
                    BenchmarkMetric.AA_INDEX_V5,
                ]
            )
        ),
        value=draw(st.floats(min_value=0.1, max_value=1_000.0)),
        model_id=draw(st.sampled_from([MODEL_ID, "other-model"])),
        hardware_id=draw(st.sampled_from([HW_ID, "other-hw", None])),
        precision=draw(st.sampled_from([PrecisionFormat.INT4, PrecisionFormat.INT8, None])),
        context_tokens=prompt,
        prompt_tokens=prompt,
        conditions=conditions(),
        source_id=draw(st.sampled_from(["A", "B", "C"])),
        tier=draw(st.sampled_from([SourceTier(t) for t in TIER_ORDER])),
        accessed=draw(st.sampled_from(DATES)),
    )


def _oracle_select(
    recs: list[BenchmarkRecord],
    metric: BenchmarkMetric,
    hardware_id: str | None,
    precision: PrecisionFormat | None,
    target: int | None,
    tolerance: float,
) -> BenchmarkRecord | None:
    def matches(r: BenchmarkRecord) -> bool:
        if (r.metric, r.model_id, r.hardware_id, r.precision) != (
            metric,
            MODEL_ID,
            hardware_id,
            precision,
        ):
            return False
        if target is None:
            return True
        return r.context_tokens is not None and abs(r.context_tokens - target) <= (
            tolerance * target
        )

    def key(r: BenchmarkRecord) -> tuple[int, int, int, str]:
        distance = abs(r.context_tokens - target) if target and r.context_tokens else 0
        return (TIER_ORDER[r.tier.value], -r.accessed.toordinal(), distance, r.source_id)

    candidates = [r for r in recs if matches(r)]
    return min(candidates, key=key) if candidates else None


@given(
    recs=st.lists(records(), max_size=8),
    target=st.sampled_from([8_192, 16_384]),
    tolerance=st.sampled_from([0.0, 0.25, 1.0]),
)
def test_property_4_resolver_matches_the_selection_oracle(
    recs: list[BenchmarkRecord], target: int, tolerance: float
) -> None:
    """Property 4: measured-first resolver matches the selection oracle.

    Validates: Requirements 9.3, 9.4, 9.6, 9.9.
    """
    record_set = BenchmarkSet(records=tuple(recs))
    for metric in (BenchmarkMetric.DECODE_TPS, BenchmarkMetric.PREFILL_TPS):
        query = BenchmarkQuery(
            conditions=conditions(),
            records=record_set,
            metric=metric,
            model_id=MODEL_ID,
            hardware_id=HW_ID,
            precision=PrecisionFormat.INT4,
            target_context=target,
            tolerance=tolerance,
        )
        expected = _oracle_select(recs, metric, HW_ID, PrecisionFormat.INT4, target, tolerance)
        assert select_benchmark(query) == expected
    quality = BenchmarkQuery(
        records=record_set,
        metric=BenchmarkMetric.AA_INDEX_V5,
        model_id=MODEL_ID,
        hardware_id=None,
        precision=None,
        target_context=None,
        tolerance=tolerance,
    )
    expected_quality = _oracle_select(recs, BenchmarkMetric.AA_INDEX_V5, None, None, None, 0.0)
    assert select_benchmark(quality) == expected_quality

    # The Performance_Engine labels decode `measured` exactly when a record is selected.
    params = PARAMS.model_copy(update={"context_match_tolerance": tolerance})
    inp = BASE.model_copy(
        update={
            "benchmarks": record_set,
            "options": BASE.options.model_copy(
                update={"target_context_length": target, "performance_prompt_tokens": target}
            ),
        }
    )
    decode = compute_performance(inp, params).decode_tps
    selected = _oracle_select(
        recs, BenchmarkMetric.DECODE_TPS, HW_ID, PrecisionFormat.INT4, target, tolerance
    )
    assert decode is not None
    assert (decode.origin.origin == "measured") == (selected is not None)
    if selected is not None:
        assert decode.value == selected.value
        assert decode.origin.source_ids == (selected.source_id,)


# --------------------------------------------------------------------------- Property 19


@given(s=scenarios())
def test_property_19_performance_formulas(s: dict[str, Any]) -> None:
    """Property 19: decode, TTFT and effective TPS follow the formulas (no record matches).

    Validates: Requirements 20.1, 21.2, 21.3, 21.4, 21.8.
    """
    result = compute_performance(_input(s), PARAMS)
    m_active = s["p_active"] * BITS[s["precision"].value] / 8 * 1.05
    decode = (
        s["bandwidth"]
        / m_active
        * ETA[s["architecture"]]
        * GAMMA[s["mode"].value]
        * _oracle_delta(s["context"])
        * s["alpha"]
    )
    beta = 1.0 if s["optimized"] else 0.035
    ttft = s["t_in_hat"] * (1 - s["r_cache"]) / (s["prefill"] * beta)
    if s["eviction"]:
        ttft += s["context"] / (s["prefill"] * beta)
    out = s["out_think"] / s["tau"]
    effective = 0.0 if out == 0 else out / (ttft + out / decode)

    assert result.decode_tps and result.ttft_s and result.effective_tps
    assert math.isclose(result.decode_tps.value, decode, rel_tol=REL)
    assert math.isclose(result.ttft_s.value, ttft, rel_tol=REL, abs_tol=1e-12)
    assert math.isclose(result.effective_tps.value, effective, rel_tol=REL, abs_tol=1e-12)
    for metric in (result.decode_tps, result.ttft_s, result.effective_tps):
        assert metric.origin.origin == "formula"


# --------------------------------------------------------------------------- Property 20


@given(
    s=scenarios(),
    b1=st.floats(min_value=1e-3, max_value=20_000.0),
    b2=st.floats(min_value=1e-3, max_value=20_000.0),
)
def test_property_20_decode_is_monotone_in_bandwidth(
    s: dict[str, Any], b1: float, b2: float
) -> None:
    """Property 20: increasing bandwidth never lowers decode TPS.

    Validates: Requirements 20.4.
    """
    low, high = sorted((b1, b2))
    assert _decode({**s, "bandwidth": high}) >= _decode({**s, "bandwidth": low})


# --------------------------------------------------------------------------- Property 21


@given(
    s=scenarios(),
    p1=st.floats(min_value=0.1, max_value=3_000.0),
    p2=st.floats(min_value=0.1, max_value=3_000.0),
)
def test_property_21_moe_dual_parameter_law(s: dict[str, Any], p1: float, p2: float) -> None:
    """Property 21: with equal precision, hardware, nodes, context, mode and η, the model
    with fewer active parameters has equal or higher decode TPS.

    Validates: Requirements 20.5.
    """
    fewer, more = sorted((p1, p2))
    assert _decode({**s, "p_active": fewer}) >= _decode({**s, "p_active": more})


# --------------------------------------------------------------------------- Property 22


@given(
    c1=st.integers(min_value=1, max_value=4_000_000),
    c2=st.integers(min_value=1, max_value=4_000_000),
    short=st.integers(min_value=1, max_value=8_192),
)
def test_property_22_context_degradation_curve_shape(c1: int, c2: int, short: int) -> None:
    """Property 22: δ_ctx is non-increasing, 1.0 up to 8 192 tokens, ≥ 0.47 at 262 144.

    Validates: Requirements 20.6.
    """
    breakpoints = PARAMS.delta_ctx_breakpoints
    low, high = sorted((c1, c2))
    assert delta_ctx(low, breakpoints) >= delta_ctx(high, breakpoints)
    assert delta_ctx(short, breakpoints) == 1.0
    assert delta_ctx(262_144, breakpoints) >= 0.47


# --------------------------------------------------------------------------- Property 23


@given(s=scenarios(), recs=st.lists(records(), max_size=4))
def test_property_23_latency_invariants(s: dict[str, Any], recs: list[BenchmarkRecord]) -> None:
    """Property 23: TTFT ≥ 0 and 0 ≤ effective TPS ≤ decode TPS, measured or formula.

    Validates: Requirements 21.6.
    """
    pinned = tuple(r.model_copy(update={"precision": s["precision"]}) for r in recs)
    result = compute_performance(_input(s, pinned), PARAMS)
    assert result.decode_tps is not None
    if result.ttft_s is not None:
        assert result.ttft_s.value >= 0
        assert result.effective_tps is not None
        assert 0 <= result.effective_tps.value <= result.decode_tps.value
