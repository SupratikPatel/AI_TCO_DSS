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


@given(
    st.lists(st.lists(st.integers(0, 1000000), min_size=6, max_size=6), min_size=1, max_size=8),
    st.lists(st.integers(1, 100), min_size=6, max_size=6),
)
def test_property_50_req_30_2_3_6_7_8_numpy_reference(base, matrix, weights):
    """Property 50: Requirements 30.2, 30.3, 30.6, 30.7, 30.8."""
    import numpy as np

    candidates = []
    raw = []
    for i, (cost, quality, speed, ttft, risk, pop) in enumerate(matrix):
        c = base.model_copy(
            update={
                "candidate_id": str(i),
                "cost_60m": cost,
                "risk": risk / 1000000,
                "popularity": pop,
                "quality": base.quality.model_copy(update={"value": quality / 10000}),
                "performance": base.performance.model_copy(
                    update={
                        "effective_tps": base.performance.effective_tps.model_copy(
                            update={"value": speed}
                        ),
                        "ttft_s": base.performance.ttft_s.model_copy(update={"value": ttft}),
                    }
                ),
            }
        )
        candidates.append(c)
        raw.append([cost, quality / 10000, speed, ttft, risk / 1000000, pop])
    x = np.array(raw, dtype=float)
    norms = np.linalg.norm(x, axis=0)
    weighted = (
        np.divide(x, norms, out=np.zeros_like(x), where=norms != 0)
        * np.array(weights)
        / sum(weights)
    )
    ideal, anti = weighted.max(axis=0), weighted.min(axis=0)
    ideal[[0, 3, 4]], anti[[0, 3, 4]] = anti[[0, 3, 4]].copy(), ideal[[0, 3, 4]].copy()
    plus, minus = np.linalg.norm(weighted - ideal, axis=1), np.linalg.norm(weighted - anti, axis=1)
    closeness = np.divide(minus, plus + minus, out=np.ones_like(minus), where=plus + minus != 0)
    result = rank_candidates(
        RankingInput(
            feasible=tuple(candidates),
            method=RankingMethod.TOPSIS,
            weights=CriterionWeights(
                **dict(zip((c.value for c in Criterion), weights, strict=True))
            ),
        ),
        load_engine_parameters(),
    )
    assert len(result.ranked) == len(matrix)
    for row in result.ranked:
        i = int(row.evaluation.candidate_id)
        assert (row.d_plus, row.d_minus, row.topsis_closeness) == pytest.approx(
            (plus[i], minus[i], closeness[i]), abs=1e-9
        )
        assert 0 <= row.topsis_closeness <= 1
    assert result == rank_candidates(
        RankingInput(
            feasible=tuple(candidates),
            method=RankingMethod.TOPSIS,
            weights=CriterionWeights(
                **dict(zip((c.value for c in Criterion), weights, strict=True))
            ),
        ),
        load_engine_parameters(),
    )


@given(st.lists(st.integers(1, 100), min_size=6, max_size=6), st.integers(1, 1000000))
def test_property_51_req_30_5_dominance(base, weights, cost):
    """Property 51: Requirements 30.5."""
    better = base.model_copy(
        update={"candidate_id": "better", "cost_60m": cost, "risk": 0.1, "popularity": 100}
    )
    worse = base.model_copy(
        update={"candidate_id": "worse", "cost_60m": cost + 1, "risk": 0.2, "popularity": 99}
    )
    result = rank_candidates(
        RankingInput(
            feasible=(worse, better),
            method=RankingMethod.TOPSIS,
            weights=CriterionWeights(
                **dict(zip((c.value for c in Criterion), weights, strict=True))
            ),
        ),
        load_engine_parameters(),
    )
    assert len(result.ranked) == 2
    assert result.ranked[0].evaluation == better
    assert result.ranked[0].topsis_closeness >= result.ranked[1].topsis_closeness
