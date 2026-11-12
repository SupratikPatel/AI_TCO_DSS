"""TCO accounting explanations stay bound to the independent simulator result."""

import pytest
from fastapi.testclient import TestClient

from ai_tco_dss.api.app import app, default_scenario
from ai_tco_dss.domain import TcoRequest
from ai_tco_dss.services import project_tco

client = TestClient(app)


def request_body(resale=False, fx=None):
    body = default_scenario().model_dump(mode="json")
    body["sizing"]["target_context_length"] = 128000
    body["financials"]["include_resale_value"] = resale
    body["fx_override"] = fx
    return {"scenario": body, "candidate_id": "onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT4"}


@pytest.mark.parametrize("resale,fx", [(False, None), (True, None), (True, 1.25)])
def test_accounting_exact_projection_fx_resale_and_comparison(resale, fx):
    body = request_body(resale, fx)
    response = client.post("/api/v1/tco", json=body)
    assert response.status_code == 200
    actual = response.json()
    details = actual.pop("accounting")
    projection = project_tco(TcoRequest.model_validate(body))
    assert actual == projection.model_dump(mode="json")
    cost = projection.candidate.tco
    rows = {r["key"]: r for r in details["rows"]}
    assert rows["cost_60m"]["value"] == cost.cost_60m
    assert rows["monthly_total"]["value"] == cost.monthly_opex_total
    components = dict(cost.monthly_opex)
    assert rows["cash_monthly"]["value"] == sum(
        components[k] for k in ("energy", "personnel", "nim_licensing")
    )
    assert rows["economic_monthly"]["value"] == sum(
        components[k] for k in ("capital_opportunity", "wait_penalty", "eviction_loss")
    )
    assert rows["resale"]["value"] == pytest.approx(
        cost.capex.value + 60 * cost.monthly_opex_total - cost.cost_60m
    )
    assert details["includes_resale"] is resale
    assert details["fx"]["rate"] == (fx or 1.1165)
    assert details["fx"]["is_override"] is (fx is not None)
    c_total = projection.timeline.points[-1].baseline_c_eu_sovereign_api_cumulative
    assert rows["baseline_c_60m"]["value"] == c_total
    assert rows["savings_60m"]["value"] == c_total - cost.cost_60m
    assert (
        details["break_even_month"]
        == dict(projection.timeline.break_even_months)["baseline_c_eu_sovereign_api_cumulative"]
    )
    assert details["candidate_id"] == body["candidate_id"]
    assert (
        "after resale" in rows["cost_60m"]["note"]
        if resale
        else "before resale" in rows["cost_60m"]["note"]
    )
    for key, value in components.items():
        trace = next(t for t in cost.traces if t.name == key)
        assert rows[key]["trace"] == trace.model_dump(mode="json")
        assert rows[key]["value"] == value


def test_accounting_sources_zero_reasons_and_neutral_utilization():
    actual = client.post("/api/v1/tco", json=request_body()).json()
    details = actual["accounting"]
    rows = {r["key"]: r for r in details["rows"]}
    assert "Disabled" in rows["nim_licensing"]["note"]
    assert "Disabled" in rows["wait_penalty"]["note"]
    assert "No context eviction risk" in rows["eviction_loss"]["note"]
    assert rows["capex"]["sources"]
    assert any(p["tier"] == "assumption" for s in rows["capex"]["sources"] for p in s["provenance"])
    assert all(
        p["accessed"] for r in details["rows"] for s in r["sources"] for p in s["provenance"]
    )
    assert "gateway" in rows["baseline_c"]["note"].lower()
    assert "4.7%" in details["utilization_text"]
    assert "likely to exceed" not in " ".join(actual["candidate"]["tco"]["warnings"])
    assert rows["savings_60m"]["value"] > 0


def test_accounting_zero_when_enabled_is_not_labelled_disabled():
    body = request_body()
    body["scenario"]["financials"].update(
        enable_nvidia_nim_licensing=True,
        nvidia_nim_license_per_gpu_yr_usd=0,
        include_wait_time_penalty=True,
    )
    rows = {r["key"]: r for r in client.post("/api/v1/tco", json=body).json()["accounting"]["rows"]}
    assert "Disabled" not in rows["nim_licensing"]["note"]
    assert "Disabled" not in rows["wait_penalty"]["note"]


def test_low_utilization_does_not_choose_a_cheaper_option():
    body = request_body()
    body["scenario"]["workload"]["active_users"] = 1
    result = client.post("/api/v1/tco", json=body).json()
    rows = {r["key"]: r for r in result["accounting"]["rows"]}
    assert rows["savings_60m"]["value"] < 0
    assert result["accounting"]["break_even_month"] is None
    assert "likely to exceed" not in " ".join(result["candidate"]["tco"]["warnings"])
