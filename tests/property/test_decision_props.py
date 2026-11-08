"""SAW invariants: Req 29.5-10/12-13, missing values and deterministic ties."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.decision import rank_candidates
from ai_tco_dss.domain import Criterion, CriterionWeights, RankingInput, RankingMethod, TcoRequest
from ai_tco_dss.services import project_tco
from ai_tco_dss.settings import load_engine_parameters


@pytest.fixture(scope="module")
def base():
    return project_tco(
        TcoRequest(
            scenario=default_scenario(),
            candidate_id="onprem:rtx-pro-6000-96gb:4x:deepseek-v4-1-flash:INT4",
        )
    ).candidate


@given(st.lists(st.integers(1, 100), min_size=6, max_size=6), st.integers(0, 1000000))
def test_saw_dominance_composition_normalization_and_determinism(base, weights, cost):
    params = load_engine_parameters()
    superior = base.model_copy(
        update={"candidate_id": "superior", "cost_60m": cost, "risk": 0.1, "popularity": 100}
    )
    inferior = base.model_copy(
        update={"candidate_id": "inferior", "cost_60m": cost + 1, "risk": 0.2, "popularity": 99}
    )
    weights = CriterionWeights(**dict(zip((c.value for c in Criterion), weights, strict=True)))
    inp = RankingInput(feasible=(inferior, superior), weights=weights, method=RankingMethod.SAW)
    result = rank_candidates(inp, params)
    assert result == rank_candidates(inp, params)
    assert result.ranked[0].evaluation.candidate_id == "superior"
    assert result.ranked[0].saw_score > result.ranked[1].saw_score
    for row in result.ranked:
        assert 0 <= row.saw_score <= 1.0 + 1e-15
        assert sum(c.contribution for c in row.criteria) == pytest.approx(row.saw_score, abs=1e-9)
        assert all(0 <= c.normalised <= 1 for c in row.criteria)


@given(st.integers(0, 1000000))
def test_singleton_constant_and_all_missing_columns(base, cost):
    c = base.model_copy(update={"cost_60m": cost, "performance": None})
    result = rank_candidates(
        RankingInput(
            feasible=(c,),
            weights=CriterionWeights(**dict.fromkeys((c.value for c in Criterion), 1)),
            method=RankingMethod.SAW,
        ),
        load_engine_parameters(),
    )
    for value in result.ranked[0].criteria:
        assert value.normalised == (0.0 if value.missing else 1.0)
