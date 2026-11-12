"""Measured-first resolver, Performance_Engine and the `size` service with performance
(Req 9.3, 9.4, 9.6, 9.9, 20.1 to 20.7, 21.1 to 21.9)."""

from typing import Any

import pytest
from pydantic import BaseModel
from tests.benchmark_fixtures import conditions

from ai_tco_dss.catalog import JsonCatalogRepository, get_default_repository
from ai_tco_dss.domain import (
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkRecord,
    BenchmarkSet,
    DecisionOptions,
    EngineParameters,
    EnterpriseFinancials,
    HardwareSpec,
    ModelSpec,
    PerformanceInput,
    PerformanceResult,
    PrecisionFormat,
    Scenario,
    SizeRequest,
    SizingInput,
    SizingOptions,
    SpeculativeMode,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import ConfigurationError, EngineInputError
from ai_tco_dss.engines.performance import compute_performance, delta_ctx
from ai_tco_dss.engines.resolver import select_benchmark
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.services import size
from ai_tco_dss.settings import load_engine_parameters
from ai_tco_dss.ui.formatting import performance_rows

PARAMS = load_engine_parameters()
MINI = "mac-mini-m5-pro-64gb"
QWEN_27B = "qwen-3-8-27b"
QWEN_A3B = "qwen-3-6-35b-a3b"
DECODE = BenchmarkMetric.DECODE_TPS
PREFILL = BenchmarkMetric.PREFILL_TPS


@pytest.fixture(scope="module")
def repo() -> JsonCatalogRepository:
    return get_default_repository()


def _s(value: Any) -> dict[str, Any]:
    return {"value": value, "source_id": "T", "tier": "assumption", "accessed": "2026-11-07"}


def _with[M: BaseModel](item: M, **changes: Any) -> M:
    return type(item).model_validate({**item.model_dump(), **changes})


def _hw(repo: JsonCatalogRepository, hardware_id: str = MINI) -> HardwareSpec:
    return next(h for h in repo.catalog().hardware if h.id == hardware_id)


def _model(repo: JsonCatalogRepository, model_id: str = QWEN_27B) -> ModelSpec:
    return next(m for m in repo.catalog().models if m.id == model_id)


def _rec(
    metric: BenchmarkMetric = DECODE,
    value: float = 12.3,
    *,
    model_id: str = QWEN_27B,
    hardware_id: str | None = MINI,
    precision: str | None = "INT4",
    context_tokens: int | None = 8_192,
    source_id: str = "REC-1",
    tier: str = "community",
    accessed: str = "2026-11-07",
) -> BenchmarkRecord:
    return BenchmarkRecord.model_validate(
        {
            "metric": metric.value,
            "value": value,
            "model_id": model_id,
            "hardware_id": hardware_id,
            "precision": precision,
            "context_tokens": context_tokens,
            "prompt_tokens": context_tokens,
            "conditions": conditions(),
            "source_id": source_id,
            "tier": tier,
            "accessed": accessed,
        }
    )


def _inp(
    repo: JsonCatalogRepository,
    hardware: HardwareSpec | None = None,
    model: ModelSpec | None = None,
    *,
    records: tuple[BenchmarkRecord, ...] = (),
    use_measured: bool = True,
    precision: PrecisionFormat = PrecisionFormat.INT4,
    profile: WorkloadProfile | None = None,
    **opts: Any,
) -> PerformanceInput:
    hardware = hardware or _hw(repo)
    model = model or _model(repo)
    profile = profile or WorkloadProfile()
    options = SizingOptions(
        weight_precision=precision,
        benchmark_conditions=conditions(),
        performance_prompt_tokens=opts.get("target_context_length", 8192),
        **{"target_context_length": 8_192, **opts},
    )
    harnesses = repo.catalog().harnesses
    workload = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=harnesses), PARAMS
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=precision,
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
        precision=precision,
        sizing=sizing,
        workload=workload,
        profile=profile,
        options=options,
        benchmarks=BenchmarkSet(records=records),
        use_measured=use_measured,
    )


def _formula_decode(bandwidth: float, p_active: float, bits: int, eta: float) -> float:
    return bandwidth / (p_active * bits / 8 * 1.05) * eta


def _perf(inp: PerformanceInput, params: EngineParameters = PARAMS) -> PerformanceResult:
    return compute_performance(inp, params)


# --------------------------------------------------------------------------- resolver (9.3-9.6)


def test_req_9_4_measured_decode_is_used_and_labelled_measured(
    repo: JsonCatalogRepository,
) -> None:
    result = _perf(_inp(repo, records=(_rec(value=12.3, source_id="REC-1"),)))
    assert result.decode_tps is not None
    assert result.decode_tps.value == 12.3
    assert result.decode_tps.origin.origin == "measured"
    assert result.decode_tps.origin.source_ids == ("REC-1",)


def test_req_9_4_context_exactly_at_the_tolerance_matches(repo: JsonCatalogRepository) -> None:
    # |10 240 - 8 192| = 2 048 = 0.25 x 8 192
    result = _perf(_inp(repo, records=(_rec(value=12.3, context_tokens=10_240),)))
    assert result.decode_tps is not None
    assert result.decode_tps.origin.origin == "measured"


def test_req_9_6_record_outside_tolerance_falls_back_to_formula(
    repo: JsonCatalogRepository,
) -> None:
    hardware, model = _hw(repo), _model(repo)
    result = _perf(_inp(repo, records=(_rec(value=12.3, context_tokens=10_241),)))
    assert result.decode_tps is not None
    assert result.decode_tps.origin.origin == "formula"
    expected = _formula_decode(
        hardware.memory_bandwidth_gbs.value, model.active_parameters_billions.value, 4, 0.70
    )
    assert result.decode_tps.value == pytest.approx(expected, rel=1e-9)
    assert result.decode_tps.origin.source_ids == (
        hardware.memory_bandwidth_gbs.source_id,
        model.active_parameters_billions.source_id,
    )


@pytest.mark.parametrize(
    "mismatch",
    [
        {"model_id": QWEN_A3B},
        {"hardware_id": "mac-studio-m5-max-128gb"},
        {"precision": "INT8"},
        {"metric": PREFILL},
    ],
)
def test_req_9_6_record_with_other_key_falls_back_to_formula(
    repo: JsonCatalogRepository, mismatch: dict[str, Any]
) -> None:
    result = _perf(_inp(repo, records=(_rec(**mismatch),)))
    assert result.decode_tps is not None
    assert result.decode_tps.origin.origin == "formula"


def test_req_9_6_use_measured_false_ignores_matching_records(
    repo: JsonCatalogRepository,
) -> None:
    result = _perf(_inp(repo, records=(_rec(value=12.3),), use_measured=False))
    assert result.decode_tps is not None
    assert result.decode_tps.origin.origin == "formula"


def _query(records: tuple[BenchmarkRecord, ...], **changes: Any) -> BenchmarkQuery:
    data: dict[str, Any] = {
        "conditions": conditions(),
        "records": BenchmarkSet(records=records),
        "metric": DECODE,
        "model_id": QWEN_27B,
        "hardware_id": MINI,
        "precision": PrecisionFormat.INT4,
        "target_context": 8_192,
        "tolerance": 0.25,
    }
    return BenchmarkQuery(**{**data, **changes})


def test_req_9_3_selection_order_tier_then_date_then_context_then_source_id() -> None:
    official = _rec(source_id="Z", tier="official", accessed="2026-01-01", context_tokens=9_000)
    newer = _rec(source_id="Y", tier="community", accessed="2026-11-07", context_tokens=9_000)
    older = _rec(source_id="X", tier="community", accessed="2026-10-01", context_tokens=8_192)
    closer = _rec(source_id="W", tier="community", accessed="2026-11-07", context_tokens=8_192)
    same_b = _rec(source_id="B", tier="community", accessed="2026-11-07", context_tokens=8_192)
    assert select_benchmark(_query((newer, official, older))) == official
    assert select_benchmark(_query((older, newer))) == newer
    assert select_benchmark(_query((newer, closer))) == closer
    assert select_benchmark(_query((closer, same_b))) == same_b
    assert select_benchmark(_query(())) is None


def test_req_9_9_quality_record_resolved_without_hardware_precision_or_context() -> None:
    low = _rec(
        BenchmarkMetric.AA_INDEX_V5,
        20.1,
        hardware_id=None,
        precision=None,
        context_tokens=None,
        source_id="IND-01",
        tier="third_party",
    )
    high = _rec(
        BenchmarkMetric.AA_INDEX_V5,
        21.0,
        hardware_id=None,
        precision=None,
        context_tokens=None,
        source_id="VENDOR",
        tier="official",
    )
    query = _query(
        (low, high),
        metric=BenchmarkMetric.AA_INDEX_V5,
        hardware_id=None,
        precision=None,
        target_context=None,
    )
    assert select_benchmark(query) == high


@pytest.mark.parametrize("tolerance", [-0.1, 1.1])
def test_req_9_10_resolver_rejects_tolerance_outside_0_1(tolerance: float) -> None:
    with pytest.raises(ConfigurationError) as exc:
        select_benchmark(_query((_rec(),), tolerance=tolerance))
    assert exc.value.setting == "context_match_tolerance"


# --------------------------------------------------------------------------- decode (20.x)


def test_req_20_2_eta_defaults_dense_0_70_and_moe_0_425(repo: JsonCatalogRepository) -> None:
    hardware = _hw(repo)
    bandwidth = hardware.memory_bandwidth_gbs.value
    dense = _model(repo, QWEN_27B)
    moe = _model(repo, QWEN_A3B)
    for model, eta in ((dense, 0.70), (moe, 0.425)):
        result = _perf(_inp(repo, hardware, model))
        assert result.decode_tps is not None
        p_active = model.active_parameters_billions.value
        assert result.decode_tps.value == pytest.approx(
            _formula_decode(bandwidth, p_active, 4, eta), rel=1e-9
        )
    assert (PARAMS.eta_dense, PARAMS.eta_moe) == (0.70, 0.425)


def test_req_20_3_gamma_defaults_per_mode_and_none_is_the_default(
    repo: JsonCatalogRepository,
) -> None:
    assert SizingOptions().speculative_mode == SpeculativeMode.NONE
    base = _perf(_inp(repo)).decode_tps
    assert base is not None
    expected = {
        SpeculativeMode.NONE: 1.0,
        SpeculativeMode.APPLE_MTP_DFLASH: 1.425,
        SpeculativeMode.BUILTIN_MTP: 1.80,
        SpeculativeMode.EXTERNAL_DRAFT: 2.75,
    }
    for mode, gamma in expected.items():
        decode = _perf(_inp(repo, speculative_mode=mode)).decode_tps
        assert decode is not None
        assert decode.value == pytest.approx(base.value * gamma, rel=1e-9)


def test_req_20_6_delta_ctx_reduces_formula_decode(repo: JsonCatalogRepository) -> None:
    short = _perf(_inp(repo, target_context_length=8_192)).decode_tps
    long = _perf(_inp(repo, target_context_length=262_144)).decode_tps
    assert short is not None and long is not None
    assert long.value == pytest.approx(short.value * 0.50, rel=1e-9)
    assert delta_ctx(16_384, PARAMS.delta_ctx_breakpoints) == pytest.approx(0.945)
    assert delta_ctx(1_000, PARAMS.delta_ctx_breakpoints) == 1.0
    assert delta_ctx(4_000_000, PARAMS.delta_ctx_breakpoints) == 0.40


@pytest.mark.parametrize("bandwidth", [0.0, -1.0])
def test_req_20_7_invalid_bandwidth_rejected(repo: JsonCatalogRepository, bandwidth: float) -> None:
    hardware = _with(_hw(repo), memory_bandwidth_gbs=_s(bandwidth))
    with pytest.raises(EngineInputError) as exc:
        _perf(_inp(repo, hardware))
    assert exc.value.field == "memory_bandwidth_gbs"


@pytest.mark.parametrize("p_active", [None, 0.0, -3.0])
def test_req_20_7_invalid_active_parameters_rejected(
    repo: JsonCatalogRepository, p_active: float | None
) -> None:
    value = None if p_active is None else _s(p_active)
    model = _with(_model(repo), active_parameters_billions=value)
    with pytest.raises(EngineInputError) as exc:
        _perf(_inp(repo, model=model))
    assert exc.value.field == "active_parameters_billions"


def test_req_20_7_invalid_bits_rejected(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo).model_copy(update={"precision": "INT0"})
    with pytest.raises(EngineInputError) as exc:
        _perf(inp)
    assert exc.value.field == "bits"


def test_req_20_7_invalid_speculative_mode_rejected(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo)
    options = inp.options.model_copy(update={"speculative_mode": "turbo"})
    with pytest.raises(EngineInputError) as exc:
        _perf(inp.model_copy(update={"options": options}))
    assert exc.value.field == "speculative_mode"


def test_req_20_7_invalid_input_rejected_even_when_a_record_matches(
    repo: JsonCatalogRepository,
) -> None:
    """A measured record does not hide an invalid formula input of the combination."""
    hardware = _with(_hw(repo), memory_bandwidth_gbs=_s(0.0))
    with pytest.raises(EngineInputError):
        _perf(_inp(repo, hardware, records=(_rec(),)))


# --------------------------------------------------------------------------- prefill, TTFT (21.x)


def test_req_21_1_prefill_falls_back_to_base_prefill_at_32k(repo: JsonCatalogRepository) -> None:
    hardware = _hw(repo)
    base = hardware.base_prefill_tps_at_32k
    assert base is not None
    result = _perf(_inp(repo))
    assert result.prefill_tps is not None
    assert result.prefill_tps.value == base.value
    assert result.prefill_tps.origin.origin == "formula"
    assert result.prefill_tps.origin.source_ids == (base.source_id,)


def test_req_21_1_measured_prefill_record_is_used(repo: JsonCatalogRepository) -> None:
    record = _rec(PREFILL, 999.0, source_id="PF-1")
    result = _perf(_inp(repo, records=(record,)))
    assert result.prefill_tps is not None
    assert result.prefill_tps.value == 999.0
    assert result.prefill_tps.origin.origin == "measured"
    assert result.ttft_s is not None
    assert result.ttft_s.origin.origin == "formula"
    assert result.ttft_s.origin.source_ids == ("PF-1",)


def test_req_21_2_ttft_formula_and_origin(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo)
    result = _perf(inp)
    prefill = inp.hardware.base_prefill_tps_at_32k
    assert prefill is not None and result.ttft_s is not None
    r_cache = inp.profile.prompt_cache_hit_rate
    expected = inp.workload.t_in_hat * (1 - r_cache) / (prefill.value * 1.0)
    assert result.ttft_s.value == pytest.approx(expected, rel=1e-9)
    assert result.ttft_s.origin.origin == "formula"
    assert result.ttft_s.origin.source_ids == (prefill.source_id,)
    slow = _perf(_inp(repo, enable_optimized_backend=False)).ttft_s
    assert slow is not None
    assert slow.value == pytest.approx(expected / 0.035, rel=1e-9)


def test_req_21_3_eviction_adds_cold_re_prefill(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo)
    evicted = inp.model_copy(
        update={"sizing": inp.sizing.model_copy(update={"context_eviction_risk": True})}
    )
    base, penalised = _perf(inp).ttft_s, _perf(evicted).ttft_s
    prefill = inp.hardware.base_prefill_tps_at_32k
    assert base is not None and penalised is not None and prefill is not None
    rebuild = inp.options.target_context_length / prefill.value
    assert penalised.value == pytest.approx(base.value + rebuild, rel=1e-9)


def test_req_21_4_effective_tps_formula(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo)
    result = _perf(inp)
    assert result.ttft_s and result.decode_tps and result.effective_tps
    out = inp.profile.avg_output_tokens * 2.5  # medium thinking, tau = 1 for Qwen
    expected = out / (result.ttft_s.value + out / result.decode_tps.value)
    assert result.effective_tps.value == pytest.approx(expected, rel=1e-9)
    assert result.effective_tps.origin.origin == "formula"
    assert 0 <= result.effective_tps.value <= result.decode_tps.value


def test_req_21_5_one_million_prefill_resolution_order(repo: JsonCatalogRepository) -> None:
    measured = _rec(PREFILL, 400.0, context_tokens=1_000_000, source_id="PF-1M")
    result = _perf(_inp(repo, records=(measured,)))
    assert result.prefill_1m_minutes is not None
    assert result.prefill_1m_minutes.value == pytest.approx(1_000_000 / 400.0 / 60)
    assert result.prefill_1m_minutes.origin.origin == "measured"
    assert result.prefill_1m_minutes.origin.source_ids == ("PF-1M",)

    catalog_1m = {**_s(500.0), "source_id": "HW-1M"}
    hardware = _with(_hw(repo), prefill_tps_at_1m=catalog_1m)
    result = _perf(_inp(repo, hardware))
    assert result.prefill_1m_minutes is not None
    assert result.prefill_1m_minutes.value == pytest.approx(1_000_000 / 500.0 / 60)
    assert result.prefill_1m_minutes.origin.origin == "formula"
    assert result.prefill_1m_minutes.origin.source_ids == ("HW-1M",)
    assert not any("overestimated" in w for w in result.warnings)

    result = _perf(_inp(repo))
    base = _hw(repo).base_prefill_tps_at_32k
    assert base is not None and result.prefill_1m_minutes is not None
    assert result.prefill_1m_minutes.value == pytest.approx(1_000_000 / base.value / 60)
    assert result.prefill_1m_minutes.origin.origin == "formula"
    assert result.prefill_1m_minutes.origin.source_ids == (base.source_id,)
    assert any("overestimated" in w for w in result.warnings)


def test_req_21_7_no_prefill_data_gives_not_available_and_warning(
    repo: JsonCatalogRepository,
) -> None:
    hardware = _with(_hw(repo), base_prefill_tps_at_32k=None, prefill_tps_at_1m=None)
    result = _perf(_inp(repo, hardware))
    assert result.decode_tps is not None
    assert result.prefill_tps is None
    assert result.ttft_s is None
    assert result.effective_tps is None
    assert result.prefill_1m_minutes is None
    assert any(MINI in w and QWEN_27B in w and "prefill" in w for w in result.warnings)


def test_req_21_8_zero_output_gives_zero_effective_tps_and_keeps_ttft(
    repo: JsonCatalogRepository,
) -> None:
    inp = _inp(repo)
    zero = inp.model_copy(update={"workload": inp.workload.model_copy(update={"out_think": 0.0})})
    result = _perf(zero)
    assert result.effective_tps is not None
    assert result.effective_tps.value == 0.0
    assert result.ttft_s is not None
    assert result.ttft_s.value > 0


@pytest.mark.parametrize("r_cache", [-0.01, 1.01])
def test_req_21_9_r_cache_outside_0_1_rejected(repo: JsonCatalogRepository, r_cache: float) -> None:
    inp = _inp(repo)
    profile = inp.profile.model_copy(update={"prompt_cache_hit_rate": r_cache})
    with pytest.raises(EngineInputError) as exc:
        _perf(inp.model_copy(update={"profile": profile}))
    assert exc.value.field == "r_cache"
    assert "[0.0, 1.0]" in exc.value.allowed


def test_req_21_9_r_cache_range_ends_accepted(repo: JsonCatalogRepository) -> None:
    inp = _inp(repo)
    for r_cache in (0.0, 1.0):
        profile = inp.profile.model_copy(update={"prompt_cache_hit_rate": r_cache})
        result = _perf(inp.model_copy(update={"profile": profile}))
        assert result.ttft_s is not None and result.ttft_s.value >= 0


def test_req_9_4_measured_ttft_record_is_used(repo: JsonCatalogRepository) -> None:
    record = _rec(
        BenchmarkMetric.TTFT_S,
        4.2,
        context_tokens=round(_inp(repo).workload.t_in_hat),
        source_id="TT-1",
    )
    result = _perf(_inp(repo, records=(record,)))
    assert result.ttft_s is not None
    assert result.ttft_s.value == 4.2
    assert result.ttft_s.origin.origin == "measured"
    assert result.ttft_s.origin.source_ids == ("TT-1",)


def test_performance_result_has_traces(repo: JsonCatalogRepository) -> None:
    result = _perf(_inp(repo))
    names = {trace.name for trace in result.traces}
    assert {"decode_tps", "prefill_tps", "ttft_s", "effective_tps", "prefill_1m_minutes"} <= names


# --------------------------------------------------------------------------- `size` service


def _request(hardware_id: str, model_id: str, **sizing: Any) -> SizeRequest:
    scenario = Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(**{"target_context_length": 8_192, **sizing}),
        decision=DecisionOptions(),
    )
    return SizeRequest(
        scenario=scenario,
        hardware_id=hardware_id,
        model_id=model_id,
        precision=PrecisionFormat.INT4,
    )


def test_req_9_4_size_excludes_incomplete_catalog_decode_record(
    repo: JsonCatalogRepository,
) -> None:
    """Task 6 demo: Mac mini M5 Pro + Qwen 3.8-27B INT4 at 8 192 tokens."""
    records = [
        r
        for r in repo.catalog().benchmarks
        if r.metric == DECODE
        and (r.model_id, r.hardware_id, r.precision) == (QWEN_27B, MINI, PrecisionFormat.INT4)
    ]
    assert len(records) == 1
    record = records[0]
    result = size(_request(MINI, QWEN_27B), repo=repo)
    assert result.performance is not None
    decode = result.performance.decode_tps
    assert decode is not None
    assert decode.value != record.value
    assert decode.origin.origin == "formula"
    assert any(record.source_id in w and "excluded" in w for w in result.performance.warnings)
    for metric in (result.performance.ttft_s, result.performance.effective_tps):
        assert metric is not None
        assert metric.origin.origin == "formula"


def test_req_9_9_size_returns_the_aa_v5_score(repo: JsonCatalogRepository) -> None:
    result = size(_request(MINI, QWEN_27B), repo=repo)
    assert result.aa_index_v5 is not None
    assert result.aa_index_v5.value == 20.1
    assert result.aa_index_v5.benchmark == BenchmarkMetric.AA_INDEX_V5
    assert result.aa_index_v5.origin.origin == "measured"
    assert result.aa_index_v5.origin.source_ids == ("IND-01",)


def test_req_21_1_size_gives_no_performance_for_infeasible_pairings(
    repo: JsonCatalogRepository,
) -> None:
    result = size(_request("mac-studio-m5-max-128gb", "qwen-3-8-flash-next"), repo=repo)
    assert result.sizing.is_feasible is False
    assert result.performance is None


def test_req_9_7_size_performance_sources_exist_in_the_registry(
    repo: JsonCatalogRepository,
) -> None:
    registry = {s.source_id for s in repo.catalog().sources}
    result = size(_request(MINI, QWEN_A3B), repo=repo)
    assert result.performance is not None
    performance = result.performance
    for metric in (
        performance.decode_tps,
        performance.prefill_tps,
        performance.ttft_s,
        performance.effective_tps,
        performance.prefill_1m_minutes,
    ):
        assert metric is not None
        assert metric.origin.source_ids
        assert set(metric.origin.source_ids) <= registry


def test_req_21_1_view_1_performance_rows_show_values_and_origins(
    repo: JsonCatalogRepository,
) -> None:
    result = size(_request(MINI, QWEN_27B), repo=repo)
    assert result.performance is not None
    rows = performance_rows(result.performance)
    assert rows["Metric"] == [
        "Decode TPS",
        "Prefill TPS",
        "TTFT",
        "Effective TPS",
        "1M-token prefill",
    ]
    assert rows["Value"][0] == "15.2 tok/s"
    assert rows["Origin"][0].startswith("formula (")
    assert rows["Origin"][2].startswith("formula (")
    assert rows["Origin"][3].startswith("formula (")
