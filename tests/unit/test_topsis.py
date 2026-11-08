"""Task 10: Req 30.2-8, 12.4/8, 43.5; independent TOPSIS oracle."""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app, default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.decision import rank_candidates
from ai_tco_dss.domain import (
    Criterion,
    CriterionWeights,
    RankingInput,
    RecommendRequest,
    ScenarioRequest,
)
from ai_tco_dss.services import evaluate_scenario, recommend
from ai_tco_dss.settings import load_engine_parameters


@pytest.fixture(scope="module")
def base():
    return recommend(RecommendRequest(scenario=default_scenario())).ranked[0].evaluation


def ranking(candidates, weights=(1, 1, 1, 1, 1, 1), method="topsis"):
    return rank_candidates(
        RankingInput(
            feasible=tuple(candidates),
            weights=CriterionWeights(
                **dict(zip((c.value for c in Criterion), weights, strict=True))
            ),
            method=method,
        ),
        load_engine_parameters(),
    )


def oracle(raw, weights):
    x = np.array(raw, dtype=float)
    for j in range(6):
        present = x[~np.isnan(x[:, j]), j]
        worst = (max(present) if j in (0, 3, 4) else min(present)) if len(present) else 0
        x[np.isnan(x[:, j]), j] = worst
    norms = np.linalg.norm(x, axis=0)
    v = np.divide(x, norms, out=np.zeros_like(x), where=norms != 0)
    v *= np.array(weights) / sum(weights)
    ideal, anti = v.max(axis=0), v.min(axis=0)
    for j in (0, 3, 4):
        ideal[j], anti[j] = anti[j], ideal[j]
    plus = np.linalg.norm(v - ideal, axis=1)
    minus = np.linalg.norm(v - anti, axis=1)
    close = np.divide(minus, plus + minus, out=np.ones_like(minus), where=plus + minus != 0)
    return plus, minus, close


def test_req_30_reference_distances_missing_values_and_paired_ranks(base):
    candidates = [
        base.model_copy(
            update={
                "candidate_id": str(i),
                "cost_60m": cost,
                "risk": risk,
                "popularity": pop,
                "performance": None if i == 1 else base.performance,
            }
        )
        for i, (cost, risk, pop) in enumerate(((100, 0.8, 0), (200, 0.2, 9), (300, 0.1, 3)))
    ]
    raw = [
        [
            c.cost_60m,
            c.quality.value,
            c.performance.effective_tps.value if c.performance else None,
            c.performance.ttft_s.value if c.performance else None,
            c.risk,
            c.popularity,
        ]
        for c in candidates
    ]
    weights = (5, 2, 3, 4, 1, 0)
    plus, minus, close = oracle(raw, weights)
    result = ranking(candidates, weights)
    assert result.ranking_error is None
    saw = ranking(candidates, weights, "saw")
    saw_ranks = {r.evaluation.candidate_id: r.rank for r in saw.ranked}
    for r in result.ranked:
        i = int(r.evaluation.candidate_id)
        assert (r.d_plus, r.d_minus, r.topsis_closeness) == pytest.approx(
            (plus[i], minus[i], close[i]), abs=1e-9
        )
        assert r.topsis_rank == r.rank
        assert r.saw_rank == saw_ranks[str(i)]
        assert r.criteria == next(
            s.criteria for s in saw.ranked if s.evaluation.candidate_id == str(i)
        )
    assert result == ranking(candidates, weights)
    assert "TOPSIS" in result.explanation


@pytest.mark.parametrize("count", [0, 1, 3])
def test_req_30_6_7_zero_norm_singleton_identical_and_ties(base, count):
    candidates = [
        base.model_copy(
            update={
                "candidate_id": str(i),
                "cost_60m": 0,
                "risk": 0,
                "popularity": 0,
                "performance": None,
                "quality": None,
            }
        )
        for i in reversed(range(count))
    ]
    result = ranking(candidates)
    assert result.ranking_error is None
    assert [r.evaluation.candidate_id for r in result.ranked] == [str(i) for i in range(count)]
    assert all(r.topsis_closeness == 1 and r.d_plus == r.d_minus == 0 for r in result.ranked)


def test_req_30_8_tie_break_by_cost_then_id_and_invalid_weights(base):
    candidates = [
        base.model_copy(update={"candidate_id": id, "cost_60m": cost})
        for id, cost in (("z", 20), ("b", 10), ("a", 10))
    ]
    assert [r.evaluation.candidate_id for r in ranking(candidates, (0, 1, 0, 0, 0, 0)).ranked] == [
        "a",
        "b",
        "z",
    ]
    for weights in ((0,) * 6, (-1, 1, 1, 1, 1, 1)):
        assert ranking(candidates, weights).ranking_error


def test_req_12_4_8_30_2_43_5_api_parity_and_fx_isolation():
    client = TestClient(app)
    original = get_default_repository().catalog()
    scenario = default_scenario().model_dump(mode="json")
    normal = recommend(RecommendRequest.model_validate({"scenario": scenario}))
    scenario["decision"]["method"] = "topsis"
    for fx in (None, 0.5, 1.234567, 2):
        scenario["fx_override"] = fx
        body = {"scenario": scenario}
        for route, service, contract in (
            ("recommend", recommend, RecommendRequest),
            ("evaluate", evaluate_scenario, ScenarioRequest),
        ):
            response = client.post(f"/api/v1/{route}", json=body)
            assert response.status_code == 200
            assert response.json() == service(contract.model_validate(body)).model_dump(mode="json")
        result = response.json()
        assert result["fx_is_override"] == (fx is not None)
        assert result["baselines"]["currency"] == "USD"
        if fx is None:
            assert {
                r["evaluation"]["candidate_id"] for r in result["recommendation"]["ranked"]
            } == {r.evaluation.candidate_id for r in normal.ranked}
            assert result["recommendation"]["rejected"] == [
                r.model_dump(mode="json") for r in normal.rejected
            ]
    assert get_default_repository().catalog() is original
    for fx in ("bad", 0.49, 2.01, 1.1234567):
        scenario["fx_override"] = fx
        response = client.post("/api/v1/evaluate", json={"scenario": scenario})
        assert response.status_code == 422
        assert any("fx_override" in field for field in response.json()["fields"])


def test_expert_options_return_catalog_preset_weights():
    options = TestClient(app).get("/api/v1/options").json()
    assert options["preset_weights"] == [
        [p.id, p.weights.model_dump(mode="json")]
        for p in get_default_repository().catalog().presets
    ]


def test_fx_override_changes_eur_inputs_but_preserves_native_usd_and_default_results():
    scenario = default_scenario()
    before = evaluate_scenario(ScenarioRequest(scenario=scenario))
    override = scenario.model_copy(update={"fx_override": 1.2})
    after = evaluate_scenario(ScenarioRequest(scenario=override))
    repo = get_default_repository()
    original, changed = repo.catalog(), repo.catalog(1.2)
    assert changed.fx_active_rate == 1.2
    for source, converted in zip(original.rentals, changed.rentals, strict=True):
        if source.monthly_price.original_value is not None:
            assert converted.monthly_price.value == pytest.approx(
                source.monthly_price.original_value * 1.2
            )
        else:
            assert converted.monthly_price.value == source.monthly_price.value
    assert before != after
    assert before == evaluate_scenario(ScenarioRequest(scenario=scenario))
    assert before.fx_rate == original.fx_active_rate
    assert after.fx_rate == 1.2 and after.fx_is_override
