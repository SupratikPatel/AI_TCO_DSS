"""Real MVP workloads: Req 38.5, 39.4-39.7. No network or mocked engines."""

from concurrent.futures import ThreadPoolExecutor
from statistics import median
from threading import Barrier
from time import perf_counter

from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app, default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import RecommendRequest, Scenario, ScenarioRequest
from ai_tco_dss.services import evaluate_scenario, recommend


def scenarios():
    base = default_scenario().model_dump(mode="json")
    for i in range(10):
        body = {**base, "workload": {**base["workload"], "active_users": float(i + 1)}}
        body["fx_override"] = round(1.0 + i / 100, 2)
        yield Scenario.model_validate(body)


def test_req_39_4_5_6_ten_concurrent_scenarios_equal_sequential():
    repo = get_default_repository()
    before = repo.catalog().model_dump_json()
    requests = [ScenarioRequest(scenario=s) for s in scenarios()]
    sequential = [evaluate_scenario(r) for r in requests]
    barrier = Barrier(10)

    def evaluate(request):
        barrier.wait(timeout=30)
        return evaluate_scenario(request)

    with ThreadPoolExecutor(max_workers=10) as pool:
        assert list(pool.map(evaluate, requests)) == sequential
    assert repo.catalog().model_dump_json() == before


def test_req_38_5_43_8_concurrent_api_clients_match_service():
    requests = [ScenarioRequest(scenario=s) for s in scenarios()]
    expected = [evaluate_scenario(r).model_dump(mode="json") for r in requests]
    barrier = Barrier(10)

    def call(request):
        with TestClient(app) as client:
            barrier.wait(timeout=30)
            response = client.post("/api/v1/evaluate", json=request.model_dump(mode="json"))
            assert response.status_code == 200
            return response.json()

    with ThreadPoolExecutor(max_workers=10) as pool:
        assert list(pool.map(call, requests)) == expected


def test_req_39_7_warm_recommend_median_below_500ms():
    request = RecommendRequest(scenario=default_scenario())
    recommend(request)
    times = []
    for _ in range(5):
        start = perf_counter()
        result = recommend(request)
        times.append(perf_counter() - start)
        assert len(result.ranked) == 35 and len(result.rejected) == 638
    assert median(times) < 0.5, times
