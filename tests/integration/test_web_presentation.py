"""Task 11: 34.1, 35.4, 37.4, 43.5/6/7 Python remains the presentation authority."""

import pytest
from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app
from ai_tco_dss.domain import ScenarioRequest
from ai_tco_dss.services import evaluate_scenario

client = TestClient(app)


@pytest.mark.parametrize("method", ["saw", "topsis"])
@pytest.mark.parametrize("fx", [None, 1.2])
def test_kpi_chart_payload_exact_service_parity(method, fx):
    """No derived money, ranking, break-even or compliance is recomputed by the adapter."""
    scenario = client.get("/api/v1/scenario/default").json()
    scenario["decision"]["method"] = method
    scenario["fx_override"] = fx
    request = ScenarioRequest.model_validate({"scenario": scenario})
    expected = evaluate_scenario(request)
    response = client.post("/api/v1/evaluate", json=request.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json() == expected.model_dump(mode="json")
    top = expected.recommendation.ranked[0].evaluation
    assert top.eu_compliant
    assert top.performance is not None
    assert top.tco is not None
    assert top.utilization is not None
    assert expected.baselines.currency == "USD"
    assert expected.fx_is_override == (fx is not None)
    if fx is not None:
        assert expected.fx_rate == fx
    assert expected.timeline is not None
    assert expected.timeline.anchor_candidate_id == top.candidate_id
    assert [point.month for point in expected.timeline.points] == list(range(1, 61))
    assert expected.timeline.break_even_months
