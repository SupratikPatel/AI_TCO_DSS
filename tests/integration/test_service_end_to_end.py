"""Req 38/41: real catalog, all use cases/presets, repository swap and API parity."""

from itertools import product

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ai_tco_dss.api.app import app, default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.catalog.memory_repository import InMemoryCatalogRepository
from ai_tco_dss.domain import PresetId, RecommendRequest, ScenarioRequest, TcoRequest, UseCaseId
from ai_tco_dss.services import evaluate_scenario, project_tco, recommend


@pytest.mark.parametrize("use_case,preset", tuple(product(UseCaseId, PresetId)))
def test_req_38_1_4_5_41_6_7_all_normal_combinations(use_case, preset):
    repo = get_default_repository()
    catalog = repo.catalog()
    memory = InMemoryCatalogRepository(catalog, repo.load_workload())
    scenario = default_scenario()
    scenario = scenario.model_copy(
        update={
            "decision": scenario.decision.model_copy(
                update={"use_case": use_case, "preset": preset}
            )
        }
    )
    request = RecommendRequest(scenario=scenario)
    result = recommend(request, repo=repo)
    assert result == recommend(request, repo=memory)
    assert result.ranked
    assert len(result.ranked) + len(result.rejected) > 400
    ids = {s.source_id for s in catalog.sources}
    for row in result.ranked:
        c = row.evaluation
        assert not c.failures
        assert set(c.price_origin.source_ids) <= ids
        assert c.quality and set(c.quality.origin.source_ids) <= ids
    full = evaluate_scenario(ScenarioRequest(scenario=scenario), repo=memory)
    assert full.recommendation == result
    assert full == type(full).model_validate_json(full.model_dump_json())
    assert full.baselines.currency == "USD"
    assert full.timeline is None or len(full.timeline.points) == 60


def test_req_38_default_api_service_parity_validation():
    client = TestClient(app)
    body = {"scenario": default_scenario().model_dump(mode="json")}
    for route, service, contract in [
        ("recommend", recommend, RecommendRequest),
        ("evaluate", evaluate_scenario, ScenarioRequest),
    ]:
        response = client.post(f"/api/v1/{route}", json=body)
        assert response.status_code == 200
        assert response.json() == service(contract.model_validate(body)).model_dump(mode="json")
    body["scenario"]["decision"]["use_case"] = "unknown"
    assert client.post("/api/v1/recommend", json=body).status_code == 422
    with pytest.raises(ValidationError, match="use_case"):
        recommend(body)
    with pytest.raises(ValidationError):
        evaluate_scenario({})


def test_project_tco_decision_metadata_and_non_onprem_identifiers():
    scenario = default_scenario()
    result = recommend(RecommendRequest(scenario=scenario))
    for kind in ("onprem", "api", "rental", "hybrid"):
        c = next(
            c for c in (*[r.evaluation for r in result.ranked], *result.rejected) if c.kind == kind
        )
        projection = project_tco(TcoRequest(scenario=scenario, candidate_id=c.candidate_id))
        assert projection.candidate == c
