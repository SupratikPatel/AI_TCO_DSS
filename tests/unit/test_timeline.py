"""Rental, hybrid and timeline acceptance tests (Requirements 25, 26)."""

import pytest

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    DecisionOptions,
    EnterpriseFinancials,
    HybridCostInput,
    RentalCostInput,
    Scenario,
    SizingOptions,
    TcoRequest,
)
from ai_tco_dss.domain.errors import EngineInputError
from ai_tco_dss.engines.baselines import compute_hybrid_cost, compute_rental_cost
from ai_tco_dss.services import load_workload, project_tco
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
ID = "onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT4"


def projection(resale=False, ratio=0.7):
    return project_tco(
        TcoRequest(
            candidate_id=ID,
            scenario=Scenario(
                workload=load_workload(),
                sizing=SizingOptions(),
                decision=DecisionOptions(),
                financials=EnterpriseFinancials(
                    include_resale_value=resale, local_offload_ratio=ratio
                ),
            ),
        )
    )


@pytest.mark.parametrize("ratio", [-0.1, 1.1, float("nan"), float("inf"), "bad"])
def test_req_25_6_invalid_ratio(ratio):
    local = projection().candidate.tco
    inp = HybridCostInput.model_construct(
        local=local, api_c_monthly_usd=100, local_offload_ratio=ratio
    )
    with pytest.raises(EngineInputError, match="local_offload_ratio"):
        compute_hybrid_cost(inp, PARAMS)


def test_req_25_1_25_7_rental_usd_setup_once():
    rental = get_default_repository().catalog().rentals[0]
    result = compute_rental_cost(RentalCostInput(rental=rental, personnel_monthly_usd=123), PARAMS)
    assert result.cost_60m == pytest.approx(
        rental.setup_fee.value + 60 * (rental.monthly_price.value + 123)
    )
    assert result.origin.origin == "formula"
    assert rental.monthly_price.source_id in result.origin.source_ids


@pytest.mark.parametrize("resale", [False, True])
@pytest.mark.parametrize("ratio", [0.0, 0.7, 1.0])
def test_req_25_2_to_5_26_1_to_7_timeline(resale, ratio):
    result = projection(resale, ratio)
    timeline, local = result.timeline, result.candidate.tco
    assert timeline is not None and local is not None
    assert timeline.anchor_candidate_id == ID
    assert len(timeline.points) == 60
    assert timeline.include_resale == resale
    for m, point in enumerate(timeline.points, 1):
        assert point.month == m
        residual = (
            local.capex.value * max(0, 1 - (1 - local.resale_retention_3yr) * m / 36)
            if resale
            else 0
        )
        assert point.on_prem_cumulative == pytest.approx(
            local.capex.value + m * local.monthly_opex_total - residual
        )
        assert point.hybrid_split_cumulative == pytest.approx(
            point.on_prem_cumulative + m * (1 - ratio) * result.baselines.c_monthly.value
        )
        for key, metric in [
            ("a_subscription", result.baselines.a_monthly),
            ("b_global_api", result.baselines.b_monthly),
            ("c_eu_sovereign_api", result.baselines.c_monthly),
        ]:
            assert getattr(point, f"baseline_{key}_cumulative") == pytest.approx(m * metric.value)
    for field, month in timeline.break_even_months:
        expected = next(
            (
                p.month
                for p in timeline.points
                if getattr(p, field) is not None and p.on_prem_cumulative <= getattr(p, field)
            ),
            None,
        )
        assert month == expected
    if not resale:
        for first, second in zip(timeline.points, timeline.points[1:], strict=False):
            for field in type(first).model_fields:
                if getattr(first, field) is not None:
                    assert getattr(second, field) >= getattr(first, field)


def test_req_26_4_26_8_single_stream():
    result = projection()
    assert result.timeline is not None
    assert not result.timeline.include_resale
    price = next(
        m for m in get_default_repository().catalog().models if m.id == "gpt-oss-120b"
    ).open_weights_output_price_per_1m
    speed = result.candidate.performance.decode_tps
    expected = result.candidate.capex / (speed.value * 3600 * 8760 * price.value / 1e6)
    assert result.timeline.single_stream_break_even_years.value == pytest.approx(expected)
    assert result.timeline.single_stream_break_even_years.origin.origin == "formula"
