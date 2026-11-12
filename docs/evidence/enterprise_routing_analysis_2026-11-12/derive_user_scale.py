"""Read-only model diagnostics; no inference, network or production writes.

Run from the workspace root with uv run python and this script's path.
Saved scenarios are explicit; they do not claim to reproduce the user's live UI.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path

from ai_tco_dss.api.app import default_scenario
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import RecommendRequest, Scenario, ScenarioResult
from ai_tco_dss.services.scenario_service import recommend
from ai_tco_dss.settings import load_engine_parameters

ROOT = Path(__file__).resolve().parent
catalog = get_default_repository().catalog()
base = default_scenario().model_dump(mode="json")
saved = json.loads(Path("docs/evidence/peak_capacity_sensitivity_2026-11-11.json").read_text(encoding="utf-8"))["cases"][0]["scenario"]
result = {
    "purpose": "New diagnostics at 1000, 1001, 1050 and 2000 users; saved defaults, not the active UI.",
    "engine_version": ScenarioResult.model_fields["engine_version"].default,
    "catalog_fingerprint": hashlib.sha256(catalog.model_dump_json().encode()).hexdigest(),
    "engine_parameters": load_engine_parameters().model_dump(mode="json"),
    "hardware_ids": [h.id for h in catalog.hardware],
    "model_ids": [m.id for m in catalog.models],
    "cases": [],
}
for name, original in [("enterprise_defaults", base), ("saved_self_managed_baseline", saved)]:
    for users in [1000, 1001, 1050, 2000]:
        inputs = json.loads(json.dumps(original))
        inputs["workload"]["active_users"] = users
        scenario = Scenario.model_validate(inputs)
        recommendation = recommend(RecommendRequest(scenario=scenario))
        failure_counts = Counter(f.name for c in recommendation.rejected for f in c.failures)
        closest = sorted(recommendation.rejected, key=lambda c: (len(c.failures), c.cost_60m, c.candidate_id))[:8]
        only_monthly = [c for c in recommendation.rejected if {f.name for f in c.failures} == {"users_served"}]
        row = {
            "name": name, "users": users, "scenario": scenario.model_dump(mode="json"),
            "admitted": len(recommendation.ranked), "rejected": len(recommendation.rejected),
            "winner": recommendation.ranked[0].evaluation.model_dump(mode="json") if recommendation.ranked else None,
            "failure_counts": dict(failure_counts),
            "api_failures": [{"id": c.candidate_id, "failures": [f.model_dump(mode="json") for f in c.failures]}
                             for c in recommendation.rejected if c.kind == "api"],
            "closest_rejections": [c.model_dump(mode="json") for c in closest],
            "rejected_only_monthly_capacity": [
                {"id": c.candidate_id, "utilization": c.utilization,
                 "capacity_users_at_same_workload": users / c.utilization if c.utilization else None}
                for c in only_monthly
            ],
            "warnings": recommendation.warnings,
        }
        result["cases"].append(row)
        print(name, users, "admitted", len(recommendation.ranked), "winner",
              recommendation.ranked[0].evaluation.candidate_id if recommendation.ranked else None,
              "failures", dict(failure_counts))
Scenario.model_validate({**base, "workload": {**base["workload"], "active_users": 100000}})
result["validated_user_bound"] = 100000
(ROOT / "user_scale_diagnostic.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
