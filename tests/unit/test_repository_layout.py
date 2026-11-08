"""Repository layout (Requirement 1)."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "specs"

# Original workspace-root name -> new name under specs/ (Req 1.1, 1.2).
RELOCATIONS = {
    "index_agent_router.md": "00_INDEX_AND_AGENT_ROUTER.md",
    "workload_profiler_physical_sizing_engine (1).md": "01_WORKLOAD_AND_PHYSICS_ENGINE.md",
    "financial_tco_eu_finops_cross_border_personnel_arbitrage (1).md": (
        "02_TCO_FINOPS_AND_EU_COMPLIANCE.md"
    ),
    "2026_calibrated_hardware_model_intelligence_seed_catalog (1).md": (
        "03_CALIBRATED_2026_SEED_DATA.md"
    ),
    "pydantic_v2_core_schemas_contracts (1).md": "04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md",
    "visualization_ux_standards_phased_execution_plan (1).md": (
        "05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md"
    ),
    "research_sources_benchmark_evidence (1).md": "06_RESEARCH_SOURCES.md",
}

SUBPACKAGES = ("domain", "catalog", "engines", "decision", "services", "ui")
TEST_DIRS = ("unit", "calibration", "property", "integration")
SEAMS_HEADING = "## Extension Seams (post-MVP)"

# Exact, author-approved 2026-11-07 delivery amendments. Everything else in the
# relocated domain documents must still compare byte-for-byte after normalization.
WEB_NOTICE = (
    "> **Active architecture decision - 2026-11-07:** The MVP frontend is a dedicated "
    "React/TypeScript web application with Vite, Tailwind and shadcn/ui, backed by FastAPI "
    "and the existing Python services. Streamlit is the legacy prototype. Read "
    "[the web migration contract](09_WEB_FRONTEND_MIGRATION.md) and "
    "[the Stitch design reference](08_MVP_DESIGN_REFERENCE.md) before implementation. "
    "Where historical UI instructions below conflict, Requirement 43 and the migration "
    "contract take precedence.\n\n"
)
WEB_AUTHORITY = """## Active document authority

Read progress.md first, then CLAUDE.md, Requirement 43, specs/09_WEB_FRONTEND_MIGRATION.md,
specs/08_MVP_DESIGN_REFERENCE.md and the revised Tasks 8-13 under .kiro/specs/ai-tco-dss-mvp/.
The numbered domain documents retain the mathematical background; historical
Streamlit paths and framework recommendations do not define the target frontend.
Tasks 1-7 remain completed history; the previous Task 8 backend work is reusable.

"""
WEB_TARGET = """## 0. Active web implementation target

The React/TypeScript frontend implements the actual Stitch design with Vite,
Tailwind CSS, editable shadcn/ui components and Plotly.js. FastAPI is now an MVP
adapter to the existing Python service layer. See specs/08_MVP_DESIGN_REFERENCE.md
and specs/09_WEB_FRONTEND_MIGRATION.md. The framework evaluation and Streamlit
execution plan below describe the earlier prototype decision, now superseded.

The domain concepts, progressive disclosure, chart semantics and auditability
remain relevant. Browser layout, styling, state, component and screenshot tests
replace Streamlit widget, CSS workaround and fragment requirements. API inputs and
outputs use Pydantic/OpenAPI contracts; all numerical computation stays in Python.
The root npm run dev launcher will start both frontend and API after implementation.

"""


def _old_name_variants(old: str) -> tuple[str, str]:
    """Return the old name with and without the ' (1)' suffix."""
    plain = old.replace(" (1).md", ".md")
    return plain, plain.replace(".md", " (1).md")


def _replace_old_names(text: str) -> str:
    for old, new in RELOCATIONS.items():
        plain, suffixed = _old_name_variants(old)
        text = text.replace(suffixed, new).replace(plain, new)
    return text


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False
    )


def _normalise(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if text.startswith("> **Active architecture decision"):
        assert text.startswith(WEB_NOTICE), "Unapproved change to the migration notice"
        text = text.removeprefix(WEB_NOTICE)
    text = text.replace(WEB_AUTHORITY, "").replace(WEB_TARGET, "")
    text = text.replace(
        "(Python 3.12/Pydantic/FastAPI backend; React/TypeScript/Vite/Tailwind/shadcn/ui "
        "frontend; Plotly.js charts)",
        "(`Python 3.12+`, `Pydantic v2`, `FastAPI`, `Pandas/NumPy`, `Plotly`, "
        "`Streamlit`, `Pytest`)",
    )
    if SEAMS_HEADING in text:
        text = text[: text.index(SEAMS_HEADING)]
    return text.rstrip("\n")


def _baseline_content(rel_path: str) -> str:
    """First committed version of the file (following renames), else the staged version."""
    log = _git("log", "--follow", "--name-only", "--format=%H", "--", rel_path)
    entries = [line for line in log.stdout.splitlines() if line.strip()]
    if len(entries) >= 2:
        first_sha, first_path = entries[-2], entries[-1]
        return _git("show", f"{first_sha}:{first_path}").stdout
    staged = _git("show", f":{rel_path}")
    assert staged.returncode == 0, f"{rel_path} is neither committed nor staged"
    return staged.stdout


@pytest.mark.parametrize("new_name", sorted(RELOCATIONS.values()))
def test_req_1_1_1_2_spec_files_exist_under_specs(new_name: str) -> None:
    assert (SPECS / new_name).is_file()


def test_req_1_3_corrections_ledger_exists() -> None:
    assert (SPECS / "07_DATA_CORRECTIONS.md").is_file()


def test_req_1_3_corrections_ledger_tracked_by_git() -> None:
    assert _git("ls-files", "--error-unmatch", "specs/07_DATA_CORRECTIONS.md").returncode == 0


@pytest.mark.parametrize("old_name", sorted(RELOCATIONS))
def test_req_1_4_1_5_old_paths_are_gone(old_name: str) -> None:
    for variant in _old_name_variants(old_name):
        assert not (ROOT / variant).exists(), f"old path still present: {variant}"


@pytest.mark.parametrize("new_name", sorted(RELOCATIONS.values()))
def test_req_1_4_1_5_relocated_files_are_tracked(new_name: str) -> None:
    rel = f"specs/{new_name}"
    assert _git("ls-files", "--error-unmatch", rel).returncode == 0, f"{rel} not tracked"


@pytest.mark.parametrize("new_name", sorted(RELOCATIONS.values()))
def test_req_1_4_git_log_follow_lists_history(new_name: str) -> None:
    """Req 1.4: once commits exist, `git log --follow` lists them on the new path.

    The files were untracked at relocation time (Req 1.5), so before the first
    commit they must be staged in the index and absent from HEAD.
    """
    rel = f"specs/{new_name}"
    history = _git("log", "--follow", "--format=%H", "--", rel).stdout.split()
    if history:
        return
    assert _git("ls-files", "--error-unmatch", rel).returncode == 0
    assert _git("cat-file", "-e", f"HEAD:{rel}").returncode != 0


@pytest.mark.parametrize("new_name", sorted(RELOCATIONS.values()))
def test_req_1_10_content_equals_original_after_replacements(new_name: str) -> None:
    rel = f"specs/{new_name}"
    expected = _normalise(_replace_old_names(_baseline_content(rel)))
    actual = _normalise((SPECS / new_name).read_text(encoding="utf-8"))
    assert actual == expected


def test_req_1_9_no_old_names_in_specs() -> None:
    hits: list[str] = []
    for path in sorted(SPECS.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for old in RELOCATIONS:
            for variant in _old_name_variants(old):
                if variant in text:
                    hits.append(f"{path.relative_to(ROOT)}: {variant}")
    assert hits == []


def test_req_1_6_package_layout() -> None:
    pkg = ROOT / "src" / "ai_tco_dss"
    assert (pkg / "__init__.py").is_file()
    assert (pkg / "settings.py").is_file()
    for name in SUBPACKAGES:
        assert (pkg / name).is_dir(), name
        assert (pkg / name / "__init__.py").is_file(), name


def test_req_1_8_test_directories() -> None:
    for name in TEST_DIRS:
        assert (ROOT / "tests" / name).is_dir(), name


REFERENCE_FILES = (
    "fx.json",
    "electricity.json",
    "staffing_hubs.json",
    "harnesses.json",
    "use_cases.json",
    "rentals.json",
)


def test_req_1_7_data_layout() -> None:
    data = ROOT / "data"
    assert (data / "sources.json").is_file()
    for name in ("catalog/hardware", "catalog/models", "benchmarks", "reference"):
        assert (data / name).is_dir(), name
    for name in REFERENCE_FILES:
        assert (data / "reference" / name).is_file(), name
    assert (data / "workloads" / "default.json").is_file()
