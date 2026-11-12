"""Task 13: 2.6, 38.5, 39.4-7, 40.1, 43.1/8/9 cutover acceptance."""

import importlib.util
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]


def verifier():
    spec = importlib.util.spec_from_file_location("verify", ROOT / "scripts/verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_req_43_8_combined_checks_continue_after_failure(monkeypatch):
    module = verifier()
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=1 if "pytest" in command else 0)

    monkeypatch.setattr(module.subprocess, "run", run)
    assert module.main([]) == 1
    scripts = [c[2] for c in calls if len(c) > 2 and c[1] == "run"]
    assert scripts == [
        "typecheck",
        "lint",
        "test",
        "types:check",
        "build",
        "test:browser",
        "test:launcher",
    ]


def test_req_43_1_streamlit_retired():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert not any(d.startswith("streamlit") for d in project["project"]["dependencies"])
    for path in (ROOT / "src/ai_tco_dss").rglob("*.py"):
        assert "import streamlit" not in path.read_text(encoding="utf-8"), path
    assert not (ROOT / ".streamlit/config.toml").exists()
    for launcher in ("run.bat", "run.sh"):
        source = (ROOT / launcher).read_text()
        assert "streamlit" not in source
        assert "npm" in source and "uv sync --locked" in source


def test_req_2_6_43_8_ci_and_launch_documentation():
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    for required in (
        "push:",
        "pull_request:",
        "windows-latest",
        "3.12",
        "npm ci",
        "uv sync --locked",
        "playwright install chromium",
        "uv run python scripts/verify.py",
    ):
        assert required in ci
    readme = (ROOT / "README.md").read_text()
    for command in (
        "npm ci",
        "npm run dev",
        "npm run build",
        "npm run start",
        "uv run python scripts/verify.py",
    ):
        assert command in readme


def test_req_40_1_extension_seams():
    source = (ROOT / "specs/00_INDEX_AND_AGENT_ROUTER.md").read_text()
    section = source.split("## Extension Seams (post-MVP)")[1]
    rows = [line for line in section.splitlines() if line.startswith("| ")][1:]
    assert len(rows) == 8
    for row in rows:
        assert "src/ai_tco_dss/" in row
        assert any(
            s in row
            for s in (
                "size",
                "recommend",
                "evaluate_scenario",
                "CatalogRepository",
                "BenchmarkRecord",
                "WorkloadProfile",
            )
        )


def test_req_43_9_same_origin_production(tmp_path):
    from ai_tco_dss.api.production import create_app

    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text('<div id="root">app</div>')
    (tmp_path / "assets/app-abc.js").write_text("export {}")
    client = TestClient(create_app(tmp_path))
    for url in ("/", "/ranking"):
        response = client.get(url)
        assert response.status_code == 200 and 'id="root"' in response.text
        assert response.headers["cache-control"] == "no-cache"
    response = client.get("/assets/app-abc.js")
    assert response.status_code == 200 and "javascript" in response.headers["content-type"]
    assert "immutable" in response.headers["cache-control"]
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/openapi.json").json()["info"]["title"] == "AI TCO DSS"
    for url in ("/api/v1/missing", "/assets/missing.js", "/missing.css", "/%2e%2e/pyproject.toml"):
        assert client.get(url).status_code == 404
    assert client.post("/ranking").status_code == 405
    with pytest.raises(RuntimeError, match="npm run build"):
        create_app(tmp_path / "missing")
