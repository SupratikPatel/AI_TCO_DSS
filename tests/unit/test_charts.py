"""View 1 memory-fit chart (Req 35.1, 35.2, 35.3, 35.8, 35.9, 35.11, 37.1)."""

import ast
from pathlib import Path
from typing import Any

import pytest

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

CHARTS = Path(__file__).resolve().parents[2] / "src" / "ai_tco_dss" / "ui" / "charts.py"
SEGMENTS = ("weights", "kv_cache_active", "agent_state_parked", "os_reserved", "runtime_overhead")
DISPLAY = DisplaySettings(currency="USD", fx_rate=1.1165)
FORBIDDEN_MODULES = {"streamlit", "os", "pathlib", "io", "socket", "urllib", "http", "requests"}


def _size(hardware_id: str, model_id: str) -> SizeResult:
    scenario = Scenario(
        workload=WorkloadProfile(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(target_context_length=8_192),
        decision=DecisionOptions(),
    )
    return size(
        SizeRequest(
            scenario=scenario,
            hardware_id=hardware_id,
            model_id=model_id,
            precision=PrecisionFormat.INT4,
        )
    )


@pytest.fixture(scope="module")
def pairings() -> SizePairings:
    mac = _size("mac-studio-m5-max-128gb", "qwen-3-8-flash-next")
    strata = _size("rtx-5070-strata-64gb", "qwen-3-8-27b")
    strata = strata.model_copy(
        update={
            "sizing": strata.sizing.model_copy(update={"context_eviction_risk": True}),
            "aa_index_v5": QualityScore(
                value=20.149,
                benchmark=BenchmarkMetric.AA_INDEX_V5,
                origin=ValueOrigin(origin="measured", source_ids=("IND-01",)),
                fallback_note=None,
            ),
        }
    )
    return SizePairings(items=(mac, strata))


def _bars(fig: Any) -> list[Any]:
    return [trace for trace in fig.data if trace.type == "bar"]


def _shapes(fig: Any, prefix: str) -> list[Any]:
    return [s for s in fig.layout.shapes if (s.name or "").startswith(prefix)]


def test_req_35_1_segments_in_fixed_order(pairings: SizePairings) -> None:
    fig = memory_fit_figure(pairings, DISPLAY)
    bars = _bars(fig)
    assert tuple(b.name for b in bars) == SEGMENTS
    assert fig.layout.barmode == "stack"
    for bar in bars:
        assert bar.orientation == "h"
        assert len(bar.x) == len(pairings.items)
    for index, item in enumerate(pairings.items):
        breakdown = dict(item.sizing.memory_breakdown)
        for bar in bars:
            assert bar.x[index] == pytest.approx(breakdown[bar.name], abs=0.01)
    assert fig.layout.xaxis.title.text == "GB"


def test_req_35_1_threshold_lines(pairings: SizePairings) -> None:
    fig = memory_fit_figure(pairings, DISPLAY)
    vram = _shapes(fig, "usable_vram")
    system = _shapes(fig, "usable_system_ram")
    assert [s.x0 for s in vram] == [i.sizing.usable_memory_gb for i in pairings.items]
    for shape in vram + system:
        assert shape.x0 == shape.x1  # vertical
    # Only the Strata appliance reports a separate system RAM value.
    assert [s.x0 for s in system] == [64.0]


def test_req_35_2_35_9_labels_with_scores_or_na(pairings: SizePairings) -> None:
    fig = memory_fit_figure(pairings, DISPLAY)
    labels = list(_bars(fig)[0].y)
    assert len(labels) == 2
    assert "AA v5 n/a" in labels[0] and "97.8%" in labels[0]
    assert "AA v5 20.1" in labels[1]
    strata_rate = pairings.items[1].sizing.token_agreement_rate
    expected = "n/a" if strata_rate is None else f"{strata_rate:.1%}"
    assert f"agreement {expected}" in labels[1]


def test_req_35_3_eviction_hatch_and_badge(pairings: SizePairings) -> None:
    fig = memory_fit_figure(pairings, DISPLAY)
    for bar in _bars(fig):
        assert tuple(bar.marker.pattern.shape) == ("", theme.EVICTION_HATCH)
    badges = [a for a in fig.layout.annotations if a.text == "EVICTION RISK"]
    assert len(badges) == 1
    assert badges[0].y == list(_bars(fig)[0].y)[1]


def test_req_37_1_only_okabe_ito_colours(pairings: SizePairings) -> None:
    fig = memory_fit_figure(pairings, DISPLAY)
    for bar in _bars(fig):
        assert bar.marker.color in theme.OKABE_ITO
        assert bar.marker.pattern.fgcolor in theme.OKABE_ITO
    assert len({b.marker.color for b in _bars(fig)}) == len(SEGMENTS)


def test_req_37_1_theme_constants() -> None:
    assert theme.OKABE_ITO == (
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
        "#000000",
    )


def test_req_35_8_equal_input_gives_equal_figure(pairings: SizePairings) -> None:
    assert memory_fit_figure(pairings, DISPLAY) == memory_fit_figure(pairings, DISPLAY)


def test_req_35_11_empty_input_returns_annotated_empty_figure() -> None:
    fig = memory_fit_figure(SizePairings(items=()), DISPLAY)
    assert len(fig.data) == 0
    assert [a.text for a in fig.layout.annotations] == ["No data available"]


def test_req_35_8_charts_module_has_no_io_or_streamlit() -> None:
    tree = ast.parse(CHARTS.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "charts.py must not open files"
    assert not imported & FORBIDDEN_MODULES
