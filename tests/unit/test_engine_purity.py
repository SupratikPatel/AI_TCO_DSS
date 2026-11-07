"""Engine purity (Req 38.2): no file or network access, no module-level mutable state."""

import ast
import builtins
import pathlib
import socket
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    PrecisionFormat,
    SizingInput,
    SizingOptions,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines.sizing import size_deployment
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

SRC = Path(__file__).resolve().parents[2] / "src" / "ai_tco_dss"
PURE_PACKAGES = {
    "engines": ("ai_tco_dss.domain", "ai_tco_dss.engines"),
    "decision": ("ai_tco_dss.domain", "ai_tco_dss.engines", "ai_tco_dss.decision"),
}
MUTABLE_NODES = (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)
MUTABLE_CALLS = {"list", "dict", "set", "defaultdict", "OrderedDict", "Counter", "deque"}


def _blocked(*_: Any, **__: Any) -> Any:
    raise AssertionError("I/O is not allowed inside an engine (Req 38.2)")


@pytest.fixture
def no_io(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Block file and socket access while the test body runs."""
    monkeypatch.setattr(builtins, "open", _blocked)
    monkeypatch.setattr(pathlib.Path, "open", _blocked)
    monkeypatch.setattr(pathlib.Path, "read_text", _blocked)
    monkeypatch.setattr(socket, "socket", _blocked)
    yield


def _inputs() -> tuple[WorkloadInput, list[SizingInput]]:
    repo = get_default_repository()
    catalog = repo.catalog()
    profile = repo.load_workload()
    models = {m.id: m for m in catalog.models}
    workload = WorkloadInput(
        profile=profile, model=models["qwen-3-8-flash-next"], harnesses=catalog.harnesses
    )
    sizing = [
        SizingInput(
            hardware=hardware,
            model=models["qwen-3-8-27b"],
            precision=PrecisionFormat.INT4,
            requested_nodes=float(hardware.valid_node_counts.value[0]),
            options=SizingOptions(target_context_length=8_192),
            profile=WorkloadProfile(),
            license_alternatives=("Gemma 4 12B",),
        )
        for hardware in catalog.hardware
    ]
    return workload, sizing


@pytest.fixture
def unblocked() -> tuple[Any, ...]:
    """Inputs and results computed with I/O allowed (built before `no_io` is applied)."""
    params = load_engine_parameters()
    workload, sizing = _inputs()
    results = (compute_workload(workload, params), [size_deployment(i, params) for i in sizing])
    return params, workload, sizing, results


def test_req_38_2_engines_return_equal_results_with_io_blocked(
    unblocked: tuple[Any, ...], no_io: None
) -> None:
    params, workload, sizing, (expected_workload, expected_sizing) = unblocked
    assert compute_workload(workload, params) == expected_workload
    assert [size_deployment(inp, params) for inp in sizing] == expected_sizing


def test_no_io_fixture_blocks_file_access(no_io: None) -> None:
    with pytest.raises(AssertionError, match=r"Req 38\.2"):
        Path(__file__).read_text(encoding="utf-8")


def _modules(package: str) -> list[Path]:
    return sorted((SRC / package).glob("*.py"))


def _top_level_name(name: str) -> str:
    return name.split(".")[0]


def _import_violations(path: Path, allowed: tuple[str, ...]) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        for name in names:
            if name.startswith("ai_tco_dss"):
                if not any(name == a or name.startswith(a + ".") for a in allowed):
                    found.append(f"{path.name}: forbidden import {name}")
            elif _top_level_name(name) not in sys.stdlib_module_names:
                found.append(f"{path.name}: non-stdlib import {name}")
    return found


def _mutable_globals(path: Path) -> list[str]:
    found = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        value = node.value if isinstance(node, ast.Assign | ast.AnnAssign) else None
        if value is None:
            continue
        is_call = isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
        if isinstance(value, MUTABLE_NODES) or (
            is_call and value.func.id in MUTABLE_CALLS  # type: ignore[union-attr]
        ):
            found.append(f"{path.name}: line {node.lineno}: module-level mutable value")
    return found


@pytest.mark.parametrize("package", sorted(PURE_PACKAGES))
def test_req_38_2_pure_packages_import_only_domain_and_stdlib(package: str) -> None:
    violations = [
        v for path in _modules(package) for v in _import_violations(path, PURE_PACKAGES[package])
    ]
    assert violations == []


@pytest.mark.parametrize("package", sorted(PURE_PACKAGES))
def test_req_38_2_pure_packages_declare_no_module_level_mutable_state(package: str) -> None:
    violations = [v for path in _modules(package) for v in _mutable_globals(path)]
    assert violations == []


def test_req_38_2_engine_modules_exist() -> None:
    assert {p.name for p in _modules("engines")} >= {"__init__.py", "workload.py", "sizing.py"}


def test_ast_checks_detect_violations(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text(
        "import numpy\nfrom ai_tco_dss.catalog import loading\nCACHE = {}\nITEMS = list()\n",
        encoding="utf-8",
    )
    assert _import_violations(bad, PURE_PACKAGES["engines"]) == [
        "bad.py: non-stdlib import numpy",
        "bad.py: forbidden import ai_tco_dss.catalog",
    ]
    assert len(_mutable_globals(bad)) == 2
