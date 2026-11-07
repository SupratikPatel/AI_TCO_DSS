"""Dashboard import boundaries (Req 37.7, 37.8, 38.6)."""

import ast
from pathlib import Path

import pytest

UI_DIR = Path(__file__).resolve().parents[2] / "src" / "ai_tco_dss" / "ui"
FORBIDDEN = ("ai_tco_dss.engines", "ai_tco_dss.decision", "ai_tco_dss.catalog")
ALLOWED = ("ai_tco_dss.services", "ai_tco_dss.domain", "ai_tco_dss.ui")


def _imported_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.append(node.module)
            names.extend(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def _matches(name: str, packages: tuple[str, ...]) -> bool:
    return any(name == p or name.startswith(p + ".") for p in packages)


def boundary_violations(source: str, filename: str) -> list[str]:
    """Return one message per forbidden or non-allowed `ai_tco_dss` import."""
    messages = []
    for name in _imported_names(ast.parse(source, filename=filename)):
        if name == "ai_tco_dss" or not name.startswith("ai_tco_dss"):
            continue
        if _matches(name, FORBIDDEN) or not _matches(name, ALLOWED):
            messages.append(f"{filename}: forbidden import {name}")
    return sorted(set(messages))


@pytest.mark.parametrize("path", sorted(UI_DIR.glob("*.py")), ids=lambda p: p.name)
def test_req_37_7_38_6_ui_modules_import_only_allowed_packages(path: Path) -> None:
    assert boundary_violations(path.read_text(encoding="utf-8"), path.name) == []


@pytest.mark.parametrize(
    ("source", "name"),
    [
        ("import ai_tco_dss.engines.sizing", "ai_tco_dss.engines.sizing"),
        ("from ai_tco_dss.decision import ranking", "ai_tco_dss.decision"),
        ("from ai_tco_dss.catalog.json_repository import x", "ai_tco_dss.catalog.json_repository"),
        ("from ai_tco_dss import catalog", "ai_tco_dss.catalog"),
    ],
)
def test_req_37_8_violation_message_names_file_and_import(source: str, name: str) -> None:
    messages = boundary_violations(source, "synthetic.py")
    assert f"synthetic.py: forbidden import {name}" in messages


def test_allowed_imports_pass() -> None:
    source = "import streamlit as st\nfrom ai_tco_dss.services import catalog_overview\n"
    assert boundary_violations(source, "ok.py") == []
