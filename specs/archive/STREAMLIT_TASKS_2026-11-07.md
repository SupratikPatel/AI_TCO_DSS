> Historical plan, superseded by Requirement 43 and specs/09_WEB_FRONTEND_MIGRATION.md. Do not execute pending Streamlit work from this archive.

# Implementation Plan: AI TCO DSS MVP

## Overview

The plan implements the design in 13 top-level tasks, in the order of `design.md` § "Task Slicing for Context Switching". The language is Python 3.12 (Pydantic v2, pydantic-settings, Streamlit, Plotly, pytest, hypothesis, uv). Every task is test-first: its test sub-tasks come before its implementation sub-tasks. Each task ends with a Dashboard demo step (where engine or Service_Layer behaviour changes) and a progress update.

Conventions used by every task:

- **Task_Scope.** Each top-level task lists `Load` (files and sections, given as file path + section heading), `Modify` (explicit file or directory paths), `Covers` (criterion ids `N.M` from `requirements.md`), one `Verify` command line and one `Demo` step. Sub-tasks inherit the Task_Scope of their parent task. A session executes one top-level task, or resumes the task recorded as `in-progress` or `blocked` in `progress.md`.
- **Spec paths.** `requirements.md`, `design.md` and `tasks.md` mean the files under `.kiro/specs/ai-tco-dss-mvp/`.
- **Verification.** `uv run python scripts/verify.py <focus paths>` runs the focus tests (it skips a focus path that does not exist because an optional `*` test file was not written, and prints a notice), then `ruff check`, `ruff format --check`, `mypy`, the Validate_CLI (once the `ai-tco-validate` console script is declared in `pyproject.toml`) and the full `pytest` suite. It exits 0 only if every step passes. It works in PowerShell 5.1 and bash.
- **Property tests.** Each property from `design.md` § "Correctness Properties" is one sub-task and one `hypothesis` test (at least 100 examples) whose docstring names the property number and the criterion ids. Property tests for criteria that begin with "FOR ALL" or are labelled as a property are required by Requirement 41.5 and are not marked optional. All other property tests are marked optional with `*`; the task's required unit tests cover their criteria.
- **Project Rules.** The rules in `CLAUDE.md` § "Project Rules" apply from Task 2 onwards (Task 1 creates them).
- **Streamlit skill.** Every task that creates or changes files under `src/ai_tco_dss/ui/` or Dashboard tests that use AppTest (Tasks 5 to 12) first activates the `developing-with-streamlit` agent skill and follows the bundled references for the installed Streamlit version (`.kiro/steering/streamlit-ui.md`).

## Tasks

- [ ] 1. Bootstrap toolchain and session artefacts
  - **Load:** `CLAUDE.md` (whole file); `requirements.md` § "Introduction", § "Glossary", § "Requirement 1: Repository Organisation", § "Requirement 2: Engineering Toolchain and Continuous Integration", § "Requirement 3: Progress File for Session Continuity", § "Requirement 4: Next Session Prompt and Self-Contained Tasks", § "Requirement 5: Global Project Rules", § "Requirement 6: Incremental Visible Progress", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Key Design Decisions", § "Module and File Layout", § "Session-Continuity Artefacts", § "Task Slicing for Context Switching", § "Testing Strategy" › "Tools and configuration"; `tasks.md` (whole file); `specs/00_INDEX_AND_AGENT_ROUTER.md` § "2. AI Coding Agent Context Router (Read Only What You Need)"
  - **Modify:** `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `README.md`, `scripts/verify.py`, `scripts/relocate_specs.py`, `CLAUDE.md` (append only), `.kiro/steering/project-rules.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `src/ai_tco_dss/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/domain/__init__.py`, `src/ai_tco_dss/catalog/__init__.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/decision/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/ui/__init__.py`, `src/ai_tco_dss/ui/app.py`, `tests/conftest.py`, `tests/unit/test_repository_layout.py`, `tests/unit/test_toolchain.py`, `tests/unit/test_session_artefacts.py`, `tests/unit/test_relocate_specs.py`, `tests/unit/test_offline_guard.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.10, 1.11, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3, 6.4, 41.1, 41.2, 41.8
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_repository_layout.py tests/unit/test_toolchain.py tests/unit/test_session_artefacts.py tests/unit/test_relocate_specs.py tests/unit/test_offline_guard.py tests/integration/test_app_smoke.py`
  - **Demo:** No engine or Service_Layer behaviour changes. `uv run streamlit run src/ai_tco_dss/ui/app.py` opens a placeholder start page titled "AI TCO DSS" with the caption "Catalog not loaded yet"; `uv run pytest` shows the layout and session-artefact tests green.

  - [ ] 1.1 Write failing tests for repository layout and toolchain
    - `tests/unit/test_repository_layout.py`: `specs/00_…` to `specs/06_…` exist with the names of Req 1.1/1.2 and `specs/07_DATA_CORRECTIONS.md` exists; `src/ai_tco_dss/settings.py` and the six sub-packages with `__init__.py` exist; the four test directories exist; a case-sensitive search of `specs/` for the seven old file names (with and without ` (1)`) finds zero matches; each relocated spec file is tracked by git and `git log --follow` lists its history; each relocated file equals its first committed version after applying the Req 1.9 replacements, ignoring an appended `## Extension Seams (post-MVP)` section in `specs/00_INDEX_AND_AGENT_ROUTER.md` (added by Task 13 for Req 40.1)
    - `tests/unit/test_toolchain.py`: `pyproject.toml` declares `requires-python = ">=3.12,<3.13"`, runtime and dev dependencies (including `ruff`, `mypy`, `pytest`, `hypothesis`), `[tool.ruff]`, `[tool.mypy]` with `strict = true` and `[tool.pytest.ini_options]`; `uv.lock` exists and `uv lock --check` exits 0
    - Run the tests and observe the failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.10, 2.1, 2.2, 2.3_

  - [ ] 1.2 Write failing tests for session artefacts
    - `tests/unit/test_session_artefacts.py` checks:
      - `progress.md`: the seven level-2 headings in order; one `Task Status` row per task id of `tasks.md`, no duplicates, titles as in `tasks.md`, status in {`not-started`, `in-progress`, `done`, `blocked`}, ISO date only for `done`; `Decisions Log` rows carry date, decision, rationale, affected ids; `Known Deviations` ids exist in `specs/07_DATA_CORRECTIONS.md` or the section states that no deviations are recorded; `Next Step` names the first `not-started` task id in `tasks.md` order; `Next Session Prompt` is exactly one fenced block of at most 50 lines that lists `CLAUDE.md`, `progress.md`, `requirements.md`, `design.md`, `tasks.md` in this order, names the same task id as `Next Step`, contains that task's Load and Modify items from `tasks.md`, and contains no placeholder (`<…>`, `TODO`, `TBD`); if no task is `not-started`, the prompt says so and lists the `in-progress`/`blocked` ids
      - `tasks.md`: every top-level task has `Load`, `Modify`, `Covers`, `Verify` and `Demo` lines; every `Covers` and `_Requirements_` id exists in `requirements.md`; every `Load` path exists in a hard-coded list of pre-Task-1 files or lies under a `Modify` path of an earlier task; no task text refers to prior conversation (phrases such as "as discussed", "earlier chat")
      - `CLAUDE.md`: exactly one `## Project Rules` heading after the original content; the text above it has the SHA-256 of the original file (recorded in the test before the append); the section has eight numbered rules
      - `.kiro/steering/project-rules.md`: front matter delimited by `---` containing `inclusion: always`; the same eight rule items, same order, identical wording after whitespace trimming
      - `specs/07_DATA_CORRECTIONS.md`: sections `Entries`, `Contract Deviations`, `Okabe-Ito Archetype Mapping`, `Calibration Known Deviations`, `Assumptions`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 41.1, 41.2_

  - [ ] 1.3 Write failing tests for the spec relocation script
    - `tests/unit/test_relocate_specs.py` uses a temporary git repository: a tracked file is moved with `git mv` and `git log --follow` on the new path lists the old commit; an untracked file is moved, added under the new path and the old path is gone; an existing target leaves both files unchanged, prints the conflicting path and exits non-zero; running on the real repository is a no-op because all targets already exist and no source remains
    - _Requirements: 1.4, 1.5, 1.11_

  - [ ] 1.4 Write the offline guard, hypothesis profile and placeholder smoke test
    - `tests/conftest.py`: autouse session fixture that makes `socket.socket.connect` raise; hypothesis profile `default` with `max_examples=100`, `deadline=None`, loaded for every run
    - `tests/unit/test_offline_guard.py`: a connect attempt raises
    - `tests/integration/test_app_smoke.py`: `streamlit.testing.v1.AppTest.from_file("src/ai_tco_dss/ui/app.py")` runs within 30 s with no exception
    - _Requirements: 6.4, 41.8_

  - [ ] 1.5 Create `pyproject.toml` and `uv.lock` with uv
    - Package `ai-tco-dss`, src layout (`src/ai_tco_dss`), build backend hatchling, `requires-python = ">=3.12,<3.13"`, `.python-version` = `3.12`
    - `uv add pydantic pydantic-settings streamlit plotly pandas numpy`; `uv add --dev pytest hypothesis ruff mypy pandas-stubs`; `uv lock`
    - Configure `[tool.ruff]` (lint + format, `src/` and `tests/`), `[tool.mypy]` (`strict = true`, `files = ["src/ai_tco_dss"]`, pydantic plugin), `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["src"]`)
    - `.gitignore`: `.venv/`, caches (`__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.hypothesis`), `reports/*` except `reports/.gitkeep`
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 1.6 Create the package skeleton and placeholder Dashboard
    - `__init__.py` in `src/ai_tco_dss/` and in `domain`, `catalog`, `engines`, `decision`, `services`, `ui`
    - `src/ai_tco_dss/settings.py`: module docstring and an empty typed skeleton (Task 2 fills it)
    - `src/ai_tco_dss/ui/app.py`: `st.title("AI TCO DSS")` and `st.caption("Catalog not loaded yet")`; no import from `engines`, `decision` or `catalog`
    - Make ruff and mypy pass on the skeleton
    - _Requirements: 1.6, 2.4, 2.5, 6.4_

  - [ ] 1.7 Create `scripts/verify.py`, `scripts/relocate_specs.py` and README commands
    - `scripts/verify.py` per the Overview conventions (D-12): focus tests → `ruff check` → `ruff format --check` → `mypy` → Validate_CLI if declared → full `pytest`; prints each step name; exits with the first non-zero code
    - `scripts/relocate_specs.py`: the old→new mapping of Req 1.1/1.2; `git mv` for tracked files, move + `git add` for untracked files, conflict check before any change, cross-reference replacement of Req 1.9 in `specs/`; idempotent
    - `README.md`: one single-line command each for the tests (`uv run pytest`), task verification (`uv run python scripts/verify.py`) and the Dashboard (`uv run streamlit run src/ai_tco_dss/ui/app.py`)
    - _Requirements: 1.4, 1.5, 1.9, 1.11, 2.4, 2.5, 6.3_

  - [ ] 1.8 Append Project Rules to `CLAUDE.md` and create the steering file
    - Append `## Project Rules` with the eight rules from `design.md` § "Session-Continuity Artefacts" › "`CLAUDE.md` — appended section" after the last existing line; change no existing line
    - Create `.kiro/steering/project-rules.md` with front matter `inclusion: always` and the identical eight items
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 41.1, 41.2_

  - [ ] 1.9 Create the Corrections_Ledger `specs/07_DATA_CORRECTIONS.md`
    - Use `design.md` § "Session-Continuity Artefacts" › "`specs/07_DATA_CORRECTIONS.md` template": entries C-001 to C-015, empty `Contract Deviations` table, the Okabe-Ito table from `design.md` § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", empty `Calibration Known Deviations` table, the `Assumptions` table
    - Do not write any of the seven old spec file names into the ledger (the Req 1.9 search covers `specs/`)
    - _Requirements: 1.3, 3.5_

  - [ ] 1.10 Create `progress.md`
    - Seven sections in the order of Req 3.1; `Task Status` with one row per task id of this `tasks.md` (all `not-started`, task 1 rows `in-progress`); `Decisions Log` with D-01 to D-12, the three accepted open points (Task 5 combines workload and sizing; CSV export as one ZIP per D-11 and C-012; multi-node decode per Req 20.1 per D-08 and C-011) and the placeholder Dashboard in Task 1; `Known Deviations` referencing C-009, C-011 and C-012; `Next Step` = Task 2; `Next Session Prompt` for Task 2 with Task 2's Load and Modify items copied from this file
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 4.1, 4.5_

  - [ ] 1.11 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Set all task 1 rows to `done` with today's date, describe the state in `Current Status`, append the Changelog entry with all files created, keep `Next Step` and the prompt on Task 2
    - Run the Task 1 `Verify` command; it must exit 0
    - _Requirements: 3.3, 4.2, 6.4, 41.2_

- [ ] 2. Domain contracts and schema export
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Glossary", § "Requirement 7: Domain Contracts", § "Requirement 12: Currency and FX Conversion", § "Requirement 40: Extension Seams for Post-MVP Features"; `design.md` § "Domain base (`domain/base.py`)", § "Settings (`settings.py`)", § "Engine call convention", § "Data Models" (all subsections), § "Error Handling", § "Correctness Properties" › "Property 1" and "Property 6"; `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (whole file); `specs/07_DATA_CORRECTIONS.md` § "Contract Deviations"
  - **Modify:** `src/ai_tco_dss/domain/`, `src/ai_tco_dss/settings.py`, `pyproject.toml`, `uv.lock`, `schemas/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_contracts.py`, `tests/unit/test_schema_export.py`, `tests/property/strategies.py`, `tests/property/test_contract_props.py`
  - **Covers:** 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 12.7, 40.2, 40.4, 40.5
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_contracts.py tests/unit/test_schema_export.py tests/property/test_contract_props.py`
  - **Demo:** No engine or Service_Layer behaviour changes. `uv run ai-tco-schemas` writes `schemas/*.json`; a second run leaves `git status --short schemas/` empty.

  - [ ] 2.1 Write failing unit tests for the contracts
    - `tests/unit/test_contracts.py`: every contract class has `frozen=True` and `extra="forbid"`; assignment raises a `ValidationError` naming the field and keeps the value; unknown field, constraint violation, missing field and wrong type each raise an error naming the field (and the constraint); a minimal `BenchmarkRecord` with only Glossary fields validates; missing or invalid `source_id`, `tier`, `accessed` raise errors naming each field; every field name, enum member or default differing from the code block in `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (parsed with `ast`) has a row in the ledger's `Contract Deviations` table
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 40.4, 40.5_

  - [ ] 2.2 Write failing tests for the schema export
    - `tests/unit/test_schema_export.py`: the command creates `schemas/` if missing and writes one file per Service_Layer request/result contract, each valid JSON with `title` = class name; two runs give byte-identical files and exit 0; a contract whose schema generation fails (monkeypatched) makes the command exit non-zero and print the contract name
    - _Requirements: 7.8, 7.9, 7.10, 40.2_

  - [ ] 2.3 Write property test for contract JSON round trip
    - **Property 1: Contract JSON round trip** (required by Req 41.5)
    - **Validates: Requirements 7.11**
    - Create `tests/property/strategies.py` with generators for every contract within the requirement bounds, including boundary values; test in `tests/property/test_contract_props.py`

  - [ ] 2.4 Write property test for FX round trip
    - **Property 6: FX round trip** (required by Req 41.5)
    - **Validates: Requirements 12.7**
    - Test in `tests/property/test_contract_props.py` against `domain/money.py`

  - [ ] 2.5 Implement domain base, enums, errors and money helpers
    - `domain/base.py` (`Contract`, `SourceTier`, `TIER_RANK`, `Sourced[T]`, `Money`, `ValueOrigin`, `Metric`, `FormulaTrace`), `domain/enums.py` (spec 04 enums without `ElectricityTariffTier.CUSTOM`, plus the new enums), `domain/errors.py` (DssError hierarchy), `domain/money.py` (`usd_to_eur`, `eur_to_usd`, `round_display`)
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 12.7_

  - [ ] 2.6 Implement catalog and scenario contracts and `EngineParameters`
    - `domain/catalog.py` and `domain/scenario.py` per `design.md` § "Catalog contracts" and § "Scenario contracts"; tuples only for collections (D-03); validators for `SourceEntry` url/reference, `ModelSpec` api fields, `fx_override` decimals
    - `settings.py`: `Settings(BaseSettings)` with prefix `AI_TCO_` and the defaults of `design.md` § "Settings (`settings.py`)"; `load_engine_parameters()` returns `EngineParameters` and raises `ConfigurationError` for out-of-range values
    - _Requirements: 7.2, 7.5, 7.7, 40.4, 40.5_

  - [ ] 2.7 Implement result, input and request contracts
    - `domain/results.py`, `domain/inputs.py`, `domain/requests.py` per `design.md` § "Result contracts" and § "Engine call convention"; re-export public contracts from `domain/__init__.py`
    - _Requirements: 7.2, 7.11_

  - [ ] 2.8 Implement the schema export command
    - `domain/export_schemas.py`; console script `ai-tco-schemas` in `pyproject.toml`; `json.dumps(sort_keys=True, indent=2)` plus trailing newline; exit 1 with the contract name on failure; generate and add `schemas/`
    - _Requirements: 7.8, 7.9, 7.10, 40.2_

  - [ ] 2.9 Record contract deviations in the ledger
    - Add one `Contract Deviations` row (contract, field, old, new, sources, date) for every change listed in `design.md` § "Scenario contracts" and § "Enumerations" (e.g. `currency` EUR→USD, removed `CUSTOM` tariff, renamed `max_capex_budget_usd`)
    - _Requirements: 7.7_

  - [ ] 2.10 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Next task: Task 3 with its Load and Modify items; run the Task 2 `Verify` command
    - _Requirements: 3.3, 4.2_

- [ ] 3. Catalog repository, Validate_CLI, seed subset and Dashboard skeleton
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 1: Repository Organisation", § "Requirement 6: Incremental Visible Progress", § "Requirement 8: Source Registry and Provenance", § "Requirement 9: Benchmark Records and Measured-First Resolution", § "Requirement 11: Extensible Catalog Files and Validate CLI", § "Requirement 12: Currency and FX Conversion", § "Requirement 13: Reference Data", § "Requirement 37: Visual Accessibility and UI Architecture", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 39: Concurrency and Performance Budget"; `design.md` § "Key Design Decisions", § "Concurrency Model", § "Catalog port (`catalog/repository.py`)", § "Validate_CLI (`catalog/validate.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "JSON file formats", § "Correctness Properties" › "Property 2", "Property 3", "Property 5"; `specs/03_CALIBRATED_2026_SEED_DATA.md` § "2. Calibrated 2026 Hardware Seed Catalog", § "3. Calibrated 2026 Model Seed Catalog", § "4. Intra-EU Engineering Compensation & FinOps Seed Table"; `specs/06_RESEARCH_SOURCES.md` § "1. Primary Empirical Video Benchmark Citations", § "2. Industry Technical Standards, Empirical Whitepapers & Regulatory References"; `src/ai_tco_dss/domain/`; `src/ai_tco_dss/settings.py`
  - **Modify:** `src/ai_tco_dss/catalog/`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/app.py`, `src/ai_tco_dss/ui/state.py`, `data/sources.json`, `data/catalog/README.md`, `data/catalog/hardware/`, `data/catalog/models/`, `data/benchmarks/`, `data/reference/`, `data/workloads/default.json`, `pyproject.toml`, `uv.lock`, `README.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/fixtures/catalog_min/`, `tests/unit/test_validate_cli.py`, `tests/unit/test_repository.py`, `tests/unit/test_import_boundaries.py`, `tests/unit/test_repository_layout.py`, `tests/property/test_catalog_props.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 1.7, 6.1, 6.4, 6.5, 8.1, 8.3, 8.4, 8.5, 8.7, 8.8, 8.9, 8.10, 9.1, 9.2, 9.8, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 12.2, 12.3, 12.4, 12.9, 13.8, 37.7, 37.8, 38.3, 38.6, 39.1, 39.2, 39.3
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_validate_cli.py tests/unit/test_repository.py tests/unit/test_import_boundaries.py tests/unit/test_repository_layout.py tests/property/test_catalog_props.py tests/integration/test_app_smoke.py`
  - **Demo:** Start page (Dashboard, no inputs) shows "Catalog: 2 hardware, 2 models" and the FX rate 1.1165 USD/EUR with source `ECB-FX`. Deleting a `source_id` entry from `data/sources.json` makes `uv run ai-tco-validate` print one error line per dangling reference plus the total, and exit 1.

  - [ ] 3.1 Create the minimal fixture catalog and write failing Validate_CLI tests
    - `tests/fixtures/catalog_min/`: two hardware, two models, one benchmark file, all reference files, `sources.json`, `workloads/default.json`, all valid
    - `tests/unit/test_validate_cli.py` (copies the fixture to `tmp_path` and injects faults): source entry fields and tiers; duplicate `source_id`; unknown `source_id`; missing provenance; YT tier/`single-source` rule; invalid tier, bad date format, future date; missing or < 1 `context_tokens`; unparseable JSON with line:column; duplicate ids across folders; filename-id mismatch; dangling `model_id`/`hardware_id`; reference bounds; error line format `path: field_path: message`, total count, exit 1; success summary per file type and exit 0
    - _Requirements: 8.1, 8.4, 8.5, 8.7, 8.8, 8.9, 8.10, 9.1, 9.2, 9.8, 11.3, 11.4, 11.5, 11.6, 11.8, 11.9, 12.2, 13.8_

  - [ ] 3.2 Write failing repository tests
    - `tests/unit/test_repository.py`: one file per item named `<id>.json`; a new valid file appears on the next repository instance and non-`.json` files are ignored; an invalid file raises `CatalogLoadError` with file and field path and no partial Catalog; EUR money is returned as USD (`× rate`); `fx.json` missing/non-positive/bad date/unknown source raises naming `fx.json` and the field; `get_default_repository()` reads files once (spy on the loader) and returns the same instance; assigning a catalog field raises and leaves values unchanged; `data/catalog/README.md` examples validate against `HardwareSpec`/`ModelSpec`
    - _Requirements: 11.1, 11.2, 11.7, 11.10, 12.3, 12.9, 38.3, 39.1, 39.2, 39.3_

  - [ ] 3.3 Write failing import-boundary tests
    - `tests/unit/test_import_boundaries.py`: AST scan of every `src/ai_tco_dss/ui/*.py`; any import of `ai_tco_dss.engines`, `ai_tco_dss.decision` or `ai_tco_dss.catalog` (or submodules) fails with `"<file>: forbidden import <name>"`; a synthetic module checks the message
    - _Requirements: 37.7, 37.8, 38.6_

  - [ ] 3.4 Extend the smoke and layout tests
    - `tests/integration/test_app_smoke.py`: the start page renders within 30 s, without exception, and shows the hardware and model counts obtained from `catalog_overview`
    - `tests/unit/test_repository_layout.py`: add the Req 1.7 checks (`data/sources.json`, the four data directories, six reference files, `data/workloads/default.json`)
    - _Requirements: 1.7, 6.1, 6.4, 6.5_

  - [ ]* 3.5 Write property test for provenance coverage
    - **Property 2: Provenance coverage**
    - **Validates: Requirements 8.3, 8.5**
    - File: `tests/property/test_catalog_props.py`

  - [ ]* 3.6 Write property test for validator fault reporting
    - **Property 3: Validator reports every injected fault in one run**
    - **Validates: Requirements 8.10, 11.3**
    - File: `tests/property/test_catalog_props.py`

  - [ ]* 3.7 Write property test for repository FX conversion
    - **Property 5: Repository FX conversion**
    - **Validates: Requirements 12.3, 12.4**
    - File: `tests/property/test_catalog_props.py`

  - [ ] 3.8 Implement catalog loading and FX conversion
    - `catalog/loading.py`: raw JSON read with parse errors, provenance walker (D-02), contract validation with field paths, filename/duplicate/cross-reference checks, error collection without early stop
    - `catalog/fx.py`: `convert_catalog(catalog, rate)` returns a USD catalog with `fx_source_id` and `original_value`
    - _Requirements: 8.3, 8.4, 8.5, 8.9, 9.8, 11.3, 11.5, 11.6, 11.8, 12.3_

  - [ ] 3.9 Implement the Validate_CLI
    - `catalog/validate.py` with the check order of `design.md` § "Validate_CLI"; console script `ai-tco-validate`; README command `uv run ai-tco-validate`
    - _Requirements: 8.1, 8.7, 8.8, 8.10, 11.4, 11.9, 13.8_

  - [ ] 3.10 Implement the repositories
    - `catalog/repository.py` (Protocol), `catalog/json_repository.py` (`JsonCatalogRepository`, lock-guarded `get_default_repository()`, FX-override cache of 8), `catalog/memory_repository.py`; `catalog/__init__.py` exports
    - _Requirements: 11.1, 11.2, 11.10, 12.3, 12.4, 12.9, 38.3, 39.1, 39.2, 39.3_

  - [ ] 3.11 Write the seed data subset
    - `data/sources.json` with YT entries present in `specs/06` (tier `community`), IND-01 to IND-10, `ECB-FX`, `ASSUMPTION-MVP`, `ASSUMPTION-WORKLOAD-DEFAULT`; two hardware files (`mac-studio-m5-max-128gb`, `rtx-pro-6000-96gb`), two model files, `data/benchmarks/quality.json` seed, all `data/reference/*.json` of `design.md` § "JSON file formats", `data/workloads/default.json`; `data/catalog/README.md` with one annotated hardware and one model example (meaning, unit, required/optional per field)
    - `uv run ai-tco-validate` reports 0 errors
    - _Requirements: 1.7, 8.1, 8.3, 8.7, 9.1, 11.1, 11.7, 12.2_

  - [ ] 3.12 Implement `catalog_overview` and the Dashboard skeleton
    - `services/scenario_service.py` + `services/__init__.py`: `catalog_overview(repo=None, fx_override=None)` returning `CatalogOverview`
    - `ui/state.py` (session keys) and `ui/app.py`: start page via `@st.cache_resource`-wrapped service access showing counts and FX rate; catalog load errors shown with `st.error`
    - _Requirements: 6.1, 6.4, 38.3, 38.6_

  - [ ] 3.13 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; if the Dashboard does not start cleanly, keep the task not done and record the failure in `Known Deviations`
    - Next task: Task 4; run the Task 3 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4, 6.5_

- [ ] 4. Curated MVP catalog with web-verified values
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 8: Source Registry and Provenance", § "Requirement 10: Curated MVP Catalog Contents", § "Requirement 13: Reference Data", § "Requirement 14: Workload Profile and Explicit Assumptions", § "Requirement 31: Use Cases and Quality Floors", § "Requirement 32: Presets and Popularity Snapshot"; `design.md` § "Research Findings That Shape the Design", § "Validate_CLI (`catalog/validate.py`)", § "JSON file formats", § "Decision constants (Reference_Data, all `assumption`)", § "Session-Continuity Artefacts"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "1. The Four Cloud Comparison Baselines", § "2.2 Industrial vs. Office Electricity & Cooling PUE", § "2.5 Intra-EU Engineering Salary Arbitrage (Munich HQ vs. Romania EU Branch)"; `specs/03_CALIBRATED_2026_SEED_DATA.md` (whole file); `specs/06_RESEARCH_SOURCES.md` (whole file); `specs/07_DATA_CORRECTIONS.md` (whole file); `data/` (whole directory); `src/ai_tco_dss/catalog/validate.py`; `src/ai_tco_dss/catalog/loading.py`
  - **Modify:** `data/`, `src/ai_tco_dss/catalog/validate.py`, `src/ai_tco_dss/catalog/loading.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_mvp_catalog.py`, `tests/unit/test_reference_data.py`, `tests/property/test_preset_validator_props.py`
  - **Covers:** 8.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 31.2, 31.3, 32.1, 32.2, 32.3, 32.4, 32.5, 32.6, 32.8
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_mvp_catalog.py tests/unit/test_reference_data.py tests/property/test_preset_validator_props.py`
  - **Demo:** Start page (Dashboard, no inputs) shows "Catalog: 9 hardware, 12 models, 2 rentals". Removing `data/catalog/models/gpt-oss-120b.json` makes `uv run ai-tco-validate` report the missing MVP item `gpt-oss-120b` and exit 1.

  - [ ] 4.1 Write failing MVP catalog tests
    - `tests/unit/test_mvp_catalog.py`: exactly the 8 open-weights and 4 API model files and the 9 hardware files of Req 10; gpt-oss-120b MoE 117B/5.1B with provenance; API prices > 0 with tier `official`; valid node counts per Req 10.5; GEX63/GEX430 prices and setup fees; non-empty license types and `eu_commercial_license_valid = false` for the Llama 4 license; quality scores in [0, 100] with registered sources and no zero placeholders; ledger entries for gpt-oss-120b and GEX63; YT entries `community`, IND tiers by publisher type; the validator reports a removed MVP item or a missing required provenance and exits non-zero
    - _Requirements: 8.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11_

  - [ ] 4.2 Write failing reference data tests
    - `tests/unit/test_reference_data.py`: three tariffs with values and bounds; four hubs with salary, tax (0–100), delay (0–24) each sourced; harness tokens incl. `custom-lean` assumption; four use cases with benchmarks per Req 31.2 and `assumption` floors in [0, 100]; rentals equal to Req 10.6; Romania tax equals the chosen ledger value; default workload values with `assumption` provenance; four presets with six weights in [0, 1] summing to 1 ± 1e-6 and the dominance rules of Req 32.2–32.5; popularity snapshot date, provenance, unique ids, values ≥ 0
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 31.2, 31.3, 32.1, 32.2, 32.3, 32.4, 32.5, 32.6_

  - [ ]* 4.3 Write property test for preset and popularity validation
    - **Property 52: Preset and popularity validation**
    - **Validates: Requirements 32.8**
    - File: `tests/property/test_preset_validator_props.py`

  - [ ] 4.4 Add MVP completeness, preset and popularity rules to the Validate_CLI
    - MVP completeness (Req 10.11) runs only for the repository `data/` root, so the fixture catalog of Task 3 still validates; preset and popularity rules (Req 32.8)
    - _Requirements: 10.11, 32.8_

  - [ ] 4.5 Web-verify and write the nine hardware files
    - Fetch vendor pages (NVIDIA, Apple, AMD) for memory, bandwidth, power, prices; record `accessed` dates; YouTube values stay `community` + `single-source`; add every new source to `data/sources.json`
    - _Requirements: 8.3, 10.4, 10.5_

  - [ ] 4.6 Web-verify and write the eight open-weights model files and quality records
    - Hugging Face `config.json` for layers, KV heads, head dim, context; parameter counts; licenses; OpenRouter `/api/v1/models` for open-weights output prices; AA v5, Terminal-Bench, SWE-bench scores in `data/benchmarks/quality.json`; register sources
    - _Requirements: 10.1, 10.2, 10.7, 10.8_

  - [ ] 4.7 Web-verify and write the four commercial API model files
    - Official pricing pages (Anthropic, OpenAI, Google) for input, output and cache-read prices; EU-pinned endpoint availability; context length; register sources
    - _Requirements: 10.3, 10.7, 10.8_

  - [ ] 4.8 Web-verify and write the reference data
    - `rentals.json` (Hetzner GEX63/GEX430 pages, re-check the 15 June 2026 price change), `fx.json` (ECB), `electricity.json`, `staffing_hubs.json` (ANAF CAM for Romania), `harnesses.json`, `use_cases.json`, `presets.json` and `baselines.json` per `design.md` § "Decision constants", `popularity.json` (OpenRouter rankings snapshot); register sources
    - _Requirements: 8.2, 10.6, 13.1, 13.2, 13.3, 13.4, 13.5, 14.1, 31.2, 31.3, 32.1, 32.6_

  - [ ] 4.9 Update the Corrections_Ledger for the curated data
    - Confirm or update C-001, C-002, C-003 (2.25 % chosen), C-013, C-014; resolve C-010 and C-015; add an entry for every contradiction found while verifying; add or update the data-related `Assumptions` rows (FX rate, quality floors, preset weights, gateway fee, reference API model)
    - _Requirements: 10.9, 10.10, 13.6_

  - [ ] 4.10 Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Ensure all tests pass, ask the user if questions arise
    - Next task: Task 5; run the Task 4 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 5. Workload and Sizing engines, `size` service and View 1 card
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 14: Workload Profile and Explicit Assumptions", § "Requirement 15: Effective Token Volume Computation", § "Requirement 16: Usable Memory and Operating System Traps", § "Requirement 17: Weights, KV Cache, KV Pool and Concurrency", § "Requirement 18: Multi-Node Topology and Tiered Offload", § "Requirement 19: Quality, License and Context Flags", § "Requirement 35: Views 1 and 2", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Engine call convention", § "Workload_Engine (`engines/workload.py`)", § "Sizing_Engine (`engines/sizing.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", § "Correctness Properties" › "Workload and sizing", § "Testing Strategy"; `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` § "1.1 Token Volume, Tokenizer Inflation, Thinking Effort & Verification Multipliers", § "1.2 Agentic Harness Scaffolding ($S_{\text{harness}}$), MCP Pruning & Mega-Sessions", § "1.3 Multi-Agent State Retention vs. The Conversational Eviction Tax", § "Stage 1: Memory Architecture, OS Split Traps, Attention Formats & 3-Tier Offload", § "Stage 3: Quantization Fidelity, 6-Layer Harnesses & Hardware Lifecycle Clocks", § "Stage 4: Multi-Node Topologies, Disaggregation & Heterogeneous Routing"; `src/ai_tco_dss/domain/`; `src/ai_tco_dss/catalog/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`; `data/`
  - **Modify:** `src/ai_tco_dss/engines/workload.py`, `src/ai_tco_dss/engines/sizing.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/catalog/json_repository.py`, `src/ai_tco_dss/catalog/memory_repository.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/theme.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_workload.py`, `tests/unit/test_sizing.py`, `tests/unit/test_engine_purity.py`, `tests/unit/test_charts.py`, `tests/property/test_workload_props.py`, `tests/property/test_sizing_props.py`, `tests/property/test_ui_props.py`
  - **Covers:** 14.2, 14.3, 14.4, 14.6, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11, 17.12, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 35.1, 35.2, 35.3, 35.8, 35.9, 35.11, 37.1, 38.2, 41.3, 41.4
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_workload.py tests/unit/test_sizing.py tests/unit/test_engine_purity.py tests/unit/test_charts.py tests/property/test_workload_props.py tests/property/test_sizing_props.py tests/property/test_ui_props.py`
  - **Demo:** View 1 tab, memory-fit card: select hardware "Mac Studio (M5 Max 128GB)", model "Qwen 3.8 Flash Next", precision INT4, target context 8 192, override off → the bar exceeds the 103.04 GB usable line, the pairing is infeasible and the warning shows `sudo sysctl iogpu.wired_limit_mb=117760`; switch the Mac wired-memory override on → the line moves to 115 GB and the pairing is feasible. AA labels show "n/a" until Task 6.

  - [ ] 5.1 Write failing Workload_Engine tests
    - `tests/unit/test_workload.py`: Default_Workload_File reference values (22 000 requests, κ_mega 1.98, T̂_in 48 000 / 62 400, out_think 3 750 / 4 875, monthly tokens 2 254 230 000 / 2 930 499 000, output demand 82 500 000); `working_days_per_month` bounds and default; workload field bounds; `load_workload` with another file uses only that file plus defaults; missing path, invalid JSON and out-of-range fields raise `WorkloadFileError` naming path and fields; invalid mega ratio, negative tokens and unknown thinking preset are rejected
    - _Requirements: 14.2, 14.3, 14.4, 14.6, 14.7, 15.8_

  - [ ] 5.2 Write failing Sizing_Engine tests
    - `tests/unit/test_sizing.py`: `test_req_16_6_mac_128gb_trap` (103 GB infeasible / 115 GB feasible, trap flag true in both, exact flag equality, ≤ 1.0 GB deviation or ledger entry); `test_req_17_10_deepseek_mla_1m` (`M_kv_single == 0.89` within 5 % and strictly `< 0.9`); missing override fields fall back with warning; bound violations name field and hardware id; missing KV parameters name model id and parameters; α_scaling values; Thunderbolt cables 0/1/6/28; exactly one Strata warning; agreement rate exactly 0.90 gives no warning
    - _Requirements: 16.6, 16.8, 16.9, 17.10, 17.12, 18.4, 18.5, 18.9, 19.4, 41.3, 41.4_

  - [ ] 5.3 Write failing engine purity tests
    - `tests/unit/test_engine_purity.py`: `no_io` fixture blocks `open`, `Path.open/read_text` and sockets while `compute_workload` and `size_deployment` run and the results equal unblocked runs; AST check that `engines/` and `decision/` import only `ai_tco_dss.domain` and the standard library and declare no module-level `list`, `dict` or `set`
    - _Requirements: 38.2_

  - [ ] 5.4 Write failing View 1 chart tests
    - `tests/unit/test_charts.py`: `memory_fit_figure` example with one Mac and one discrete GPU pairing (segments order, VRAM line, system-RAM line only where present, "EVICTION RISK" badge and hatch, "n/a" labels); empty input returns a figure without data traces and a "No data available" annotation; the module imports no file, network or Streamlit API
    - _Requirements: 35.1, 35.2, 35.3, 35.8, 35.9, 35.11_

  - [ ]* 5.5 Write property test for workload formulas
    - **Property 9: Workload formulas**
    - **Validates: Requirements 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 15.7**
    - File: `tests/property/test_workload_props.py`

  - [ ] 5.6 Write property test for workload monotonicity
    - **Property 10: Workload monotonicity** (required by Req 41.5)
    - **Validates: Requirements 15.6**
    - File: `tests/property/test_workload_props.py`

  - [ ]* 5.7 Write property test for usable memory by architecture
    - **Property 11: Usable memory by architecture**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.8 Write property test for the Mac default-split trap
    - **Property 12: Mac default-split trap**
    - **Validates: Requirements 16.5, 16.7**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.9 Write property test for weight and KV-per-token formulas
    - **Property 13: Weight and KV-per-token formulas**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.10 Write property test for KV pool, concurrency and OOM
    - **Property 14: KV pool, concurrency and OOM**
    - **Validates: Requirements 17.5, 17.6, 18.3, 18.6**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.11 Write property test for memory breakdown and eviction flag
    - **Property 15: Memory breakdown and eviction flag**
    - **Validates: Requirements 17.7, 17.8, 17.11**
    - File: `tests/property/test_sizing_props.py`

  - [ ] 5.12 Write property test for memory monotonicity
    - **Property 16: More memory never hurts** (required by Req 41.5)
    - **Validates: Requirements 17.9**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.13 Write property test for node-count handling
    - **Property 17: Node-count handling**
    - **Validates: Requirements 18.1, 18.2, 18.7, 18.8**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.14 Write property test for quality, license and context flags
    - **Property 18: Quality, license and context flags never change feasibility**
    - **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7**
    - File: `tests/property/test_sizing_props.py`

  - [ ]* 5.15 Write property test for View 1 chart structure
    - **Property 54: View 1 chart structure**
    - **Validates: Requirements 35.1, 35.2, 35.3, 35.8, 35.9, 37.1**
    - File: `tests/property/test_ui_props.py`

  - [ ] 5.16 Implement the Workload_Engine and workload loading
    - `engines/workload.py`: `compute_workload(WorkloadInput, EngineParameters) -> WorkloadResult` with the formulas of `design.md` § "Workload_Engine"
    - `load_workload(path)` in `catalog/json_repository.py` and `catalog/memory_repository.py`
    - _Requirements: 14.3, 14.4, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_

  - [ ] 5.17 Implement the Sizing_Engine
    - `engines/sizing.py`: `size_deployment(SizingInput, EngineParameters) -> SizingResult` following steps 1–11 of `design.md` § "Sizing_Engine", with `FormulaTrace`s for usable memory, weights, KV and pool; record any Req 16.6 deviation above 1.0 GB in the ledger
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11, 17.12, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8, 18.9, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_

  - [ ] 5.18 Implement the `size` service
    - `services/scenario_service.py` + `services/__init__.py`: `size(SizeRequest, repo=None) -> SizeResult` (validates the request, checks ids, builds inputs, `performance=None` until Task 6); export from `services`
    - _Requirements: 14.3, 38.2_

  - [ ] 5.19 Implement the View 1 chart and card
    - `ui/theme.py` Okabe-Ito constants; `ui/charts.py` `memory_fit_figure(pairings, display)`; `ui/cards.py` `memory_fit_card()` decorated with `@st.fragment` (hardware/model multiselects, precision, context, override toggles; calls `size` per pairing; increments `render_counts["memory_fit"]`); `ui/app.py` View 1 tab
    - _Requirements: 35.1, 35.2, 35.3, 35.8, 35.9, 35.11, 37.1_

  - [ ] 5.20 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 6; run the Task 5 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 6. Performance engine, measured-first resolver and calibration
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 9: Benchmark Records and Measured-First Resolution", § "Requirement 20: Decode Throughput", § "Requirement 21: Prefill, TTFT and Effective Throughput", § "Requirement 42: Calibration Tests and Calibration Report"; `design.md` § "Settings (`settings.py`)", § "Measured-first resolver (`engines/resolver.py`)", § "Performance_Engine (`engines/performance.py`)", § "Service Layer (`services/`)", § "Correctness Properties" › "Performance" and "Service layer and calibration", § "Testing Strategy" › "Calibration tests (`tests/calibration/`)"; `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` § "Stage 2: Memory Bandwidth (Decode) vs. Compute (Prefill) & The MoE Law"; `specs/07_DATA_CORRECTIONS.md` § "Calibration Known Deviations"; `src/ai_tco_dss/settings.py`; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/cards.py`; `data/benchmarks/`
  - **Modify:** `src/ai_tco_dss/engines/resolver.py`, `src/ai_tco_dss/engines/performance.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/services/calibration_report.py`, `src/ai_tco_dss/ui/cards.py`, `pyproject.toml`, `README.md`, `.gitignore`, `reports/.gitkeep`, `data/benchmarks/`, `data/sources.json`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_performance.py`, `tests/unit/test_settings.py`, `tests/unit/test_calibration_report.py`, `tests/calibration/test_calibration.py`, `tests/property/test_performance_props.py`, `tests/property/test_calibration_props.py`
  - **Covers:** 9.3, 9.4, 9.5, 9.6, 9.9, 9.10, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 42.1, 42.2, 42.3, 42.4, 42.5, 42.6, 42.7
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_performance.py tests/unit/test_settings.py tests/unit/test_calibration_report.py tests/calibration tests/property/test_performance_props.py tests/property/test_calibration_props.py`
  - **Demo:** View 1 tab, memory-fit card: select "Mac Mini M5 Pro 64GB" + "Qwen 3.8-27B", INT4, context 8 192 → the performance rows show decode TPS with the value of the matching record in `data/benchmarks/decode.json` labelled `measured` with its `source_id` (e.g. YT-21), and TTFT and effective TPS labelled `formula`; the bar label shows the AA v5 score. `uv run ai-tco-calibrate` prints record counts and MAPE for decode and prefill TPS and writes `reports/calibration.csv`.

  - [ ] 6.1 Write failing Performance_Engine tests
    - `tests/unit/test_performance.py`: measured decode used and labelled `measured`; record outside tolerance falls back to formula; quality record resolved without hardware/context; η defaults 0.70/0.425; γ defaults per mode with `none` default; invalid bandwidth, `P_active`, bits or mode rejected naming the field; prefill fallback to `base_prefill_tps_at_32k`; 1M prefill order with overestimation warning; no prefill data → TTFT, effective TPS, 1M prefill `None` plus warning; `out_think = 0` → effective TPS 0 with TTFT; `r_cache` outside [0, 1] rejected
    - _Requirements: 9.4, 9.6, 9.9, 20.2, 20.3, 20.7, 21.1, 21.5, 21.7, 21.8, 21.9_

  - [ ] 6.2 Write failing settings tests
    - `tests/unit/test_settings.py`: default tolerance 0.25; `AI_TCO_CONTEXT_MATCH_TOLERANCE` = -0.1 or 1.1 raises `ConfigurationError` naming setting and value; δ_ctx breakpoints and calibration tolerances (30 %/50 %) present with their defaults
    - _Requirements: 9.5, 9.10, 20.6, 42.2_

  - [ ] 6.3 Write failing calibration tests and report tests
    - `tests/calibration/test_calibration.py`: one parametrised case per `decode_tps`/`prefill_tps` record; formula value via `use_measured=False` with the record's hardware, model, precision, context (defaults when absent); pass if APE ≤ tolerance, `xfail` with the ledger id if listed in `Calibration Known Deviations`, fail otherwise; skip invalid records with the reason of Req 42.6
    - `tests/unit/test_calibration_report.py`: printed counts, MAPE (1 decimal), top-5 order and fields; CSV equals the printed values; zero-record metric prints count 0 and MAPE not available without error; skipped count per metric
    - _Requirements: 42.1, 42.3, 42.4, 42.5, 42.6, 42.7_

  - [ ]* 6.4 Write property test for the measured-first resolver
    - **Property 4: Measured-first resolver matches the selection oracle**
    - **Validates: Requirements 9.3, 9.4, 9.6, 9.9**
    - File: `tests/property/test_performance_props.py`

  - [ ]* 6.5 Write property test for performance formulas
    - **Property 19: Performance formulas**
    - **Validates: Requirements 20.1, 21.2, 21.3, 21.4, 21.8**
    - File: `tests/property/test_performance_props.py`

  - [ ] 6.6 Write property test for decode monotonicity in bandwidth
    - **Property 20: Decode is monotone in bandwidth** (required by Req 41.5)
    - **Validates: Requirements 20.4**
    - File: `tests/property/test_performance_props.py`

  - [ ] 6.7 Write property test for the MoE dual-parameter law
    - **Property 21: MoE dual-parameter law** (required by Req 41.5)
    - **Validates: Requirements 20.5**
    - File: `tests/property/test_performance_props.py`

  - [ ]* 6.8 Write property test for the context degradation curve
    - **Property 22: Context degradation curve shape**
    - **Validates: Requirements 20.6**
    - File: `tests/property/test_performance_props.py`

  - [ ] 6.9 Write property test for latency invariants
    - **Property 23: Latency invariants** (required by Req 41.5)
    - **Validates: Requirements 21.6**
    - File: `tests/property/test_performance_props.py`

  - [ ]* 6.10 Write property test for calibration outcome classification
    - **Property 59: Calibration outcome classification**
    - **Validates: Requirements 42.3**
    - File: `tests/property/test_calibration_props.py`

  - [ ]* 6.11 Write property test for the calibration report builder
    - **Property 60: Calibration report builder**
    - **Validates: Requirements 42.4, 42.6**
    - File: `tests/property/test_calibration_props.py`

  - [ ] 6.12 Implement the measured-first resolver and settings checks
    - `engines/resolver.py` `select_benchmark(BenchmarkQuery)` with the sort key of `design.md`; `settings.py` tolerance range check, δ_ctx breakpoints with log2 interpolation, calibration tolerances
    - _Requirements: 9.3, 9.4, 9.5, 9.6, 9.9, 9.10, 20.6, 42.2_

  - [ ] 6.13 Implement the Performance_Engine
    - `engines/performance.py`: `compute_performance` and `compute_api_performance` (decode, prefill, TTFT with eviction re-prefill, effective TPS, 1M prefill, Value_Origins, FormulaTraces, `use_measured` switch)
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.7, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9_

  - [ ] 6.14 Implement the Calibration_Report CLI
    - `services/calibration_report.py`; console script `ai-tco-calibrate`; writes `reports/calibration.csv`; README command `uv run ai-tco-calibrate`; `.gitignore` keeps `reports/.gitkeep`; record any calibration deviation (including multi-node records, D-08) in `Calibration Known Deviations`
    - _Requirements: 42.4, 42.5, 42.6, 42.7_

  - [ ] 6.15 Extend the `size` service and View 1 card with performance
    - `size` returns `PerformanceResult` (feasible pairings) and the AA v5 `QualityScore`; `ui/cards.py` shows decode TPS, prefill TPS, TTFT, effective TPS, 1M prefill with origin labels
    - _Requirements: 9.4, 9.9, 21.1, 21.5_

  - [ ] 6.16 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 7; run the Task 6 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 7. TCO engine, utilization, Baselines A–D and `project_tco`
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 13: Reference Data", § "Requirement 22: On-Premise Cost Components", § "Requirement 23: Utilization and Viability Threshold", § "Requirement 24: Cloud Baselines A–D", § "Requirement 34: Dashboard Layout and KPI Ribbon", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Key Design Decisions", § "TCO_Engine (`engines/tco.py`)", § "Baseline_Engine (`engines/baselines.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Correctness Properties" › "TCO and utilization" and "Baselines, rental, hybrid and timeline"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "1. The Four Cloud Comparison Baselines", § "2. Sovereign On-Premise TCO & Hidden Enterprise Costs"; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`; `data/reference/`
  - **Modify:** `src/ai_tco_dss/engines/tco.py`, `src/ai_tco_dss/engines/baselines.py`, `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/formatting.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_tco.py`, `tests/unit/test_baselines.py`, `tests/property/test_tco_props.py`, `tests/property/test_baseline_props.py`, `tests/integration/test_service_validation.py`
  - **Covers:** 13.7, 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10, 22.11, 22.12, 22.13, 22.14, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8, 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8, 24.9, 24.10, 24.11, 34.3, 41.3, 41.4
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_tco.py tests/unit/test_baselines.py tests/property/test_tco_props.py tests/property/test_baseline_props.py tests/integration/test_service_validation.py`
  - **Demo:** View 2 tab, timeline card: choose candidate "RTX Pro 6000 96GB × 4 + gpt-oss-120b INT4" → the cost table shows CapEx, the six monthly OpEx components, Utilization with its viability badge, Baselines A/B/C monthly and the compliance tax delta; changing the staffing hub from `ro-cluj-bucharest` to `de-munich-hq` raises the personnel OpEx row.

  - [ ] 7.1 Write failing TCO_Engine tests
    - `tests/unit/test_tco.py`: eviction loss formula with assumption inputs; Munich-vs-Romania savings; out-of-range inputs and unknown hub/tariff raise naming the field; disabled NIM/wait/eviction give exactly 0 and are reported; non-USD money raises; measured aggregate throughput used and labelled; infeasible or zero capacity → Utilization `None`, threshold false, capacity-insufficient, warning; boundaries 0.55, 0.70, 1.0
    - _Requirements: 22.8, 22.10, 22.12, 22.13, 22.14, 23.3, 23.5, 23.6, 23.7, 23.8_

  - [ ] 7.2 Write failing Baseline_Engine tests
    - `tests/unit/test_baselines.py`: `test_req_24_4_baseline_b_reference` with the hand-computed values of `design.md` (B 4 479.84108, C 5 427.825, A 5 000, delta 427.825, ≤ 1 % relative tolerance, inputs read from the catalog so verified prices recompute the expectation); the four flag combinations of Req 24.2/24.3; Baseline D unavailable for infeasible candidates; invalid inputs rejected naming each field; USD label and `formula` origin with source ids
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.10, 24.11, 41.3, 41.4_

  - [ ] 7.3 Write failing service validation test for edited reference data
    - `tests/integration/test_service_validation.py`: copy `data/` to `tmp_path`, change one tariff value, a new repository on the copy gives a different `project_tco` energy OpEx; no source change
    - _Requirements: 13.7_

  - [ ]* 7.4 Write property test for on-premise cost components
    - **Property 24: On-premise cost components**
    - **Validates: Requirements 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.13**
    - File: `tests/property/test_tco_props.py`

  - [ ]* 7.5 Write property test for the resale curve
    - **Property 25: Resale curve**
    - **Validates: Requirements 22.9**
    - File: `tests/property/test_tco_props.py`

  - [ ] 7.6 Write property test for TCO monotonicity
    - **Property 26: TCO monotonicity** (required by Req 41.5)
    - **Validates: Requirements 22.11**
    - File: `tests/property/test_tco_props.py`

  - [ ]* 7.7 Write property test for the utilization formula
    - **Property 27: Utilization formula**
    - **Validates: Requirements 23.1, 23.2, 23.4**
    - File: `tests/property/test_tco_props.py`

  - [ ]* 7.8 Write property test for utilization classification and viability badge
    - **Property 28: Utilization classification and viability badge**
    - **Validates: Requirements 23.5, 23.6, 23.7, 34.3**
    - File: `tests/property/test_tco_props.py`

  - [ ]* 7.9 Write property test for baseline formulas
    - **Property 29: Baseline formulas**
    - **Validates: Requirements 24.1, 24.4, 24.5, 24.6, 24.7, 24.11**
    - File: `tests/property/test_baseline_props.py`

  - [ ] 7.10 Write property test for Baseline C versus Baseline B
    - **Property 30: EU-pinned API is never cheaper than global** (required by Req 41.5)
    - **Validates: Requirements 24.8**
    - File: `tests/property/test_baseline_props.py`

  - [ ] 7.11 Write property test for baselines growing with users
    - **Property 31: Baselines grow with users** (required by Req 41.5)
    - **Validates: Requirements 24.9**
    - File: `tests/property/test_baseline_props.py`

  - [ ] 7.12 Implement the TCO_Engine
    - `engines/tco.py`: `compute_tco(TcoInput, EngineParameters) -> TcoResult` with CapEx, six OpEx components, resale, Munich-vs-Romania savings, Utilization with the capacity fallback (D-07), warnings and FormulaTraces
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 22.10, 22.11, 22.12, 22.13, 22.14, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8_

  - [ ] 7.13 Implement Baselines A–D
    - `engines/baselines.py`: `api_monthly_cost`, `compute_baselines`, `compute_baseline_d` per `design.md` § "Baseline_Engine"
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8, 24.9, 24.10, 24.11_

  - [ ] 7.14 Implement `project_tco` and the View 2 cost table
    - `project_tco(TcoRequest) -> TcoProjection` with `timeline=None`; `ui/formatting.py` `viability_badge(utilization)`; `ui/cards.py` `timeline_card()` (`@st.fragment`, candidate selector, staffing hub, cost table; increments `render_counts["timeline"]`); `ui/app.py` View 2 tab
    - _Requirements: 13.7, 23.5, 34.3_

  - [ ] 7.15 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 8; run the Task 7 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 8. EU rental, hybrid split, 60-month timeline and View 2 chart
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 25: EU Dedicated Rental and Hybrid Split", § "Requirement 26: 60-Month Timeline and Break-Even", § "Requirement 35: Views 1 and 2", § "Requirement 37: Visual Accessibility and UI Architecture"; `design.md` § "Key Design Decisions", § "Baseline_Engine (`engines/baselines.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", § "Correctness Properties" › "Baselines, rental, hybrid and timeline" and "Dashboard and export"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "Baseline C: EU-Sovereign Metered Enterprise API & Dedicated EU Cloud Rental", § "2.7 Sovereign On-Premise 60-Month TCO Integration Formula"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` § "2.2 Semantic, Colorblind-Safe Financial Palette (Okabe-Ito / IBCS Aligned)", § "3. The Six Interactive Plotly Views (`src/ui/charts.py`)"; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`
  - **Modify:** `.streamlit/config.toml`, `specs/08_MVP_DESIGN_REFERENCE.md`, `src/ai_tco_dss/ui/app.py`, `tests/integration/test_app_smoke.py`, `src/ai_tco_dss/engines/baselines.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/theme.py`, `src/ai_tco_dss/ui/cards.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_tco.py`, `tests/unit/test_timeline.py`, `tests/unit/test_charts.py`, `tests/property/test_baseline_props.py`, `tests/property/test_ui_props.py`
  - **Covers:** 25.1, 25.2, 25.3, 25.4, 25.5, 25.6, 25.7, 26.1, 26.2, 26.3, 26.4, 26.5, 26.6, 26.7, 26.8, 26.9, 35.4, 35.5, 35.6, 35.7, 35.8, 35.10, 37.1, 37.3
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_timeline.py tests/unit/test_charts.py tests/property/test_baseline_props.py tests/property/test_ui_props.py`
  - **Demo:** View 2 tab, timeline card: candidate "RTX Pro 6000 96GB × 4 + gpt-oss-120b INT4", strict EU sovereignty on → the chart shows the on-premise, EU rental, Baseline A–D and hybrid series over months 1–60, `t* = <m>` markers where break-even exists, the "Utilization Danger Zone (<70%)" shading when Utilization < 0.70, and Baseline A dashed with "[NON-COMPLIANT / BLOCKED]" and no marker.

  - [ ] 8.1 Write failing timeline tests
    - `tests/unit/test_timeline.py`: `local_offload_ratio` -0.1, 1.1 and non-numeric rejected naming the range; costs in USD; `include_resale_value` default false; single-stream break-even years example and `None` when decode or price is 0 or missing; anchor selection per D-09 (rank-independent example via `project_tco`)
    - _Requirements: 25.6, 25.7, 26.4, 26.8, 26.9_

  - [ ] 8.2 Write failing View 2 chart tests
    - `tests/unit/test_charts.py`: `tco_timeline_figure` example with all series, missing D omitted from chart and legend, `t*` markers, legend note for no break-even, danger zone at 0.69 and absent at 0.70, Baseline A dashed/annotated when ineligible and solid otherwise
    - _Requirements: 35.4, 35.5, 35.6, 35.7, 35.10_

  - [ ]* 8.3 Write property test for rental and hybrid cumulative formulas
    - **Property 32: Rental and hybrid cumulative formulas**
    - **Validates: Requirements 25.1, 25.2, 25.5**
    - File: `tests/property/test_baseline_props.py`

  - [ ]* 8.4 Write property test for hybrid boundary ratios
    - **Property 33: Hybrid boundary ratios**
    - **Validates: Requirements 25.3, 25.4**
    - File: `tests/property/test_baseline_props.py`

  - [ ]* 8.5 Write property test for timeline structure
    - **Property 34: Timeline structure**
    - **Validates: Requirements 26.1, 26.2, 26.3**
    - File: `tests/property/test_baseline_props.py`

  - [ ]* 8.6 Write property test for the break-even oracle
    - **Property 35: Break-even oracle**
    - **Validates: Requirements 26.5, 26.6**
    - File: `tests/property/test_baseline_props.py`

  - [ ] 8.7 Write property test for non-decreasing cumulative series
    - **Property 36: Cumulative series never decrease without resale** (required by Req 41.5)
    - **Validates: Requirements 26.7**
    - File: `tests/property/test_baseline_props.py`

  - [ ]* 8.8 Write property test for View 2 chart structure
    - **Property 55: View 2 chart structure**
    - **Validates: Requirements 35.4, 35.5, 35.6, 35.7, 35.8, 35.10, 37.1, 37.3**
    - File: `tests/property/test_ui_props.py`

  - [ ] 8.9 Implement rental, hybrid, timeline and break-even
    - `engines/baselines.py`: `compute_rental_cost`, `compute_hybrid_cost`, `compute_timeline` (60 points, resale switch, break-even per series, single-stream break-even years)
    - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5, 25.6, 25.7, 26.1, 26.2, 26.3, 26.5, 26.6, 26.7, 26.8, 26.9_

  - [ ] 8.10 Extend `project_tco` with the timeline
    - Anchor on-premise deployment per D-09, default rental and hybrid API model, `include_resale_value` from the scenario
    - _Requirements: 26.1, 26.3, 26.4_

  - [ ] 8.11 Implement the View 2 chart
    - `ui/theme.py` `ARCHETYPE_STYLE` (colour + line style/fill per archetype); `ui/charts.py` `tco_timeline_figure(projection, display)`; `ui/cards.py` timeline card shows the chart and the resale toggle
    - _Requirements: 35.4, 35.5, 35.6, 35.7, 35.8, 35.10, 37.1, 37.3_

  - [ ] 8.12 Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Ensure all tests pass, ask the user if questions arise
    - Run the Demo; next task: Task 9; run the Task 8 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 9. Decision engine (SAW), use cases, presets, `recommend`/`evaluate_scenario` and Normal mode
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 9: Benchmark Records and Measured-First Resolution", § "Requirement 27: Candidate Generation", § "Requirement 28: Hard Filters and Rejection Reasons", § "Requirement 29: Criteria, Normalisation and SAW Ranking", § "Requirement 31: Use Cases and Quality Floors", § "Requirement 32: Presets and Popularity Snapshot", § "Requirement 33: Normal Mode and Expert Mode", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Request flow: `recommend` / `evaluate_scenario`", § "Decision pipeline (`decision/`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Error Handling", § "Correctness Properties" › "Decision engine" and "Property 8", "Property 53", § "Testing Strategy" › "Integration tests (`tests/integration/`)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` § "2.1 The 5-Second Rule & 3-Tier Progressive Disclosure Layout"; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`; `data/reference/`
  - **Modify:** `src/ai_tco_dss/decision/`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/sidebar.py`, `src/ai_tco_dss/ui/ranking_tab.py`, `src/ai_tco_dss/ui/state.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_decision.py`, `tests/unit/test_ui_state.py`, `tests/property/test_decision_props.py`, `tests/property/test_ui_props.py`, `tests/integration/test_service_end_to_end.py`, `tests/integration/test_repository_swap.py`, `tests/integration/test_service_validation.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 9.7, 12.8, 27.1, 27.2, 27.3, 27.4, 27.5, 27.6, 27.7, 27.8, 28.1, 28.2, 28.3, 28.4, 28.5, 28.6, 28.7, 28.8, 29.1, 29.2, 29.3, 29.4, 29.5, 29.6, 29.7, 29.8, 29.9, 29.10, 29.11, 29.12, 29.13, 31.1, 31.4, 31.5, 31.6, 31.7, 32.7, 32.9, 32.10, 33.1, 33.2, 33.6, 33.7, 38.1, 38.4, 38.7, 38.8, 41.6, 41.7
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_decision.py tests/unit/test_ui_state.py tests/property/test_decision_props.py tests/property/test_ui_props.py tests/integration/test_service_end_to_end.py tests/integration/test_repository_swap.py tests/integration/test_service_validation.py tests/integration/test_app_smoke.py`
  - **Demo:** Ranking tab in Normal mode with use case `agentic-coding`, 25 active users and preset `best-fit` (the new-session defaults) → the ranked table, the explanation of the rank-1 candidate and an expandable rejected list with failed filters (name, measured value, threshold); selecting preset `cheapest` changes the order; entering "abc" as active users shows the 1–100 000 range error and keeps 25.

  - [ ] 9.1 Write failing decision unit tests
    - `tests/unit/test_decision.py`: 16 rental candidates for the MVP catalog; zero hybrids plus warning when no on-prem candidate is feasible; filter examples (unset thresholds skipped, not-applicable filters pass, hybrid fails if a part fails, missing TPS/TTFT and quality "not available", "no EU-pinned endpoint"); quality fallback note; popularity absent → 0 plus note; normalisation with a single candidate; tie-break by TCO then id; invalid weights → `ranking_error`; explanation format; unknown use case rejected listing the four allowed ids; preset weights used exactly as stored
    - _Requirements: 27.3, 27.8, 28.3, 28.6, 28.7, 28.8, 29.3, 29.5, 29.7, 29.9, 29.11, 31.6, 31.7, 32.7, 32.9_

  - [ ] 9.2 Write failing service integration tests
    - `tests/integration/test_service_end_to_end.py`: `evaluate_scenario` and `recommend` on the MVP catalog with the default workload complete, validate against their output contracts, return ≥ 1 ranked candidate with Value_Origins (registered `source_id`s) for decode TPS, TTFT, effective TPS, quality and price, include rejected candidates with full failure lists; all use case × preset combinations run; the four public functions return Domain_Contracts
    - `tests/integration/test_repository_swap.py`: an `InMemoryCatalogRepository` built from the JSON catalog gives equal results for `evaluate_scenario`, `recommend`, `size`, `project_tco`
    - `tests/integration/test_service_validation.py`: invalid contract arguments and unknown hardware/model/rental ids raise naming the field or id and type, and no engine is called (spy)
    - _Requirements: 9.7, 28.5, 38.1, 38.4, 38.7, 38.8, 41.6, 41.7_

  - [ ] 9.3 Write failing Normal-mode UI tests
    - `tests/unit/test_ui_state.py`: `validate_active_users` and `validate_fx_override` examples (valid, out of range, non-numeric, too many decimals) keep the previous value and return a range message
    - `tests/integration/test_app_smoke.py`: new session → Normal mode, `agentic-coding`, 25 users, `best-fit`; exactly three scenario inputs in Normal mode; the four use cases offered; invalid user count shows an error next to the input and does not re-evaluate
    - _Requirements: 12.8, 31.1, 32.10, 33.1, 33.6, 33.7_

  - [ ]* 9.4 Write property test for candidate enumeration
    - **Property 37: Candidate enumeration**
    - **Validates: Requirements 27.1, 27.2, 27.3, 27.6, 27.7**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.5 Write property test for hybrid local selection
    - **Property 38: Hybrid local selection**
    - **Validates: Requirements 27.4**
    - File: `tests/property/test_decision_props.py`

  - [ ] 9.6 Write property test for deterministic candidate generation
    - **Property 39: Candidate generation is deterministic** (required by Req 41.5)
    - **Validates: Requirements 27.5**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.7 Write property test for the hard-filter oracle
    - **Property 40: Hard-filter oracle**
    - **Validates: Requirements 28.1, 28.2, 28.3, 28.6, 28.7, 28.8**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.8 Write property test for rejected list ordering
    - **Property 41: Rejected list ordering**
    - **Validates: Requirements 28.4**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.9 Write property test for quality resolution order
    - **Property 42: Quality resolution order**
    - **Validates: Requirements 29.2, 29.3, 31.4, 31.5, 31.6**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.10 Write property test for risk bounds and monotonicity
    - **Property 43: Risk bounds and monotonicity**
    - **Validates: Requirements 29.4**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.11 Write property test for normalisation
    - **Property 44: Normalisation**
    - **Validates: Requirements 29.5, 29.12**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.12 Write property test for SAW score composition and order
    - **Property 45: SAW score composition and order**
    - **Validates: Requirements 29.1, 29.6, 29.7, 29.8**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.13 Write property test for explanation content
    - **Property 46: Explanation content**
    - **Validates: Requirements 29.9**
    - File: `tests/property/test_decision_props.py`

  - [ ] 9.14 Write property test for SAW dominance
    - **Property 47: SAW respects dominance** (required by Req 41.5)
    - **Validates: Requirements 29.10**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.15 Write property test for invalid weights
    - **Property 48: Invalid weights produce no ranking**
    - **Validates: Requirements 29.11**
    - File: `tests/property/test_decision_props.py`

  - [ ] 9.16 Write property test for deterministic ranking
    - **Property 49: Ranking is deterministic** (required by Req 41.5)
    - **Validates: Requirements 29.13**
    - File: `tests/property/test_decision_props.py`

  - [ ]* 9.17 Write property test for Dashboard input validators
    - **Property 8: Dashboard input validators**
    - **Validates: Requirements 12.8, 33.7**
    - File: `tests/property/test_ui_props.py`

  - [ ]* 9.18 Write property test for Normal mode ignoring Expert values
    - **Property 53: Normal mode ignores Expert values**
    - **Validates: Requirements 33.2**
    - File: `tests/property/test_ui_props.py`

  - [ ] 9.19 Implement quality resolution
    - `decision/quality.py`: `resolve_quality` (matching → second choice → AA v5 × ratio → none, fallback note) and `aa_scaling_ratio`
    - _Requirements: 29.2, 29.3, 31.4, 31.5, 31.6_

  - [ ] 9.20 Implement candidate generation and evaluation
    - `decision/candidates.py`: on-prem, API, rental and hybrid candidates with the id formats, ordering and per-call memoisation of `design.md`; rental sizing on the rental GPU item; per-candidate `EngineInputError` becomes a rejected candidate with failure `input_error`
    - _Requirements: 27.1, 27.2, 27.3, 27.4, 27.5, 27.6, 27.7, 27.8_

  - [ ] 9.21 Implement the hard filters
    - `decision/filters.py`: the nine filters with `FilterFailure` records and rejected-list ordering
    - _Requirements: 28.1, 28.2, 28.3, 28.4, 28.6, 28.7, 28.8_

  - [ ] 9.22 Implement criteria, normalisation, SAW and explanation
    - `decision/ranking.py`: six criteria incl. risk formula, normalisation with missing values, weight validation, SAW with tie comparator, per-criterion scores, explanation; `decision/__init__.py` exports
    - _Requirements: 29.1, 29.4, 29.5, 29.6, 29.7, 29.8, 29.9, 29.10, 29.11, 29.12, 29.13, 32.7, 32.9_

  - [ ] 9.23 Implement `recommend` and `evaluate_scenario`
    - Input re-validation, id checks, baselines for the reference API model, anchor timeline, Value_Origins, referenced sources, warnings; export from `services`
    - _Requirements: 9.7, 28.5, 31.7, 38.1, 38.7, 38.8_

  - [ ] 9.24 Implement Normal mode, sidebar and ranking tab
    - `ui/state.py` defaults and validators; `ui/sidebar.py` Normal inputs (use case, active users as `st.text_input`, preset); `build_scenario` from the default workload and preset weights with SAW; `ui/ranking_tab.py` ranked table, explanation and rejected list; `ui/app.py` wiring with `@st.cache_data(max_entries=64)` around `evaluate_scenario`
    - _Requirements: 31.1, 32.10, 33.1, 33.2, 33.6, 33.7_

  - [ ] 9.25 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 10; run the Task 9 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 10. TOPSIS, Expert mode and FX override
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 12: Currency and FX Conversion", § "Requirement 30: TOPSIS Expert Ranking", § "Requirement 33: Normal Mode and Expert Mode"; `design.md` § "Decision pipeline (`decision/`)", § "Concurrency Model", § "Dashboard (`ui/`)", § "Correctness Properties" › "Property 50" and "Property 51"; `src/ai_tco_dss/decision/ranking.py`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`
  - **Modify:** `src/ai_tco_dss/decision/ranking.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/sidebar.py`, `src/ai_tco_dss/ui/state.py`, `src/ai_tco_dss/ui/ranking_tab.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_topsis.py`, `tests/property/test_decision_props.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 12.4, 12.8, 30.1, 30.2, 30.3, 30.4, 30.5, 30.6, 30.7, 30.8, 33.3, 33.4, 33.5
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_topsis.py tests/property/test_decision_props.py tests/integration/test_app_smoke.py`
  - **Demo:** Sidebar: switch to Expert mode → the weight inputs show the `best-fit` preset weights and SAW is selected; choose TOPSIS → the ranking tab shows SAW rank, TOPSIS rank and closeness (3 decimals) side by side; enter FX override 1.20 → EUR-denominated costs (e.g. the Hetzner rental candidates' 60-month TCO) change in the ranking; entering 2.5 shows the 0.50–2.00 range error and keeps the previous rate.

  - [ ] 10.1 Write failing TOPSIS unit tests
    - `tests/unit/test_topsis.py`: hand-computed three-candidate example (C, D⁺, D⁻); zero-norm criterion → 0; single candidate → closeness 1.0; equal closeness ordered by TCO then id; TOPSIS table rows ordered by TOPSIS rank with adjacent SAW rank, TOPSIS rank, closeness
    - _Requirements: 30.2, 30.3, 30.4, 30.6, 30.7, 30.8_

  - [ ] 10.2 Write failing Expert-mode smoke tests
    - `tests/integration/test_app_smoke.py`: Expert mode shows all inputs of Req 33.3; ranking-method toggle has exactly SAW and TOPSIS with SAW preselected; Normal→Expert copies preset weights and sets SAW; Expert→Normal keeps use case, users and preset; FX override 1.20 changes results without touching `fx.json`; invalid override rejected with the range message
    - _Requirements: 12.4, 12.8, 30.1, 33.3, 33.4, 33.5_

  - [ ]* 10.3 Write property test for TOPSIS against a reference computation
    - **Property 50: TOPSIS matches the reference computation**
    - **Validates: Requirements 30.2, 30.3, 30.6, 30.7, 30.8**
    - File: `tests/property/test_decision_props.py` (NumPy reference oracle inside the test)

  - [ ] 10.4 Write property test for TOPSIS dominance
    - **Property 51: TOPSIS respects dominance** (required by Req 41.5)
    - **Validates: Requirements 30.5**
    - File: `tests/property/test_decision_props.py`

  - [ ] 10.5 Implement TOPSIS
    - `decision/ranking.py` `rank_topsis` (vector normalisation, missing values replaced by the worst observed value, ideal/anti-ideal, closeness, tie-break) and both ranks in `RankedCandidate`
    - _Requirements: 30.2, 30.3, 30.5, 30.6, 30.7, 30.8_

  - [ ] 10.6 Implement Expert mode and the FX override pass-through
    - `ui/state.py` and `ui/sidebar.py` Expert inputs, weight inputs, method toggle, mode-switch rules, FX override text input with the validator; services pass `Scenario.fx_override` to `repo.catalog(fx_override)`
    - _Requirements: 12.4, 12.8, 30.1, 33.3, 33.4, 33.5_

  - [ ] 10.7 Show the SAW/TOPSIS comparison in the ranking tab
    - `ui/ranking_tab.py` comparison table; `ui/app.py` passes the method from the sidebar
    - _Requirements: 30.3, 30.4_

  - [ ] 10.8 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 11; run the Task 10 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 11. KPI ribbon, display currency, theme and accessibility, fragments
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 12: Currency and FX Conversion", § "Requirement 26: 60-Month Timeline and Break-Even", § "Requirement 34: Dashboard Layout and KPI Ribbon", § "Requirement 37: Visual Accessibility and UI Architecture"; `design.md` § "Research Findings That Shape the Design", § "Dashboard (`ui/`)", § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", § "Correctness Properties" › "Property 7"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` § "2.1 The 5-Second Rule & 3-Tier Progressive Disclosure Layout", § "2.2 Semantic, Colorblind-Safe Financial Palette (Okabe-Ito / IBCS Aligned)"; `specs/07_DATA_CORRECTIONS.md` § "Okabe-Ito Archetype Mapping"; `src/ai_tco_dss/ui/`
  - **Modify:** `src/ai_tco_dss/ui/kpi.py`, `src/ai_tco_dss/ui/theme.py`, `src/ai_tco_dss/ui/formatting.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_kpi.py`, `tests/unit/test_theme.py`, `tests/property/test_ui_props.py`, `tests/integration/test_fragments.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 12.1, 12.5, 26.10, 34.1, 34.2, 34.4, 34.5, 34.6, 34.7, 37.1, 37.2, 37.3, 37.4, 37.5, 37.6
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_kpi.py tests/unit/test_theme.py tests/property/test_ui_props.py tests/integration/test_fragments.py tests/integration/test_app_smoke.py`
  - **Demo:** Main page with the Normal-mode defaults → the KPI ribbon shows five cards (architecture, break-even vs Baseline C, monthly savings, performance, Utilization with badge) for the rank-1 candidate; switching Display currency to EUR relabels every monetary value with € (amount ÷ active FX rate) while break-even months stay the same; changing a widget in the View 1 card does not rerun the View 2 card.

  - [ ] 11.1 Write failing KPI tests
    - `tests/unit/test_kpi.py`: card builder for each candidate kind; "no break-even within 60 months"; empty ranking → "No feasible option" and "not available"; missing metric → "not applicable"; service failure → error and cleared values
    - _Requirements: 34.2, 34.5, 34.6, 34.7_

  - [ ] 11.2 Write failing theme and accessibility tests
    - `tests/unit/test_theme.py`: eight Okabe-Ito constants; every trace colour in `memory_fit_figure` and `tco_timeline_figure` outputs is one of them; `ARCHETYPE_STYLE` equals the ledger's Okabe-Ito table (original hex, Okabe-Ito hex, style); no two archetypes share colour + style in one figure; compliance and OOM text badges present; `memory_fit_card` and `timeline_card` are `@st.fragment`-decorated
    - _Requirements: 37.1, 37.2, 37.3, 37.4, 37.5_

  - [ ] 11.3 Write failing fragment and layout smoke tests
    - `tests/integration/test_fragments.py`: changing a View 1 card widget increments only `render_counts["memory_fit"]`; if AppTest cannot drive fragment reruns, call the undecorated card functions with a fake `st` module and record the limitation in the ledger
    - `tests/integration/test_app_smoke.py`: three tiers in order (KPI ribbon, tabs incl. ranking, collapsed audit drawer); USD at session start; KPI recompute within 5 s of an input change; service failure keeps inputs
    - _Requirements: 12.1, 34.1, 34.4, 34.7, 37.6_

  - [ ] 11.4 Write property test for display currency
    - **Property 7: Display currency changes labels only** (required by Req 41.5)
    - **Validates: Requirements 12.5, 26.10**
    - File: `tests/property/test_ui_props.py`

  - [ ] 11.5 Implement display currency formatting
    - `ui/formatting.py`: `format_money(amount_usd, display)` ($ unchanged / € = amount ÷ rate, 2 decimals), DataFrame builders and chart axis/tooltip labels in the display currency
    - _Requirements: 12.1, 12.5, 26.10_

  - [ ] 11.6 Implement the KPI ribbon
    - `ui/kpi.py`: five `st.metric` cards in `st.columns(5)`, badge text per Req 34.3, empty-ranking state with a button that opens the rejected list, error state
    - _Requirements: 34.2, 34.5, 34.6, 34.7_

  - [ ] 11.7 Apply theme, badges and fragments in charts and cards
    - `ui/theme.py` final styles; `ui/charts.py` uses theme constants only and display-currency axes; `ui/cards.py` fragment decoration and compliance/OOM badges
    - _Requirements: 37.1, 37.3, 37.4, 37.5, 37.6_

  - [ ] 11.8 Wire the three-tier layout and display currency in the app
    - `ui/app.py`: KPI ribbon, tabs (Ranking, View 1, View 2), collapsed audit drawer placeholder, display currency toggle, error handling that clears `result` and keeps inputs
    - _Requirements: 12.1, 34.1, 34.4, 34.7_

  - [ ] 11.9 Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Run the Demo; next task: Task 12; run the Task 11 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 12. Audit drawer and export
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 8: Source Registry and Provenance", § "Requirement 12: Currency and FX Conversion", § "Requirement 36: Audit Drawer and Export"; `design.md` § "Key Design Decisions", § "Dashboard (`ui/`)", § "Error Handling", § "Correctness Properties" › "Property 56" and "Property 57"; `src/ai_tco_dss/ui/`; `src/ai_tco_dss/domain/results.py`
  - **Modify:** `src/ai_tco_dss/ui/audit.py`, `src/ai_tco_dss/ui/formatting.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_audit.py`, `tests/property/test_ui_props.py`, `tests/integration/test_app_smoke.py`
  - **Covers:** 8.6, 12.6, 36.1, 36.2, 36.3, 36.4, 36.5, 36.6, 36.7, 36.8
  - **Verify:** `uv run python scripts/verify.py tests/unit/test_audit.py tests/property/test_ui_props.py tests/integration/test_app_smoke.py`
  - **Demo:** Open the audit drawer with the Normal-mode defaults → the rank-1 candidate is selected and shows formulas with substituted values, the deduplicated source list with tiers and `assumption` badges, Value_Origin labels next to the five performance values, and the FX rate with its source and "fx.json" label; "Export JSON" downloads a file that re-validates as `ScenarioResult`; "Export CSV" downloads a ZIP with `ranking_USD.csv` and `timeline_USD.csv` (60 rows).

  - [ ] 12.1 Write failing audit and export tests
    - `tests/unit/test_audit.py`: formula traces for sizing, the five performance values and CapEx/OpEx/60-month TCO with substituted inputs and units; Value_Origin labels; `assumption` badge only for tier `assumption`; FX info with ≥ 4 decimals and source label; CSV ZIP with header rows, one row per ranked candidate, exactly 60 timeline rows and the currency code in monetary headers; no-result and zero-ranked messages and CSV disabled without a result
    - _Requirements: 8.6, 12.6, 36.1, 36.3, 36.5, 36.7_

  - [ ] 12.2 Write failing audit smoke tests
    - `tests/integration/test_app_smoke.py`: drawer collapsed on load; rank-1 selected by default after a new result; selecting another candidate updates the drawer; inputs unchanged when no candidate is available
    - _Requirements: 36.6, 36.7_

  - [ ]* 12.3 Write property test for the audit source list
    - **Property 56: Audit source list**
    - **Validates: Requirements 36.2**
    - File: `tests/property/test_ui_props.py`

  - [ ] 12.4 Write property test for the export round trip
    - **Property 57: Export round trip** (required by Req 41.5)
    - **Validates: Requirements 36.4, 36.8**
    - File: `tests/property/test_ui_props.py`

  - [ ] 12.5 Implement the audit drawer content
    - `ui/audit.py`: candidate selectbox (default rank-1), formula traces, source list from `ScenarioResult.sources`, Value_Origin labels, FX info, `assumption` badges, empty-state message
    - _Requirements: 8.6, 12.6, 36.1, 36.2, 36.3, 36.6, 36.7_

  - [ ] 12.6 Implement JSON and CSV export
    - `ui/formatting.py` CSV builders; `ui/audit.py` `st.download_button` for JSON (`model_dump_json(indent=2)`, USD) and for the ZIP with both CSVs (D-11, ledger C-012), disabled without a result
    - _Requirements: 36.4, 36.5, 36.7, 36.8_

  - [ ] 12.7 Wire the audit drawer into the app
    - `ui/app.py` places the drawer in tier 3 inside `st.expander("Audit & export", expanded=False)` and resets the selection to rank-1 on a new result
    - _Requirements: 36.6_

  - [ ] 12.8 Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Ensure all tests pass, ask the user if questions arise
    - Run the Demo; next task: Task 13; run the Task 12 `Verify` command
    - _Requirements: 3.3, 4.2, 6.4_

- [ ] 13. Concurrency, performance budget, CI, README and extension seams
  - **Load:** `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 2: Engineering Toolchain and Continuous Integration", § "Requirement 7: Domain Contracts", § "Requirement 14: Workload Profile and Explicit Assumptions", § "Requirement 38: Service Layer and Ports-and-Adapters Architecture", § "Requirement 39: Concurrency and Performance Budget", § "Requirement 40: Extension Seams for Post-MVP Features", § "Requirement 41: Test-Driven Development and Test Suites"; `design.md` § "Concurrency Model", § "Extension Seams (post-MVP)", § "Correctness Properties" › "Property 58", § "Testing Strategy"; `specs/00_INDEX_AND_AGENT_ROUTER.md` (whole file); `specs/07_DATA_CORRECTIONS.md` § "Assumptions"; `README.md`; `src/ai_tco_dss/`; `data/`
  - **Modify:** `.github/workflows/ci.yml`, `README.md`, `specs/00_INDEX_AND_AGENT_ROUTER.md` (append the `## Extension Seams (post-MVP)` section only), `specs/07_DATA_CORRECTIONS.md`, `src/ai_tco_dss/catalog/json_repository.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/settings.py`, `progress.md`, `tests/integration/test_concurrency.py`, `tests/integration/test_performance_budget.py`, `tests/unit/test_contract_signatures.py`, `tests/unit/test_schema_coverage.py`, `tests/unit/test_assumptions_table.py`, `tests/unit/test_ci_and_readme.py`, `tests/unit/test_extension_seams.py`, `tests/property/test_service_props.py`, `tests/property/test_property_coverage.py`
  - **Covers:** 2.6, 2.7, 2.8, 2.9, 7.1, 14.5, 38.5, 39.4, 39.5, 39.6, 39.7, 40.1, 40.3, 41.5
  - **Verify:** `uv run python scripts/verify.py tests/integration/test_concurrency.py tests/integration/test_performance_budget.py tests/unit/test_contract_signatures.py tests/unit/test_schema_coverage.py tests/unit/test_assumptions_table.py tests/unit/test_ci_and_readme.py tests/unit/test_extension_seams.py tests/property/test_service_props.py tests/property/test_property_coverage.py`
  - **Demo:** No new Dashboard behaviour. After the user pushes a branch, the GitHub Actions run shows the six named steps (`install`, `ruff-check`, `ruff-format`, `mypy`, `validate`, `pytest`); `README.md` lists the five commands of Req 2.9.

  - [ ] 13.1 Write failing concurrency tests
    - `tests/integration/test_concurrency.py`: 10 threads × 10 distinct scenarios via `ThreadPoolExecutor` raise no exception, equal the sequential results field by field, and the catalog `model_dump()` is unchanged afterwards
    - _Requirements: 39.4, 39.5, 39.6_

  - [ ] 13.2 Write the performance budget test
    - `tests/integration/test_performance_budget.py`: after catalog warm-up, the median of 5 `recommend` calls on the default scenario is < 0.5 s
    - _Requirements: 39.7_

  - [ ] 13.3 Write contract signature and schema coverage tests
    - `tests/unit/test_contract_signatures.py`: every public engine, decision and Service_Layer function takes and returns Domain_Contracts from `domain/` (inspect type hints)
    - `tests/unit/test_schema_coverage.py`: after running the export, every parameter and return type of the four Service_Layer functions is a Domain_Contract with a schema file in `schemas/`; failures name the function and type
    - _Requirements: 7.1, 40.3_

  - [ ] 13.4 Write the Assumptions table consistency test
    - `tests/unit/test_assumptions_table.py`: the ledger `Assumptions` table has a row for every default listed in Req 14.5 and each stated value equals the value in `settings.py` or `data/`
    - _Requirements: 14.5_

  - [ ] 13.5 Write CI, README and extension seam tests
    - `tests/unit/test_ci_and_readme.py`: the workflow triggers on push and pull_request, uses Python 3.12, has the six named steps with the README commands, and installs with `uv sync --locked` first; `README.md` has one single-line command each for tests, Validate_CLI, Calibration_Report, schema export and Dashboard
    - `tests/unit/test_extension_seams.py`: `specs/00_INDEX_AND_AGENT_ROUTER.md` has exactly one seam entry per post-MVP feature of Req 40.1, each naming the interface, package directory and changed modules (or "none")
    - _Requirements: 2.6, 2.7, 2.8, 2.9, 40.1_

  - [ ] 13.6 Write property test for service determinism
    - **Property 58: Service determinism** (required by Req 41.5)
    - **Validates: Requirements 38.5**
    - File: `tests/property/test_service_props.py`; include the default scenario and every use case × preset combination as explicit examples

  - [ ] 13.7 Write the property coverage meta-test
    - `tests/property/test_property_coverage.py`: scans `requirements.md` for criteria that start with "FOR ALL" or are labelled as a property and asserts each id appears in a property test docstring under `tests/property/`
    - _Requirements: 41.5_

  - [ ] 13.8 Create the GitHub Actions workflow
    - `.github/workflows/ci.yml`: on push and pull_request; Python 3.12; steps `install` (`uv sync --locked`), `ruff-check`, `ruff-format`, `mypy`, `validate`, `pytest`, each with the README command
    - _Requirements: 2.6, 2.7, 2.8_

  - [ ] 13.9 Complete the README commands
    - `README.md`: tests, Validate_CLI, Calibration_Report, schema export (`uv run ai-tco-schemas`) and Dashboard, each one line; CI commands identical
    - _Requirements: 2.9_

  - [ ] 13.10 Append the extension seam table to `specs/00_INDEX_AND_AGENT_ROUTER.md`
    - Append `## Extension Seams (post-MVP)` with the table of `design.md` § "Extension Seams (post-MVP)"; change no existing line
    - _Requirements: 40.1_

  - [ ] 13.11 Fix concurrency and assumption findings
    - Make the concurrency and budget tests pass (lock-guarded repository, no shared mutable state in `scenario_service.py`); align the ledger `Assumptions` table with `settings.py` and `data/`
    - _Requirements: 14.5, 38.5, 39.4, 39.5, 39.6, 39.7_

  - [ ] 13.12 Final checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command
    - Ensure all tests pass, ask the user if questions arise
    - No `not-started` task remains: the Next Session Prompt states this and lists any `in-progress` or `blocked` task ids
    - Run the Task 13 `Verify` command
    - _Requirements: 3.3, 4.2, 4.6, 6.4_

## Notes

- Tasks marked with `*` are optional property tests and can be skipped for a faster MVP; their criteria are also covered by the task's required unit tests. Property tests without `*` are required by Requirement 41.5 and checked by the meta-test in 13.7.
- Each sub-task references criterion ids for traceability; each top-level task lists the full `Covers` set.
- Checkpoints are in 4.10, 8.12, 12.8 and 13.12, so the top-level numbering matches `design.md` § "Task Slicing for Context Switching".
- Task 1 adds a placeholder `src/ai_tco_dss/ui/app.py` and the README Dashboard command so that the Dashboard starts after every task (Req 6.4); Task 1 records this in the `Decisions Log`.
- The accepted open design points are recorded in Task 1's `Decisions Log`: Task 5 combines workload and sizing; CSV export is one ZIP with two CSVs (D-11, ledger C-012); multi-node decode follows Requirement 20.1 literally (D-08, ledger C-011) and the calibration report quantifies the error.
- Per `CLAUDE.md`, sessions stage files with `git add` but do not commit or push.
- The dependency graph orders test sub-tasks before the implementation sub-tasks of the same task, because the Project Rules require tests first.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "1.4"] },
    { "id": 1, "tasks": ["1.5", "1.6", "1.7", "1.8", "1.9"] },
    { "id": 2, "tasks": ["1.10"] },
    { "id": 3, "tasks": ["1.11"] },
    { "id": 4, "tasks": ["2.1", "2.2", "2.3"] },
    { "id": 5, "tasks": ["2.4"] },
    { "id": 6, "tasks": ["2.5"] },
    { "id": 7, "tasks": ["2.6"] },
    { "id": 8, "tasks": ["2.7"] },
    { "id": 9, "tasks": ["2.8", "2.9"] },
    { "id": 10, "tasks": ["2.10"] },
    { "id": 11, "tasks": ["3.1", "3.2", "3.3", "3.4", "3.5"] },
    { "id": 12, "tasks": ["3.6", "3.8"] },
    { "id": 13, "tasks": ["3.7", "3.9"] },
    { "id": 14, "tasks": ["3.10", "3.11"] },
    { "id": 15, "tasks": ["3.12"] },
    { "id": 16, "tasks": ["3.13"] },
    { "id": 17, "tasks": ["4.1", "4.2", "4.3"] },
    { "id": 18, "tasks": ["4.4", "4.5"] },
    { "id": 19, "tasks": ["4.6"] },
    { "id": 20, "tasks": ["4.7"] },
    { "id": 21, "tasks": ["4.8"] },
    { "id": 22, "tasks": ["4.9"] },
    { "id": 23, "tasks": ["4.10"] },
    { "id": 24, "tasks": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.7", "5.15"] },
    { "id": 25, "tasks": ["5.6", "5.8"] },
    { "id": 26, "tasks": ["5.9"] },
    { "id": 27, "tasks": ["5.10"] },
    { "id": 28, "tasks": ["5.11"] },
    { "id": 29, "tasks": ["5.12"] },
    { "id": 30, "tasks": ["5.13"] },
    { "id": 31, "tasks": ["5.14"] },
    { "id": 32, "tasks": ["5.16"] },
    { "id": 33, "tasks": ["5.17"] },
    { "id": 34, "tasks": ["5.18", "5.19"] },
    { "id": 35, "tasks": ["5.20"] },
    { "id": 36, "tasks": ["6.1", "6.2", "6.3", "6.4", "6.10"] },
    { "id": 37, "tasks": ["6.5", "6.11"] },
    { "id": 38, "tasks": ["6.6"] },
    { "id": 39, "tasks": ["6.7"] },
    { "id": 40, "tasks": ["6.8"] },
    { "id": 41, "tasks": ["6.9"] },
    { "id": 42, "tasks": ["6.12"] },
    { "id": 43, "tasks": ["6.13"] },
    { "id": 44, "tasks": ["6.14", "6.15"] },
    { "id": 45, "tasks": ["6.16"] },
    { "id": 46, "tasks": ["7.1", "7.2", "7.3", "7.4", "7.9"] },
    { "id": 47, "tasks": ["7.5", "7.10"] },
    { "id": 48, "tasks": ["7.6", "7.11"] },
    { "id": 49, "tasks": ["7.7"] },
    { "id": 50, "tasks": ["7.8"] },
    { "id": 51, "tasks": ["7.12"] },
    { "id": 52, "tasks": ["7.13"] },
    { "id": 53, "tasks": ["7.14"] },
    { "id": 54, "tasks": ["7.15"] },
    { "id": 55, "tasks": ["8.1", "8.2", "8.3", "8.8"] },
    { "id": 56, "tasks": ["8.4"] },
    { "id": 57, "tasks": ["8.5"] },
    { "id": 58, "tasks": ["8.6"] },
    { "id": 59, "tasks": ["8.7"] },
    { "id": 60, "tasks": ["8.9"] },
    { "id": 61, "tasks": ["8.10", "8.11"] },
    { "id": 62, "tasks": ["8.12"] },
    { "id": 63, "tasks": ["9.1", "9.2", "9.3", "9.4", "9.17"] },
    { "id": 64, "tasks": ["9.5", "9.18"] },
    { "id": 65, "tasks": ["9.6"] },
    { "id": 66, "tasks": ["9.7"] },
    { "id": 67, "tasks": ["9.8"] },
    { "id": 68, "tasks": ["9.9"] },
    { "id": 69, "tasks": ["9.10"] },
    { "id": 70, "tasks": ["9.11"] },
    { "id": 71, "tasks": ["9.12"] },
    { "id": 72, "tasks": ["9.13"] },
    { "id": 73, "tasks": ["9.14"] },
    { "id": 74, "tasks": ["9.15"] },
    { "id": 75, "tasks": ["9.16"] },
    { "id": 76, "tasks": ["9.19"] },
    { "id": 77, "tasks": ["9.20"] },
    { "id": 78, "tasks": ["9.21"] },
    { "id": 79, "tasks": ["9.22"] },
    { "id": 80, "tasks": ["9.23", "9.24"] },
    { "id": 81, "tasks": ["9.25"] },
    { "id": 82, "tasks": ["10.1", "10.2", "10.3"] },
    { "id": 83, "tasks": ["10.4"] },
    { "id": 84, "tasks": ["10.5", "10.6"] },
    { "id": 85, "tasks": ["10.7"] },
    { "id": 86, "tasks": ["10.8"] },
    { "id": 87, "tasks": ["11.1", "11.2", "11.3", "11.4"] },
    { "id": 88, "tasks": ["11.5", "11.7"] },
    { "id": 89, "tasks": ["11.6"] },
    { "id": 90, "tasks": ["11.8"] },
    { "id": 91, "tasks": ["11.9"] },
    { "id": 92, "tasks": ["12.1", "12.2", "12.3"] },
    { "id": 93, "tasks": ["12.4"] },
    { "id": 94, "tasks": ["12.5"] },
    { "id": 95, "tasks": ["12.6"] },
    { "id": 96, "tasks": ["12.7"] },
    { "id": 97, "tasks": ["12.8"] },
    { "id": 98, "tasks": ["13.1", "13.2", "13.3", "13.4", "13.5", "13.6", "13.7"] },
    { "id": 99, "tasks": ["13.8", "13.9", "13.10", "13.11"] },
    { "id": 100, "tasks": ["13.12"] }
  ]
}
```
