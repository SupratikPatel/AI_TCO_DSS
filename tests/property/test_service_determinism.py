"""Req 38.5: real service determinism over valid Normal-mode scenarios."""

from hypothesis import given
from hypothesis import strategies as st

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.catalog.memory_repository import InMemoryCatalogRepository
from ai_tco_dss.domain import PresetId, RecommendRequest, Scenario, UseCaseId
from ai_tco_dss.services import recommend


@given(st.sampled_from(tuple(UseCaseId)), st.sampled_from(tuple(PresetId)), st.integers(1, 100))
def test_req_38_5_recommend_determinism(use_case, preset, users):
    body = default_scenario().model_dump(mode="json")
    body["workload"]["active_users"] = users
    body["decision"].update(use_case=use_case, preset=preset)
    request = RecommendRequest(scenario=Scenario.model_validate(body))
    repo = get_default_repository()
    replacement = InMemoryCatalogRepository(repo.catalog(), repo.load_workload())
    assert recommend(request, repo=repo) == recommend(request, repo=replacement)
