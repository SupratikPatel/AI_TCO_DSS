"""FastAPI boundary: Requirements 38.2, 43.2, 43.5, 43.8."""

import pytest
from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app
from ai_tco_dss.domain.errors import CatalogLoadError, ConfigurationError


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_req_43_health_openapi_and_no_fabricated_rankings(client):
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    schema = client.get("/openapi.json").json()
    assert schema["paths"]["/api/v1/size"]["post"]["requestBody"]
    assert "SizeResult" in schema["components"]["schemas"]
    assert client.post("/api/v1/recommend").status_code == 404


def test_req_43_validation_errors(client):
    response = client.post("/api/v1/size", json={})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
    assert response.json()["fields"]


@pytest.mark.parametrize(
    "error,code,status",
    [
        (CatalogLoadError((("private/path", "value", "broken"),)), "catalog_error", 503),
        (ConfigurationError("private-setting", "secret"), "configuration_error", 503),
        (RuntimeError("private stack detail"), "server_error", 500),
    ],
)
def test_req_43_safe_errors(client, monkeypatch, error, code, status):
    def fail():
        raise error

    monkeypatch.setattr("ai_tco_dss.api.app.services.catalog_overview", fail)
    response = client.get("/api/v1/catalog")
    assert response.status_code == status
    assert response.json()["code"] == code
    assert "private" not in response.text
