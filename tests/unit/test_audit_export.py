"""Task 12: Req 36.1-8, 8.6, 12.6 and 43.6 audit/export boundary."""

import csv
import io
import zipfile

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

from ai_tco_dss.api.app import app
from ai_tco_dss.domain import RankingMethod, ScenarioRequest, ScenarioResult
from ai_tco_dss.services import evaluate_scenario

client = TestClient(app)


@pytest.fixture(scope="module")
def result():
    scenario = client.get("/api/v1/scenario/default").json()
    return evaluate_scenario(ScenarioRequest.model_validate({"scenario": scenario}))


def test_audit_selected_candidate_traces_origins_and_unique_sources(result):
    """36.1/2/3/6: use the actual selected evaluation, never the simulator."""
    for row in result.recommendation.ranked[:2]:
        candidate = row.evaluation
        response = client.post(
            "/api/v1/audit",
            json={
                "result": result.model_dump(mode="json"),
                "candidate_id": candidate.candidate_id,
            },
        )
        assert response.status_code == 200
        audit = response.json()
        assert audit["candidate_id"] == candidate.candidate_id
        for section in ("sizing", "performance", "tco"):
            actual = getattr(candidate, section)
            assert actual is not None
            traces = [t["trace"] for t in audit["formulas"] if t["section"] == section]
            assert traces == [t.model_dump(mode="json") for t in actual.traces]
        assert set(audit["performance"]) == {
            "decode_tps",
            "prefill_tps",
            "ttft_s",
            "effective_tps",
            "prefill_1m_minutes",
        }
        for name, metric in audit["performance"].items():
            assert metric == getattr(candidate.performance, name).model_dump(mode="json")
        ids = [s["source_id"] for s in audit["sources"]]
        assert len(ids) == len(set(ids))
        contributing = set(candidate.price_origin.source_ids)
        for metric in audit["performance"].values():
            contributing.update(metric["origin"]["source_ids"])
        assert contributing <= set(ids)
        registry = {s.source_id: s for s in result.sources}
        for source in audit["sources"]:
            assert source["title"] == registry[source["source_id"]].title
            assert source["url"] or source["reference"]
            assert source["provenance"]
            for provenance in source["provenance"]:
                assert len(provenance["accessed"]) == 10
                assert provenance["tier"]
        assert any(p["tier"] == "assumption" for s in audit["sources"] for p in s["provenance"])
        assert audit["fx"]["rate"] == result.fx_rate
        assert audit["fx"]["source_id"] == result.fx_source_id
        assert audit["fx"]["rate_date"] == str(result.fx_rate_date)
        assert audit["fx"]["is_override"] is False


@pytest.mark.parametrize("currency", ["USD", "EUR"])
def test_export_exact_roundtrip_and_csv_zip(result, currency):
    """36.4/5/8: same full result, six raw criteria, all seven series and 60 months."""
    payload = result.model_dump(mode="json")
    response = client.post("/api/v1/export/json", json={"result": payload, "currency": currency})
    assert response.status_code == 200
    assert ScenarioResult.model_validate_json(response.content) == result
    assert "attachment" in response.headers["content-disposition"]
    response = client.post("/api/v1/export/csv", json={"result": payload, "currency": currency})
    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert archive.namelist() == [f"ranking_{currency}.csv", f"timeline_{currency}.csv"]
        ranking = list(csv.DictReader(io.StringIO(archive.read(archive.namelist()[0]).decode())))
        timeline = list(csv.DictReader(io.StringIO(archive.read(archive.namelist()[1]).decode())))
    assert len(ranking) == len(result.recommendation.ranked)
    assert [int(p["month"]) for p in timeline] == list(range(1, 61))
    assert len(timeline[0]) == 8
    rate = result.fx_rate if currency == "EUR" else 1
    for row, expected in zip(ranking, result.recommendation.ranked, strict=True):
        assert row["candidate_id"] == expected.evaluation.candidate_id
        assert int(row["rank"]) == expected.rank
        assert float(row[f"tco_60m_{currency}"]) == pytest.approx(
            expected.evaluation.cost_60m / rate
        )
        assert float(row["aggregate_score"]) == expected.saw_score
        assert {c.criterion.value for c in expected.criteria} - {"tco_60m"} <= row.keys()
    for row, point in zip(timeline, result.timeline.points, strict=True):
        for key, value in point.model_dump().items():
            if key != "month":
                assert (
                    row[f"{key}_{currency}"] == ""
                    if value is None
                    else float(row[f"{key}_{currency}"]) == pytest.approx(value / rate)
                )


def test_audit_empty_and_invalid_selection_and_export_errors(result):
    """36.7: explicit unavailable selection; incomplete timelines cannot produce a fake CSV."""
    payload = result.model_dump(mode="json")
    assert (
        client.post(
            "/api/v1/audit", json={"result": payload, "candidate_id": "missing"}
        ).status_code
        == 404
    )
    payload["recommendation"]["ranked"] = []
    assert (
        client.post(
            "/api/v1/audit", json={"result": payload, "candidate_id": "missing"}
        ).status_code
        == 404
    )
    payload["timeline"] = None
    assert (
        client.post("/api/v1/export/csv", json={"result": payload, "currency": "USD"}).status_code
        == 422
    )
    assert (
        client.post("/api/v1/export/json", json={"result": payload, "currency": "USD"}).status_code
        == 200
    )


def test_override_export_and_audit_keep_original_result_fx(result):
    scenario = result.scenario.model_copy(update={"fx_override": 1.2})
    changed = evaluate_scenario(ScenarioRequest(scenario=scenario))
    payload = changed.model_dump(mode="json")
    audit = client.post(
        "/api/v1/audit",
        json={
            "result": payload,
            "candidate_id": changed.recommendation.ranked[0].evaluation.candidate_id,
        },
    ).json()
    assert audit["fx"]["is_override"] is True
    assert audit["fx"]["rate"] == 1.2
    exported = client.post("/api/v1/export/json", json={"result": payload, "currency": "EUR"})
    assert ScenarioResult.model_validate_json(exported.content) == changed


@pytest.mark.parametrize("kind", ["api", "rental", "hybrid"])
def test_audit_deployment_cost_formulas_are_not_retained_local_costs(result, kind):
    """36.1: trace the actual deployment accounting, including setup and API shares."""
    from ai_tco_dss.services.audit_export import AuditRequest, candidate_audit

    candidate = next(c for c in result.recommendation.rejected if c.kind == kind)
    row = result.recommendation.ranked[0].model_copy(update={"evaluation": candidate})
    displayed = result.model_copy(
        update={"recommendation": result.recommendation.model_copy(update={"ranked": (row,)})}
    )
    audit = candidate_audit(AuditRequest(result=displayed, candidate_id=candidate.candidate_id))
    costs = {f.trace.name: f.trace for f in audit.formulas if f.section == "cost"}
    assert costs["capex"].result == candidate.capex
    assert costs["monthly_cost"].result == candidate.monthly_cost
    assert costs["cost_60m"].result == candidate.cost_60m
    assert costs["monthly_cost"].symbolic != "monthly cost = deployment operating cost"
    if kind == "rental":
        assert "personnel" in costs["monthly_cost"].symbolic
        assert "personnel" in costs
        assert not any(f.section == "tco" for f in audit.formulas)
    if kind == "hybrid":
        assert "local" in costs["monthly_cost"].symbolic
        assert any(f.section.startswith("component") for f in audit.formulas)
    if kind == "api":
        assert "per_request" in costs["monthly_cost"].symbolic
    assert all(s.provenance for s in audit.sources)


def test_onprem_monthly_opex_formula_covers_every_component(result):
    from ai_tco_dss.services.audit_export import AuditRequest, candidate_audit

    candidate = result.recommendation.ranked[0].evaluation
    audit = candidate_audit(AuditRequest(result=result, candidate_id=candidate.candidate_id))
    trace = next(f.trace for f in audit.formulas if f.trace.name == "monthly_opex_total")
    assert trace.result == candidate.monthly_cost
    assert all(name in trace.symbolic for name, _ in candidate.tco.monthly_opex)


def test_topsis_export_aggregate_score_is_closeness(result):
    from ai_tco_dss.services.audit_export import ExportRequest, csv_zip

    scenario = result.scenario.model_copy(
        update={
            "decision": result.scenario.decision.model_copy(update={"method": RankingMethod.TOPSIS})
        }
    )
    displayed = evaluate_scenario(ScenarioRequest(scenario=scenario))
    with zipfile.ZipFile(io.BytesIO(csv_zip(ExportRequest(result=displayed)))) as archive:
        rows = list(csv.DictReader(io.StringIO(archive.read("ranking_USD.csv").decode())))
    assert float(rows[0]["aggregate_score"]) == displayed.recommendation.ranked[0].topsis_closeness


@settings(max_examples=8, deadline=None)
@given(
    users=st.integers(1, 200),
    method=st.sampled_from(["saw", "topsis"]),
    fx=st.sampled_from([None, 0.5, 1.1165, 2.0]),
)
def test_export_roundtrip_property(result, users, method, fx):
    """36.8 / Property 57: actual service results across feasible/empty, method and FX changes."""
    scenario = result.scenario.model_copy(
        update={
            "workload": result.scenario.workload.model_copy(update={"active_users": users}),
            "decision": result.scenario.decision.model_copy(
                update={"method": RankingMethod(method)}
            ),
            "fx_override": fx,
        }
    )
    displayed = evaluate_scenario(ScenarioRequest(scenario=scenario))
    response = client.post(
        "/api/v1/export/json",
        json={
            "result": displayed.model_dump(mode="json"),
            "currency": "EUR",
        },
    )
    assert response.status_code == 200
    assert ScenarioResult.model_validate_json(response.content) == displayed
