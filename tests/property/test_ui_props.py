"""Property tests for the Dashboard chart factories (Property 54)."""

from functools import cache

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ai_tco_dss.domain import (
    BenchmarkMetric,
    DecisionOptions,
    DisplaySettings,
    EnterpriseFinancials,
    PrecisionFormat,
    QualityScore,
    Scenario,
    SizePairings,
    SizeRequest,
    SizeResult,
    SizingOptions,
    ValueOrigin,
    WorkloadProfile,
)
from ai_tco_dss.services import size
from ai_tco_dss.ui import theme
from ai_tco_dss.ui.charts import memory_fit_figure

SEGMENTS = ("weights", "kv_cache_active", "agent_state_parked", "os_reserved", "runtime_overhead")
DISPLAY = DisplaySettings(currency="USD", fx_rate=1.1165)
GB = st.floats(min_value=0.0, max_value=4096.0, allow_nan=False)


@given(
    utilization=st.floats(min_value=0, max_value=2, allow_nan=False),
    currency=st.sampled_from(["USD", "EUR"]),
)
def test_property_55_timeline_styles_and_threshold(utilization, currency):
    """Req 35.4-8/10, 37.1/3: all series and the exact 70% boundary."""
    from ai_tco_dss.domain import TcoRequest
    from ai_tco_dss.services import project_tco
    from ai_tco_dss.ui.charts import tco_timeline_figure

    scenario = Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(),
        decision=DecisionOptions(),
    )
    result = project_tco(
        TcoRequest(scenario=scenario, candidate_id="onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT4")
    )
    result = result.model_copy(
        update={"candidate": result.candidate.model_copy(update={"utilization": utilization})}
    )
    fig = tco_timeline_figure(result, DisplaySettings(currency=currency, fx_rate=1.1165))
    lines = [t for t in fig.data if len(t.x) == 60]
    assert len(lines) == 7
    assert all(t.line.color in theme.OKABE_ITO for t in lines)
    assert any("Danger Zone" in a.text for a in fig.layout.annotations) == (utilization < 0.70)
    assert all(list(t.x) == list(range(1, 61)) for t in lines)
    assert currency in fig.layout.yaxis.title.text


@cache
def _template() -> SizeResult:
    scenario = Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(target_context_length=8_192),
        decision=DecisionOptions(),
    )
    return size(
        SizeRequest(
            scenario=scenario,
            hardware_id="mac-studio-m5-max-128gb",
            model_id="qwen-3-8-flash-next",
            precision=PrecisionFormat.INT4,
        )
    )


@st.composite
def size_results(draw: st.DrawFn) -> SizeResult:
    template = _template()
    aa = draw(st.none() | st.floats(min_value=0.0, max_value=100.0))
    sizing = template.sizing.model_copy(
        update={
            "hardware_id": draw(st.sampled_from(["hw-a", "hw-b", "hw-c"])),
            "model_id": draw(st.sampled_from(["model-a", "model-b"])),
            "usable_memory_gb": round(draw(GB), 2),
            "usable_system_ram_gb": draw(st.none() | GB),
            "context_eviction_risk": draw(st.booleans()),
            "token_agreement_rate": draw(st.none() | st.floats(min_value=0.0, max_value=1.0)),
            "memory_breakdown": tuple((key, draw(GB)) for key in SEGMENTS),
        }
    )
    quality = None
    if aa is not None:
        quality = QualityScore(
            value=aa,
            benchmark=BenchmarkMetric.AA_INDEX_V5,
            origin=ValueOrigin(origin="measured", source_ids=("IND-01",)),
            fallback_note=None,
        )
    return template.model_copy(update={"sizing": sizing, "aa_index_v5": quality})


# Feature: ai-tco-dss-mvp, Property 54: View 1 chart structure
@settings(suppress_health_check=[HealthCheck.too_slow])
@given(items=st.lists(size_results(), min_size=0, max_size=5))
def test_property_54_view_1_chart_structure(items: list[SizeResult]) -> None:
    """Property 54 (Req 35.1, 35.2, 35.3, 35.8, 35.9, 37.1): View 1 chart structure."""
    pairings = SizePairings(items=tuple(items))
    fig = memory_fit_figure(pairings, DISPLAY)
    assert fig == memory_fit_figure(pairings, DISPLAY)
    if not items:
        assert len(fig.data) == 0
        assert [a.text for a in fig.layout.annotations] == ["No data available"]
        return

    bars = [t for t in fig.data if t.type == "bar"]
    assert tuple(b.name for b in bars) == SEGMENTS
    labels = list(bars[0].y)
    assert len(labels) == len(set(labels)) == len(items)
    for bar in bars:
        assert list(bar.y) == labels
        assert bar.marker.color in theme.OKABE_ITO
        assert bar.marker.pattern.fgcolor in theme.OKABE_ITO
    for trace in fig.data:
        assert trace.type == "bar"

    badges = [a.y for a in fig.layout.annotations if a.text == "EVICTION RISK"]
    vram = [s for s in fig.layout.shapes if (s.name or "").startswith("usable_vram")]
    system = [s for s in fig.layout.shapes if (s.name or "").startswith("usable_system_ram")]
    assert len(vram) == len(items)
    assert len(system) == sum(i.sizing.usable_system_ram_gb is not None for i in items)

    for index, item in enumerate(items):
        breakdown = dict(item.sizing.memory_breakdown)
        for bar in bars:
            assert bar.x[index] == pytest.approx(breakdown[bar.name], abs=0.01)
        risk = item.sizing.context_eviction_risk
        shapes = {bar.marker.pattern.shape[index] for bar in bars}
        assert shapes == ({theme.EVICTION_HATCH} if risk else {""})
        assert (labels[index] in badges) is risk
        aa = "n/a" if item.aa_index_v5 is None else f"{item.aa_index_v5.value:.1f}"
        rate = item.sizing.token_agreement_rate
        agreement = "n/a" if rate is None else f"{rate * 100:.1f}%"
        assert f"AA v5 {aa}" in labels[index]
        assert f"agreement {agreement}" in labels[index]
        assert vram[index].x0 == item.sizing.usable_memory_gb
