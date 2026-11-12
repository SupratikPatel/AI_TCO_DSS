"""Real service parity and rental/timeline reuse: 25.1, 26.1, 35.4, 43.5, 43.7."""

from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app
from ai_tco_dss.domain import SizeRequest, TcoRequest
from ai_tco_dss.services import catalog_overview, load_workload, project_tco, size

client = TestClient(app)


def request_body():
    return {
        "scenario": client.get("/api/v1/scenario/default").json(),
        "hardware_id": "rtx-pro-6000-96gb",
        "model_id": "gpt-oss-120b",
        "nodes": 4,
        "precision": "INT4",
    }


def test_req_43_catalog_workload_defaults():
    overview = catalog_overview().model_dump(mode="json")
    assert client.get("/api/v1/catalog").json() == overview
    assert client.get("/api/v1/workloads/default").json() == load_workload().model_dump(mode="json")
    options = client.get("/api/v1/options").json()
    assert "gpt-oss-120b" in options["open_model_ids"]
    assert "claude-sonnet-5-5" not in options["open_model_ids"]


def test_req_43_size_tco_parity_determinism_and_26_timeline():
    body = request_body()
    response = client.post("/api/v1/size", json=body)
    assert response.status_code == 200
    assert response.json() == size(SizeRequest.model_validate(body)).model_dump(mode="json")
    tco = {
        "scenario": body["scenario"],
        "candidate_id": "onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT4",
    }
    response = client.post("/api/v1/tco", json=tco)
    assert response.status_code == 200
    result = response.json()
    assert {k: v for k, v in result.items() if k != "accounting"} == project_tco(
        TcoRequest.model_validate(tco)
    ).model_dump(mode="json")
    assert result["accounting"]["candidate_id"] == tco["candidate_id"]
    assert result == client.post("/api/v1/tco", json=tco).json()
    assert result["baselines"]["currency"] == "USD"
    assert len(result["timeline"]["points"]) == 60
    assert result["timeline"]["rental_id"]
    assert result["timeline"]["anchor_candidate_id"] == tco["candidate_id"]


def test_req_43_unknown_and_engine_input_errors():
    body = request_body()
    body["hardware_id"] = "unknown"
    assert client.post("/api/v1/size", json=body).status_code == 404
    body["hardware_id"] = "rtx-pro-6000-96gb"
    body["nodes"] = 1.5
    assert client.post("/api/v1/size", json=body).status_code == 422
    body["scenario"]["workload"]["active_users"] = 0
    assert client.post("/api/v1/size", json=body).json()["code"] == "validation_error"


def test_req_43_browser_scenarios_are_stateless():
    a, b = request_body(), request_body()
    b["scenario"]["workload"]["active_users"] = 70
    first = client.post("/api/v1/size", json=a).json()
    other = client.post("/api/v1/size", json=b).json()
    assert first["workload"]["monthly_requests"] != other["workload"]["monthly_requests"]
    assert client.post("/api/v1/size", json=a).json() == first
