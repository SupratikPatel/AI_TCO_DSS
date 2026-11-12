"""Engineering toolchain (Requirement 2) and README commands (Req 6.3)."""

import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

RUNTIME_DEPS = {"pydantic", "pydantic-settings", "fastapi", "uvicorn", "plotly", "pandas", "numpy"}
DEV_DEPS = {"ruff", "mypy", "pytest", "hypothesis"}


def _pyproject() -> dict[str, Any]:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)


def _names(requirements: list[str]) -> set[str]:
    return {re.split(r"[\s<>=!~\[;]", req, maxsplit=1)[0].lower() for req in requirements}


def test_req_2_1_requires_python() -> None:
    assert _pyproject()["project"]["requires-python"] == ">=3.12,<3.13"


def test_req_2_1_python_version_file() -> None:
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12"


def test_req_2_1_runtime_dependencies_declared() -> None:
    declared = _names(_pyproject()["project"]["dependencies"])
    assert declared >= RUNTIME_DEPS


def test_req_2_1_dev_dependencies_declared() -> None:
    declared = _names(_pyproject()["dependency-groups"]["dev"])
    assert declared >= DEV_DEPS


def test_req_2_3_tool_configuration() -> None:
    tool = _pyproject()["tool"]
    assert "ruff" in tool
    assert "format" in tool["ruff"]
    assert "lint" in tool["ruff"]
    assert tool["mypy"]["strict"] is True
    assert "ini_options" in tool["pytest"]


def test_req_2_1_2_2_lock_file_matches_pyproject() -> None:
    """Req 2.1/2.2: uv.lock exists and matches pyproject.toml (checked offline)."""
    assert (ROOT / "uv.lock").is_file()
    uv = shutil.which("uv")
    assert uv is not None, "uv must be on PATH"
    result = subprocess.run(
        [uv, "lock", "--check", "--offline"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_req_6_3_readme_has_exactly_one_dashboard_command() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    commands = [line for line in readme.splitlines() if "Start both services:" in line]
    assert len(commands) == 1
    assert "npm run dev" in commands[0]


def test_readme_has_test_and_verify_commands() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "`uv run pytest`" in readme
    assert "`uv run python scripts/verify.py`" in readme
