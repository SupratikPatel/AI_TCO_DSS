"""JSON Schema export (Req 7.8, 7.9, 7.10, 40.2)."""

import json
import tomllib
from pathlib import Path

import pytest

from ai_tco_dss.domain import export_schemas
from ai_tco_dss.domain.requests import SizeRequest

ROOT = Path(__file__).resolve().parents[2]

SERVICE_CONTRACTS = {
    "ScenarioRequest",
    "ScenarioResult",
    "RecommendRequest",
    "Recommendation",
    "SizeRequest",
    "SizeResult",
    "TcoRequest",
    "TcoProjection",
}


def _snapshot(directory: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(directory.glob("*.json"))}


def test_req_7_8_creates_directory_and_one_file_per_service_contract(tmp_path: Path) -> None:
    out = tmp_path / "schemas"
    assert export_schemas.main(["--out", str(out)]) == 0
    assert {p.stem for p in out.glob("*.json")} == SERVICE_CONTRACTS
    for path in out.glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["title"] == path.stem
        assert schema["type"] == "object"


def test_req_7_9_second_run_is_byte_identical(tmp_path: Path) -> None:
    out = tmp_path / "schemas"
    assert export_schemas.main(["--out", str(out)]) == 0
    first = _snapshot(out)
    assert export_schemas.main(["--out", str(out)]) == 0
    assert _snapshot(out) == first
    assert all(content.endswith(b"}\n") for content in first.values())


def test_req_7_10_failure_names_contract_and_exits_non_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def broken(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr(SizeRequest, "model_json_schema", broken)
    assert export_schemas.main(["--out", str(tmp_path / "schemas")]) != 0
    assert "SizeRequest" in capsys.readouterr().err


def test_committed_schemas_match_the_contracts(tmp_path: Path) -> None:
    """`schemas/` in the repository equals a fresh export (rerun gives no git diff)."""
    out = tmp_path / "schemas"
    assert export_schemas.main(["--out", str(out)]) == 0
    assert _snapshot(ROOT / "schemas") == _snapshot(out)


def test_console_script_declared() -> None:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        scripts = tomllib.load(fh)["project"]["scripts"]
    assert scripts["ai-tco-schemas"] == "ai_tco_dss.domain.export_schemas:main"
