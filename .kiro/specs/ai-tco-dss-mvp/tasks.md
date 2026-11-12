# Implementation Plan: AI TCO DSS MVP

## Overview

**Revised 2026-11-07:** Tasks 1-7 are historical completed work. Tasks 8-13 below
replace the pending Streamlit implementation plan. Read
[the migration contract](../../../specs/09_WEB_FRONTEND_MIGRATION.md) and
[Stitch reference](../../../specs/08_MVP_DESIGN_REFERENCE.md) before working.
The original pending scopes are archived in specs/archive/STREAMLIT_TASKS_2026-11-07.md.
Existing Task 8 Python timeline functionality is reusable, but its UI was rejected.


The plan implements the design in 13 top-level tasks, in the order of `design.md` § "Task Slicing for Context Switching". The backend is Python 3.12; the target frontend is React/TypeScript (Requirement 43). Every task is test-first: its test sub-tasks come before its implementation sub-tasks. Each task ends with a Dashboard demo step (where engine or Service_Layer behaviour changes) and a progress update.

Conventions used by every task:

- **Task_Scope.** Each top-level task lists `Load` (files and sections, given as file path + section heading), `Modify` (explicit file or directory paths), `Covers` (criterion ids `N.M` from `requirements.md`), one `Verify` command line and one `Demo` step. Sub-tasks inherit the Task_Scope of their parent task. A session executes one top-level task, or resumes the task recorded as `in-progress` or `blocked` in `progress.md`.
- **Spec paths.** `requirements.md`, `design.md` and `tasks.md` mean the files under `.kiro/specs/ai-tco-dss-mvp/`.
- **Verification.** `uv run python scripts/verify.py <focus paths>` runs the focus tests (it skips a focus path that does not exist because an optional `*` test file was not written, and prints a notice), then `ruff check`, `ruff format --check`, `mypy`, the Validate_CLI (once the `ai-tco-validate` console script is declared in `pyproject.toml`) and the full `pytest` suite. It exits 0 only if every step passes. It works in PowerShell 5.1 and bash.
- **Property tests.** Each property from `design.md` § "Correctness Properties" is one sub-task and one `hypothesis` test (at least 100 examples) whose docstring names the property number and the criterion ids. Property tests for criteria that begin with "FOR ALL" or are labelled as a property are required by Requirement 41.5 and are not marked optional. All other property tests are marked optional with `*`; the task's required unit tests cover their criteria.
- **Project Rules.** The rules in `CLAUDE.md` § "Project Rules" apply from Task 2 onwards (Task 1 creates them).
- **Historical Streamlit skill convention (Tasks 1-7 only).** Every task that creates or changes files under `src/ai_tco_dss/ui/` or Dashboard tests that use AppTest (Tasks 5 to 12) first activates the `developing-with-streamlit` agent skill and follows the bundled references for the installed Streamlit version (`.kiro/steering/streamlit-ui.md`).

## Tasks

- [x] 1. Bootstrap toolchain and session artefacts
  - **Load:** `CLAUDE.md` (whole file); `requirements.md` § "Introduction", § "Glossary", § "Requirement 1: Repository Organisation", § "Requirement 2: Engineering Toolchain and Continuous Integration", § "Requirement 3: Progress File for Session Continuity", § "Requirement 4: Next Session Prompt and Self-Contained Tasks", § "Requirement 5: Global Project Rules", § "Requirement 6: Incremental Visible Progress", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Key Design Decisions", § "Module and File Layout", § "Session-Continuity Artefacts", § "Task Slicing for Context Switching", § "Testing Strategy" › "Tools and configuration"; `tasks.md` (whole file); `specs/00_INDEX_AND_AGENT_ROUTER.md` § "2. AI Coding Agent Context Router (Read Only What You Need)"
  - **Modify:** `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `README.md`, `scripts/verify.py`, `scripts/relocate_specs.py`, `CLAUDE.md` (append only), `.kiro/steering/project-rules.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `src/ai_tco_dss/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/domain/__init__.py`, `src/ai_tco_dss/catalog/__init__.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/decision/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/ui/__init__.py`, `src/ai_tco_dss/ui/app.py`, `tests/conftest.py`, `tests/unit/test_repository_layout.py`, `tests/unit/test_toolchain.py`, `tests/unit/test_session_artefacts.py`, `tests/unit/test_relocate_specs.py`, `tests/unit/test_offline_guard.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.10, 1.11, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3, 6.4, 41.1, 41.2, 41.8
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_repository_layout.py tests/unit/test_toolchain.py tests/unit/test_session_artefacts.py tests/unit/test_relocate_specs.py tests/unit/test_offline_guard.py tests/integration/test_app_smoke.py`
  - **Demo:** No engine or Service_Layer behaviour changes. `uv run streamlit run src/ai_tco_dss/ui/app.py` opens a placeholder start page titled "AI TCO DSS" with the caption "Catalog not loaded yet"; `uv run pytest` shows the layout and session-artefact tests green.

  - [x] 1.1 Write failing tests for repository layout and toolchain
    - `tests/unit/test_repository_layout.py`: `specs/00_…` to `specs/06_…` exist with the names of Req 1.1/1.2 and `specs/07_DATA_CORRECTIONS.md` exists; `src/ai_tco_dss/settings.py` and the six sub-packages with `__init__.py` exist; the four test directories exist; a case-sensitive search of `specs/` for the seven old file names (with and without ` (1)`) finds zero matches; each relocated spec file is tracked by git and `git log --follow` lists its history; each relocated file equals its first committed version after applying the Req 1.9 replacements, ignoring an appended `## Extension Seams (post-MVP)` section in `specs/00_INDEX_AND_AGENT_ROUTER.md` (added by Task 13 for Req 40.1)
    - `tests/unit/test_toolchain.py`: `pyproject.toml` declares `requires-python = ">=3.12,<3.13"`, runtime and dev dependencies (including `ruff`, `mypy`, `pytest`, `hypothesis`), `[tool.ruff]`, `[tool.mypy]` with `strict = true` and `[tool.pytest.ini_options]`; `uv.lock` exists and `uv lock --check` exits 0
    - Run the tests and observe the failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.10, 2.1, 2.2, 2.3_

  - [x] 1.2 Write failing tests for session artefacts
    - `tests/unit/test_session_artefacts.py` checks:
      - `progress.md`: the seven level-2 headings in order; one `Task Status` row per task id of `tasks.md`, no duplicates, titles as in `tasks.md`, status in {`not-started`, `in-progress`, `done`, `blocked`}, ISO date only for `done`; `Decisions Log` rows carry date, decision, rationale, affected ids; `Known Deviations` ids exist in `specs/07_DATA_CORRECTIONS.md` or the section states that no deviations are recorded; `Next Step` names the first `not-started` task id in `tasks.md` order; `Next Session Prompt` is exactly one fenced block of at most 50 lines that lists `CLAUDE.md`, `progress.md`, `requirements.md`, `design.md`, `tasks.md` in this order, names the same task id as `Next Step`, contains that task's Load and Modify items from `tasks.md`, and contains no placeholder (`<…>`, `TODO`, `TBD`); if no task is `not-started`, the prompt says so and lists the `in-progress`/`blocked` ids
      - `tasks.md`: every top-level task has `Load`, `Modify`, `Covers`, `Verify` and `Demo` lines; every `Covers` and `_Requirements_` id exists in `requirements.md`; every `Load` path exists in a hard-coded list of pre-Task-1 files or lies under a `Modify` path of an earlier task; no task text refers to prior conversation (phrases such as "as discussed", "earlier chat")
      - `CLAUDE.md`: exactly one `## Project Rules` heading after the original content; the text above it has the SHA-256 of the original file (recorded in the test before the append); the section has eight numbered rules
      - `.kiro/steering/project-rules.md`: front matter delimited by `---` containing `inclusion: always`; the same eight rule items, same order, identical wording after whitespace trimming
      - `specs/07_DATA_CORRECTIONS.md`: sections `Entries`, `Contract Deviations`, `Okabe-Ito Archetype Mapping`, `Calibration Known Deviations`, `Assumptions`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 41.1, 41.2_

  - [x] 1.3 Write failing tests for the spec relocation script
    - `tests/unit/test_relocate_specs.py` uses a temporary git repository: a tracked file is moved with `git mv` and `git log --follow` on the new path lists the old commit; an untracked file is moved, added under the new path and the old path is gone; an existing target leaves both files unchanged, prints the conflicting path and exits non-zero; running on the real repository is a no-op because all targets already exist and no source remains
    - _Requirements: 1.4, 1.5, 1.11_

  - [x] 1.4 Write the offline guard, hypothesis profile and placeholder smoke test
    - `tests/conftest.py`: autouse session fixture that makes `socket.socket.connect` raise; hypothesis profile `default` with `max_examples=100`, `deadline=None`, loaded for every run
    - `tests/unit/test_offline_guard.py`: a connect attempt raises
    - `tests/integration/test_app_smoke.py`: `streamlit.testing.v1.AppTest.from_file("src/ai_tco_dss/ui/app.py")` runs within 30 s with no exception
    - _Requirements: 6.4, 41.8_

  - [x] 1.5 Create `pyproject.toml` and `uv.lock` with uv
    - Package `ai-tco-dss`, src layout (`src/ai_tco_dss`), build backend hatchling, `requires-python = ">=3.12,<3.13"`, `.python-version` = `3.12`
    - `uv add pydantic pydantic-settings streamlit plotly pandas numpy`; `uv add --dev pytest hypothesis ruff mypy pandas-stubs`; `uv lock`
    - Configure `[tool.ruff]` (lint + format, `src/` and `tests/`), `[tool.mypy]` (`strict = true`, `files = ["src/ai_tco_dss"]`, pydantic plugin), `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["src"]`)
    - `.gitignore`: `.venv/`, caches (`__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.hypothesis`), `reports/*` except `reports/.gitkeep`
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 1.6 Create the package skeleton and placeholder Dashboard
    - `__init__.py` in `src/ai_tco_dss/` and in `domain`, `catalog`, `engines`, `decision`, `services`, `ui`
    - `src/ai_tco_dss/settings.py`: module docstring and an empty typed skeleton (Task 2 fills it)
    - `src/ai_tco_dss/ui/app.py`: `st.title("AI TCO DSS")` and `st.caption("Catalog not loaded yet")`; no import from `engines`, `decision` or `catalog`
    - Make ruff and mypy pass on the skeleton
    - _Requirements: 1.6, 2.4, 2.5, 6.4_

  - [x] 1.7 Create `scripts/verify.py`, `scripts/relocate_specs.py` and README commands
    - `scripts/verify.py` per the Overview conventions (D-12): focus tests → `ruff check` → `ruff format --check` → `mypy` → Validate_CLI if declared → full `pytest`; prints each step name; exits with the first non-zero code
    - `scripts/relocate_specs.py`: the old→new mapping of Req 1.1/1.2; `git mv` for tracked files, move + `git add` for untracked files, conflict check before any change, cross-reference replacement of Req 1.9 in `specs/`; idempotent
    - `README.md`: one single-line command each for the tests (`uv run pytest`), task verification (`uv run python scripts/verify.py`) and the Dashboard (`uv run streamlit run src/ai_tco_dss/ui/app.py`)
    - _Requirements: 1.4, 1.5, 1.9, 1.11, 2.4, 2.5, 6.3_

  - [x] 1.8 Append Project Rules to `CLAUDE.md` and create the steering file
    - Append `## Project Rules` with the eight rules from `design.md` § "Session-Continuity Artefacts" › "`CLAUDE.md` — appended section" after the last existing line; change no existing line
    - Create `.kiro/steering/project-rules.md` with front matter `inclusion: always` and the identical eight items
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 41.1, 41.2_

  - [x] 1.9 Create the Corrections_Ledger `specs/07_DATA_CORRECTIONS.md`
    - Use `design.md` § "Session-Continuity Artefacts" › "`specs/07_DATA_CORRECTIONS.md` template": entries C-001 to C-015, empty `Contract Deviations` table, the Okabe-Ito table from `design.md` § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", empty `Calibration Known Deviations` table, the `Assumptions` table
    - Do not write any of the seven old spec file names into the ledger (the Req 1.9 search covers `specs/`)
    - _Requirements: 1.3, 3.5_

  - [x] 1.10 Create `progress.md`
    - Seven sections in the order of Req 3.1; `Task Status` with one row per task id of this `tasks.md` (all `not-started`, task 1 rows `in-progress`); `Decisions Log` with D-01 to D-12, the three accepted open points (Task 5 combines workload and sizing; CSV export as one ZIP per D-11 and C-012; multi-node decode per Req 20.1 per D-08 and C-011) and the placeholder Dashboard in Task 1; `Known Deviations` referencing C-009, C-011 and C-012; `Next Step` = Task 2; `Next Session Prompt` for Task 2 with Task 2's Load and Modify items copied from this file
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 4.1, 4.5_

  - [x] 1.11 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Set all task 1 rows to `done` with today's date, describe the state in `Current Status`, append the Changelog entry with all files created, keep `Next Step` and the prompt on Task 2
    - Run the Task 1 `Verify` command; it must exit 0
    - _Requirements: 3.3, 4.2, 6.4, 41.2_

- [x] 2. Domain contracts and schema export
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Glossary", § "Requirement 7: Domain Contracts", § "Requirement 12: Currency and FX Conversion", § "Requirement 40: Extension Seams for Post-MVP Features"; `design.md` § "Domain base (`domain/base.py`)", § "Settings (`settings.py`)", § "Engine call convention", § "Data Models" (all subsections), § "Error Handling", § "Correctness Properties" › "Property 1" and "Property 6"; `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (whole file); `specs/07_DATA_CORRECTIONS.md` § "Contract Deviations"
  - **Modify:** `src/ai_tco_dss/domain/`, `src/ai_tco_dss/settings.py`, `pyproject.toml`, `uv.lock`, `schemas/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_contracts.py`, `tests/unit/test_schema_export.py`, `tests/property/strategies.py`, `tests/property/test_contract_props.py`
  - **Covers:** 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 12.7, 40.2, 40.4, 40.5
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_contracts.py tests/unit/test_schema_export.py tests/property/test_contract_props.py`
  - **Demo:** No engine or Service_Layer behaviour changes. `uv run ai-tco-schemas` writes `schemas/*.json`; a second run leaves `git status --short schemas/` empty.

  - [x] 2.1 Write failing unit tests for the contracts
    - `tests/unit/test_contracts.py`: every contract class has `frozen=True` and `extra="forbid"`; assignment raises a `ValidationError` naming the field and keeps the value; unknown field, constraint violation, missing field and wrong type each raise an error naming the field (and the constraint); a minimal `BenchmarkRecord` with only Glossary fields validates; missing or invalid `source_id`, `tier`, `accessed` raise errors naming each field; every field name, enum member or default differing from the code block in `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (parsed with `ast`) has a row in the ledger's `Contract Deviations` table
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 40.4, 40.5_

  - [x] 2.2 Write failing tests for the schema export
    - `tests/unit/test_schema_export.py`: the command creates `schemas/` if missing and writes one file per Service_Layer request/result contract, each valid JSON with `title` = class name; two runs give byte-identical files and exit 0; a contract whose schema generation fails (monkeypatched) makes the command exit non-zero and print the contract name
    - _Requirements: 7.8, 7.9, 7.10, 40.2_

  - [x] 2.3 Write property test for contract JSON round trip
    - **Property 1: Contract JSON round trip** (required by Req 41.5)
    - **Validates: Requirements 7.11**
    - Create `tests/property/strategies.py` with generators for every contract within the requirement bounds, including boundary values; test in `tests/property/test_contract_props.py`

  - [x] 2.4 Write property test for FX round trip
    - **Property 6: FX round trip** (required by Req 41.5)
    - **Validates: Requirements 12.7**
    - Test in `tests/property/test_contract_props.py` against `domain/money.py`

  - [x] 2.5 Implement domain base, enums, errors and money helpers
    - `domain/base.py` (`Contract`, `SourceTier`, `TIER_RANK`, `Sourced[T]`, `Money`, `ValueOrigin`, `Metric`, `FormulaTrace`), `domain/enums.py` (spec 04 enums without `ElectricityTariffTier.CUSTOM`, plus the new enums), `domain/errors.py` (DssError hierarchy), `domain/money.py` (`usd_to_eur`, `eur_to_usd`, `round_display`)
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 12.7_

  - [x] 2.6 Implement catalog and scenario contracts and `EngineParameters`
    - `domain/catalog.py` and `domain/scenario.py` per `design.md` § "Catalog contracts" and § "Scenario contracts"; tuples only for collections (D-03); validators for `SourceEntry` url/reference, `ModelSpec` api fields, `fx_override` decimals
    - `settings.py`: `Settings(BaseSettings)` with prefix `AI_TCO_` and the defaults of `design.md` § "Settings (`settings.py`)"; `load_engine_parameters()` returns `EngineParameters` and raises `ConfigurationError` for out-of-range values
    - _Requirements: 7.2, 7.5, 7.7, 40.4, 40.5_

  - [x] 2.7 Implement result, input and request contracts
    - `domain/results.py`, `domain/inputs.py`, `domain/requests.py` per `design.md` § "Result contracts" and § "Engine call convention"; re-export public contracts from `domain/__init__.py`
    - _Requirements: 7.2, 7.11_

  - [x] 2.8 Implement the schema export command
    - `domain/export_schemas.py`; console script `ai-tco-schemas` in `pyproject.toml`; `json.dumps(sort_keys=True, indent=2)` plus trailing newline; exit 1 with the contract name on failure; generate and add `schemas/`
    - _Requirements: 7.8, 7.9, 7.10, 40.2_

  - [x] 2.9 Record contract deviations in the ledger
    - Add one `Contract Deviations` row (contract, field, old, new, sources, date) for every change listed in `design.md` § "Scenario contracts" and § "Enumerations" (e.g. `currency` EUR→USD, removed `CUSTOM` tariff, renamed `max_capex_budget_usd`)
    - _Requirements: 7.7_

  - [x] 2.10 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Next task: Task 3 with its Load and Modify items; run the Task 2 `Verify` command
    - _Requirements: 3.3, 4.2_

- [x] 3. Catalog repository, Validate_CLI, seed subset and Dashboard skeleton
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 1: Repository Organisation", § "Requirement 6: Incremental Visible Progress", § "Requirement 8: Source Registry and Provenance", § "Requirement 9: Benchmark Records and Measured-First Resolution", § "Requirement 11: Extensible Catalog Files and Validate CLI", § "Requirement 12: Currency and FX Conversion", § "Requirement 13: Reference Data", § "Requirement 37: Visual Accessibility and UI Architecture", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 39: Concurrency and Performance Budget"; `design.md` § "Key Design Decisions", § "Concurrency Model", § "Catalog port (`catalog/repository.py`)", § "Validate_CLI (`catalog/validate.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "JSON file formats", § "Correctness Properties" › "Property 2", "Property 3", "Property 5"; `specs/03_CALIBRATED_2026_SEED_DATA.md` § "2. Calibrated 2026 Hardware Seed Catalog", § "3. Calibrated 2026 Model Seed Catalog", § "4. Intra-EU Engineering Compensation & FinOps Seed Table"; `specs/06_RESEARCH_SOURCES.md` § "1. Primary Empirical Video Benchmark Citations", § "2. Industry Technical Standards, Empirical Whitepapers & Regulatory References"; `src/ai_tco_dss/domain/`; `src/ai_tco_dss/settings.py`
  - **Modify:** `src/ai_tco_dss/catalog/`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/app.py`, `src/ai_tco_dss/ui/state.py`, `data/sources.json`, `data/catalog/README.md`, `data/catalog/hardware/`, `data/catalog/models/`, `data/benchmarks/`, `data/reference/`, `data/workloads/default.json`, `pyproject.toml`, `uv.lock`, `README.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/fixtures/catalog_min/`, `tests/unit/test_validate_cli.py`, `tests/unit/test_repository.py`, `tests/unit/test_import_boundaries.py`, `tests/unit/test_repository_layout.py`, `tests/property/test_catalog_props.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 1.7, 6.1, 6.4, 6.5, 8.1, 8.3, 8.4, 8.5, 8.7, 8.8, 8.9, 8.10, 9.1, 9.2, 9.8, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 12.2, 12.3, 12.4, 12.9, 13.8, 37.7, 37.8, 38.3, 38.6, 39.1, 39.2, 39.3
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_validate_cli.py tests/unit/test_repository.py tests/unit/test_import_boundaries.py tests/unit/test_repository_layout.py tests/property/test_catalog_props.py tests/integration/test_app_smoke.py`
  - **Demo:** Start page (Dashboard, no inputs) shows "Catalog: 2 hardware, 2 models" and the FX rate 1.1165 USD/EUR with source `ECB-FX`. Deleting a `source_id` entry from `data/sources.json` makes `uv run ai-tco-validate` print one error line per dangling reference plus the total, and exit 1.

  - [x] 3.1 Create the minimal fixture catalog and write failing Validate_CLI tests
    - `tests/fixtures/catalog_min/`: two hardware, two models, one benchmark file, all reference files, `sources.json`, `workloads/default.json`, all valid
    - `tests/unit/test_validate_cli.py` (copies the fixture to `tmp_path` and injects faults): source entry fields and tiers; duplicate `source_id`; unknown `source_id`; missing provenance; YT tier/`single-source` rule; invalid tier, bad date format, future date; missing or < 1 `context_tokens`; unparseable JSON with line:column; duplicate ids across folders; filename-id mismatch; dangling `model_id`/`hardware_id`; reference bounds; error line format `path: field_path: message`, total count, exit 1; success summary per file type and exit 0
    - _Requirements: 8.1, 8.4, 8.5, 8.7, 8.8, 8.9, 8.10, 9.1, 9.2, 9.8, 11.3, 11.4, 11.5, 11.6, 11.8, 11.9, 12.2, 13.8_

  - [x] 3.2 Write failing repository tests
    - `tests/unit/test_repository.py`: one file per item named `<id>.json`; a new valid file appears on the next repository instance and non-`.json` files are ignored; an invalid file raises `CatalogLoadError` with file and field path and no partial Catalog; EUR money is returned as USD (`× rate`); `fx.json` missing/non-positive/bad date/unknown source raises naming `fx.json` and the field; `get_default_repository()` reads files once (spy on the loader) and returns the same instance; assigning a catalog field raises and leaves values unchanged; `data/catalog/README.md` examples validate against `HardwareSpec`/`ModelSpec`
    - _Requirements: 11.1, 11.2, 11.7, 11.10, 12.3, 12.9, 38.3, 39.1, 39.2, 39.3_

  - [x] 3.3 Write failing import-boundary tests
    - `tests/unit/test_import_boundaries.py`: AST scan of every `src/ai_tco_dss/ui/*.py`; any import of `ai_tco_dss.engines`, `ai_tco_dss.decision` or `ai_tco_dss.catalog` (or submodules) fails with `"<file>: forbidden import <name>"`; a synthetic module checks the message
    - _Requirements: 37.7, 37.8, 38.6_

  - [x] 3.4 Extend the smoke and layout tests
    - `tests/integration/test_app_smoke.py`: the start page renders within 30 s, without exception, and shows the hardware and model counts obtained from `catalog_overview`
    - `tests/unit/test_repository_layout.py`: add the Req 1.7 checks (`data/sources.json`, the four data directories, six reference files, `data/workloads/default.json`)
    - _Requirements: 1.7, 6.1, 6.4, 6.5_

  - [x]* 3.5 Write property test for provenance coverage
    - **Property 2: Provenance coverage**
    - **Validates: Requirements 8.3, 8.5**
    - File: `tests/property/test_catalog_props.py`

  - [x]* 3.6 Write property test for validator fault reporting
    - **Property 3: Validator reports every injected fault in one run**
    - **Validates: Requirements 8.10, 11.3**
    - File: `tests/property/test_catalog_props.py`

  - [x]* 3.7 Write property test for repository FX conversion
    - **Property 5: Repository FX conversion**
    - **Validates: Requirements 12.3, 12.4**
    - File: `tests/property/test_catalog_props.py`

  - [x] 3.8 Implement catalog loading and FX conversion
    - `catalog/loading.py`: raw JSON read with parse errors, provenance walker (D-02), contract validation with field paths, filename/duplicate/cross-reference checks, error collection without early stop
    - `catalog/fx.py`: `convert_catalog(catalog, rate)` returns a USD catalog with `fx_source_id` and `original_value`
    - _Requirements: 8.3, 8.4, 8.5, 8.9, 9.8, 11.3, 11.5, 11.6, 11.8, 12.3_

  - [x] 3.9 Implement the Validate_CLI
    - `catalog/validate.py` with the check order of `design.md` § "Validate_CLI"; console script `ai-tco-validate`; README command `uv run ai-tco-validate`
    - _Requirements: 8.1, 8.7, 8.8, 8.10, 11.4, 11.9, 13.8_

  - [x] 3.10 Implement the repositories
    - `catalog/repository.py` (Protocol), `catalog/json_repository.py` (`JsonCatalogRepository`, lock-guarded `get_default_repository()`, FX-override cache of 8), `catalog/memory_repository.py`; `catalog/__init__.py` exports
    - _Requirements: 11.1, 11.2, 11.10, 12.3, 12.4, 12.9, 38.3, 39.1, 39.2, 39.3_

  - [x] 3.11 Write the seed data subset
    - `data/sources.json` with YT entries present in `specs/06` (tier `community`), IND-01 to IND-10, `ECB-FX`, `ASSUMPTION-MVP`, `ASSUMPTION-WORKLOAD-DEFAULT`; two hardware files (`mac-studio-m5-max-128gb`, `rtx-pro-6000-96gb`), two model files, `data/benchmarks/quality.json` seed, all `data/reference/*.json` of `design.md` § "JSON file formats", `data/workloads/default.json`; `data/catalog/README.md` with one annotated hardware and one model example (meaning, unit, required/optional per field)
    - `uv run ai-tco-validate` reports 0 errors
    - _Requirements: 1.7, 8.1, 8.3, 8.7, 9.1, 11.1, 11.7, 12.2_

  - [x] 3.12 Implement `catalog_overview` and the Dashboard skeleton
    - `services/scenario_service.py` + `services/__init__.py`: `catalog_overview(repo=None, fx_override=None)` returning `CatalogOverview`
    - `ui/state.py` (session keys) and `ui/app.py`: start page via `@st.cache_resource`-wrapped service access showing counts and FX rate; catalog load errors shown with `st.error`
    - _Requirements: 6.1, 6.4, 38.3, 38.6_

  - [x] 3.13 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; if the Dashboard does not start cleanly, keep the task not done and record the failure in `Known Deviations`
    - Next task: Task 4; run the Task 3 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4, 6.5_

- [x] 4. Curated MVP catalog with web-verified values
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 8: Source Registry and Provenance", § "Requirement 10: Curated MVP Catalog Contents", § "Requirement 13: Reference Data", § "Requirement 14: Workload Profile and Explicit Assumptions", § "Requirement 31: Use Cases and Quality Floors", § "Requirement 32: Presets and Popularity Snapshot"; `design.md` § "Research Findings That Shape the Design", § "Validate_CLI (`catalog/validate.py`)", § "JSON file formats", § "Decision constants (Reference_Data, all `assumption`)", § "Session-Continuity Artefacts"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "1. The Four Cloud Comparison Baselines", § "2.2 Industrial vs. Office Electricity & Cooling PUE", § "2.5 Intra-EU Engineering Salary Arbitrage (Munich HQ vs. Romania EU Branch)"; `specs/03_CALIBRATED_2026_SEED_DATA.md` (whole file); `specs/06_RESEARCH_SOURCES.md` (whole file); `specs/07_DATA_CORRECTIONS.md` (whole file); `data/` (whole directory); `src/ai_tco_dss/catalog/validate.py`; `src/ai_tco_dss/catalog/loading.py`
  - **Modify:** `data/`, `src/ai_tco_dss/catalog/validate.py`, `src/ai_tco_dss/catalog/loading.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_mvp_catalog.py`, `tests/unit/test_reference_data.py`, `tests/property/test_preset_validator_props.py`
  - **Covers:** 8.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 31.2, 31.3, 32.1, 32.2, 32.3, 32.4, 32.5, 32.6, 32.8
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_mvp_catalog.py tests/unit/test_reference_data.py tests/property/test_preset_validator_props.py`
  - **Demo:** Start page (Dashboard, no inputs) shows "Catalog: 9 hardware, 12 models, 2 rentals". Removing `data/catalog/models/gpt-oss-120b.json` makes `uv run ai-tco-validate` report the missing MVP item `gpt-oss-120b` and exit 1.

  - [x] 4.1 Write failing MVP catalog tests
    - `tests/unit/test_mvp_catalog.py`: exactly the 8 open-weights and 4 API model files and the 9 hardware files of Req 10; gpt-oss-120b MoE 117B/5.1B with provenance; API prices > 0 with tier `official`; valid node counts per Req 10.5; GEX63/GEX430 prices and setup fees; non-empty license types and `eu_commercial_license_valid = false` for the Llama 4 license; quality scores in [0, 100] with registered sources and no zero placeholders; ledger entries for gpt-oss-120b and GEX63; YT entries `community`, IND tiers by publisher type; the validator reports a removed MVP item or a missing required provenance and exits non-zero
    - _Requirements: 8.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11_

  - [x] 4.2 Write failing reference data tests
    - `tests/unit/test_reference_data.py`: three tariffs with values and bounds; four hubs with salary, tax (0–100), delay (0–24) each sourced; harness tokens incl. `custom-lean` assumption; four use cases with benchmarks per Req 31.2 and `assumption` floors in [0, 100]; rentals equal to Req 10.6; Romania tax equals the chosen ledger value; default workload values with `assumption` provenance; four presets with six weights in [0, 1] summing to 1 ± 1e-6 and the dominance rules of Req 32.2–32.5; popularity snapshot date, provenance, unique ids, values ≥ 0
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 31.2, 31.3, 32.1, 32.2, 32.3, 32.4, 32.5, 32.6_

  - [x]* 4.3 Write property test for preset and popularity validation
    - **Property 52: Preset and popularity validation**
    - **Validates: Requirements 32.8**
    - File: `tests/property/test_preset_validator_props.py`

  - [x] 4.4 Add MVP completeness, preset and popularity rules to the Validate_CLI
    - MVP completeness (Req 10.11) runs only for the repository `data/` root, so the fixture catalog of Task 3 still validates; preset and popularity rules (Req 32.8)
    - _Requirements: 10.11, 32.8_

  - [x] 4.5 Web-verify and write the nine hardware files
    - Fetch vendor pages (NVIDIA, Apple, AMD) for memory, bandwidth, power, prices; record `accessed` dates; YouTube values stay `community` + `single-source`; add every new source to `data/sources.json`
    - _Requirements: 8.3, 10.4, 10.5_

  - [x] 4.6 Web-verify and write the eight open-weights model files and quality records
    - Hugging Face `config.json` for layers, KV heads, head dim, context; parameter counts; licenses; OpenRouter `/api/v1/models` for open-weights output prices; AA v5, Terminal-Bench, SWE-bench scores in `data/benchmarks/quality.json`; register sources
    - _Requirements: 10.1, 10.2, 10.7, 10.8_

  - [x] 4.7 Web-verify and write the four commercial API model files
    - Official pricing pages (Anthropic, OpenAI, Google) for input, output and cache-read prices; EU-pinned endpoint availability; context length; register sources
    - _Requirements: 10.3, 10.7, 10.8_

  - [x] 4.8 Web-verify and write the reference data
    - `rentals.json` (Hetzner GEX63/GEX430 pages, re-check the 15 June 2026 price change), `fx.json` (ECB), `electricity.json`, `staffing_hubs.json` (ANAF CAM for Romania), `harnesses.json`, `use_cases.json`, `presets.json` and `baselines.json` per `design.md` § "Decision constants", `popularity.json` (OpenRouter rankings snapshot); register sources
    - _Requirements: 8.2, 10.6, 13.1, 13.2, 13.3, 13.4, 13.5, 14.1, 31.2, 31.3, 32.1, 32.6_

  - [x] 4.9 Update the Corrections_Ledger for the curated data
    - Confirm or update C-001, C-002, C-003 (2.25 % chosen), C-013, C-014; resolve C-010 and C-015; add an entry for every contradiction found while verifying; add or update the data-related `Assumptions` rows (FX rate, quality floors, preset weights, gateway fee, reference API model)
    - _Requirements: 10.9, 10.10, 13.6_

  - [x] 4.10 Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Ensure all tests pass, ask the user if questions arise
    - Next task: Task 5; run the Task 4 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [x] 5. Workload and Sizing engines, `size` service and View 1 card
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 14: Workload Profile and Explicit Assumptions", § "Requirement 15: Effective Token Volume Computation", § "Requirement 16: Usable Memory and Operating System Traps", § "Requirement 17: Weights, KV Cache, KV Pool and Concurrency", § "Requirement 18: Multi-Node Topology and Tiered Offload", § "Requirement 19: Quality, License and Context Flags", § "Requirement 35: Views 1 and 2", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Engine call convention", § "Workload_Engine (`engines/workload.py`)", § "Sizing_Engine (`engines/sizing.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", § "Correctness Properties" › "Workload and sizing", § "Testing Strategy"; `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` § "1.1 Token Volume, Tokenizer Inflation, Thinking Effort & Verification Multipliers", § "1.2 Agentic Harness Scaffolding ($S_{\text{harness}}$), MCP Pruning & Mega-Sessions", § "1.3 Multi-Agent State Retention vs. The Conversational Eviction Tax", § "Stage 1: Memory Architecture, OS Split Traps, Attention Formats & 3-Tier Offload", § "Stage 3: Quantization Fidelity, 6-Layer Harnesses & Hardware Lifecycle Clocks", § "Stage 4: Multi-Node Topologies, Disaggregation & Heterogeneous Routing"; `src/ai_tco_dss/domain/`; `src/ai_tco_dss/catalog/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`; `data/`
  - **Modify:** `src/ai_tco_dss/engines/workload.py`, `src/ai_tco_dss/engines/sizing.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/catalog/json_repository.py`, `src/ai_tco_dss/catalog/memory_repository.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/theme.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_workload.py`, `tests/unit/test_sizing.py`, `tests/unit/test_engine_purity.py`, `tests/unit/test_charts.py`, `tests/property/test_workload_props.py`, `tests/property/test_sizing_props.py`, `tests/property/test_ui_props.py`
  - **Covers:** 14.2, 14.3, 14.4, 14.6, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11, 17.12, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 35.1, 35.2, 35.3, 35.8, 35.9, 35.11, 37.1, 38.2, 41.3, 41.4
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_workload.py tests/unit/test_sizing.py tests/unit/test_engine_purity.py tests/unit/test_charts.py tests/property/test_workload_props.py tests/property/test_sizing_props.py tests/property/test_ui_props.py`
  - **Demo:** View 1 tab, memory-fit card: select hardware "Mac Studio (M5 Max 128GB)", model "Qwen 3.8 Flash Next", precision INT4, target context 8 192, override off → the bar exceeds the 103.04 GB usable line, the pairing is infeasible and the warning shows `sudo sysctl iogpu.wired_limit_mb=117760`; switch the Mac wired-memory override on → the line moves to 115 GB and the pairing is feasible. AA labels show "n/a" until Task 6.

  - [x] 5.1 Write failing Workload_Engine tests
    - `tests/unit/test_workload.py`: Default_Workload_File reference values (22 000 requests, κ_mega 1.98, T̂_in 48 000 / 62 400, out_think 3 750 / 4 875, monthly tokens 2 254 230 000 / 2 930 499 000, output demand 82 500 000); `working_days_per_month` bounds and default; workload field bounds; `load_workload` with another file uses only that file plus defaults; missing path, invalid JSON and out-of-range fields raise `WorkloadFileError` naming path and fields; invalid mega ratio, negative tokens and unknown thinking preset are rejected
    - _Requirements: 14.2, 14.3, 14.4, 14.6, 14.7, 15.8_

  - [x] 5.2 Write failing Sizing_Engine tests
    - `tests/unit/test_sizing.py`: `test_req_16_6_mac_128gb_trap` (103 GB infeasible / 115 GB feasible, trap flag true in both, exact flag equality, ≤ 1.0 GB deviation or ledger entry); `test_req_17_10_deepseek_mla_1m` (`M_kv_single == 0.89` within 5 % and strictly `< 0.9`); missing override fields fall back with warning; bound violations name field and hardware id; missing KV parameters name model id and parameters; α_scaling values; Thunderbolt cables 0/1/6/28; exactly one Strata warning; agreement rate exactly 0.90 gives no warning
    - _Requirements: 16.6, 16.8, 16.9, 17.10, 17.12, 18.4, 18.5, 18.9, 19.4, 41.3, 41.4_

  - [x] 5.3 Write failing engine purity tests
    - `tests/unit/test_engine_purity.py`: `no_io` fixture blocks `open`, `Path.open/read_text` and sockets while `compute_workload` and `size_deployment` run and the results equal unblocked runs; AST check that `engines/` and `decision/` import only `ai_tco_dss.domain` and the standard library and declare no module-level `list`, `dict` or `set`
    - _Requirements: 38.2_

  - [x] 5.4 Write failing View 1 chart tests
    - `tests/unit/test_charts.py`: `memory_fit_figure` example with one Mac and one discrete GPU pairing (segments order, VRAM line, system-RAM line only where present, "EVICTION RISK" badge and hatch, "n/a" labels); empty input returns a figure without data traces and a "No data available" annotation; the module imports no file, network or Streamlit API
    - _Requirements: 35.1, 35.2, 35.3, 35.8, 35.9, 35.11_

  - [x]* 5.5 Write property test for workload formulas
    - **Property 9: Workload formulas**
    - **Validates: Requirements 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 15.7**
    - File: `tests/property/test_workload_props.py`

  - [x] 5.6 Write property test for workload monotonicity
    - **Property 10: Workload monotonicity** (required by Req 41.5)
    - **Validates: Requirements 15.6**
    - File: `tests/property/test_workload_props.py`

  - [x]* 5.7 Write property test for usable memory by architecture
    - **Property 11: Usable memory by architecture**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.8 Write property test for the Mac default-split trap
    - **Property 12: Mac default-split trap**
    - **Validates: Requirements 16.5, 16.7**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.9 Write property test for weight and KV-per-token formulas
    - **Property 13: Weight and KV-per-token formulas**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.10 Write property test for KV pool, concurrency and OOM
    - **Property 14: KV pool, concurrency and OOM**
    - **Validates: Requirements 17.5, 17.6, 18.3, 18.6**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.11 Write property test for memory breakdown and eviction flag
    - **Property 15: Memory breakdown and eviction flag**
    - **Validates: Requirements 17.7, 17.8, 17.11**
    - File: `tests/property/test_sizing_props.py`

  - [x] 5.12 Write property test for memory monotonicity
    - **Property 16: More memory never hurts** (required by Req 41.5)
    - **Validates: Requirements 17.9**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.13 Write property test for node-count handling
    - **Property 17: Node-count handling**
    - **Validates: Requirements 18.1, 18.2, 18.7, 18.8**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.14 Write property test for quality, license and context flags
    - **Property 18: Quality, license and context flags never change feasibility**
    - **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7**
    - File: `tests/property/test_sizing_props.py`

  - [x]* 5.15 Write property test for View 1 chart structure
    - **Property 54: View 1 chart structure**
    - **Validates: Requirements 35.1, 35.2, 35.3, 35.8, 35.9, 37.1**
    - File: `tests/property/test_ui_props.py`

  - [x] 5.16 Implement the Workload_Engine and workload loading
    - `engines/workload.py`: `compute_workload(WorkloadInput, EngineParameters) -> WorkloadResult` with the formulas of `design.md` § "Workload_Engine"
    - `load_workload(path)` in `catalog/json_repository.py` and `catalog/memory_repository.py`
    - _Requirements: 14.3, 14.4, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

  - [x] 5.17 Implement the Sizing_Engine
    - `engines/sizing.py`: `size_deployment(SizingInput, EngineParameters) -> SizingResult` following steps 1–11 of `design.md` § "Sizing_Engine", with `FormulaTrace`s for usable memory, weights, KV and pool; record any Req 16.6 deviation above 1.0 GB in the ledger
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11, 17.12, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_

  - [x] 5.18 Implement the `size` service
    - `services/scenario_service.py` + `services/__init__.py`: `size(SizeRequest, repo=None) -> SizeResult` (validates the request, checks ids, builds inputs, `performance=None` until Task 6); export from `services`
    - _Requirements: 14.3, 38.2_

  - [x] 5.19 Implement the View 1 chart and card
    - `ui/theme.py` Okabe-Ito constants; `ui/charts.py` `memory_fit_figure(pairings, display)`; `ui/cards.py` `memory_fit_card()` decorated with `@st.fragment` (hardware/model multiselects, precision, context, override toggles; calls `size` per pairing; increments `render_counts["memory_fit"]`); `ui/app.py` View 1 tab
    - _Requirements: 35.1, 35.2, 35.3, 35.8, 35.9, 35.11, 37.1_

  - [x] 5.20 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 6; run the Task 5 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [x] 6. Performance engine, measured-first resolver and calibration
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 9: Benchmark Records and Measured-First Resolution", § "Requirement 20: Decode Throughput", § "Requirement 21: Prefill, TTFT and Effective Throughput", § "Requirement 42: Calibration Tests and Calibration Report"; `design.md` § "Settings (`settings.py`)", § "Measured-first resolver (`engines/resolver.py`)", § "Performance_Engine (`engines/performance.py`)", § "Service Layer (`services/`)", § "Correctness Properties" › "Performance" and "Service layer and calibration", § "Testing Strategy" › "Calibration tests (`tests/calibration/`)"; `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` § "Stage 2: Memory Bandwidth (Decode) vs. Compute (Prefill) & The MoE Law"; `specs/07_DATA_CORRECTIONS.md` § "Calibration Known Deviations"; `src/ai_tco_dss/settings.py`; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/cards.py`; `data/benchmarks/`
  - **Modify:** `src/ai_tco_dss/engines/resolver.py`, `src/ai_tco_dss/engines/performance.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/services/calibration_report.py`, `src/ai_tco_dss/ui/cards.py`, `pyproject.toml`, `README.md`, `.gitignore`, `reports/.gitkeep`, `data/benchmarks/`, `data/sources.json`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_performance.py`, `tests/unit/test_settings.py`, `tests/unit/test_calibration_report.py`, `tests/calibration/test_calibration.py`, `tests/property/test_performance_props.py`, `tests/property/test_calibration_props.py`
  - **Covers:** 9.3, 9.4, 9.5, 9.6, 9.9, 9.10, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 42.1, 42.2, 42.3, 42.4, 42.5, 42.6, 42.7
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_performance.py tests/unit/test_settings.py tests/unit/test_calibration_report.py tests/calibration tests/property/test_performance_props.py tests/property/test_calibration_props.py`
  - **Demo:** View 1 tab, memory-fit card: select "Mac Mini M5 Pro 64GB" + "Qwen 3.8-27B", INT4, context 8 192 → the performance rows show decode TPS with the value of the matching record in `data/benchmarks/decode.json` labelled `measured` with its `source_id` (e.g. YT-21), and TTFT and effective TPS labelled `formula`; the bar label shows the AA v5 score. `uv run ai-tco-calibrate` prints record counts and MAPE for decode and prefill TPS and writes `reports/calibration.csv`.

  - [x] 6.1 Write failing Performance_Engine tests
    - `tests/unit/test_performance.py`: measured decode used and labelled `measured`; record outside tolerance falls back to formula; quality record resolved without hardware/context; η defaults 0.70/0.425; γ defaults per mode with `none` default; invalid bandwidth, `P_active`, bits or mode rejected naming the field; prefill fallback to `base_prefill_tps_at_32k`; 1M prefill order with overestimation warning; no prefill data → TTFT, effective TPS, 1M prefill `None` plus warning; `out_think = 0` → effective TPS 0 with TTFT; `r_cache` outside [0, 1] rejected
    - _Requirements: 9.4, 9.6, 9.9, 20.2, 20.3, 20.7, 21.1, 21.5, 21.7, 21.8, 21.9_

  - [x] 6.2 Write failing settings tests
    - `tests/unit/test_settings.py`: default tolerance 0.25; `AI_TCO_CONTEXT_MATCH_TOLERANCE` = -0.1 or 1.1 raises `ConfigurationError` naming setting and value; δ_ctx breakpoints and calibration tolerances (30 %/50 %) present with their defaults
    - _Requirements: 9.5, 9.10, 20.6, 42.2_

  - [x] 6.3 Write failing calibration tests and report tests
    - `tests/calibration/test_calibration.py`: one parametrised case per `decode_tps`/`prefill_tps` record; formula value via `use_measured=False` with the record's hardware, model, precision, context (defaults when absent); pass if APE ≤ tolerance, `xfail` with the ledger id if listed in `Calibration Known Deviations`, fail otherwise; skip invalid records with the reason of Req 42.6
    - `tests/unit/test_calibration_report.py`: printed counts, MAPE (1 decimal), top-5 order and fields; CSV equals the printed values; zero-record metric prints count 0 and MAPE not available without error; skipped count per metric
    - _Requirements: 42.1, 42.3, 42.4, 42.5, 42.6, 42.7_

  - [x]* 6.4 Write property test for the measured-first resolver
    - **Property 4: Measured-first resolver matches the selection oracle**
    - **Validates: Requirements 9.3, 9.4, 9.6, 9.9**
    - File: `tests/property/test_performance_props.py`

  - [x]* 6.5 Write property test for performance formulas
    - **Property 19: Performance formulas**
    - **Validates: Requirements 20.1, 21.2, 21.3, 21.4, 21.8**
    - File: `tests/property/test_performance_props.py`

  - [x] 6.6 Write property test for decode monotonicity in bandwidth
    - **Property 20: Decode is monotone in bandwidth** (required by Req 41.5)
    - **Validates: Requirements 20.4**
    - File: `tests/property/test_performance_props.py`

  - [x] 6.7 Write property test for the MoE dual-parameter law
    - **Property 21: MoE dual-parameter law** (required by Req 41.5)
    - **Validates: Requirements 20.5**
    - File: `tests/property/test_performance_props.py`

  - [x]* 6.8 Write property test for the context degradation curve
    - **Property 22: Context degradation curve shape**
    - **Validates: Requirements 20.6**
    - File: `tests/property/test_performance_props.py`

  - [x] 6.9 Write property test for latency invariants
    - **Property 23: Latency invariants** (required by Req 41.5)
    - **Validates: Requirements 21.6**
    - File: `tests/property/test_performance_props.py`

  - [x]* 6.10 Write property test for calibration outcome classification
    - **Property 59: Calibration outcome classification**
    - **Validates: Requirements 42.3**
    - File: `tests/property/test_calibration_props.py`

  - [x]* 6.11 Write property test for the calibration report builder
    - **Property 60: Calibration report builder**
    - **Validates: Requirements 42.4, 42.6**
    - File: `tests/property/test_calibration_props.py`

  - [x] 6.12 Implement the measured-first resolver and settings checks
    - `engines/resolver.py` `select_benchmark(BenchmarkQuery)` with the sort key of `design.md`; `settings.py` tolerance range check, δ_ctx breakpoints with log2 interpolation, calibration tolerances
    - _Requirements: 9.3, 9.4, 9.5, 9.6, 9.9, 9.10, 20.6, 42.2_

  - [x] 6.13 Implement the Performance_Engine
    - `engines/performance.py`: `compute_performance` and `compute_api_performance` (decode, prefill, TTFT with eviction re-prefill, effective TPS, 1M prefill, Value_Origins, FormulaTraces, `use_measured` switch)
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.7, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9_

  - [x] 6.14 Implement the Calibration_Report CLI
    - `services/calibration_report.py`; console script `ai-tco-calibrate`; writes `reports/calibration.csv`; README command `uv run ai-tco-calibrate`; `.gitignore` keeps `reports/.gitkeep`; record any calibration deviation (including multi-node records, D-08) in `Calibration Known Deviations`
    - _Requirements: 42.4, 42.5, 42.6, 42.7_

  - [x] 6.15 Extend the `size` service and View 1 card with performance
    - `size` returns `PerformanceResult` (feasible pairings) and the AA v5 `QualityScore`; `ui/cards.py` shows decode TPS, prefill TPS, TTFT, effective TPS, 1M prefill with origin labels
    - _Requirements: 9.4, 9.9, 21.1, 21.5_

  - [x] 6.16 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 7; run the Task 6 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [x] 7. TCO engine, utilization, Baselines A–D and `project_tco`
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 13: Reference Data", § "Requirement 22: On-Premise Cost Components", § "Requirement 23: Utilization and Viability Threshold", § "Requirement 24: Cloud Baselines A–D", § "Requirement 34: Dashboard Layout and KPI Ribbon", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Key Design Decisions", § "TCO_Engine (`engines/tco.py`)", § "Baseline_Engine (`engines/baselines.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Correctness Properties" › "TCO and utilization" and "Baselines, rental, hybrid and timeline"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "1. The Four Cloud Comparison Baselines", § "2. Sovereign On-Premise TCO & Hidden Enterprise Costs"; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`; `data/reference/`
  - **Modify:** `src/ai_tco_dss/engines/tco.py`, `src/ai_tco_dss/engines/baselines.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/formatting.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_tco.py`, `tests/unit/test_baselines.py`, `tests/property/test_tco_props.py`, `tests/property/test_baseline_props.py`, `tests/integration/test_service_validation.py`
  - **Covers:** 13.7, 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10, 22.11, 22.12, 22.13, 22.14, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8, 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8, 24.9, 24.10, 24.11, 34.3, 41.3, 41.4
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_tco.py tests/unit/test_baselines.py tests/property/test_tco_props.py tests/property/test_baseline_props.py tests/integration/test_service_validation.py`
  - **Demo:** View 2 tab, timeline card: choose candidate "RTX Pro 6000 96GB × 4 + gpt-oss-120b INT4" → the cost table shows CapEx, the six monthly OpEx components, Utilization with its viability badge, Baselines A/B/C monthly and the compliance tax delta; changing the staffing hub from `ro-cluj-bucharest` to `de-munich-hq` raises the personnel OpEx row.

  - [x] 7.1 Write failing TCO_Engine tests
    - `tests/unit/test_tco.py`: eviction loss formula with assumption inputs; Munich-vs-Romania savings; out-of-range inputs and unknown hub/tariff raise naming the field; disabled NIM/wait/eviction give exactly 0 and are reported; non-USD money raises; measured aggregate throughput used and labelled; infeasible or zero capacity → Utilization `None`, threshold false, capacity-insufficient, warning; boundaries 0.55, 0.70, 1.0
    - _Requirements: 22.8, 22.10, 22.12, 22.13, 22.14, 23.3, 23.5, 23.6, 23.7, 23.8_

  - [x] 7.2 Write failing Baseline_Engine tests
    - `tests/unit/test_baselines.py`: `test_req_24_4_baseline_b_reference` with the hand-computed values of `design.md` (B 4 479.84108, C 5 427.825, A 5 000, delta 427.825, ≤ 1 % relative tolerance, inputs read from the catalog so verified prices recompute the expectation); the four flag combinations of Req 24.2/24.3; Baseline D unavailable for infeasible candidates; invalid inputs rejected naming each field; USD label and `formula` origin with source ids
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.10, 24.11, 41.3, 41.4_

  - [x] 7.3 Write failing service validation test for edited reference data
    - `tests/integration/test_service_validation.py`: copy `data/` to `tmp_path`, change one tariff value, a new repository on the copy gives a different `project_tco` energy OpEx; no source change
    - _Requirements: 13.7_

  - [x]* 7.4 Write property test for on-premise cost components
    - **Property 24: On-premise cost components**
    - **Validates: Requirements 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.13**
    - File: `tests/property/test_tco_props.py`

  - [x]* 7.5 Write property test for the resale curve
    - **Property 25: Resale curve**
    - **Validates: Requirements 22.9**
    - File: `tests/property/test_tco_props.py`

  - [x] 7.6 Write property test for TCO monotonicity
    - **Property 26: TCO monotonicity** (required by Req 41.5)
    - **Validates: Requirements 22.11**
    - File: `tests/property/test_tco_props.py`

  - [x]* 7.7 Write property test for the utilization formula
    - **Property 27: Utilization formula**
    - **Validates: Requirements 23.1, 23.2, 23.4**
    - File: `tests/property/test_tco_props.py`

  - [x]* 7.8 Write property test for utilization classification and viability badge
    - **Property 28: Utilization classification and viability badge**
    - **Validates: Requirements 23.5, 23.6, 23.7, 34.3**
    - File: `tests/property/test_tco_props.py`

  - [x]* 7.9 Write property test for baseline formulas
    - **Property 29: Baseline formulas**
    - **Validates: Requirements 24.1, 24.4, 24.5, 24.6, 24.7, 24.11**
    - File: `tests/property/test_baseline_props.py`

  - [x] 7.10 Write property test for Baseline C versus Baseline B
    - **Property 30: EU-pinned API is never cheaper than global** (required by Req 41.5)
    - **Validates: Requirements 24.8**
    - File: `tests/property/test_baseline_props.py`

  - [x] 7.11 Write property test for baselines growing with users
    - **Property 31: Baselines grow with users** (required by Req 41.5)
    - **Validates: Requirements 24.9**
    - File: `tests/property/test_baseline_props.py`

  - [x] 7.12 Implement the TCO_Engine
    - `engines/tco.py`: `compute_tco(TcoInput, EngineParameters) -> TcoResult` with CapEx, six OpEx components, resale, Munich-vs-Romania savings, Utilization with the capacity fallback (D-07), warnings and FormulaTraces
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10, 22.11, 22.12, 22.13, 22.14, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8_

  - [x] 7.13 Implement Baselines A–D
    - `engines/baselines.py`: `api_monthly_cost`, `compute_baselines`, `compute_baseline_d` per `design.md` § "Baseline_Engine"
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8, 24.9, 24.10, 24.11_

  - [x] 7.14 Implement `project_tco` and the View 2 cost table
    - `project_tco(TcoRequest) -> TcoProjection` with `timeline=None`; `ui/formatting.py` `viability_badge(utilization)`; `ui/cards.py` `timeline_card()` (`@st.fragment`, candidate selector, staffing hub, cost table; increments `render_counts["timeline"]`); `ui/app.py` View 2 tab
    - _Requirements: 13.7, 23.5, 34.3_

  - [x] 7.15 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 8; run the Task 7 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [x] 8. Stitch web foundation, FastAPI boundary and size/TCO vertical slice
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `frontend/`, `package.json`, `package-lock.json`, `design/stitch/`, `src/ai_tco_dss/api/`, `pyproject.toml`, `uv.lock`, `scripts/`, `tests/unit/`, `tests/integration/`, `.gitignore`, `README.md`, `specs/08_MVP_DESIGN_REFERENCE.md`, `specs/09_WEB_FRONTEND_MIGRATION.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `.kiro/specs/ai-tco-dss-mvp/tasks.md`
  - **Covers:** 25.1, 26.1, 35.4, 38.2, 43.1, 43.2, 43.3, 43.4, 43.5, 43.7, 43.8, 43.9
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_api.py tests/integration/test_web_api.py`
  - **Demo:** Root npm run dev launches both processes; real memory/TCO inputs update the reference-matched React screen. Show light/dark browser comparisons with Stitch and API/service parity.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 8.1 Export canonical Stitch assets and record a screen manifest and design tokens
  - [x] 8.2 Write failing API parity, error and web interaction tests
  - [x] 8.3 Implement FastAPI catalog, default-workload, size and TCO endpoints with OpenAPI types
  - [x] 8.4 Implement React shell, scenario controls and real memory/TCO panels matching Stitch
  - [x] 8.5 Implement root npm run dev orchestration and frontend type/build/component/browser checks
  - [x] 8.6 Run browser reference comparisons, verify Python and web checks, update progress and next prompt

- [x] 9. Decision engine (SAW), use cases, presets and Normal-mode web recommendations
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `src/ai_tco_dss/decision/`, `src/ai_tco_dss/services/`, `src/ai_tco_dss/api/`, `frontend/`, `tests/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`
  - **Covers:** 27.1, 28.1, 29.1, 31.1, 32.9, 33.1, 38.1, 43.2, 43.6
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_decision.py tests/integration/test_service_end_to_end.py`
  - **Demo:** Use case, user count and preset produce real rankings, top contributions and complete rejection reasons; no fabricated recommendation before the engine exists.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 9.1 Write failing candidate, filter, quality, SAW and service tests
  - [x] 9.2 Implement quality resolution, candidate enumeration and all hard filters
  - [x] 9.3 Implement criterion normalization, ranking and explanations
  - [x] 9.4 Expose recommend/evaluate through FastAPI and generate client types
  - [x] 9.5 Build the Stitch ranking tab and Normal-mode flow with real result states
  - [x] 9.6 Verify Python/API/frontend/browser checks and update progress

- [x] 10. TOPSIS, Expert web controls and FX override
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `src/ai_tco_dss/decision/`, `src/ai_tco_dss/services/`, `src/ai_tco_dss/api/`, `frontend/`, `tests/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`
  - **Covers:** 12.4, 30.1, 30.2, 33.3, 43.6, 43.7
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_topsis.py`
  - **Demo:** Expert controls match the Stitch validation screen, preserve valid values and show SAW/TOPSIS ranks with an FX display override.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 10.1 Write failing TOPSIS and Expert interaction tests
  - [x] 10.2 Implement TOPSIS and service/API pass-through
  - [x] 10.3 Implement Expert panels, weights and validated FX inputs
  - [x] 10.4 Verify mode transitions, stale-response handling and currency invariants
  - [x] 10.5 Run all applicable checks and update progress

- [x] 11. Web KPI ribbon, chart semantics, responsive themes and accessibility
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `frontend/`, `src/ai_tco_dss/api/`, `tests/`, `specs/08_MVP_DESIGN_REFERENCE.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`
  - **Covers:** 12.5, 34.1, 35.4, 37.1, 37.4, 43.3, 43.4, 43.6, 43.7
  - **Verify:** `uv run python scripts/verify.py`
  - **Demo:** All three tabs share five consistent KPIs and visually verified light/dark layouts; controls, chart legends and tables work at desktop/tablet/mobile widths.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 11.1 Write interaction tests for KPI, theme, missing-data and currency states
  - [x] 11.2 Complete shared KPI and display formatting components
  - [x] 11.3 Complete chart styles and independent simulator state
  - [x] 11.4 Verify responsive layout, keyboard access, contrast and loading/empty/error states against Stitch
  - [x] 11.5 Record browser evidence and update progress

- [x] 12. Web audit drawer and JSON/CSV export
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `frontend/`, `src/ai_tco_dss/api/`, `src/ai_tco_dss/services/`, `tests/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`
  - **Covers:** 36.1, 36.2, 36.3, 36.4, 36.5, 36.6, 36.7, 36.8, 43.6
  - **Verify:** `uv run python scripts/verify.py`
  - **Demo:** Selecting a candidate updates the reference-styled audit drawer; sources/formulas are real; JSON round-trips and CSV ZIP contains ranking plus 60 timeline rows.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 12.1 Write failing audit-selection, source and export round-trip tests
  - [x] 12.2 Implement audit result transport and drawer contents
  - [x] 12.3 Implement JSON and display-currency CSV ZIP exports
  - [x] 12.4 Verify browser downloads, empty states and selected-candidate behavior
  - [x] 12.5 Run checks and update progress

- [x] 13. Web cutover, concurrency, performance, CI and documentation
  - **Load:** `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  - **Modify:** `frontend/`, `package.json`, `package-lock.json`, `src/ai_tco_dss/`, `.streamlit/`, `pyproject.toml`, `uv.lock`, `run.bat`, `run.sh`, `scripts/`, `tests/`, `.github/`, `README.md`, `specs/`, `.kiro/steering/`, `progress.md`
  - **Covers:** 2.6, 38.5, 39.4, 39.7, 40.1, 43.1, 43.8, 43.9
  - **Verify:** `uv run python scripts/verify.py`
  - **Demo:** Clean checkout starts the web app through the documented launcher; combined CI checks pass and no Streamlit dependency is needed for the product.
  - Web checks: run the implemented npm type/lint/build/component scripts and Playwright flows. Python verification alone is insufficient; do not skip browser acceptance.
  - [x] 13.1 Write concurrency, performance, launcher and build/serving tests
  - [x] 13.2 Add combined Python/API/frontend/browser verification and CI
  - [x] 13.3 Separate numeric tests from legacy UI tests and retire Streamlit adapter/config/dependency
  - [x] 13.4 Finalize same-origin production serving, launchers, README and extension seams
  - [x] 13.5 Run clean-checkout and visual acceptance checks; update progress with the remaining numerical-validation backlog

## Notes

The archived property/task dependency mapping belongs to the old Streamlit plan.
Regenerate coverage mapping as web tests are implemented. Tasks 8-13 follow the
order above; no further Streamlit styling is planned. Preserve all backend numeric
regressions, provenance, offline tests and expected calibration deviations.
Frontend commands must be created and verified in Task 8; they do not exist yet.
