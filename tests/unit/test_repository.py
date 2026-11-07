"""Catalog repositories (Req 11.1, 11.2, 11.7, 11.10, 12.3, 12.9, 38.3, 39.1 to 39.3)."""

import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from ai_tco_dss.catalog import (
    CatalogRepository,
    InMemoryCatalogRepository,
    JsonCatalogRepository,
    get_default_repository,
    json_repository,
    loading,
)
from ai_tco_dss.domain import HardwareSpec, ModelSpec, Money
from ai_tco_dss.domain.errors import CatalogLoadError

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "catalog_min"
README = ROOT / "data" / "catalog" / "README.md"
RATE = 1.1165


@pytest.fixture
def root(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(FIXTURE, target)
    return target


def _edit(path: Path, change: Any) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def _all_money(model: BaseModel) -> list[Money]:
    found: list[Money] = []
    for value in model.__dict__.values():
        items = value if isinstance(value, tuple) else (value,)
        for item in items:
            if isinstance(item, Money):
                found.append(item)
            elif isinstance(item, BaseModel):
                found.extend(_all_money(item))
    return found


def test_req_11_1_items_loaded_one_file_per_item(root: Path) -> None:
    catalog = JsonCatalogRepository(root).catalog()
    assert [h.id for h in catalog.hardware] == ["mac-studio-m5-max-128gb", "rtx-pro-6000-96gb"]
    assert [m.id for m in catalog.models] == ["claude-sonnet-5-5", "qwen-3-8-27b"]
    assert len(catalog.rentals) == 2
    assert len(catalog.benchmarks) == 3


def test_req_11_2_new_file_appears_on_next_instance(root: Path) -> None:
    before = JsonCatalogRepository(root).catalog()
    data = json.loads((root / "catalog/models/qwen-3-8-27b.json").read_text(encoding="utf-8"))
    data["id"] = "qwen-3-8-27b-copy"
    (root / "catalog/models/qwen-3-8-27b-copy.json").write_text(json.dumps(data), "utf-8")
    (root / "catalog/models/README.txt").write_text("ignored", encoding="utf-8")
    after = JsonCatalogRepository(root).catalog()
    assert len(after.models) == len(before.models) + 1
    assert "qwen-3-8-27b-copy" in {m.id for m in after.models}


def test_req_11_10_invalid_file_raises_with_file_and_field(root: Path) -> None:
    _edit(root / "catalog/hardware/rtx-pro-6000-96gb.json", lambda d: d.pop("idle_watts"))
    with pytest.raises(CatalogLoadError) as exc:
        JsonCatalogRepository(root)
    files_and_fields = [(f.replace("\\", "/"), field) for f, field, _ in exc.value.errors]
    assert any(
        f.endswith("catalog/hardware/rtx-pro-6000-96gb.json") and field == "idle_watts"
        for f, field in files_and_fields
    ), exc.value.errors


def test_req_11_10_unparseable_file_raises(root: Path) -> None:
    (root / "catalog/models/qwen-3-8-27b.json").write_text("{", encoding="utf-8")
    with pytest.raises(CatalogLoadError, match=r"qwen-3-8-27b\.json"):
        JsonCatalogRepository(root)


def test_req_12_3_eur_money_returned_as_usd(root: Path) -> None:
    catalog = JsonCatalogRepository(root).catalog()
    mac = next(h for h in catalog.hardware if h.id == "mac-studio-m5-max-128gb")
    assert mac.street_price.currency == "USD"
    assert mac.street_price.value == pytest.approx(5099 * RATE)
    assert mac.street_price.original_value == 5099
    assert mac.street_price.fx_source_id == "ECB-FX"
    assert all(m.currency == "USD" for m in _all_money(catalog))
    assert catalog.fx_active_rate == RATE
    assert catalog.fx_is_override is False


def test_req_12_4_fx_override_converts_without_touching_files(root: Path) -> None:
    before = (root / "reference/fx.json").read_bytes()
    repo = JsonCatalogRepository(root)
    overridden = repo.catalog(1.2)
    rental = next(r for r in overridden.rentals if r.id == "hetzner-gex63")
    assert rental.monthly_price.value == pytest.approx(999 * 1.2)
    assert overridden.fx_is_override is True
    assert overridden.fx_active_rate == 1.2
    assert repo.catalog(1.2) is overridden
    assert (root / "reference/fx.json").read_bytes() == before


@pytest.mark.parametrize(
    ("change", "field"),
    [
        (lambda d: d.update(eur_to_usd=-1), "eur_to_usd"),
        (lambda d: d.pop("eur_to_usd"), "eur_to_usd"),
        (lambda d: d.update(rate_date="06/11/2026"), "rate_date"),
        (lambda d: d.update(source_id="NO-SUCH-SOURCE"), "source_id"),
    ],
)
def test_req_12_9_bad_fx_file_raises_naming_fx_json(root: Path, change: Any, field: str) -> None:
    _edit(root / "reference/fx.json", change)
    with pytest.raises(CatalogLoadError) as exc:
        JsonCatalogRepository(root)
    assert any(
        f.replace("\\", "/").endswith("reference/fx.json") and field in fld
        for f, fld, _ in exc.value.errors
    ), exc.value.errors


def test_req_12_9_missing_fx_file_raises(root: Path) -> None:
    (root / "reference/fx.json").unlink()
    with pytest.raises(CatalogLoadError, match=r"fx\.json"):
        JsonCatalogRepository(root)


def test_req_39_1_39_2_default_repository_loads_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Path] = []
    original = loading.load_catalog

    def spy(root: Path) -> Any:
        calls.append(root)
        return original(root)

    monkeypatch.setattr(loading, "load_catalog", spy)
    monkeypatch.setattr(json_repository, "_default_repository", None)
    first = get_default_repository()
    second = get_default_repository()
    assert first is second
    assert first.catalog() is second.catalog()
    assert len(calls) == 1


def test_req_39_3_catalog_is_immutable(root: Path) -> None:
    catalog = JsonCatalogRepository(root).catalog()
    mac = catalog.hardware[0]
    with pytest.raises(ValidationError):
        mac.name = "changed"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        catalog.fx_active_rate = 2.0  # type: ignore[misc]
    assert mac.name == "Mac Studio (M5 Max 128GB)"
    assert isinstance(catalog.hardware, tuple)


def test_req_38_3_repositories_implement_the_protocol(root: Path) -> None:
    json_repo = JsonCatalogRepository(root)
    memory_repo = InMemoryCatalogRepository(json_repo.catalog(), json_repo.load_workload())
    for repo in (json_repo, memory_repo):
        assert isinstance(repo, CatalogRepository)
    assert memory_repo.catalog() == json_repo.catalog()
    assert memory_repo.load_workload().active_users == 25


# --------------------------------------------------------------------------- README (11.7)


def _readme_section(title: str) -> str:
    text = README.read_text(encoding="utf-8")
    start = text.index(f"## {title}")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else None]


@pytest.mark.parametrize(
    ("title", "contract"), [("Hardware item", HardwareSpec), ("Model item", ModelSpec)]
)
def test_req_11_7_readme_example_validates_and_documents_every_field(
    title: str, contract: type[BaseModel]
) -> None:
    section = _readme_section(title)
    block = re.search(r"```json\n(.*?)```", section, re.S)
    assert block is not None
    example = json.loads(block.group(1))
    contract.model_validate(example)
    required = {n for n, f in contract.model_fields.items() if f.is_required()}
    assert required <= example.keys()
    rows = {
        cells[0].strip("` "): cells
        for cells in (
            [c.strip() for c in line.strip().strip("|").split("|")]
            for line in section.splitlines()
            if line.startswith("| `")
        )
    }
    for name, field in contract.model_fields.items():
        assert name in rows, f"{title}: field {name} not documented"
        expected = "required" if field.is_required() else "optional"
        assert expected in rows[name], f"{title}: {name} should be {expected}"
