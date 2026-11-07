"""Edited Reference_Data reaches the engine results without code changes (Req 13.7)."""

import json
import shutil
from pathlib import Path

from ai_tco_dss.catalog import JsonCatalogRepository
from ai_tco_dss.catalog.json_repository import DEFAULT_DATA_ROOT
from ai_tco_dss.domain import (
    DecisionOptions,
    ElectricityTariffTier,
    EnterpriseFinancials,
    Scenario,
    SizingOptions,
    TcoRequest,
)
from ai_tco_dss.services import project_tco

CANDIDATE_ID = "onprem:rtx-pro-6000-96gb:4x:gpt-oss-120b:INT4"
TARIFF = ElectricityTariffTier.DE_INDUSTRIAL_BDEW


def _energy(repo: JsonCatalogRepository) -> float:
    scenario = Scenario(
        workload=repo.load_workload(),
        financials=EnterpriseFinancials(electricity_tariff_tier=TARIFF),
        sizing=SizingOptions(),
        decision=DecisionOptions(),
    )
    projection = project_tco(TcoRequest(scenario=scenario, candidate_id=CANDIDATE_ID), repo=repo)
    assert projection.candidate.tco is not None
    return dict(projection.candidate.tco.monthly_opex)["energy"]


def test_req_13_7_edited_tariff_changes_energy_opex(tmp_path: Path) -> None:
    root = tmp_path / "data"
    shutil.copytree(DEFAULT_DATA_ROOT, root)
    before = _energy(JsonCatalogRepository(root))

    path = root / "reference" / "electricity.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entry = next(t for t in data["tariffs"] if t["id"] == TARIFF.value)
    old = entry["price_per_kwh"]["value"]
    entry["price_per_kwh"]["value"] = old * 2
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    after = _energy(JsonCatalogRepository(root))
    assert after != before
    assert after == before * 2 or abs(after - before * 2) <= 1e-9 * after
