# Requirements Document

## Introduction

The Enterprise AI Infrastructure Decision Support System (TCO for Sovereign AI) is the software artefact of a TUM Master's thesis. The system answers three questions for an enterprise that wants to run Large Language Models (LLMs):

1. Will a given LLM physically run on given hardware, and how fast (memory fit, KV cache, decode and prefill throughput, time to first token)?
2. What is the 60-month Total Cost of Ownership (TCO) of a deployment option compared with cloud baselines, including EU staffing, electricity and compliance costs?
3. Which deployment option is recommended for a given use case, based on a ranked multi-criteria decision analysis (MCDA) with explanations?

This document covers the **MVP** only: catalog and provenance, workload, sizing, performance, TCO, cloud baselines (A–D, EU dedicated rental, hybrid split, break-even), the decision engine, and a Streamlit + Plotly dashboard (Views 1 and 2). The following items are **post-MVP**. They are not built in the MVP, but the architecture provides extension seams for them: FastAPI endpoints, an MCP server, a multi-user website, an automated benchmark scraper (Artificial Analysis API, OpenRouter `/api/v1/models`, Hugging Face `config.json`), LiteLLM and PowerBI workload import, an agentic chatbot, a database-backed catalog repository, an "add hardware/model" UI form, and dashboard Views 3–5.

The domain knowledge comes from the existing specification files in the workspace root (router, workload/physics engine, TCO/FinOps, seed catalog, Pydantic schemas, visualization, research sources). Where these files contradict each other or verified external sources, the verified value wins and the deviation is recorded in a corrections ledger. YouTube-derived values (YT-01..YT-22) cannot be fetched and are therefore recorded with tier `community` and a single source.

The work is spec-driven and test-driven, and spans multiple chat sessions. The requirements therefore include session-continuity artefacts (progress file, next-session prompt, global project rules) so that a fresh session can continue the work without conversation history.

## Glossary

- **DSS**: The Enterprise AI Infrastructure Decision Support System as a whole, implemented as the Python package `ai_tco_dss` under `src/ai_tco_dss/`.
- **Repository_Layout**: The agreed directory structure of the project (`specs/`, `src/ai_tco_dss/`, `data/`, `tests/`, `.kiro/`, `progress.md`, `CLAUDE.md`).
- **Progress_File**: The file `progress.md` at the repository root that records current status, a task status table, a decisions log, a changelog, known deviations, the next step and the Next_Session_Prompt.
- **Next_Session_Prompt**: A ready-to-paste text block inside the Progress_File that tells a fresh chat session which files to read and which task to execute next.
- **Project_Rules**: The global working rules for every session, stored in `CLAUDE.md` (appended to the existing behavioral guidelines) and in the Steering_File.
- **Steering_File**: The Kiro steering file `.kiro/steering/project-rules.md` with `inclusion: always` front matter.
- **Task_Scope**: The explicit list of files and specification documents that a single implementation task is allowed to read and modify.
- **Domain_Contract**: A Pydantic v2 model in `src/ai_tco_dss/domain/` that defines an input or output of an engine or of the Service_Layer.
- **Source_Registry**: The file `data/sources.json` listing every cited source with a `source_id`, title, URL or reference, publisher, and tier.
- **Source_Tier**: The trust level of a value: `official` (vendor or regulator), `third_party` (independent benchmark organisation such as Artificial Analysis, Terminal-Bench, SWE-bench), `community` (community or YouTube measurement), `formula` (computed by an engine), or `assumption` (author-chosen value pending real data).
- **Provenance_Record**: Metadata attached to a numeric catalog value: `source_id`, Source_Tier, and access date (ISO 8601).
- **Benchmark_Record**: A measured data point with fields `metric`, `value`, `model_id`, optional `hardware_id`, optional `precision`, optional `context_tokens`, optional `engine`, `source_id`, Source_Tier and `accessed` date.
- **Value_Origin**: A label on every computed performance or cost result stating whether the value is `measured` (taken from a Benchmark_Record) or `formula` (computed by an engine), together with the contributing `source_id` values.
- **Corrections_Ledger**: The file `specs/07_DATA_CORRECTIONS.md` that records every correction of, or known deviation from, the original specification values with old value, new value, sources and decision date.
- **Catalog**: The set of hardware, model, benchmark and reference data loaded from `data/`.
- **Catalog_Item_File**: One JSON file per hardware or model item under `data/catalog/hardware/` or `data/catalog/models/`.
- **Catalog_Repository**: The Python protocol (port) through which engines and the Service_Layer obtain Catalog data.
- **Json_Catalog_Repository**: The MVP implementation of the Catalog_Repository that reads JSON files from `data/`.
- **Validate_CLI**: The command-line entry point that validates all Catalog files against the Domain_Contracts and the Source_Registry.
- **Reference_Data**: The JSON files under `data/reference/` (`fx.json`, `electricity.json`, `staffing_hubs.json`, `harnesses.json`, `use_cases.json`, `rentals.json`) plus the popularity snapshot.
- **FX_Rate**: The EUR→USD conversion rate stored in `data/reference/fx.json` with source and date.
- **Display_Currency**: The currency in which the Dashboard shows monetary values; USD by default, switchable to EUR.
- **Workload_Profile**: The Domain_Contract describing user count, request volume, token volumes, context lengths, concurrency, harness and scheduling of a scenario.
- **Default_Workload_File**: The file `data/workloads/default.json` containing dummy default workload values.
- **Working_Days_Per_Month**: The number of working days per month used for workload volumes; default 22 (assumption).
- **Requests_Per_User_Per_Day**: The number of LLM requests one active user issues per working day; default 40 (assumption).
- **Workload_Engine**: The pure engine that derives effective token volumes (tokenizer inflation, thinking, verification, harness scaffolding, MCP pruning, mega-session compounding) from a Workload_Profile.
- **Sizing_Engine**: The pure engine that computes usable memory, weight memory, KV cache, KV pool, concurrency, multi-node topology and feasibility for a hardware–model–precision–node-count combination.
- **Performance_Engine**: The pure engine that computes decode TPS, prefill TPS, TTFT, effective TPS and 1M-token prefill time, using measured Benchmark_Records first and formulas as fallback.
- **TCO_Engine**: The pure engine that computes CapEx, monthly OpEx, utilization and 60-month cumulative on-premise TCO.
- **Baseline_Engine**: The pure engine that computes Baselines A–D, EU dedicated rental cost, the hybrid split, break-even months and the 60-month timeline.
- **Decision_Engine**: The pure engine that generates Candidates, applies Hard_Filters, computes Criteria, normalises and ranks Candidates, and produces explanations.
- **Service_Layer**: The module `src/ai_tco_dss/services/` exposing `evaluate_scenario`, `recommend`, `size` and `project_tco`; the only entry point used by adapters.
- **Adapter**: A delivery mechanism that calls the Service_Layer (Streamlit Dashboard in the MVP; FastAPI, MCP server and scraper post-MVP).
- **Dashboard**: The Streamlit + Plotly user interface in `src/ai_tco_dss/ui/`.
- **Simulator_Card**: A Dashboard panel in Views 1 and 2 that owns its own input widgets.
- **Candidate**: One deployment option evaluated by the Decision_Engine: an on-premise hardware × node count × model × precision combination, a cloud API model, an EU dedicated rental × model combination, or a hybrid split.
- **Hard_Filter**: A pass/fail rule that removes a Candidate from ranking and records a rejection reason.
- **Criterion**: A ranking dimension: 60-month TCO (minimise), quality (maximise), effective TPS (maximise), TTFT (minimise), risk (minimise), popularity (maximise).
- **SAW**: Simple Additive Weighting (weighted sum) ranking method; the default.
- **TOPSIS**: Technique for Order of Preference by Similarity to Ideal Solution; an Expert_Mode alternative ranking method.
- **Use_Case**: One of `writing-email`, `summarisation-rag`, `coding-assistant`, `agentic-coding`, defined in `data/reference/use_cases.json`.
- **Quality_Floor**: The minimum benchmark score a model must reach for a Use_Case, measured on the Use_Case's matching benchmark.
- **Preset**: A named Criterion weight set for Normal_Mode: `cheapest`, `best-fit`, `most-capable`, `popular`.
- **Popularity_Snapshot**: A dated manual snapshot of OpenRouter usage rankings stored in Reference_Data with a Provenance_Record.
- **Normal_Mode**: The Dashboard mode in which the user selects only Use_Case, user count and Preset.
- **Expert_Mode**: The Dashboard mode in which the user can set all scenario parameters, Criterion weights and the ranking method.
- **Utilization**: Demanded tokens per month divided by capacity tokens per month of a deployment (definition in Requirement 23).
- **Break_Even_Month**: The first month m in [1, 60] in which the cumulative on-premise TCO is less than or equal to the cumulative cost of a compared baseline.
- **Hybrid_Split**: A deployment in which a share `local_offload_ratio` of demanded tokens is served on-premise and the remainder by an EU-pinned frontier API.
- **EU_Rental**: A dedicated GPU server rented in an EU data centre (Hetzner GEX63, Hetzner GEX430).
- **Calibration_Report**: The command-line report that prints formula-versus-measured Mean Absolute Percentage Error (MAPE) per metric.
- **MVP_Catalog**: The curated set of hardware, models and EU_Rentals listed in Requirement 10.

## Requirements

### Requirement 1: Repository Organisation

**User Story:** As the thesis author, I want the specification files and code organised in an agreed layout, so that every session and every coding agent finds files at predictable paths.

#### Acceptance Criteria

1. THE DSS SHALL store the six existing domain specification files under `specs/` according to the following mapping from the original workspace-root file name to the new file name: `index_agent_router.md` → `00_INDEX_AND_AGENT_ROUTER.md`; `workload_profiler_physical_sizing_engine (1).md` → `01_WORKLOAD_AND_PHYSICS_ENGINE.md`; `financial_tco_eu_finops_cross_border_personnel_arbitrage (1).md` → `02_TCO_FINOPS_AND_EU_COMPLIANCE.md`; `2026_calibrated_hardware_model_intelligence_seed_catalog (1).md` → `03_CALIBRATED_2026_SEED_DATA.md`; `pydantic_v2_core_schemas_contracts (1).md` → `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md`; `visualization_ux_standards_phased_execution_plan (1).md` → `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`.
2. THE DSS SHALL store the research sources file `research_sources_benchmark_evidence (1).md` as `specs/06_RESEARCH_SOURCES.md`.
3. THE DSS SHALL contain the Corrections_Ledger as a git-tracked file at `specs/07_DATA_CORRECTIONS.md`.
4. IF a specification file is tracked by git at relocation time, THEN THE DSS SHALL relocate the file with `git mv`, so that `git log --follow` on the new path lists the commits made under the old path and the old path no longer exists in the working tree.
5. IF a specification file is untracked by git at relocation time, THEN THE DSS SHALL move the file to its new path, add the file to git under the new path, and leave no file at the old path.
6. THE DSS SHALL place the Python package at `src/ai_tco_dss/` with the module `settings.py` and the sub-packages `domain`, `catalog`, `engines`, `decision`, `services` and `ui`, each sub-package being a directory directly under `src/ai_tco_dss/` that contains an `__init__.py` file.
7. THE DSS SHALL contain the file `data/sources.json`, the directories `data/catalog/hardware/`, `data/catalog/models/`, `data/benchmarks/` and `data/reference/`, the six files `fx.json`, `electricity.json`, `staffing_hubs.json`, `harnesses.json`, `use_cases.json` and `rentals.json` directly inside `data/reference/`, and the file `data/workloads/default.json`.
8. THE DSS SHALL contain the four test directories `tests/unit/`, `tests/calibration/`, `tests/property/` and `tests/integration/`.
9. WHEN a specification file is relocated, THE DSS SHALL replace every occurrence of the file's old name, with or without the ` (1)` suffix, in all files under `specs/` with the new file name, so that a case-sensitive search of `specs/` for each of the seven old file names returns zero matches.
10. WHEN a specification file is relocated, THE DSS SHALL keep the file content identical to the original content except for the cross-reference replacements defined in criterion 9.
11. IF the target path of a specification file already exists at relocation time, THEN THE DSS SHALL leave both the existing target file and the source file unchanged and report the conflicting path to the user instead of overwriting the target.

### Requirement 2: Engineering Toolchain and Continuous Integration

**User Story:** As the thesis author, I want a reproducible Python toolchain with automated checks, so that every change is verified the same way locally and in CI.

#### Acceptance Criteria

1. THE DSS SHALL declare `requires-python = ">=3.12,<3.13"` in `pyproject.toml`, SHALL declare every runtime and development dependency (including `ruff`, `mypy`, `pytest` and `hypothesis`) in `pyproject.toml`, and SHALL keep the `uv` lock file `uv.lock` committed to the repository.
2. WHEN `uv sync --locked` runs from the repository root of a clean checkout on Python 3.12, THE DSS SHALL install all declared dependencies and exit with code 0, without modifying `uv.lock`.
3. THE DSS SHALL configure `ruff` (lint and format), `mypy` (with `strict = true`) and `pytest` in `pyproject.toml`, so that each tool runs without command-line configuration flags.
4. WHEN `ruff check` and `ruff format --check` run from the repository root on `src/` and `tests/`, THE DSS SHALL report zero lint violations and zero files requiring reformatting.
5. WHEN `mypy` runs on `src/ai_tco_dss/` with the strict-mode configuration from `pyproject.toml`, THE DSS SHALL report zero type errors.
6. WHEN a commit is pushed to any branch or a pull request is opened or updated, THE GitHub Actions workflow SHALL install dependencies with `uv sync --locked` on Python 3.12, and SHALL then run `ruff check`, `ruff format --check`, `mypy`, the Validate_CLI and `pytest`, using the same commands that are documented in `README.md`.
7. IF any step of the GitHub Actions workflow exits with a non-zero code, THEN THE GitHub Actions workflow SHALL mark the run as failed, and SHALL identify the failing step by name in the run result.
8. IF `uv.lock` does not match the dependencies declared in `pyproject.toml`, THEN THE GitHub Actions workflow SHALL fail at the dependency installation step before running any check.
9. THE DSS SHALL document in `README.md` one single-line shell command each, runnable from the repository root after `uv sync`, for running the tests, the Validate_CLI, the Calibration_Report, the JSON Schema export and the Dashboard.

### Requirement 3: Progress File for Session Continuity

**User Story:** As the thesis author who switches between chat sessions, I want a single progress file that captures the project state, so that a fresh session can continue the work without prior conversation history.

#### Acceptance Criteria

1. THE DSS SHALL contain a Progress_File at the repository root path `progress.md` with exactly one level-2 heading for each of the sections `Current Status`, `Task Status`, `Decisions Log`, `Changelog`, `Known Deviations`, `Next Step` and `Next Session Prompt`, in this order.
2. THE Progress_File `Task Status` section SHALL contain one row for every task id present in the spec `tasks.md`, with no missing and no duplicate task ids. Each row SHALL hold the task id, the task title as written in `tasks.md`, exactly one status from `not-started`, `in-progress`, `done` or `blocked`, and a completion date in ISO 8601 format (YYYY-MM-DD). The completion date SHALL be filled only for tasks with status `done` and left empty for all other statuses.
3. WHEN an implementation task finishes, THE executing session SHALL, before reporting the task as complete, set the task's `Task Status` row to `done` with the current date, rewrite `Current Status` to describe the state after the task, append one `Changelog` entry containing the date, the task id and the list of files created or modified, and set `Next Step` to the task id and title of the next task with status `not-started` in `tasks.md` order.
4. WHEN a design or scope decision is made during a session, THE executing session SHALL append one entry to the Progress_File `Decisions Log` containing the ISO 8601 date, the decision, the rationale and the affected requirement or task ids, and SHALL leave all earlier `Decisions Log` entries unchanged. A design or scope decision is any choice that adds, removes or changes a requirement, task, Domain_Contract, file location or value fixed in the spec documents, or that selects between alternatives the spec documents leave open.
5. THE Progress_File `Known Deviations` section SHALL list each known deviation with at least one Corrections_Ledger entry id, and every referenced id SHALL exist in `specs/07_DATA_CORRECTIONS.md`. IF no deviations are known, THEN THE Progress_File `Known Deviations` section SHALL state that no deviations are recorded.
6. WHEN the executing session updates the Progress_File `Next Step` section, THE executing session SHALL update the `Next Session Prompt` section so that it names the same next task id, lists the files to read (at minimum `CLAUDE.md`, `progress.md` and the spec documents in the next task's Task_Scope), and can be pasted into a fresh session without edits.
7. IF an implementation task cannot be completed in a session, THEN THE executing session SHALL set the task's `Task Status` row to `blocked` or `in-progress`, record the blocking reason or the remaining open work in `Current Status`, and set `Next Step` and `Next Session Prompt` to resume that task, without marking the task `done`.

### Requirement 4: Next Session Prompt and Self-Contained Tasks

**User Story:** As the thesis author, I want a ready-to-paste prompt and self-contained tasks, so that I can start any task in a fresh chat with minimal setup.

#### Acceptance Criteria

1. THE Progress_File SHALL contain exactly one Next_Session_Prompt, placed in a single fenced code block of at most 50 lines, that lists the files to read first in the order Project_Rules (`CLAUDE.md`), Progress_File, spec `requirements.md`, spec `design.md`, spec `tasks.md`, names the next task id, and lists a Task_Scope identical to the Task_Scope given for that task id in the spec `tasks.md`.
2. WHEN an implementation task's status is set to `done` in the Progress_File `Task Status` section, THE executing session SHALL rewrite the Next_Session_Prompt, before reporting the task as complete, so that it names the first task in spec `tasks.md` order whose status is `not-started`, together with that task's Task_Scope.
3. THE spec `tasks.md` SHALL list for every task: the files and specification sections to load, with each section identified by file path and section heading; the files and directories the task may create or modify, as explicit paths; the ids of the covered requirement criteria in the form `<requirement number>.<criterion number>`, each of which exists in the spec `requirements.md`; and one verification command line that runs from the repository root and exits with code 0 only when the task's checks pass.
4. THE spec `tasks.md` SHALL describe every task so that the description references only the Project_Rules, the Progress_File, the spec documents and the files in the task's Task_Scope, and contains no reference to decisions or content that exist only in prior conversation history.
5. THE Next_Session_Prompt SHALL be usable by pasting it unchanged into a fresh chat session, containing no placeholder text that the user must fill in and no reference to content that exists only in prior conversation history.
6. IF no task with status `not-started` remains when an implementation task's status is set to `done`, THEN THE executing session SHALL rewrite the Next_Session_Prompt to state that no not-started task remains and to list the ids of all tasks with status `in-progress` or `blocked`.
7. THE spec `tasks.md` SHALL list as files to load for a task only files that either exist in the Repository_Layout before the first task starts or are created by a task that precedes that task in spec `tasks.md` order.

### Requirement 5: Global Project Rules

**User Story:** As the thesis author, I want global project rules that load automatically in every session, so that every agent follows the same process and data rules.

#### Acceptance Criteria

1. THE DSS SHALL contain exactly one level-2 heading `## Project Rules` in `CLAUDE.md`, placed after the last line of the existing content (the title, the introduction, sections 1–4 and the closing "These guidelines are working if" paragraph).
2. THE DSS SHALL keep every line of the existing content of `CLAUDE.md` above the `## Project Rules` heading unchanged character for character, compared with the version before the section was appended.
3. THE DSS SHALL contain the Steering_File `.kiro/steering/project-rules.md`, which SHALL begin with a front matter block delimited by `---` on its first line and on a closing line, and the front matter block SHALL contain the line `inclusion: always`.
4. THE Project_Rules SHALL list each of the following eight rules as a separate numbered list item: (1) at the start of every session, read the Progress_File before reading or modifying any other project file; (2) work test-first, writing a test that fails before writing the implementation that makes it pass; (3) attach a Provenance_Record (`source_id`, Source_Tier, ISO 8601 access date) to every numeric value in the Catalog; (4) when both a measured value (Benchmark_Record) and a formula value exist for the same metric, use the measured value; (5) use USD as the default currency; (6) modify only files listed in the current Task_Scope; (7) record every detected data contradiction in the Corrections_Ledger with old value, new value, sources and decision date; (8) before finishing a task, update the Progress_File and the Next_Session_Prompt.
5. THE Steering_File and the `## Project Rules` section of `CLAUDE.md` SHALL contain the same rule items in the same order, with identical wording for each item once leading and trailing whitespace is ignored.
6. WHEN a rule item is added, removed or reworded in either the Steering_File or the `## Project Rules` section of `CLAUDE.md`, THE DSS SHALL apply the same change to the other file in the same change set, so that criterion 5 still holds afterwards.

### Requirement 6: Incremental Visible Progress

**User Story:** As the thesis author, I want each task to produce something visible in the Streamlit app early, so that I can demo progress continuously.

#### Acceptance Criteria

1. THE spec `tasks.md` SHALL schedule a runnable Dashboard skeleton in one of the top-level implementation tasks numbered 1 to 3, where the skeleton obtains Catalog data only through the Service_Layer and displays the number of hardware items and the number of model items loaded from the Catalog.
2. THE spec `tasks.md` SHALL include a demo step for every task that adds or changes engine or Service_Layer behaviour, where the demo step names the Dashboard view and element that shows the new behaviour, the input values the user sets, and the expected visible output.
3. THE `README.md` SHALL document exactly one command, run from the repository root, that starts the Dashboard.
4. WHEN an implementation task is marked done in the Progress_File task status table, THE Dashboard SHALL start with the command documented in `README.md` and render its start page within 30 seconds, without showing any Python exception, traceback or Streamlit error message in the browser page or the terminal.
5. IF the Dashboard does not meet the start condition in criterion 4 at the end of an implementation task, THEN THE Progress_File SHALL record that task's status as not done and record the observed start failure in the known deviations section.

### Requirement 7: Domain Contracts

**User Story:** As a developer, I want strict, immutable data contracts for all engine inputs and outputs, so that engines are deterministic and future adapters can reuse the same contracts.

#### Acceptance Criteria

1. THE DSS SHALL define every input parameter and every return value of the Workload_Engine, Sizing_Engine, Performance_Engine, TCO_Engine, Baseline_Engine and Decision_Engine, and of the Service_Layer functions `evaluate_scenario`, `recommend`, `size` and `project_tco`, as a Domain_Contract built with Pydantic v2 and located in `src/ai_tco_dss/domain/`.
2. THE Domain_Contracts SHALL be configured with `frozen=True` and `extra="forbid"`.
3. IF code attempts to assign a new value to a field of an existing Domain_Contract instance, THEN THE Domain_Contract SHALL raise a validation error that names the field, and the field SHALL keep its original value.
4. IF a Domain_Contract receives a field that is not declared, THEN THE Domain_Contract SHALL raise a validation error that names the undeclared field and SHALL NOT create an instance.
5. IF a Domain_Contract receives a value that violates a declared constraint (numeric minimum or maximum, string or list length limit, or allowed enumeration member), THEN THE Domain_Contract SHALL raise a validation error that names the field and the violated constraint and SHALL NOT create an instance.
6. IF a Domain_Contract is constructed without a required field, or with a value that cannot be validated as the declared field type, THEN THE Domain_Contract SHALL raise a validation error that names each affected field and SHALL NOT create an instance.
7. THE Domain_Contracts SHALL take field names, enumeration members and default values from `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md`, and every field name, enumeration member or default value that differs from that file SHALL have an entry in the Corrections_Ledger stating the contract name, field, old value, new value, sources and decision date.
8. WHEN a developer runs the schema export command, THE DSS SHALL create the `schemas/` directory if it does not exist and write one JSON Schema file per Service_Layer input and output Domain_Contract, each file named after its contract and containing the JSON Schema that Pydantic v2 generates for that contract.
9. WHEN the schema export command is run twice with no change to the Domain_Contracts, THE DSS SHALL produce byte-identical files on the second run and exit with status code 0.
10. IF the schema export command cannot generate or write the schema of a Domain_Contract, THEN THE DSS SHALL exit with a non-zero status code and print an error message naming that Domain_Contract.
11. FOR ALL valid Domain_Contract instances, serialising the instance to JSON and then validating that JSON with the same Domain_Contract SHALL produce an instance equal to the original (round-trip property).

### Requirement 8: Source Registry and Provenance

**User Story:** As the thesis author, I want every catalog number to carry its source, trust tier and access date, so that every result in the thesis is traceable and auditable.

#### Acceptance Criteria

1. THE Source_Registry SHALL contain one entry per source referenced by the Catalog, and each entry SHALL have a non-empty `source_id`, a non-empty title, a non-empty URL or bibliographic reference, a non-empty publisher, and exactly one Source_Tier from the set `official`, `third_party`, `community`, `formula`, `assumption`.
2. THE Source_Registry SHALL contain the entries YT-01 to YT-22 that are present in `specs/06_RESEARCH_SOURCES.md` with Source_Tier `community`, and the 10 entries IND-01 to IND-10 with Source_Tier chosen by publisher type: `official` if the publisher is the vendor of the described product, a regulator or a statistics authority; `third_party` if the publisher is an independent benchmark or analysis organisation; `community` for any other publisher.
3. THE Catalog SHALL attach a Provenance_Record, consisting of a `source_id`, a Source_Tier and an access date in ISO 8601 format `YYYY-MM-DD`, to every numeric field in every Catalog_Item_File, Benchmark_Record and Reference_Data file, where the `source_id`, Source_Tier and `accessed` fields of a Benchmark_Record count as the Provenance_Record of that record's numeric fields.
4. IF a Provenance_Record references a `source_id` that is missing from the Source_Registry, THEN THE Validate_CLI SHALL report an error naming the file, the field and the missing `source_id`.
5. IF a numeric field in a Catalog_Item_File, Benchmark_Record or Reference_Data file lacks a Provenance_Record, THEN THE Validate_CLI SHALL report an error naming the file and the field.
6. WHEN the audit drawer of the Dashboard displays a value whose Provenance_Record has Source_Tier `assumption`, THE Dashboard SHALL display an `assumption` badge adjacent to that value, and THE Dashboard SHALL display no `assumption` badge next to values with any other Source_Tier.
7. IF a catalog value is derived from exactly one source and that source is one of YT-01 to YT-22, THEN THE Catalog SHALL record the value's Provenance_Record with Source_Tier `community` and the note `single-source`.
8. IF the Source_Registry contains two or more entries with the same `source_id`, or an entry lacks any field listed in criterion 1, or an entry has a Source_Tier outside the five allowed values, THEN THE Validate_CLI SHALL report an error naming the `source_id` and the duplicate, missing or invalid field.
9. IF a Provenance_Record has a Source_Tier outside the five allowed values, an access date not in `YYYY-MM-DD` format, an access date later than the date of the validation run, or references one of YT-01 to YT-22 with a Source_Tier other than `community`, THEN THE Validate_CLI SHALL report an error naming the file, the field and the violated rule.
10. WHEN the Validate_CLI finishes a run, THE Validate_CLI SHALL report all errors found across all Catalog files and the Source_Registry in that single run, without stopping at the first error, and SHALL exit with status 0 if it found zero errors and a non-zero status otherwise.

### Requirement 9: Benchmark Records and Measured-First Resolution

**User Story:** As the thesis author, I want measured benchmarks to take priority over formulas, so that results are grounded in empirical evidence and the thesis can show where formulas are used.

#### Acceptance Criteria

1. THE Catalog SHALL store measured performance and quality data as Benchmark_Records in JSON files under `data/benchmarks/`, with each Benchmark_Record carrying the fields listed for Benchmark_Record in the Glossary.
2. THE Catalog SHALL store a `context_tokens` integer value of at least 1 on every Benchmark_Record whose `metric` is prefill speed, decode speed, aggregate throughput or TTFT.
3. WHEN two or more Benchmark_Records match the same metric, model, hardware and precision and lie within the context-match tolerance, THE Performance_Engine SHALL select exactly one record in this order: highest Source_Tier (`official` > `third_party` > `community`); then latest `accessed` date; then smallest absolute difference between the record's `context_tokens` and the target context; then the lowest `source_id` in lexicographic order.
4. WHEN the Performance_Engine resolves a prefill TPS, decode TPS or TTFT value for a target model, hardware, precision and context length, and at least one Benchmark_Record has equal `metric`, `model_id`, `hardware_id` and `precision` and a `context_tokens` value satisfying |`context_tokens` − target context| ≤ tolerance × target context, THE Performance_Engine SHALL use the value of the selected record and set Value_Origin to `measured`.
5. THE DSS SHALL define the context-match tolerance in `settings.py` as a fraction of the target context, with permitted values from 0 to 1 inclusive and default 0.25 (±25 %), labelled `assumption`.
6. IF no Benchmark_Record has equal `metric`, `model_id`, `hardware_id` and `precision` with a `context_tokens` value inside the context-match tolerance, including the case where every otherwise matching record lies outside the tolerance, THEN THE Performance_Engine SHALL compute the value with the formula from `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` and set Value_Origin to `formula`.
7. THE Service_Layer SHALL return a Value_Origin with a list of at least one contributing `source_id` for every decode TPS, prefill TPS, TTFT, effective TPS, quality score and price value in every result. Every listed `source_id` SHALL exist in the Source_Registry. For a `measured` value the list SHALL contain the `source_id` of the selected Benchmark_Record. For a `formula` value the list SHALL contain the `source_id` values of the Catalog values used as formula inputs.
8. IF a Benchmark_Record whose `metric` is prefill speed, decode speed, aggregate throughput or TTFT has no `context_tokens` value or a value below 1, THEN THE Validate_CLI SHALL report an error naming the file and the record, and exit with a non-zero exit code.
9. WHEN the Performance_Engine resolves a quality score for a target model, and at least one Benchmark_Record has equal `metric` and `model_id`, THE Performance_Engine SHALL select one record using the order in criterion 3 without the context-difference step, use its value, and set Value_Origin to `measured`.
10. IF the context-match tolerance in `settings.py` is below 0 or above 1, THEN THE DSS SHALL raise a configuration error naming the setting and its value, and SHALL return no result.

### Requirement 10: Curated MVP Catalog Contents

**User Story:** As the thesis author, I want a curated, current-generation catalog, so that recommendations reflect hardware and models an enterprise would procure today.

#### Acceptance Criteria

1. THE MVP_Catalog SHALL contain exactly one Catalog_Item_File under `data/catalog/models/` for each of the open-weights models Gemma 4 12B, Qwen 3.8-27B, Qwen 3.6-35B-A3B, gpt-oss-120b, Qwen 3.8 Flash Next, GLM 5.3 Flash, DeepSeek V4.1 Flash and Kimi K3.1 Pro.
2. THE MVP_Catalog SHALL describe gpt-oss-120b as a mixture-of-experts model with 117 billion total parameters and 5.1 billion active parameters, each parameter count carrying a Provenance_Record.
3. THE MVP_Catalog SHALL contain exactly one Catalog_Item_File under `data/catalog/models/` for each of the commercial API models Claude Opus 5.5, Claude Sonnet 5.5, GPT-6.1 and Gemini 3.1 Pro, each recording a global (non-region-specific) input price, output price and cache-read price in USD per million tokens as a value greater than 0, and each price carrying a Provenance_Record with Source_Tier `official`.
4. THE MVP_Catalog SHALL contain exactly one Catalog_Item_File under `data/catalog/hardware/` for each of the hardware items RTX 5060 Ti 16GB, RTX 5070 with 64 GB DDR5 Strata offload, Mac Mini M5 Pro 64GB, Mac Studio M5 Max 128GB, Mac Studio M5 Ultra 256GB, AMD Strix Halo 128GB, DGX Spark 128GB, RTX Pro 6000 96GB and H100 SXM 80GB.
5. THE MVP_Catalog SHALL declare the valid node counts {1, 2, 4} for DGX Spark 128GB, {1, 4, 8} for RTX Pro 6000 96GB, {8} for H100 SXM 80GB and {1} for every other hardware item listed in criterion 4.
6. THE MVP_Catalog SHALL contain the EU_Rentals Hetzner GEX63 (1× RTX Pro 6000 96GB, €999 per month plus €999 one-time setup fee) and Hetzner GEX430 (4× RTX Pro 6000 96GB, €3,599 per month plus €3,599 one-time setup fee), each price carrying a Provenance_Record.
7. THE MVP_Catalog SHALL record a non-empty license type for every model listed in criteria 1 and 3, and SHALL set `eu_commercial_license_valid = false` for every model whose license type is the Meta Llama 4 Multimodal License.
8. THE MVP_Catalog SHALL record for every model listed in criteria 1 and 3 each available quality score among Artificial Analysis Intelligence Index v5, Terminal-Bench and SWE-bench as a value in the range 0 to 100, each with a Provenance_Record whose `source_id` exists in the Source_Registry, and SHALL leave an unavailable score absent rather than recording it as 0.
9. THE Corrections_Ledger SHALL contain an entry for gpt-oss-120b recording the old classification "dense", the new classification "mixture-of-experts (117B total, 5.1B active)", the supporting `source_id` values and the decision date in ISO 8601 format.
10. THE Corrections_Ledger SHALL contain an entry for Hetzner GEX63 recording the old monthly price €1,197, the new monthly price €999, the supporting `source_id` values and the decision date in ISO 8601 format.
11. IF any item listed in criteria 1, 3, 4 or 6 is missing from the Catalog, or any price, parameter count or quality score required by criteria 2, 3, 6 or 8 lacks a Provenance_Record whose `source_id` exists in the Source_Registry, THEN THE Validate_CLI SHALL report the identifier of each affected item and the missing field, and SHALL exit with a non-zero exit status.

### Requirement 11: Extensible Catalog Files and Validate CLI

**User Story:** As a thesis reader or company user, I want to add hardware and models by dropping a JSON file into a folder, so that the catalog grows without code changes.

#### Acceptance Criteria

1. THE Catalog SHALL store each hardware item as exactly one Catalog_Item_File directly under `data/catalog/hardware/` and each model item as exactly one Catalog_Item_File directly under `data/catalog/models/`, where the file name equals the item `id` followed by the extension `.json`.
2. WHEN a new Catalog_Item_File that passes Validate_CLI validation is added under `data/catalog/hardware/` or `data/catalog/models/`, THE Json_Catalog_Repository SHALL return the new item on the next catalog load (the next creation of a Json_Catalog_Repository instance or the next restart of the Dashboard) without any change to Python source files, and SHALL ignore files in those folders whose extension is not `.json`.
3. WHEN the Validate_CLI runs, THE Validate_CLI SHALL validate every Catalog_Item_File, every Benchmark_Record file and every Reference_Data file against its Domain_Contract, and SHALL continue validating the remaining files after an error is found, so that one run reports all errors across all files.
4. IF the Validate_CLI finds one or more errors, THEN THE Validate_CLI SHALL print one line per error containing the file path, the field path (or, for a file that is not parseable JSON, the line and column of the parse error) and a message stating the cause, SHALL print the total error count, and SHALL exit with code 1.
5. IF two or more Catalog_Item_Files declare the same `id`, whether both are under `data/catalog/hardware/`, both are under `data/catalog/models/`, or one is in each folder, THEN THE Validate_CLI SHALL report one duplicate-id error that names the duplicated `id` and the file paths of all files that declare it.
6. IF a Benchmark_Record references a `model_id` or `hardware_id` that matches no item `id` in the Catalog, or if a Benchmark_Record or Provenance_Record references a `source_id` that is absent from the Source_Registry, THEN THE Validate_CLI SHALL report a dangling-reference error that names the file path, the field path and the unresolved identifier.
7. THE DSS SHALL document the Catalog_Item_File format in `data/catalog/README.md` with one annotated example for the hardware item type and one for the model item type. Each example SHALL contain every required field of its Domain_Contract, SHALL state for each field its meaning, its unit (where numeric) and whether it is required or optional, and SHALL pass validation against its Domain_Contract when copied unchanged into a Catalog_Item_File.
8. IF a Catalog_Item_File's file name without the `.json` extension differs from the `id` declared inside the file, THEN THE Validate_CLI SHALL report a filename-id mismatch error that names the file path and the declared `id`.
9. IF the Validate_CLI finds zero errors, THEN THE Validate_CLI SHALL print a summary stating the number of files validated per file type (hardware, model, Benchmark_Record, Reference_Data) and SHALL exit with code 0.
10. IF a Catalog_Item_File fails validation against its Domain_Contract or is not parseable JSON during a catalog load, THEN THE Json_Catalog_Repository SHALL raise an error that names the file path and the failing field path, and SHALL return no partial Catalog.

### Requirement 12: Currency and FX Conversion

**User Story:** As a decision-maker, I want all costs in one currency with a recorded exchange rate, so that EUR-denominated inputs and USD API prices are comparable.

#### Acceptance Criteria

1. THE DSS SHALL use USD as the internal calculation currency for all engines and the Service_Layer, and SHALL set the Display_Currency to USD when a Dashboard session starts.
2. THE Reference_Data file `fx.json` SHALL store exactly one EUR→USD FX_Rate as a positive decimal number expressed in USD per 1 EUR, together with a `source_id` that exists in the Source_Registry and a rate date in ISO 8601 format (YYYY-MM-DD).
3. WHEN a catalog or reference value is denominated in EUR, THE Catalog_Repository SHALL convert the value to USD by multiplying the EUR amount by the FX_Rate before returning the value, so that no engine and no Service_Layer function receives an EUR-denominated value.
4. WHERE Expert_Mode is active, WHEN the user enters an FX_Rate override that is a number between 0.50 and 2.00 USD per EUR inclusive with at most 6 decimal places, THE Dashboard SHALL use the override as the active FX_Rate for all conversions and recalculated results in the current session, without modifying `fx.json`.
5. WHEN the user changes the Display_Currency, THE Dashboard SHALL display every monetary value (KPI cards, tables, chart axes and chart tooltips) in the selected currency, rounded to 2 decimal places: USD values unchanged and labelled with the $ symbol, or EUR values computed as the USD amount divided by the active FX_Rate and labelled with the € symbol, while the internal USD results remain unchanged.
6. WHEN the user opens the Dashboard audit drawer, THE Dashboard SHALL display the active FX_Rate value with at least 4 decimal places, the `source_id` and rate date from `fx.json`, and a label stating whether the active FX_Rate comes from `fx.json` or from an Expert_Mode user override.
7. FOR ALL monetary amounts from 0 to 1,000,000,000,000 USD and FOR ALL FX_Rate values from 0.50 to 2.00, converting USD→EUR and then EUR→USD with the same FX_Rate and without intermediate display rounding SHALL reproduce the original amount within 0.01 USD (round-trip property).
8. IF the user enters an FX_Rate override that is non-numeric, outside the range 0.50 to 2.00 USD per EUR, or has more than 6 decimal places, THEN THE Dashboard SHALL reject the override, display an error message indicating the allowed range and precision, and keep the previously active FX_Rate and all displayed results unchanged.
9. IF `fx.json` is missing, contains no FX_Rate, contains a non-positive FX_Rate, contains a rate date not in ISO 8601 format, or references a `source_id` absent from the Source_Registry, THEN THE Catalog_Repository SHALL raise an error naming `fx.json` and the failing field, and SHALL NOT return any EUR-to-USD converted value.

### Requirement 13: Reference Data

**User Story:** As the thesis author, I want electricity tariffs, staffing hubs, harnesses, use cases and rentals as data files, so that assumptions can be changed without code changes.

#### Acceptance Criteria

1. THE Reference_Data file `electricity.json` SHALL contain exactly the tariffs `de-industrial-bdew` (€0.172/kWh), `de-office` (€0.280/kWh) and `eu-nordic` (€0.095/kWh), each stored as a price in EUR per kWh greater than 0 and at most €1.00/kWh, and each with its own Provenance_Record.
2. THE Reference_Data file `staffing_hubs.json` SHALL contain the hubs `de-munich-hq`, `de-berlin-hamburg`, `ro-cluj-bucharest` and `pl-warsaw-krakow`, each with a base MLOps salary in EUR per year (greater than 0), an employer social tax rate in percent (0 to 100 inclusive) and a recruiting delay in whole months (0 to 24 inclusive), and each of these three values SHALL carry its own Provenance_Record.
3. THE Reference_Data file `harnesses.json` SHALL contain the scaffolding tokens per turn as non-negative integers for `claude-code` (33,000), `codex` (13,000), `opencode` (7,000) and `deepseek-dsh` (4,200), each with a Provenance_Record, and SHALL contain for `custom-lean` a default value with Source_Tier `assumption` that a Workload_Profile can override with an integer from 0 to 100,000 tokens per turn.
4. THE Reference_Data file `use_cases.json` SHALL define for each of the four Use_Cases (`writing-email`, `summarisation-rag`, `coding-assistant`, `agentic-coding`) one matching benchmark, an optional second-choice benchmark (as defined in Requirement 31), and a Quality_Floor from 0 to 100 inclusive on the matching benchmark's score scale, with a Provenance_Record for each Quality_Floor.
5. THE Reference_Data file `rentals.json` SHALL contain the EU_Rentals Hetzner GEX63 and Hetzner GEX430, each with a monthly price in EUR (greater than 0), a one-time setup fee in EUR (0 or greater, stored explicitly even when 0), the GPU type, the GPU count (positive integer) and a Provenance_Record, with values equal to those stated for the MVP_Catalog in Requirement 10.
6. THE Corrections_Ledger SHALL contain one entry for the Romania employer tax inconsistency that states the 2.25 % statutory CAM value, the approximately 4 % value that includes benefits, the chosen value, the sources and the decision date, and the employer social tax rate stored for `ro-cluj-bucharest` in `staffing_hubs.json` SHALL equal the chosen value in that entry.
7. WHEN a value in a Reference_Data file is edited and the Catalog is loaded again, THE DSS SHALL use the edited value in all engine results without any change to Python source code.
8. IF a Reference_Data file is missing a required entry listed in criteria 1–5, or contains a value outside the bounds stated in criteria 1–5, THEN THE Validate_CLI SHALL report an error naming the file, the entry identifier and the field, and SHALL exit with a non-zero code.

### Requirement 14: Workload Profile and Explicit Assumptions

**User Story:** As the thesis author, I want a swappable dummy workload with every undefined term explicitly defined, so that later real company data from PowerBI can replace the dummy values without code changes.

#### Acceptance Criteria

1. THE Default_Workload_File SHALL contain a Workload_Profile that validates against the Workload_Profile Domain_Contract with 25 active users, 40 Requests_Per_User_Per_Day, 15,000 average input tokens per request, 1,500 average output tokens per request and 22 Working_Days_Per_Month, where each of these 5 values carries a Provenance_Record with Source_Tier `assumption`.
2. THE Workload_Profile SHALL define the field `working_days_per_month` as an integer from 1 to 31 inclusive, with default value 22.
3. WHEN the Service_Layer receives a path to a workload JSON file other than the Default_Workload_File and that file validates against the Workload_Profile, THE Service_Layer SHALL evaluate the scenario using only the values from that file plus Workload_Profile field defaults for fields the file omits, with no value taken from the Default_Workload_File and no change to source code under `src/ai_tco_dss/`.
4. THE Workload_Engine SHALL compute monthly requests as active users × Requests_Per_User_Per_Day × Working_Days_Per_Month, which yields 22,000 monthly requests for the Default_Workload_File.
5. THE DSS SHALL document every assumption-labelled default (Working_Days_Per_Month, Requests_Per_User_Per_Day, Utilization definition, resale curve, context-match tolerance, Quality_Floors, Criterion weights per Preset) in a single `Assumptions` table in `specs/07_DATA_CORRECTIONS.md`, with at least one row per listed default, each row stating the value, the rationale and the requirement id that uses the value, and each stated value identical to the value used in `data/` or `src/ai_tco_dss/`.
6. THE Workload_Profile SHALL accept active users as an integer from 1 to 100,000, Requests_Per_User_Per_Day as an integer from 1 to 10,000, average input tokens per request as an integer from 1 to 1,000,000, and average output tokens per request as an integer from 1 to 200,000, all bounds inclusive.
7. IF the workload JSON file path does not exist, the file is not valid JSON, or the file fails Workload_Profile validation (including any field outside the ranges in criteria 2 and 6), THEN THE Service_Layer SHALL raise a validation error that names the file path and each failing field, and SHALL return no scenario result.

### Requirement 15: Effective Token Volume Computation

**User Story:** As a FinOps analyst, I want harness, tokenizer, thinking and verification effects applied to raw token counts, so that cost and latency reflect real agentic workloads.

#### Acceptance Criteria

1. THE Workload_Engine SHALL compute effective scaffolding tokens per request as `S_effective = S_harness × (1 − r_mcp_prune)`, where `S_harness` is the scaffolding token count of the harness selected in the Workload_Profile, `r_mcp_prune = 0.75` if MCP code mode pruning is enabled in the Workload_Profile, and `r_mcp_prune = 0.0` if it is disabled.
2. THE Workload_Engine SHALL compute effective input tokens per request as `T̂_in = (T_in + S_effective) × τ_tokenizer` and effective output tokens per request as `T̂_out = T_out × τ_tokenizer`, with `τ_tokenizer = 1.30` if the selected model's family equals `Claude` and `τ_tokenizer = 1.00` for every other model family.
3. THE Workload_Engine SHALL multiply `T̂_out` by the thinking multiplier `μ_thinking` of the thinking effort preset selected in the Workload_Profile (`none` 1.0, `low` 1.5, `medium` 2.5, `extra-high` 4.94) and SHALL leave `T̂_in` unchanged by `μ_thinking`.
4. THE Workload_Engine SHALL set the verification multiplier to `ν_verify = 2.0` if the verification agent layer is enabled in the Workload_Profile and to `ν_verify = 1.0` if it is disabled.
5. THE Workload_Engine SHALL compute the mega-session compounding factor as `κ_mega = 1.0 + mega_session_ratio × 2.8`, giving `κ_mega` in the range [1.0, 3.8] for `mega_session_ratio` in [0.0, 1.0].
6. THE Workload_Engine SHALL return monthly effective token volume that is greater than or equal to the previous value whenever exactly one of active users, Requests_Per_User_Per_Day, `T_in` or `T_out` is increased by any amount while all other Workload_Profile fields stay the same (monotonicity property).
7. THE Workload_Engine SHALL compute monthly effective token volume as `monthly requests × (T̂_in + T̂_out × μ_thinking) × κ_mega × ν_verify`, using monthly requests as defined in Requirement 14, and SHALL return `S_effective`, `T̂_in`, `T̂_out × μ_thinking`, `κ_mega`, `ν_verify` and the monthly effective token volume. Each returned value SHALL be within a relative tolerance of 1e-9 of the formula value.
8. IF a Workload_Profile has `mega_session_ratio` outside [0.0, 1.0], a negative `T_in`, `T_out` or `S_harness`, or a thinking effort preset other than `none`, `low`, `medium` or `extra-high`, THEN THE Workload_Engine SHALL reject the Workload_Profile with a validation error that names each invalid field and SHALL return no effective token volume.

### Requirement 16: Usable Memory and Operating System Traps

**User Story:** As an infrastructure engineer, I want the usable memory of each device computed with OS reservations, so that the system detects models that do not fit despite advertised memory.

#### Acceptance Criteria

1. THE Sizing_Engine SHALL compute usable memory in GB for Apple Silicon hardware, and for AMD Strix Halo hardware when `linux_amd_override` is disabled, as advertised memory (GB) × (1 − `os_reserved_memory_ratio`), where `os_reserved_memory_ratio` is the value stored on that hardware's Catalog_Item_File, and SHALL report the result to a precision of 0.01 GB.
2. WHERE `apply_mac_wired_memory_override` is enabled, THE Sizing_Engine SHALL use the hardware's `tuned_max_usable_memory_gb` value from its Catalog_Item_File as usable memory for Apple Silicon hardware, in place of the value from criterion 1.
3. WHERE `linux_amd_override` is enabled, THE Sizing_Engine SHALL use the hardware's `linux_max_usable_memory_gb` value from its Catalog_Item_File as usable memory for AMD Strix Halo hardware, in place of the value from criterion 1.
4. THE Sizing_Engine SHALL compute usable memory for discrete GPUs as advertised VRAM (GB) × `gpu_memory_utilization`, using 0.90 when the scenario does not set `gpu_memory_utilization`, and SHALL report the result to a precision of 0.01 GB.
5. WHEN the Sizing_Engine sizes a model on Apple Silicon hardware, THE Sizing_Engine SHALL set `triggered_mac_default_split_trap = true` if the model's total required memory exceeds the usable memory from criterion 1 and is less than or equal to the hardware's `tuned_max_usable_memory_gb`, and SHALL set `triggered_mac_default_split_trap = false` in every other case, regardless of whether `apply_mac_wired_memory_override` is enabled. A model fits when its total required memory computed by the Sizing_Engine is less than or equal to usable memory; equality counts as a fit.
6. THE Sizing_Engine SHALL reproduce the specification's 128 GB Mac trap: for Qwen 3.8 Flash Next at 4-bit (111 GB required) on Mac Studio M5 Max 128GB, the result SHALL be infeasible with `apply_mac_wired_memory_override` disabled (reference usable memory 103 GB, which must be below 111 GB) and feasible with the override enabled (reference usable memory 115 GB, which must be at least 111 GB), with `triggered_mac_default_split_trap = true` in both cases; IF a computed usable memory value differs from its reference value by more than 1.0 GB, THEN the deviation SHALL be recorded in the Corrections_Ledger.
7. WHEN the Sizing_Engine sets `triggered_mac_default_split_trap = true`, THE Sizing_Engine SHALL add one warning to the sizing result that states the hardware_id, the model's required memory and both usable memory values, and contains the command `sudo sysctl iogpu.wired_limit_mb=<value>`, where `<value>` is `tuned_max_usable_memory_gb` × 1024 rounded down to an integer (for example, 117760 for 115 GB).
8. IF `apply_mac_wired_memory_override` is enabled and the Apple Silicon hardware has no `tuned_max_usable_memory_gb` value, or `linux_amd_override` is enabled and the AMD Strix Halo hardware has no `linux_max_usable_memory_gb` value, THEN THE Sizing_Engine SHALL use the usable memory from criterion 1 and SHALL add a warning to the sizing result that names the hardware_id and the missing override field.
9. IF `os_reserved_memory_ratio` is outside the range 0.0 (inclusive) to 1.0 (exclusive), `gpu_memory_utilization` is outside the range 0.0 (exclusive) to 1.0 (inclusive), or a `tuned_max_usable_memory_gb` or `linux_max_usable_memory_gb` value is less than or equal to 0 or greater than the hardware's advertised memory, THEN THE Sizing_Engine SHALL reject the input with a validation error that names the offending field and hardware_id, and SHALL return no sizing result for that hardware.

### Requirement 17: Weights, KV Cache, KV Pool and Concurrency

**User Story:** As an infrastructure engineer, I want weight memory, KV cache and concurrent user capacity computed per hardware–model pairing, so that I know how many users one deployment serves at the target context.

#### Acceptance Criteria

1. WHEN a model's Catalog_Item_File provides a calibrated weight footprint (`calibrated_weights_gb`) for the selected precision, THE Sizing_Engine SHALL use that footprint in GB as weight memory and SHALL set Value_Origin to `measured` with the `source_id` of the footprint's Provenance_Record.
2. IF a model lacks a calibrated weight footprint for the selected precision, THEN THE Sizing_Engine SHALL compute weight memory in GB as `P_total × (bits / 8) × 1.05`, where `P_total` is the model's total parameter count in billions and `bits` is the bit width of the selected precision, and SHALL set Value_Origin to `formula`.
3. WHILE the model attention mechanism is `multi-head-latent`, THE Sizing_Engine SHALL use 890 bytes as KV cache per token, independent of `kv_bits` and `φ_format`.
4. WHILE the model attention mechanism is `standard-mha-gqa` or `hybrid-sparse`, THE Sizing_Engine SHALL compute KV cache per token in bytes as `2 × n_layers × r_kv_active × n_kv_heads × d_head × (kv_bits / 8) × φ_format`, where `r_kv_active` is 1.0 for `standard-mha-gqa` and the model's catalog value (0 < `r_kv_active` ≤ 1) for `hybrid-sparse`, `kv_bits` is the selected KV cache precision (default 16), and `φ_format` is 1.0 for GGUF and vLLM and 1.08 for MLX.
5. THE Sizing_Engine SHALL compute single-user KV cache `M_kv_single` as KV cache per token × target context length in tokens, the KV pool as usable memory (Requirement 16) − weight memory − runtime overhead (default 2.0 GB, Source_Tier `assumption`, non-negative), and `U_max` as the floor of KV pool ÷ `M_kv_single`, where all memory quantities are expressed in GB (1 GB = 10^9 bytes).
6. IF the KV pool is less than or equal to 0 GB or `U_max` is less than 1, THEN THE Sizing_Engine SHALL set `is_feasible = false`, SHALL report `U_max = 0`, and SHALL set `oom_reason` to a text naming the shortfall in GB rounded to 1 decimal place, where the shortfall is (weight memory + runtime overhead − usable memory) when the KV pool is at most 0 GB, and (`M_kv_single` − KV pool) otherwise.
7. THE Sizing_Engine SHALL compute agent state memory in GB as `N_agents × (M_kv_single + M_repo_workspace)`, where `N_agents` is `concurrent_agent_instances` of the Workload_Profile (integer ≥ 1) and `M_repo_workspace` is a per-agent parameter with default 4.0 GB (Source_Tier `assumption`) and accepted range 2.5 to 6.0 GB.
8. THE Sizing_Engine SHALL return a memory breakdown with the keys `weights` (weight memory from criteria 1–2), `kv_cache_active` (`M_kv_single` × the lesser of the Workload_Profile `peak_concurrent_requests` and `U_max`), `agent_state_parked` (agent state memory from criterion 7), `os_reserved` (advertised memory − usable memory) and `runtime_overhead` (the runtime overhead used in criterion 5), each as a non-negative value in GB.
9. FOR ALL hardware–model–precision combinations, increasing advertised memory while keeping all other inputs equal SHALL keep a feasible combination feasible and SHALL leave `U_max` equal or higher (monotonicity property).
10. THE Sizing_Engine SHALL reproduce the specification's DeepSeek V4.1 Flash MLA case: at a target context of 1,000,000 tokens, `M_kv_single` SHALL equal 0.89 GB (890 bytes × 1,000,000 tokens) and SHALL be less than 0.9 GB.
11. IF agent state memory is strictly greater than the hardware's usable system RAM (for unified-memory hardware, the usable memory from Requirement 16), THEN THE Sizing_Engine SHALL set `context_eviction_risk = true`; otherwise THE Sizing_Engine SHALL set `context_eviction_risk = false`.
12. IF the model attention mechanism is `standard-mha-gqa` or `hybrid-sparse` and any of `n_layers`, `n_kv_heads`, `d_head` or (for `hybrid-sparse`) `r_kv_active` is absent or less than or equal to 0, THEN THE Sizing_Engine SHALL return no sizing result for that combination and SHALL raise a validation error naming the `model_id` and each missing or invalid parameter.

### Requirement 18: Multi-Node Topology and Tiered Offload

**User Story:** As an infrastructure engineer, I want multi-node clusters and offload appliances modelled with their physical constraints, so that cluster options are sized realistically.

#### Acceptance Criteria

1. WHEN a sizing request specifies a node count in {1, 2, 4, 8} that is also listed in the hardware's valid node counts, THE Sizing_Engine SHALL compute the sizing result with that node count unchanged and SHALL add no node-count warning.
2. IF a requested node count is an integer from 3 to 7, THEN THE Sizing_Engine SHALL snap the node count up to the next value in {1, 2, 4, 8} (3 → 4; 5, 6, 7 → 8), SHALL use the snapped node count as the effective node count for all subsequent sizing computations, and SHALL add a warning naming the original and the snapped node count.
3. THE Sizing_Engine SHALL compute aggregate usable memory in GB as the effective node count (the requested node count, or the snapped node count under criterion 2) multiplied by the per-node usable memory in GB.
4. THE Sizing_Engine SHALL set `α_scaling` to 1.0 for an effective node count of 1 and, for an effective node count of 2, 4 or 8, to the value of the hardware's interconnect type (NVLink 0.90, PCIe Gen5 0.75, DGX ring cable 0.72, Thunderbolt 5 RDMA 0.65), and SHALL report the applied `α_scaling` value in the sizing result.
5. WHILE the interconnect is Thunderbolt 5 RDMA, THE Sizing_Engine SHALL report `thunderbolt_mesh_cables = N × (N − 1) / 2` for effective node count N (0 cables for N = 1, 1 for N = 2, 6 for N = 4, 28 for N = 8).
6. WHILE the hardware deployment mode is `tiered-offload-appliance`, THE Sizing_Engine SHALL compute weight capacity in GB as usable VRAM plus the hardware's system RAM offload capacity, and SHALL evaluate the weight-memory fit of the model against that sum instead of against usable VRAM alone.
7. IF a requested node count is not an integer, is less than 1, or is greater than 8, THEN THE Sizing_Engine SHALL reject the request with a validation error naming the requested value and the allowed range 1 to 8, and SHALL return no sizing result.
8. IF the effective node count is not listed in the hardware's valid node counts, THEN THE Sizing_Engine SHALL mark the sizing result as infeasible and SHALL record a reason naming the effective node count and the hardware's valid node counts.
9. WHILE the hardware deployment mode is `tiered-offload-appliance`, THE Sizing_Engine SHALL add exactly one warning per sizing result stating that Strata defaults to an 8,192-token context window.

### Requirement 19: Quality, License and Context Flags

**User Story:** As a compliance officer, I want sizing results flagged for EU license validity, context floor and quantization fidelity, so that unsuitable options are visible before any cost analysis.

#### Acceptance Criteria

1. IF the model max context is below 128,000 tokens, or the maximum usable context is below 128,000 tokens, THEN THE Sizing_Engine SHALL set `meets_128k_agentic_context_floor = false` without changing `is_feasible`. The maximum usable context is the smaller of two values: the model max context, and the floor of the KV pool (bytes) ÷ KV cache per token (bytes). It is 0 when the KV pool is less than or equal to 0.
2. IF the model license is `Llama-4-EU-Ban`, THEN THE Sizing_Engine SHALL set `eu_commercial_license_valid = false` without changing `is_feasible`. It SHALL also add one warning to the sizing result that names the model and its license and lists at least one Catalog model whose license is `Apache-2.0` or `MIT`.
3. WHEN the model's token agreement rates contain an entry for the selected precision, THE Sizing_Engine SHALL return that entry's value, unchanged and within [0.0, 1.0], as `token_agreement_rate`.
4. IF `token_agreement_rate` is below 0.90, THEN THE Sizing_Engine SHALL add one agentic schema-break warning to the sizing result without changing `is_feasible`. The warning SHALL state the rate, the selected precision and the 0.90 threshold. A rate of exactly 0.90 SHALL produce no warning.
5. IF the model max context and the maximum usable context are both greater than or equal to 128,000 tokens, THEN THE Sizing_Engine SHALL set `meets_128k_agentic_context_floor = true`.
6. IF the model license is any value other than `Llama-4-EU-Ban`, THEN THE Sizing_Engine SHALL set `eu_commercial_license_valid = true` and SHALL add no license warning.
7. IF the model's token agreement rates contain no entry for the selected precision, THEN THE Sizing_Engine SHALL set `token_agreement_rate` to null and SHALL add no agentic schema-break warning.

### Requirement 20: Decode Throughput

**User Story:** As a developer, I want per-stream decode speed for each deployment, so that I can judge whether generation is fast enough for interactive work.

#### Acceptance Criteria

1. IF no decode Benchmark_Record matches the model, hardware, precision and target context under the matching rules of Requirement 9, THEN THE Performance_Engine SHALL compute the single-stream (one concurrent request) decode TPS as `bandwidth_GBps ÷ M_active_weights_GB × η_engine × γ_spec × δ_ctx × α_scaling`, with `M_active_weights_GB = P_active × (bits / 8) × 1.05`, where `bandwidth_GBps` is the hardware's per-node memory bandwidth in GB/s, `P_active` is the model's active parameter count in billions, `bits` is the weight bit width of the selected precision, and `α_scaling` is the value defined in Requirement 18, and SHALL set Value_Origin to `formula` with the `source_id` values of the hardware and model inputs.
2. THE Performance_Engine SHALL use `η_engine` defaults of 0.70 for models whose catalog architecture is dense and 0.425 for models whose catalog architecture is mixture-of-experts, labelled `assumption`.
3. THE Performance_Engine SHALL apply the `γ_spec` default that matches the deployment's speculative-decoding mode, using 1.0 for `none`, 1.425 for `apple-mtp-dflash`, 1.80 for `built-in-mtp` and 2.75 for `external-draft`, with `none` as the mode when no mode is given, labelled `assumption`.
4. FOR ALL hardware–model combinations computed by formula with memory bandwidth in (0, 20,000] GB/s, increasing memory bandwidth while keeping every other input equal SHALL leave decode TPS equal or higher (monotonicity property).
5. FOR ALL model pairs computed by formula with equal precision, hardware, node count, target context, speculative-decoding mode and `η_engine`, the model with fewer active parameters SHALL have equal or higher decode TPS (MoE dual-parameter law).
6. THE Performance_Engine SHALL use a `δ_ctx` default that equals 1.0 for target contexts up to and including 8,192 tokens, does not increase as the target context grows, and is no lower than 0.47 at 262,144 tokens. The breakpoints SHALL be defined in `settings.py` and labelled `assumption`.
7. IF a formula input is invalid (memory bandwidth ≤ 0 GB/s, `P_active` ≤ 0, `bits` ≤ 0, or a speculative-decoding mode outside `none`, `apple-mtp-dflash`, `built-in-mtp` and `external-draft`), THEN THE Performance_Engine SHALL reject the computation with a validation error naming the invalid field, and SHALL NOT return a decode TPS value for that combination.

### Requirement 21: Prefill, TTFT and Effective Throughput

**User Story:** As a developer, I want time-to-first-token and end-to-end effective speed, so that I see the real wait time of agentic turns with large prompts.

#### Acceptance Criteria

1. THE Performance_Engine SHALL resolve `prefill_TPS` for the hardware, model, precision and target context using the measured-first rules of Requirement 9. IF no prefill Benchmark_Record matches, THEN THE Performance_Engine SHALL use the hardware's catalog `base_prefill_tps_at_32k` value and set Value_Origin to `formula` with that value's `source_id`.
2. THE Performance_Engine SHALL compute TTFT in seconds as `(T_in + S_effective) × τ_tokenizer × (1 − r_cache) ÷ (prefill_TPS × β_backend)`, where `S_effective` and `τ_tokenizer` are the Workload_Engine values from Requirement 15, `r_cache` is the prompt cache hit ratio in [0.0, 1.0], and `β_backend = 1.0` when the optimized backend is enabled and 0.035 when it is disabled. The TTFT Value_Origin SHALL carry the origin and `source_id` of the `prefill_TPS` used.
3. WHILE `context_eviction_risk` is true, THE Performance_Engine SHALL add the cold re-prefill time of the evicted context to TTFT, computed in seconds as `target_context_tokens ÷ (prefill_TPS × β_backend)` with no `r_cache` reduction.
4. THE Performance_Engine SHALL compute effective TPS in tokens per second as `T_out × μ_thinking ÷ (TTFT + T_out × μ_thinking ÷ decode_TPS)`, where `μ_thinking` is the thinking multiplier from Requirement 15, `decode_TPS` is the value from Requirement 20, and TTFT includes any re-prefill time added under criterion 3.
5. THE Performance_Engine SHALL compute the 1,000,000-token prefill time in minutes as `1,000,000 ÷ prefill_TPS_1M ÷ 60`, where `prefill_TPS_1M` is resolved in this order: a matching prefill Benchmark_Record at 1,000,000 tokens context (Value_Origin `measured`); the hardware's catalog `prefill_tps_at_1m` value (Value_Origin `formula`); the `prefill_TPS` from criterion 1 (Value_Origin `formula`, with a warning that long-context prefill is likely overestimated). The result SHALL list the `source_id` of the value used.
6. FOR ALL scenarios with a computed TTFT, TTFT SHALL be greater than or equal to 0 seconds and effective TPS SHALL be greater than or equal to 0 and less than or equal to decode TPS (invariant property).
7. IF neither a matching prefill Benchmark_Record nor a catalog `base_prefill_tps_at_32k` value exists for the hardware, THEN THE Performance_Engine SHALL return TTFT, effective TPS and the 1,000,000-token prefill time as not available instead of a number, and SHALL add a warning naming the hardware and model that lack prefill data.
8. IF `T_out × μ_thinking` equals 0, THEN THE Performance_Engine SHALL return an effective TPS of 0 and SHALL still return the computed TTFT.
9. IF `r_cache` is less than 0.0 or greater than 1.0, THEN THE Performance_Engine SHALL reject the input with an error naming `r_cache` and its permitted range [0.0, 1.0], and SHALL return no performance result for that scenario.

### Requirement 22: On-Premise Cost Components

**User Story:** As a FinOps analyst, I want every on-premise cost component computed explicitly, so that the on-premise TCO includes hidden enterprise costs.

#### Acceptance Criteria

1. THE TCO_Engine SHALL compute CapEx as `(units × street_price) × μ_datacenter + cabling_and_switch_kit`, where units is the Candidate's node count (integer ≥ 1) except as defined in criterion 2, μ_datacenter is a value in [1.0, 2.5], and street_price and cabling_and_switch_kit are monetary values ≥ 0.
2. WHILE the deployment mode is `per-seat-workstation`, THE TCO_Engine SHALL set units equal to the active user count of the Workload_Profile (integer ≥ 1) instead of the node count.
3. THE TCO_Engine SHALL compute monthly energy OpEx as `units × (H_active × W_load + H_idle × W_idle) ÷ 1000 × PUE × electricity_rate`, with `H_idle = 730 − H_active`, H_active in hours per month within [0, 730], W_load and W_idle in watts ≥ 0, PUE within [1.0, 3.0], and electricity_rate per kWh ≥ 0 taken from the selected electricity tier in Reference_Data.
4. THE TCO_Engine SHALL compute monthly personnel OpEx as `FTE × annual_base_salary × (1 + τ_employer) ÷ 12`, with FTE within [0.0, 10.0] and annual_base_salary and τ_employer taken from the selected staffing hub in Reference_Data.
5. WHERE NVIDIA NIM licensing is enabled, THE TCO_Engine SHALL add `per-GPU annual license fee ÷ 12 × GPU count` to monthly OpEx, where GPU count is the total number of GPUs across all units of the Candidate.
6. THE TCO_Engine SHALL compute monthly capital opportunity cost as `CapEx × capital_opportunity_rate ÷ 12`, with capital_opportunity_rate within [0.0, 1.0] and a default of 0.045 labelled `assumption`.
7. WHERE the wait-time penalty is enabled, THE TCO_Engine SHALL add `max(0, H_local_wait − H_cloud_wait) × developer_hourly_opportunity_cost` to monthly OpEx, with H_local_wait and H_cloud_wait in hours per month ≥ 0 and developer_hourly_opportunity_cost ≥ 0.
8. IF `context_eviction_risk` is true, THEN THE TCO_Engine SHALL add to monthly OpEx the monthly eviction loss computed with the formula of `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` §2.4, with every eviction count input labelled `assumption`.
9. THE TCO_Engine SHALL compute resale value at each integer month m in [0, 60] as `CapEx × max(0, 1 − (1 − r_resale_3yr) × m ÷ 36)`, with r_resale_3yr within [0.0, 1.0], so that resale value equals CapEx at m = 0 and equals `CapEx × r_resale_3yr` at m = 36, with the curve labelled `assumption`.
10. THE TCO_Engine SHALL return the Munich-versus-Romania monthly personnel savings as personnel OpEx for hub `de-munich-hq` minus personnel OpEx for hub `ro-cluj-bucharest`, both computed with criterion 4 using the same selected FTE allocation.
11. FOR ALL scenarios that pass input validation, increasing street price, electricity rate or FTE allocation while keeping all other inputs equal SHALL produce a 60-month on-premise TCO greater than or equal to the TCO before the increase (monotonicity property).
12. IF any input to criteria 1–9 lies outside its stated range, or the selected staffing hub or electricity tier does not exist in Reference_Data, THEN THE TCO_Engine SHALL raise a validation error that names the offending field and SHALL return no partial TCO result.
13. IF NVIDIA NIM licensing is disabled, the wait-time penalty is disabled, or `context_eviction_risk` is false, THEN THE TCO_Engine SHALL set the corresponding monthly cost component to exactly 0 and SHALL still report that component in the result.
14. THE TCO_Engine SHALL receive every monetary input already converted to USD by the Catalog_Repository (Requirement 12) and SHALL express every monetary cost component in USD.

### Requirement 23: Utilization and Viability Threshold

**User Story:** As a decision-maker, I want a defined utilization metric with a viability threshold, so that I see when owned hardware sits idle and cloud APIs would be cheaper.

#### Acceptance Criteria

1. THE TCO_Engine SHALL compute Utilization as a dimensionless ratio equal to monthly demanded output tokens ÷ monthly capacity tokens. Monthly demanded output tokens are the Workload_Engine's monthly output token volume after the thinking and verification multipliers. Monthly capacity tokens equal aggregate decode throughput in tokens per second, summed across all nodes of the deployment, × 3,600 × the Workload_Profile's `active_hours_per_month` (integer from 1 to 744, default 176).
2. THE TCO_Engine SHALL report Utilization unrounded and uncapped, so a value above 1.0 is returned as computed and is not clipped to 1.0.
3. WHEN an aggregate-throughput Benchmark_Record matches the deployment's model, hardware and precision, and its `context_tokens` lies within the context-match tolerance of the target context, THE TCO_Engine SHALL use the measured value as aggregate decode throughput. THE TCO_Engine SHALL select among several matching records using the same Source_Tier priority and `accessed`-date rule as the Performance_Engine, and SHALL set the capacity Value_Origin to `measured` with the record's `source_id`.
4. IF no aggregate-throughput Benchmark_Record matches according to criterion 3, THEN THE TCO_Engine SHALL compute aggregate decode throughput with the formula fallback defined in the design document and SHALL set the capacity Value_Origin to `formula` with the `source_id` values of the formula inputs.
5. THE TCO_Engine SHALL set `meets_70_percent_utilization_threshold` to true when Utilization ≥ 0.70 and to false when Utilization < 0.70, so that a Utilization of exactly 0.70 yields true.
6. IF Utilization is below 0.55, THEN THE TCO_Engine SHALL add one idle capacity financial warning to the result. The warning SHALL state the computed Utilization value and that fixed amortization, idle power and MLOps FTE costs are likely to exceed pay-as-you-go API costs. A Utilization of exactly 0.55 SHALL produce no idle capacity financial warning.
7. IF Utilization is above 1.0, THEN THE TCO_Engine SHALL mark the deployment as capacity-insufficient for the Workload_Profile and SHALL add a warning stating the computed Utilization value and the monthly token shortfall (monthly demanded output tokens − monthly capacity tokens). A Utilization of exactly 1.0 SHALL NOT be marked capacity-insufficient.
8. IF monthly capacity tokens are 0 or cannot be computed because the deployment's Sizing_Engine result has `is_feasible = false`, THEN THE TCO_Engine SHALL report Utilization as undefined instead of dividing by zero, SHALL set `meets_70_percent_utilization_threshold` to false, SHALL mark the deployment as capacity-insufficient, and SHALL add a warning stating that capacity could not be determined.

### Requirement 24: Cloud Baselines A–D

**User Story:** As a FinOps analyst, I want the four cloud comparison baselines computed from the same workload, so that on-premise options are compared fairly with subscriptions, global APIs, EU-pinned APIs and open-weights market value.

#### Acceptance Criteria

1. WHEN a Workload_Profile is evaluated, THE Baseline_Engine SHALL compute Baseline A monthly cost in USD as the active user count of the Workload_Profile × the subscription price per seat per month of the selected subscription plan from Reference_Data, with the result matching this formula to within 0.01 USD.
2. IF `strict_eu_sovereignty` is true, THEN THE Baseline_Engine SHALL set `baseline_a_eligible = false`, add the reason "no EU data residency or enterprise DPA" to the Baseline A rejection reasons, and still return the computed Baseline A monthly cost.
3. IF `require_third_party_harness` is true, THEN THE Baseline_Engine SHALL set `baseline_a_eligible = false`, add the reason "third-party harnesses blocked on consumer plans" to the Baseline A rejection reasons, and still return the computed Baseline A monthly cost. If both `strict_eu_sovereignty` and `require_third_party_harness` are true, the rejection reasons SHALL contain both reasons. If both are false, `baseline_a_eligible` SHALL be true and the rejection reasons SHALL be empty.
4. WHEN a Workload_Profile is evaluated, THE Baseline_Engine SHALL compute Baseline B monthly cost in USD with the formula of `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` §1 Baseline B. The formula SHALL use the monthly requests of Requirement 14 (active users × Requests_Per_User_Per_Day × Working_Days_Per_Month) and token prices per 10^6 tokens, and SHALL include cache-read pricing on the cache-hit share `r_cache`, the thinking multiplier on output tokens, the mega-session factor, the verification multiplier and the 50 % batch discount on the batch-eligible share `r_batch`. The result SHALL match a hand-computed reference value to within 0.01 USD.
5. WHEN a Workload_Profile is evaluated, THE Baseline_Engine SHALL compute Baseline C monthly cost in USD as Baseline B monthly cost × 1.10 + the enterprise gateway fee per month, where the gateway fee is a non-negative USD amount from Reference_Data or the Workload_Profile.
6. WHEN a Candidate with an effective TPS from the Performance_Engine is evaluated, THE Baseline_Engine SHALL compute Baseline D monthly value in USD as monthly produced tokens ÷ 10^6 × the open-weights output price per 10^6 tokens, where monthly produced tokens = active hours per month × 3,600 × effective TPS × min(Utilization, 1.0). IF the Candidate has no effective TPS because the Sizing_Engine marked it infeasible, THEN THE Baseline_Engine SHALL mark Baseline D as unavailable with a reason that names the infeasibility and SHALL NOT return a numeric Baseline D value.
7. WHEN Baselines A and C have been computed, THE Baseline_Engine SHALL compute the compliance tax delta in USD as Baseline C monthly cost − Baseline A monthly cost, regardless of the value of `baseline_a_eligible`. The delta MAY be negative.
8. FOR ALL valid Workload_Profiles with a non-negative gateway fee, Baseline C monthly cost SHALL be greater than or equal to Baseline B monthly cost (invariant property).
9. FOR ALL valid Workload_Profiles, increasing the active user count by 1 or more while keeping all other inputs equal SHALL leave Baseline A, B and C monthly costs equal or higher (monotonicity property).
10. IF any Baseline input is outside its valid range (any token price < 0, gateway fee < 0, `r_cache` or `r_batch` outside [0, 1], thinking multiplier, mega-session factor or verification multiplier < 1, or active hours per month outside [1, 744]), THEN THE Baseline_Engine SHALL reject the input with a validation error that names each offending field, and SHALL return no baseline results for that evaluation.
11. WHEN the Baseline_Engine returns Baseline A, B, C or D results, THE Baseline_Engine SHALL label each monthly value with currency USD and a Value_Origin of `formula` that lists the `source_id` values of the prices and Reference_Data used.

### Requirement 25: EU Dedicated Rental and Hybrid Split

**User Story:** As a decision-maker, I want EU dedicated GPU rental and a hybrid local-plus-API split as options, so that I can compare sovereign alternatives that avoid full CapEx.

#### Acceptance Criteria

1. THE Baseline_Engine SHALL compute the EU_Rental cumulative cost at month m, for every integer m in [1, 60], as one-time setup fee + m × monthly rental price + m × monthly personnel OpEx. The one-time setup fee SHALL be taken from `rentals.json` and counted once, at month 1. The setup fee SHALL be 0 when `rentals.json` records a setup fee of 0. Monthly personnel OpEx SHALL be computed with the formula of Requirement 22 criterion 4, using the selected FTE allocation and staffing hub.
2. THE Baseline_Engine SHALL compute the Hybrid_Split monthly cost as local component + API component. The local component SHALL be the full monthly on-premise OpEx of the selected local deployment, as computed by the TCO_Engine under Requirement 22. The API component SHALL be (1 − `local_offload_ratio`) × Baseline C monthly cost for the same Workload_Profile.
3. WHEN `local_offload_ratio` is 1.0, THE Baseline_Engine SHALL return an API component of 0. For every month m in [1, 60], it SHALL also return a Hybrid_Split cumulative cost equal, within ±0.01 USD, to the cumulative on-premise cost of the same local deployment as defined in Requirement 26 criterion 2.
4. WHEN `local_offload_ratio` is 0.0, THE Baseline_Engine SHALL return an API component equal to the Baseline C monthly cost, within ±0.01 USD. The local component and the CapEx SHALL still be included as defined in criteria 2 and 5.
5. THE Baseline_Engine SHALL compute the Hybrid_Split cumulative cost at month m, for every integer m in [1, 60], as the CapEx of the local deployment + m × Hybrid_Split monthly cost. The CapEx SHALL be counted once, at month 1.
6. IF `local_offload_ratio` is non-numeric, less than 0.0 or greater than 1.0, THEN THE Baseline_Engine SHALL reject the input with a validation error that names `local_offload_ratio` and the allowed range [0.0, 1.0]. In that case it SHALL return no Hybrid_Split result.
7. THE Baseline_Engine SHALL express EU_Rental and Hybrid_Split costs in USD, the same currency as the Baseline A–D costs, using rental prices and setup fees already converted from EUR by the Catalog_Repository (Requirement 12).

### Requirement 26: 60-Month Timeline and Break-Even

**User Story:** As a decision-maker, I want a 60-month cumulative timeline with break-even months against each baseline, so that I see when an investment pays off.

#### Acceptance Criteria

1. WHEN the Service_Layer evaluates a scenario, THE Baseline_Engine SHALL return exactly 60 timeline points, ordered by ascending integer month m from 1 to 60. Each point SHALL contain the cumulative on-premise, EU_Rental, Baseline A, Baseline B, Baseline C, Baseline D and Hybrid_Split costs in USD. The cumulative cost of Baselines A, B, C and D at month m SHALL equal m × the respective monthly cost.
2. THE TCO_Engine SHALL compute the cumulative on-premise cost at month m as CapEx + the sum of monthly OpEx for months 1 to m, so that the month-1 point contains CapEx + monthly OpEx of month 1.
3. WHERE `include_resale_value` is enabled, THE TCO_Engine SHALL subtract the resale value at month m (Requirement 22, criterion 9) from the cumulative on-premise cost at month m, and THE Baseline_Engine SHALL use this resale-adjusted series for the timeline and for every Break_Even_Month.
4. THE DSS SHALL set `include_resale_value` to disabled by default, labelled `assumption` and listed in the `Assumptions` table of the Corrections_Ledger.
5. WHEN the timeline is computed, THE Baseline_Engine SHALL report one Break_Even_Month against each of EU_Rental, Baseline A, Baseline B, Baseline C, Baseline D and Hybrid_Split. Each Break_Even_Month SHALL be the smallest integer m in [1, 60] for which the unrounded cumulative on-premise cost in USD is less than or equal to the unrounded cumulative cost of that series in USD. The Break_Even_Month SHALL be reported regardless of the value of `baseline_a_eligible`.
6. IF no month in [1, 60] satisfies the break-even condition for a compared series, THEN THE Baseline_Engine SHALL report the Break_Even_Month for that series as `null` and SHALL still return all 60 timeline points.
7. WHILE `include_resale_value` is disabled, THE Baseline_Engine SHALL return every cumulative series such that the value at month m + 1 is greater than or equal to the value at month m, for every m from 1 to 59 (invariant property).
8. WHEN the single-stream decode TPS is greater than 0 and the open-weights output price, in USD per 10^6 output tokens, is greater than 0, THE Baseline_Engine SHALL compute the single-stream break-even years as CapEx ÷ (decode TPS × 3,600 × 8,760 × output price ÷ 10^6). It SHALL label the result `formula`, together with the assumption of 8,760 operating hours per year at 100% single-stream load.
9. IF the single-stream decode TPS or the open-weights output price is missing or equal to 0, THEN THE Baseline_Engine SHALL report the single-stream break-even years as `null` and SHALL leave the 60-month timeline and Break_Even_Months unaffected.
10. FOR ALL scenarios, changing the Display_Currency between USD and EUR SHALL leave every Break_Even_Month and the single-stream break-even years unchanged (invariant property).

### Requirement 27: Candidate Generation

**User Story:** As a decision-maker, I want all realistic deployment options generated automatically, so that the ranking covers on-premise, cloud API, EU rental and hybrid alternatives.

#### Acceptance Criteria

1. THE Decision_Engine SHALL generate exactly one on-premise Candidate for every combination of (a) hardware item in the Catalog, (b) node count that is in {1, 2, 4, 8} and also listed in that hardware item's valid node counts, (c) open-weights model in the Catalog, and (d) precision for which the model provides a calibrated weight footprint or which the hardware supports natively, counting a precision that meets both conditions only once, and SHALL include combinations whose Sizing_Engine result is `is_feasible = false` so that the Hard_Filters of Requirement 28 can record their rejection.
2. WHEN `strict_eu_sovereignty` is false, THE Decision_Engine SHALL generate exactly one Candidate per commercial API model in the Catalog, with cost computed from the model's global input, output and cache-read prices using the Baseline B formula of Requirement 24.
3. THE Decision_Engine SHALL generate exactly one Candidate for every combination of EU_Rental in the Catalog and open-weights model in the Catalog (16 Candidates for the 2 EU_Rentals and 8 open-weights models of the MVP_Catalog), including combinations in which the model does not fit the rental's memory.
4. WHEN at least one on-premise Candidate has `is_feasible = true`, THE Decision_Engine SHALL select the feasible on-premise Candidate with the lowest 60-month cumulative TCO, breaking ties by ascending hardware identifier, node count, model identifier and precision, and SHALL generate exactly one Hybrid_Split Candidate per commercial API model in the Catalog that combines the selected local deployment with that API model at the scenario's `local_offload_ratio`, costed as defined in Requirement 25 criterion 2.
5. FOR ALL Catalogs and scenarios, generating Candidates twice from the same Catalog and scenario SHALL produce lists with identical Candidates, identical cost values and identical order, where the order is by Candidate type (on-premise, commercial API, EU_Rental, Hybrid_Split) and then by ascending identifiers within each type (determinism property).
6. WHEN `strict_eu_sovereignty` is true, THE Decision_Engine SHALL generate exactly one Candidate per commercial API model in the Catalog that has an EU-pinned endpoint, with cost computed by the Baseline C formula of Requirement 24 (Baseline B × 1.10 + enterprise gateway fee).
7. IF `strict_eu_sovereignty` is true and a commercial API model has no EU-pinned endpoint, THEN THE Decision_Engine SHALL still generate exactly one Candidate for that model, priced at its global rates, so that Requirement 28 criterion 3 rejects it with the reason "no EU-pinned endpoint".
8. IF no on-premise Candidate has `is_feasible = true`, THEN THE Decision_Engine SHALL generate zero Hybrid_Split Candidates, SHALL add a warning stating that no Hybrid_Split could be formed because no feasible on-premise deployment exists, and SHALL still return all on-premise, commercial API and EU_Rental Candidates.

### Requirement 28: Hard Filters and Rejection Reasons

**User Story:** As a compliance officer, I want infeasible and non-compliant options removed with stated reasons, so that I can explain to management why an option is excluded.

#### Acceptance Criteria

1. THE Decision_Engine SHALL apply the following nine Hard_Filters, where a Candidate passes a Hard_Filter only if the stated condition holds: memory fit (`is_feasible = true`), EU license validity (`eu_commercial_license_valid = true`), EU sovereignty (criterion 3), minimum acceptable TPS (effective TPS ≥ scenario minimum TPS), maximum acceptable TTFT (TTFT ≤ scenario maximum TTFT), users served (Utilization ≤ 1.0), 128K context floor (`meets_128k_agentic_context_floor = true`, or model max context ≥ 128,000 tokens for commercial API Candidates), Use_Case Quality_Floor (the quality score resolved by Requirement 31 criterion 5 ≥ Quality_Floor) and CapEx budget (CapEx ≤ scenario CapEx budget).
2. WHEN the Decision_Engine evaluates a Candidate, THE Decision_Engine SHALL evaluate all applicable Hard_Filters without stopping at the first failure, SHALL exclude a Candidate that fails one or more Hard_Filters from ranking, and SHALL record for every failed Hard_Filter the Hard_Filter name, the measured value and the threshold.
3. WHILE `strict_eu_sovereignty` is true, IF a commercial API Candidate, or the API component of a Hybrid_Split Candidate, has no EU-pinned endpoint in the Catalog, THEN THE Decision_Engine SHALL fail the EU sovereignty Hard_Filter for that Candidate with the reason "no EU-pinned endpoint".
4. IF every Candidate fails at least one Hard_Filter, THEN THE Decision_Engine SHALL return an empty ranking and the list of all rejected Candidates sorted by number of failed Hard_Filters ascending, with ties ordered by Candidate identifier in ascending lexicographic order.
5. WHEN the Service_Layer returns the result of `evaluate_scenario` or `recommend`, THE Service_Layer SHALL include the ranking, every rejected Candidate and, for each rejected Candidate, the complete list of failed Hard_Filters recorded under criterion 2.
6. IF the scenario leaves the minimum acceptable TPS, the maximum acceptable TTFT or the CapEx budget unset, THEN THE Decision_Engine SHALL skip the corresponding Hard_Filter for all Candidates and SHALL NOT record it as a failure.
7. IF a Hard_Filter does not apply to a Candidate type (memory fit, EU license validity, users served and CapEx budget for commercial API Candidates; CapEx budget for EU_Rental Candidates), THEN THE Decision_Engine SHALL treat that Hard_Filter as passed, and SHALL fail a Hybrid_Split Candidate on a Hard_Filter if its on-premise component or its API component fails that Hard_Filter.
8. IF no quality score can be resolved for a Candidate's model under Requirement 31 criterion 5, THEN THE Decision_Engine SHALL fail the Use_Case Quality_Floor Hard_Filter for that Candidate and SHALL record the measured value as not available.

### Requirement 29: Criteria, Normalisation and SAW Ranking

**User Story:** As a decision-maker, I want feasible options ranked by weighted criteria with an explanation, so that the recommendation is transparent and reproducible.

#### Acceptance Criteria

1. WHEN the Decision_Engine ranks a scenario, THE Decision_Engine SHALL compute six Criteria for each Candidate that passed every Hard_Filter of Requirement 28: 60-month TCO in USD, quality as a benchmark score, effective TPS in tokens per second, TTFT in seconds, risk in [0, 1], and popularity taken from the Popularity_Snapshot.
2. WHEN a Candidate's model has a score on the matching benchmark that `use_cases.json` defines for the selected Use_Case, THE Decision_Engine SHALL use that score as the quality Criterion. If the model has no score on the matching benchmark, the Decision_Engine SHALL use the second-choice benchmark score defined in `use_cases.json`.
3. IF a Candidate's model has neither a matching-benchmark score nor a second-choice benchmark score, THEN THE Decision_Engine SHALL compute the quality Criterion from the Artificial Analysis Intelligence Index v5 value, scaled by the ratio that the design document defines for Requirement 31. The Decision_Engine SHALL also record, in that Candidate's result, a fallback note that names the benchmark actually used.
4. THE Decision_Engine SHALL compute the risk Criterion with the formula and defaults defined in the design document from software support years and token agreement rate. The result SHALL lie in [0, 1], and SHALL be non-increasing when software support years increase or when token agreement rate increases.
5. THE Decision_Engine SHALL normalise each Criterion across all Candidates that passed the Hard_Filters. A maximised Criterion SHALL be normalised as (x − min) ÷ (max − min). A minimised Criterion (60-month TCO, TTFT, risk) SHALL be normalised as (max − x) ÷ (max − min). IF max equals min for a Criterion, including the case of exactly one such Candidate, THEN THE Decision_Engine SHALL assign the normalised value 1.0 to every Candidate for that Criterion.
6. WHEN the Decision_Engine receives a Criterion weight vector from a Preset or from Expert_Mode, THE Decision_Engine SHALL normalise each weight as w_i ÷ Σw_j. It SHALL then rank Candidates with SAW in descending order of the SAW score, which is the sum over all six Criteria of normalised weight × normalised value and lies in [0, 1].
7. WHEN the SAW scores of two Candidates differ by at most 1e-9 in absolute value, THE Decision_Engine SHALL rank the Candidate with the lower raw 60-month TCO first. If the 60-month TCO values are also equal, it SHALL rank the Candidates by Candidate id in ascending lexicographic order.
8. THE Decision_Engine SHALL return the following for each ranked Candidate and each of the six Criteria: the raw value, the normalised value, the normalised weight, and the weighted contribution (normalised weight × normalised value). The weighted contributions of a Candidate SHALL sum to its SAW score within an absolute tolerance of 1e-9.
9. WHEN the ranking contains at least one Candidate, THE Decision_Engine SHALL return a text explanation for the top-ranked Candidate. The explanation SHALL name the two Criteria with the largest weighted contributions together with their contribution values, and SHALL include any fallback note recorded for that Candidate. Equal contributions SHALL be ordered by the Criterion order 60-month TCO, quality, effective TPS, TTFT, risk, popularity.
10. FOR ALL Candidate sets and weight vectors with every weight strictly positive, a Candidate that is dominated by another Candidate SHALL rank below the dominating Candidate (dominance property). Dominated means equal or worse on every Criterion and strictly worse on at least one, where worse means higher for a minimised Criterion and lower for a maximised Criterion.
11. IF any weight in the received weight vector is negative or not a finite number, or all weights sum to 0, THEN THE Decision_Engine SHALL return no ranking and SHALL return an error indicating which weights are invalid. The Candidate set and the Hard_Filter results SHALL remain unchanged.
12. IF the raw value of a Criterion other than popularity is unavailable for a Candidate (for example, TTFT not available under Requirement 21 criterion 7), THEN THE Decision_Engine SHALL take min and max for that Criterion over the Candidates that have a value. It SHALL assign the unavailable Candidate the normalised value 0.0 for that Criterion and SHALL mark the raw value as missing in that Candidate's per-Criterion result.
13. FOR ALL Candidate sets and weight vectors, ranking the same Candidate set with the same weights twice SHALL produce identical rankings, identical SAW scores and identical explanations (determinism property).

### Requirement 30: TOPSIS Expert Ranking

**User Story:** As an expert user, I want to compare SAW with TOPSIS, so that the thesis can discuss the sensitivity of the recommendation to the ranking method.

#### Acceptance Criteria

1. WHERE Expert_Mode is active, THE Dashboard SHALL offer a ranking-method toggle with exactly two options, SAW and TOPSIS, with SAW preselected each time Expert_Mode is opened.
2. WHEN TOPSIS is selected, THE Decision_Engine SHALL rank the same feasible Candidates that SAW ranks (the Candidates remaining after all Hard_Filters) by descending relative closeness C = D⁻ ÷ (D⁺ + D⁻), where each raw Criterion value is vector-normalised (divided by the Euclidean norm of that Criterion's raw values across the feasible Candidates) and multiplied by the SAW weight of that Criterion normalised to sum 1; D⁺ and D⁻ are the Euclidean distances of a Candidate's weighted normalised values to the ideal and anti-ideal solution; and the ideal solution takes, per Criterion, the maximum weighted normalised value for maximised Criteria and the minimum for minimised Criteria, with the anti-ideal solution taking the opposite extreme.
3. WHEN TOPSIS is selected, THE Decision_Engine SHALL return for each ranked Candidate the closeness C in [0, 1], D⁺, D⁻, the TOPSIS rank and the SAW rank computed from the same Candidates and weights.
4. WHEN TOPSIS is selected, THE Dashboard SHALL display one table row per ranked Candidate, ordered by TOPSIS rank, that shows the SAW rank (integer, 1 = best), the TOPSIS rank (integer, 1 = best) and the TOPSIS closeness rounded to 3 decimal places in adjacent columns.
5. FOR ALL sets of 2 or more feasible Candidates and weight vectors in which every weight is greater than 0, a Candidate that is dominated by another Candidate (equal or worse on every Criterion and worse on at least one, as defined in Requirement 29) SHALL receive a TOPSIS closeness less than or equal to, and a TOPSIS rank number greater than, the dominating Candidate, with equal closeness values ordered by the tie-break rule of criterion 8 (dominance property).
6. IF the Euclidean norm of a Criterion's raw values across the feasible Candidates is 0, THEN THE Decision_Engine SHALL assign the vector-normalised value 0 to every Candidate for that Criterion and SHALL continue the TOPSIS ranking without error.
7. IF D⁺ + D⁻ equals 0 for a Candidate (including the case of exactly one feasible Candidate), THEN THE Decision_Engine SHALL assign that Candidate a closeness of 1.0.
8. WHEN two Candidates have equal TOPSIS closeness values, THE Decision_Engine SHALL order the Candidates by lower 60-month TCO and then by Candidate id, using the same tie-break rule as SAW.

### Requirement 31: Use Cases and Quality Floors

**User Story:** As a business user, I want to choose a use case and get only models good enough for that use case, so that recommendations match the task.

#### Acceptance Criteria

1. THE DSS SHALL offer exactly the four Use_Cases `writing-email`, `summarisation-rag`, `coding-assistant` and `agentic-coding` as Use_Case selection options in Normal_Mode and Expert_Mode of the Dashboard, and THE Service_Layer function `recommend` SHALL accept each of these four Use_Case identifiers.
2. THE Reference_Data file `use_cases.json` SHALL map `writing-email` and `summarisation-rag` to the Artificial Analysis Intelligence Index v5 as matching benchmark with no second-choice benchmark, and SHALL map `coding-assistant` and `agentic-coding` to Terminal-Bench as matching benchmark with SWE-bench as second-choice benchmark.
3. THE Reference_Data file `use_cases.json` SHALL define for every Use_Case exactly one Quality_Floor as a number in the range 0 to 100 on the scale of the Use_Case's matching benchmark, and SHALL attach to every initial Quality_Floor a Provenance_Record with Source_Tier `assumption`.
4. IF a model has neither a value for the Use_Case's matching benchmark nor a value for the second-choice benchmark, THEN THE Decision_Engine SHALL evaluate the Quality_Floor against the model's Artificial Analysis Intelligence Index v5 value multiplied by the scaling ratio defined in the design document, and SHALL record in the Candidate's explanation the fallback benchmark name, the unscaled value, the scaling ratio and the scaled value.
5. WHEN the Decision_Engine applies the Quality_Floor Hard_Filter to a Candidate, THE Decision_Engine SHALL use the first available score in the order matching benchmark, second-choice benchmark, scaled Artificial Analysis Intelligence Index v5, and SHALL pass the Candidate only if that score is greater than or equal to the Quality_Floor.
6. IF a model has no value for the matching benchmark, the second-choice benchmark or the Artificial Analysis Intelligence Index v5, THEN THE Decision_Engine SHALL fail the Candidate on the Quality_Floor Hard_Filter and SHALL record a rejection reason indicating that no quality score is available.
7. IF the Service_Layer receives a Use_Case identifier that is not one of the four Use_Cases in criterion 1, THEN THE Service_Layer SHALL reject the request with a validation error that names the invalid identifier and lists the four allowed Use_Cases, and SHALL produce no ranking.

### Requirement 32: Presets and Popularity Snapshot

**User Story:** As a business user, I want one-click presets, so that I can get a recommendation without setting weights.

#### Acceptance Criteria

1. THE DSS SHALL define the Presets `cheapest`, `best-fit`, `most-capable` and `popular` in Reference_Data, each as a Criterion weight vector that contains exactly one weight for each of the six Criteria (60-month TCO, quality, effective TPS, TTFT, risk, popularity), with every weight in [0, 1], the weights summing to 1.0 within an absolute tolerance of 1e-6, and the Preset labelled with Source_Tier `assumption`.
2. THE `cheapest` Preset SHALL assign the 60-month TCO Criterion a weight strictly greater than the weight of every other Criterion in the `cheapest` Preset.
3. THE `most-capable` Preset SHALL assign the quality Criterion a weight strictly greater than the weight of every other Criterion in the `most-capable` Preset.
4. THE `popular` Preset SHALL assign the popularity Criterion a weight strictly greater than the weight of every other Criterion in the `popular` Preset.
5. THE `best-fit` Preset SHALL assign a weight greater than 0 to each of the six Criteria.
6. THE Reference_Data SHALL contain a Popularity_Snapshot of OpenRouter usage rankings that records the snapshot date in ISO 8601 format, a Provenance_Record whose `source_id` exists in the Source_Registry, and, for each listed model, one `model_id` and one non-negative raw popularity value.
7. IF a Candidate's model is absent from the Popularity_Snapshot, THEN THE Decision_Engine SHALL assign the model a raw popularity value of 0 and SHALL record in the Candidate's explanation that the model is absent from the Popularity_Snapshot.
8. IF a Preset weight vector violates criterion 1, or a Popularity_Snapshot entry has a negative raw popularity value or a `model_id` that appears more than once, THEN THE Validate_CLI SHALL report an error naming the file and the offending Preset or entry, and SHALL exit with a non-zero exit status.
9. WHEN the user selects a Preset in Normal_Mode, THE Decision_Engine SHALL rank Candidates using the selected Preset's weight vector exactly as stored in Reference_Data.
10. WHEN the Dashboard loads Normal_Mode for the first time in a session, THE Dashboard SHALL preselect the `best-fit` Preset.

### Requirement 33: Normal Mode and Expert Mode

**User Story:** As a business user I want a simple mode, and as an expert I want full control, so that both audiences can use the same tool.

#### Acceptance Criteria

1. WHILE Normal_Mode is active, THE Dashboard SHALL show exactly three scenario inputs: Use_Case (one of `writing-email`, `summarisation-rag`, `coding-assistant`, `agentic-coding`), active user count (integer from 1 to 100,000) and Preset (one of `cheapest`, `best-fit`, `most-capable`, `popular`). THE Dashboard SHALL hide every other scenario input.
2. WHILE Normal_Mode is active, THE Dashboard SHALL evaluate the scenario with the values in the Default_Workload_File and Reference_Data for every parameter other than Use_Case, active user count and Preset. THE Dashboard SHALL use the Criterion weight vector of the selected Preset and the SAW ranking method, and SHALL ignore any value previously entered in Expert_Mode.
3. WHILE Expert_Mode is active, THE Dashboard SHALL show inputs for Use_Case, active user count and Preset, plus inputs for target TPS, target TTFT, concurrency, target context, quantization precision, harness, MCP pruning, thinking effort, staffing hub, FTE allocation, electricity tariff, PUE, FX_Rate, `local_offload_ratio`, `include_resale_value`, Criterion weights and ranking method (SAW or TOPSIS).
4. WHEN the user switches from Expert_Mode to Normal_Mode, THE Dashboard SHALL keep the Use_Case, active user count and Preset values unchanged and SHALL evaluate the next scenario as defined in criterion 2.
5. WHEN the user switches from Normal_Mode to Expert_Mode, THE Dashboard SHALL keep the Use_Case, active user count and Preset values unchanged, SHALL set the Criterion weight inputs to the weight vector of the selected Preset, and SHALL set the ranking method input to SAW.
6. WHEN a user opens the Dashboard in a new browser session, THE Dashboard SHALL activate Normal_Mode with the active user count taken from the Default_Workload_File (25 active users), the Use_Case `agentic-coding` and the Preset `best-fit` selected.
7. IF the user enters an active user count that is not an integer or is outside 1 to 100,000, THEN THE Dashboard SHALL reject the value, SHALL show an error message naming the allowed range next to the input, SHALL keep the last valid active user count, and SHALL not re-evaluate the scenario.

### Requirement 34: Dashboard Layout and KPI Ribbon

**User Story:** As an executive, I want the verdict visible within five seconds, so that I grasp the recommendation without reading engineering detail.

#### Acceptance Criteria

1. THE Dashboard SHALL arrange content in three vertically stacked tiers in this order from top to bottom: the KPI ribbon, a tabbed visual workspace containing one tab per implemented View (Views 1 and 2 in the MVP, plus a ranking tab), and an expandable audit drawer that is collapsed on first load.
2. THE Dashboard KPI ribbon SHALL show exactly five cards, ordered left to right, all describing the rank-1 Candidate of the current ranking: (a) recommended architecture, showing the Candidate type and its hardware, node count, model and precision, or its API model, EU_Rental or Hybrid_Split identity as applicable; (b) break-even horizon, showing the Break_Even_Month against Baseline C, or the text "no break-even within 60 months" when the Break_Even_Month is `null`; (c) monthly savings, showing the compliance tax delta (Baseline C monthly cost − Baseline A monthly cost) and the Munich-versus-Romania monthly personnel savings in the active Display_Currency; (d) performance, showing effective TPS in tokens per second and TTFT in seconds; (e) Utilization as a percentage with one decimal place, plus a viability badge.
3. THE Dashboard viability badge SHALL show `viable` when `meets_70_percent_utilization_threshold` is true and Utilization is at most 1.0, `capacity-insufficient` when Utilization is above 1.0, `idle capacity warning` when Utilization is below 0.55, and `below threshold` when Utilization is at least 0.55 and below 0.70.
4. WHEN the user changes any scenario input in Normal_Mode or Expert_Mode, THE Dashboard SHALL recompute all five KPI ribbon cards by calling the Service_Layer with the changed scenario, and SHALL show the updated values within 5 seconds of the input change.
5. IF the ranking returned by the Service_Layer is empty, THEN THE Dashboard KPI ribbon SHALL show "No feasible option" in the recommended architecture card, SHALL show "not available" in the other four cards instead of numeric values, and SHALL provide a control that opens the list of rejected Candidates with their rejection reasons.
6. IF the Service_Layer returns no value for a card metric of the rank-1 Candidate, THEN THE Dashboard SHALL show "not applicable" in place of that metric and SHALL keep showing the other card values.
7. IF the Service_Layer call for a recomputation fails, THEN THE Dashboard SHALL show an error message indicating that the KPIs could not be computed, SHALL clear the previous KPI values instead of showing them as current, and SHALL keep the user's scenario inputs unchanged.

### Requirement 35: Views 1 and 2

**User Story:** As a decision-maker, I want a memory-fit chart and a 60-month TCO chart, so that I see both the physical feasibility and the financial break-even.

#### Acceptance Criteria

1. WHEN the Dashboard receives one or more Sizing_Engine results, THE Dashboard SHALL render View 1 as a horizontal stacked bar chart with one bar per hardware–model pairing, an x-axis in GB, and five segments in the fixed order `weights`, `kv_cache_active`, `agent_state_parked`, `os_reserved`, `runtime_overhead`, each segment length equal to the matching memory breakdown value within 0.01 GB, plus one vertical threshold line at the hardware's usable VRAM and one at its usable system RAM, and SHALL omit the system RAM line for hardware that reports no separate system RAM value.
2. THE Dashboard View 1 SHALL label each bar with the model's Artificial Analysis Intelligence Index v5 score, shown with one decimal place, and with the `token_agreement_rate` for the selected precision, shown as a percentage with one decimal place.
3. IF `context_eviction_risk` is true for a pairing, THEN THE Dashboard View 1 SHALL fill that pairing's bar with a hatch pattern and SHALL place the text badge "EVICTION RISK" next to the bar. Bars of pairings with `context_eviction_risk` false SHALL have neither the hatch pattern nor the badge.
4. WHEN the Dashboard receives a Baseline_Engine result, THE Dashboard SHALL render View 2 as a cumulative cost line chart with an x-axis covering months 1 to 60 and a y-axis in the active Display_Currency, containing one line per computed series out of on-premise, EU_Rental, Baseline A, Baseline B, Baseline C, Baseline D and Hybrid_Split, and SHALL omit from the chart and legend any series the Baseline_Engine did not return.
5. WHEN a Break_Even_Month exists between the on-premise series and a compared series, THE Dashboard View 2 SHALL place a marker at that month on the on-premise line and SHALL label it `t* = <month>`, where `<month>` is the integer Break_Even_Month in [1, 60].
6. IF the on-premise Utilization is strictly below 0.70, THEN THE Dashboard View 2 SHALL shade the entire plot background across months 1 to 60 and SHALL show the label "Utilization Danger Zone (<70%)". IF the on-premise Utilization is 0.70 or higher, THEN THE Dashboard View 2 SHALL show neither the shading nor the label.
7. IF `baseline_a_eligible` is false, THEN THE Dashboard View 2 SHALL draw Baseline A as a dashed line annotated "[NON-COMPLIANT / BLOCKED]", SHALL show no Break_Even_Month marker for Baseline A, and SHALL draw Baseline A as a solid line without the annotation when `baseline_a_eligible` is true.
8. THE DSS SHALL implement chart construction as pure Plotly figure factory functions in `src/ai_tco_dss/ui/charts.py` that take Domain_Contracts as their only inputs, return Plotly figures, perform no file, network or Streamlit calls, and return equal figures for equal inputs.
9. IF the Intelligence Index v5 score or the `token_agreement_rate` of a pairing is missing, THEN THE Dashboard View 1 SHALL show "n/a" for the missing value and SHALL still render that pairing's bar.
10. IF no Break_Even_Month exists in months 1 to 60 for a compared series, THEN THE Dashboard View 2 SHALL show no `t*` marker for that series and SHALL add a legend note stating that the series has no break-even within 60 months.
11. IF a chart factory function receives an empty set of pairings or series, THEN THE DSS SHALL return a Plotly figure with no data traces and a text annotation stating that no data is available, and SHALL NOT raise an exception.

### Requirement 36: Audit Drawer and Export

**User Story:** As a thesis examiner, I want formulas, sources and raw results accessible from the dashboard, so that every number can be audited.

#### Acceptance Criteria

1. WHEN the user selects a Candidate in the ranking, THE Dashboard audit drawer SHALL display, for the selected Candidate, every formula used to compute its sizing result, its performance values (decode TPS, prefill TPS, TTFT, effective TPS, 1M-token prefill time) and its cost values (CapEx, monthly OpEx, 60-month TCO), each showing the symbolic formula, the input values substituted with their units, and the computed result.
2. WHEN the user selects a Candidate in the ranking, THE Dashboard audit drawer SHALL list every `source_id` contributing to any value of the selected Candidate exactly once, each with the title and URL (or the reference where no URL exists) from the Source_Registry, the Source_Tier, and the access date in ISO 8601 format from the Provenance_Record.
3. WHEN the user selects a Candidate in the ranking, THE Dashboard audit drawer SHALL display, next to each of the five performance values of the selected Candidate, its Value_Origin label (`measured` or `formula`) together with the contributing `source_id` values.
4. WHEN the user clicks the JSON export button, THE Dashboard SHALL download one JSON file containing the full Service_Layer result for the current scenario, with monetary values in USD regardless of the Display_Currency, that validates against the result Domain_Contract without errors.
5. WHEN the user clicks the CSV export button, THE Dashboard SHALL download two CSV files: a ranking file with one header row and one row per ranked Candidate (rank, Candidate identifier, the six Criterion values and the aggregate score), and a timeline file with one header row and exactly 60 rows for months 1 to 60 (month plus the seven cumulative series of Requirement 26), with the currency code of the active Display_Currency in every monetary column header.
6. WHEN the Dashboard displays a new Service_Layer result, THE Dashboard audit drawer SHALL select the rank-1 Candidate by default until the user selects another Candidate.
7. IF no Service_Layer result exists for the current scenario inputs, or the result contains zero ranked Candidates, THEN THE Dashboard SHALL show a message in the audit drawer indicating that no Candidate is available for audit, SHALL disable the CSV export button when no result exists, and SHALL keep all scenario inputs unchanged.
8. FOR ALL exported JSON files, parsing the file with the result Domain_Contract SHALL produce an object equal to the Service_Layer result displayed at the time of export (round-trip property).

### Requirement 37: Visual Accessibility and UI Architecture

**User Story:** As a colour-vision-deficient executive, I want charts that do not rely on colour alone, so that I can read compliance and OOM status.

#### Acceptance Criteria

1. THE Dashboard SHALL define the eight Okabe-Ito colours (`#E69F00`, `#56B4E9`, `#009E73`, `#F0E442`, `#0072B2`, `#D55E00`, `#CC79A7`, `#000000`) as named constants in `src/ai_tco_dss/ui/theme.py`, and every line, marker, bar and fill colour assigned to a trace in a Plotly figure produced by the Dashboard SHALL be one of these eight values taken from those constants.
2. THE Corrections_Ledger SHALL contain one entry recording that the hex colours in `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` §2.2 are not Okabe-Ito colours, and that entry SHALL list, for each of the eight §2.2 archetypes (Sovereign Per-Seat Workstation; Sovereign Centralized Server / PD-Disagg; Heterogeneous Modality / Scavenged Rig; Dedicated EU Cloud GPU; Baseline C; Baseline B / D; Baseline A; OOM / Thermal / Eviction Warning), the original hex value, the assigned Okabe-Ito hex value, the assigned line style or fill pattern, and the decision date.
3. THE Dashboard SHALL assign each archetype exactly one Okabe-Ito colour and one line style (solid, dashed, dotted or dash-dot) or fill pattern as recorded in the Corrections_Ledger, and within any single Plotly figure no two traces representing different archetypes SHALL share the same combination of colour and line style or fill pattern.
4. WHEN the Dashboard displays a Candidate or a baseline in a chart or table, THE Dashboard SHALL show a text badge stating its compliance status (compliant or non-compliant) and, IF the Candidate fails the memory-fit check of the Sizing_Engine, a text badge stating OOM status, such that both statuses remain readable when the figure is rendered in greyscale.
5. THE Dashboard SHALL render each Simulator_Card (a Dashboard panel in Views 1 and 2 that owns its own input widgets) through a function decorated with `@st.fragment`.
6. WHEN the user changes an input widget inside one Simulator_Card, THE Dashboard SHALL re-execute only that card's fragment function, and a test SHALL verify that the render functions of all other Simulator_Cards are invoked zero additional times after the change.
7. THE Dashboard modules (all `.py` files under `src/ai_tco_dss/ui/`) SHALL import from the `ai_tco_dss` package only from `ai_tco_dss.services`, `ai_tco_dss.domain` and `ai_tco_dss.ui` and their submodules; imports of the Python standard library and third-party packages (such as Streamlit and Plotly) SHALL remain permitted.
8. IF any Dashboard module contains an `import` or `from ... import` statement that references `ai_tco_dss.engines`, `ai_tco_dss.decision` or `ai_tco_dss.catalog` or any of their submodules, THEN THE import-boundary test SHALL fail and SHALL report the offending module file and the forbidden import.

### Requirement 38: Service Layer and Ports-and-Adapters Architecture

**User Story:** As a developer, I want one service layer used by every adapter, so that Streamlit now and FastAPI, MCP and the scraper later produce identical results.

#### Acceptance Criteria

1. THE Service_Layer SHALL expose the four public functions `evaluate_scenario`, `recommend`, `size` and `project_tco`, each accepting its scenario inputs as Domain_Contract instances and returning exactly one Domain_Contract instance.
2. THE engines (Workload_Engine, Sizing_Engine, Performance_Engine, TCO_Engine, Baseline_Engine, Decision_Engine) SHALL compute their results only from their Domain_Contract arguments, SHALL NOT read or write files, SHALL NOT open network connections, SHALL NOT read or modify module-level mutable state, and SHALL return the same result when called with file system and network access blocked in the test environment.
3. THE Service_Layer SHALL obtain Catalog data only by calling Catalog_Repository protocol methods and SHALL NOT read files under `data/` directly.
4. THE Json_Catalog_Repository SHALL implement the Catalog_Repository protocol, and a test SHALL verify that an in-memory Catalog_Repository holding the same Catalog data can replace the Json_Catalog_Repository with no change to Service_Layer source code, with all four Service_Layer functions returning results equal to the Json_Catalog_Repository results for the Default_Workload_File scenario.
5. FOR ALL valid input Domain_Contracts, calling the same Service_Layer function twice with equal inputs and Catalog_Repository instances loaded from the same Catalog files SHALL return results that compare equal field by field, including ranking order and exact floating-point values, verified at minimum for the Default_Workload_File scenario and for every Use_Case combined with every Preset (determinism property).
6. THE Dashboard modules under `src/ai_tco_dss/ui/` SHALL NOT import any engine module or the Json_Catalog_Repository module, and SHALL obtain all computed results and Catalog data through the Service_Layer functions.
7. IF a Service_Layer function receives an argument that is not a valid instance of its declared input Domain_Contract, THEN THE Service_Layer SHALL raise a validation error that names the invalid argument or field and SHALL NOT call any engine.
8. IF a Service_Layer function receives an input that references a hardware, model or EU_Rental identifier that the Catalog_Repository does not contain, THEN THE Service_Layer SHALL raise an error that names the missing identifier and its item type, and SHALL return no partial result.

### Requirement 39: Concurrency and Performance Budget

**User Story:** As an operator, I want the dashboard to serve at least ten concurrent users within a response-time budget, so that a team can use the tool at the same time.

#### Acceptance Criteria

1. WHEN the first Service_Layer call in a process requests Catalog data, THE Json_Catalog_Repository SHALL read the Catalog files from `data/` exactly once and build the Catalog as immutable objects.
2. WHEN any later Service_Layer call or Dashboard session in the same process requests Catalog data, THE Json_Catalog_Repository SHALL return the same Catalog object instance without reading any Catalog file again.
3. IF a caller attempts to modify a field of any Catalog object (hardware, model, Benchmark_Record or Reference_Data item), THEN THE DSS SHALL raise an error and SHALL leave every field value of the shared Catalog unchanged.
4. WHEN 10 threads each call `evaluate_scenario` concurrently, each with one of 10 distinct valid scenarios evaluated against the MVP_Catalog, THE Service_Layer SHALL complete all 10 calls without raising an exception.
5. WHEN 10 threads each call `evaluate_scenario` concurrently, each with one of 10 distinct valid scenarios evaluated against the MVP_Catalog, THE Service_Layer SHALL return for each scenario a result in which every field value equals the corresponding field value of the result of calling `evaluate_scenario` sequentially with the same scenario.
6. WHEN 10 concurrent `evaluate_scenario` calls have completed, THE Json_Catalog_Repository SHALL hold a Catalog whose field values equal the field values before the calls started.
7. WHEN `recommend` runs 5 consecutive times on the MVP_Catalog with the Default_Workload_File scenario after the Catalog is already loaded, THE Service_Layer SHALL return the result with a median duration below 500 ms. Each duration is measured from the call to `recommend` until it returns and excludes Catalog loading time.

### Requirement 40: Extension Seams for Post-MVP Features

**User Story:** As the thesis author, I want the MVP to leave clear extension points, so that post-MVP features can be added without restructuring the code.

#### Acceptance Criteria

1. THE DSS SHALL contain in `specs/00_INDEX_AND_AGENT_ROUTER.md` exactly one extension-seam entry for each of the 8 post-MVP features (FastAPI adapter, MCP adapter, benchmark scraper writing Benchmark_Records, workload importer producing Workload_Profiles, database Catalog_Repository, catalog entry form, Views 3–5, agentic chatbot). Each entry SHALL name (a) the existing MVP interface that the feature attaches to (a named Service_Layer function, the Catalog_Repository protocol, or a named Domain_Contract), (b) the package directory under `src/ai_tco_dss/` where the feature's code would be added, and (c) the existing MVP modules that the feature requires to change, or the word "none" if no existing module changes.
2. WHEN the JSON Schema export command runs, THE DSS SHALL write to `schemas/` one JSON Schema file for each Domain_Contract used as a parameter type or return type of `evaluate_scenario`, `recommend`, `size` or `project_tco`, and each written file SHALL parse as valid JSON and contain a JSON Schema whose `title` equals the Domain_Contract class name.
3. IF a parameter type or return type of `evaluate_scenario`, `recommend`, `size` or `project_tco` is not a Domain_Contract, or has no corresponding JSON Schema file in `schemas/` after the export command runs, THEN THE DSS test suite SHALL fail with a message that names the Service_Layer function and the type.
4. WHEN a Benchmark_Record is constructed with only the fields defined in the Glossary, a `source_id` that exists in the Source_Registry, a Source_Tier equal to one of `official`, `third_party`, `community`, `formula` or `assumption`, and an `accessed` date in ISO 8601 format (YYYY-MM-DD), THE Benchmark_Record Domain_Contract SHALL accept the record without requiring any additional field, and THE Validate_CLI SHALL report zero errors for a Benchmark_Record file containing that record.
5. IF a Benchmark_Record is missing `source_id`, Source_Tier or `accessed`, or its Source_Tier is not one of the five defined values, or its `accessed` value is not a valid ISO 8601 date, THEN THE Benchmark_Record Domain_Contract SHALL raise a validation error that names each missing or invalid field.

### Requirement 41: Test-Driven Development and Test Suites

**User Story:** As the thesis author, I want tests written before code and organised by purpose, so that correctness is demonstrated in the thesis.

#### Acceptance Criteria

1. THE Project_Rules SHALL require that each implementation task first adds at least one test for every acceptance criterion id the task covers, and that the executing session runs these tests and observes at least one failure before writing any implementation code for the task.
2. THE Project_Rules SHALL require that an implementation task is marked complete in the Progress_File only after the task's new tests pass and the full `pytest` suite reports zero failures and zero errors.
3. THE DSS SHALL contain unit tests in `tests/unit/` that reproduce the specification benchmark values cited in Requirement 16.6, Requirement 17.10 and the Baseline formulas of Requirement 24, with each test referencing the requirement id it reproduces in its name or docstring.
4. THE unit tests for Requirements 16.6, 17.10 and 24 SHALL declare an explicit tolerance in every numeric assertion, using at most 1 % relative tolerance for Baseline formula outputs, at most 5 % relative tolerance for values the specification states as approximate (marked "~"), exact equality for feasibility flags, and a strict inequality for upper-bound values such as the 0.9 GB KV cache limit of Requirement 17.10.
5. THE DSS SHALL contain at least one `hypothesis` property test in `tests/property/` for every acceptance criterion in this document that begins with "FOR ALL" or is labelled as a property, with each property test referencing the criterion id (for example "17.9") in its name or docstring and generating at least 100 examples per run.
6. THE DSS SHALL contain integration tests in `tests/integration/` that call `evaluate_scenario` and `recommend` on the MVP_Catalog with the Default_Workload_File and assert that each call completes without raising an exception and returns output that validates against the corresponding Service_Layer output Domain_Contract.
7. WHEN the integration test calls `recommend` on the MVP_Catalog with the Default_Workload_File, THE Service_Layer SHALL return at least one ranked Candidate, and every returned Candidate SHALL carry a Value_Origin for each decode TPS, TTFT, effective TPS, quality score and price value.
8. WHEN `pytest` runs with network access disabled, THE test suite SHALL complete with zero failures and zero errors, and no test SHALL be skipped or marked expected-to-fail because network access is unavailable.

### Requirement 42: Calibration Tests and Calibration Report

**User Story:** As the thesis author, I want formula estimates compared against measured benchmarks, so that the thesis validation chapter can quantify model accuracy.

#### Acceptance Criteria

1. THE DSS SHALL contain calibration tests in `tests/calibration/` that generate one test case per Benchmark_Record whose `metric` is decode TPS or prefill TPS and whose `hardware_id` and `model_id` both resolve to items in the Catalog. Each test case SHALL compare the measured `value` of the record with the formula value. The formula value SHALL be computed by the Performance_Engine formula path, with measured Benchmark_Record lookup disabled. The formula SHALL use the record's `hardware_id`, `model_id`, `precision` and `context_tokens`; where `precision` or `context_tokens` is absent, it SHALL use the Performance_Engine default values.
2. THE DSS SHALL define the calibration tolerance per metric in `settings.py` as a symmetric absolute percentage error bound, with defaults of 30 % for decode TPS and 50 % for prefill TPS, each labelled `assumption`. THE DSS SHALL compute absolute percentage error as |formula value − measured value| ÷ measured value × 100.
3. IF the absolute percentage error of a Benchmark_Record is strictly greater than the tolerance of its metric, THEN THE calibration test SHALL fail, unless the record is listed as a known deviation in the Corrections_Ledger. If the record is listed there, THE calibration test SHALL be marked as an expected failure whose reason states the Corrections_Ledger entry id. An absolute percentage error equal to the tolerance SHALL pass.
4. WHEN the Calibration_Report command runs, THE Calibration_Report SHALL print, for each of decode TPS and prefill TPS, the number of compared records and the MAPE in percent rounded to one decimal place. THE Calibration_Report SHALL compute MAPE as the arithmetic mean of the absolute percentage errors of all compared records of that metric. The printed output SHALL also list the five records with the largest absolute percentage error, or all compared records if there are fewer than five. These records SHALL be sorted by absolute percentage error in descending order, with ties broken by `model_id` and then `hardware_id` in ascending order. Each listed record SHALL show its `model_id`, `hardware_id`, `source_id`, measured value, formula value and absolute percentage error.
5. WHEN the Calibration_Report command runs, THE Calibration_Report SHALL write a CSV file for inclusion in the thesis. The CSV file SHALL contain, per metric, the record count, the MAPE and the top-five record list, with the same values and the same rounding as the printed output.
6. IF a decode TPS or prefill TPS Benchmark_Record has no `hardware_id`, has a `hardware_id` or `model_id` that does not resolve to a Catalog item, or has a measured `value` less than or equal to zero, THEN THE calibration tests SHALL mark that record's test case as skipped with a reason naming the record's `model_id`, `source_id` and the missing or invalid field. THE Calibration_Report SHALL exclude the record from the count, the MAPE and the top-five list, and SHALL print the number of skipped records per metric.
7. IF a metric has zero compared records, THEN THE Calibration_Report SHALL print and write a record count of 0, a MAPE marked as not available and an empty top-five list for that metric, and SHALL complete without error.
