# Progress — AI TCO DSS MVP

## Current Status
Task 1 done (2026-11-07). The uv toolchain (Python 3.12, `pyproject.toml`, `uv.lock`), ruff, mypy (strict) and pytest are configured. The package skeleton `src/ai_tco_dss/` has empty sub-packages, an empty `settings.py` and a placeholder Dashboard (title "AI TCO DSS", caption "Catalog not loaded yet"). `scripts/verify.py` and `scripts/relocate_specs.py` exist. The Project Rules are in `CLAUDE.md` and `.kiro/steering/project-rules.md`, and the Corrections_Ledger is in `specs/07_DATA_CORRECTIONS.md`. The suite has 89 passing tests (layout, toolchain, session artefacts, relocation, offline guard, app smoke). Files are staged with `git add`, not committed. No domain contracts, catalog data or engines exist yet; Task 2 starts the domain contracts.

## Task Status
| Task | Title | Status | Completed |
|---|---|---|---|
| 1 | Bootstrap toolchain and session artefacts | done | 2026-11-07 |
| 1.1 | Write failing tests for repository layout and toolchain | done | 2026-11-07 |
| 1.2 | Write failing tests for session artefacts | done | 2026-11-07 |
| 1.3 | Write failing tests for the spec relocation script | done | 2026-11-07 |
| 1.4 | Write the offline guard, hypothesis profile and placeholder smoke test | done | 2026-11-07 |
| 1.5 | Create `pyproject.toml` and `uv.lock` with uv | done | 2026-11-07 |
| 1.6 | Create the package skeleton and placeholder Dashboard | done | 2026-11-07 |
| 1.7 | Create `scripts/verify.py`, `scripts/relocate_specs.py` and README commands | done | 2026-11-07 |
| 1.8 | Append Project Rules to `CLAUDE.md` and create the steering file | done | 2026-11-07 |
| 1.9 | Create the Corrections_Ledger `specs/07_DATA_CORRECTIONS.md` | done | 2026-11-07 |
| 1.10 | Create `progress.md` | done | 2026-11-07 |
| 1.11 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 2 | Domain contracts and schema export | not-started | |
| 2.1 | Write failing unit tests for the contracts | not-started | |
| 2.2 | Write failing tests for the schema export | not-started | |
| 2.3 | Write property test for contract JSON round trip | not-started | |
| 2.4 | Write property test for FX round trip | not-started | |
| 2.5 | Implement domain base, enums, errors and money helpers | not-started | |
| 2.6 | Implement catalog and scenario contracts and `EngineParameters` | not-started | |
| 2.7 | Implement result, input and request contracts | not-started | |
| 2.8 | Implement the schema export command | not-started | |
| 2.9 | Record contract deviations in the ledger | not-started | |
| 2.10 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 3 | Catalog repository, Validate_CLI, seed subset and Dashboard skeleton | not-started | |
| 3.1 | Create the minimal fixture catalog and write failing Validate_CLI tests | not-started | |
| 3.2 | Write failing repository tests | not-started | |
| 3.3 | Write failing import-boundary tests | not-started | |
| 3.4 | Extend the smoke and layout tests | not-started | |
| 3.5 | Write property test for provenance coverage | not-started | |
| 3.6 | Write property test for validator fault reporting | not-started | |
| 3.7 | Write property test for repository FX conversion | not-started | |
| 3.8 | Implement catalog loading and FX conversion | not-started | |
| 3.9 | Implement the Validate_CLI | not-started | |
| 3.10 | Implement the repositories | not-started | |
| 3.11 | Write the seed data subset | not-started | |
| 3.12 | Implement `catalog_overview` and the Dashboard skeleton | not-started | |
| 3.13 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 4 | Curated MVP catalog with web-verified values | not-started | |
| 4.1 | Write failing MVP catalog tests | not-started | |
| 4.2 | Write failing reference data tests | not-started | |
| 4.3 | Write property test for preset and popularity validation | not-started | |
| 4.4 | Add MVP completeness, preset and popularity rules to the Validate_CLI | not-started | |
| 4.5 | Web-verify and write the nine hardware files | not-started | |
| 4.6 | Web-verify and write the eight open-weights model files and quality records | not-started | |
| 4.7 | Web-verify and write the four commercial API model files | not-started | |
| 4.8 | Web-verify and write the reference data | not-started | |
| 4.9 | Update the Corrections_Ledger for the curated data | not-started | |
| 4.10 | Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 5 | Workload and Sizing engines, `size` service and View 1 card | not-started | |
| 5.1 | Write failing Workload_Engine tests | not-started | |
| 5.2 | Write failing Sizing_Engine tests | not-started | |
| 5.3 | Write failing engine purity tests | not-started | |
| 5.4 | Write failing View 1 chart tests | not-started | |
| 5.5 | Write property test for workload formulas | not-started | |
| 5.6 | Write property test for workload monotonicity | not-started | |
| 5.7 | Write property test for usable memory by architecture | not-started | |
| 5.8 | Write property test for the Mac default-split trap | not-started | |
| 5.9 | Write property test for weight and KV-per-token formulas | not-started | |
| 5.10 | Write property test for KV pool, concurrency and OOM | not-started | |
| 5.11 | Write property test for memory breakdown and eviction flag | not-started | |
| 5.12 | Write property test for memory monotonicity | not-started | |
| 5.13 | Write property test for node-count handling | not-started | |
| 5.14 | Write property test for quality, license and context flags | not-started | |
| 5.15 | Write property test for View 1 chart structure | not-started | |
| 5.16 | Implement the Workload_Engine and workload loading | not-started | |
| 5.17 | Implement the Sizing_Engine | not-started | |
| 5.18 | Implement the `size` service | not-started | |
| 5.19 | Implement the View 1 chart and card | not-started | |
| 5.20 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 6 | Performance engine, measured-first resolver and calibration | not-started | |
| 6.1 | Write failing Performance_Engine tests | not-started | |
| 6.2 | Write failing settings tests | not-started | |
| 6.3 | Write failing calibration tests and report tests | not-started | |
| 6.4 | Write property test for the measured-first resolver | not-started | |
| 6.5 | Write property test for performance formulas | not-started | |
| 6.6 | Write property test for decode monotonicity in bandwidth | not-started | |
| 6.7 | Write property test for the MoE dual-parameter law | not-started | |
| 6.8 | Write property test for the context degradation curve | not-started | |
| 6.9 | Write property test for latency invariants | not-started | |
| 6.10 | Write property test for calibration outcome classification | not-started | |
| 6.11 | Write property test for the calibration report builder | not-started | |
| 6.12 | Implement the measured-first resolver and settings checks | not-started | |
| 6.13 | Implement the Performance_Engine | not-started | |
| 6.14 | Implement the Calibration_Report CLI | not-started | |
| 6.15 | Extend the `size` service and View 1 card with performance | not-started | |
| 6.16 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 7 | TCO engine, utilization, Baselines A–D and `project_tco` | not-started | |
| 7.1 | Write failing TCO_Engine tests | not-started | |
| 7.2 | Write failing Baseline_Engine tests | not-started | |
| 7.3 | Write failing service validation test for edited reference data | not-started | |
| 7.4 | Write property test for on-premise cost components | not-started | |
| 7.5 | Write property test for the resale curve | not-started | |
| 7.6 | Write property test for TCO monotonicity | not-started | |
| 7.7 | Write property test for the utilization formula | not-started | |
| 7.8 | Write property test for utilization classification and viability badge | not-started | |
| 7.9 | Write property test for baseline formulas | not-started | |
| 7.10 | Write property test for Baseline C versus Baseline B | not-started | |
| 7.11 | Write property test for baselines growing with users | not-started | |
| 7.12 | Implement the TCO_Engine | not-started | |
| 7.13 | Implement Baselines A–D | not-started | |
| 7.14 | Implement `project_tco` and the View 2 cost table | not-started | |
| 7.15 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 8 | EU rental, hybrid split, 60-month timeline and View 2 chart | not-started | |
| 8.1 | Write failing timeline tests | not-started | |
| 8.2 | Write failing View 2 chart tests | not-started | |
| 8.3 | Write property test for rental and hybrid cumulative formulas | not-started | |
| 8.4 | Write property test for hybrid boundary ratios | not-started | |
| 8.5 | Write property test for timeline structure | not-started | |
| 8.6 | Write property test for the break-even oracle | not-started | |
| 8.7 | Write property test for non-decreasing cumulative series | not-started | |
| 8.8 | Write property test for View 2 chart structure | not-started | |
| 8.9 | Implement rental, hybrid, timeline and break-even | not-started | |
| 8.10 | Extend `project_tco` with the timeline | not-started | |
| 8.11 | Implement the View 2 chart | not-started | |
| 8.12 | Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 9 | Decision engine (SAW), use cases, presets, `recommend`/`evaluate_scenario` and Normal mode | not-started | |
| 9.1 | Write failing decision unit tests | not-started | |
| 9.2 | Write failing service integration tests | not-started | |
| 9.3 | Write failing Normal-mode UI tests | not-started | |
| 9.4 | Write property test for candidate enumeration | not-started | |
| 9.5 | Write property test for hybrid local selection | not-started | |
| 9.6 | Write property test for deterministic candidate generation | not-started | |
| 9.7 | Write property test for the hard-filter oracle | not-started | |
| 9.8 | Write property test for rejected list ordering | not-started | |
| 9.9 | Write property test for quality resolution order | not-started | |
| 9.10 | Write property test for risk bounds and monotonicity | not-started | |
| 9.11 | Write property test for normalisation | not-started | |
| 9.12 | Write property test for SAW score composition and order | not-started | |
| 9.13 | Write property test for explanation content | not-started | |
| 9.14 | Write property test for SAW dominance | not-started | |
| 9.15 | Write property test for invalid weights | not-started | |
| 9.16 | Write property test for deterministic ranking | not-started | |
| 9.17 | Write property test for Dashboard input validators | not-started | |
| 9.18 | Write property test for Normal mode ignoring Expert values | not-started | |
| 9.19 | Implement quality resolution | not-started | |
| 9.20 | Implement candidate generation and evaluation | not-started | |
| 9.21 | Implement the hard filters | not-started | |
| 9.22 | Implement criteria, normalisation, SAW and explanation | not-started | |
| 9.23 | Implement `recommend` and `evaluate_scenario` | not-started | |
| 9.24 | Implement Normal mode, sidebar and ranking tab | not-started | |
| 9.25 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 10 | TOPSIS, Expert mode and FX override | not-started | |
| 10.1 | Write failing TOPSIS unit tests | not-started | |
| 10.2 | Write failing Expert-mode smoke tests | not-started | |
| 10.3 | Write property test for TOPSIS against a reference computation | not-started | |
| 10.4 | Write property test for TOPSIS dominance | not-started | |
| 10.5 | Implement TOPSIS | not-started | |
| 10.6 | Implement Expert mode and the FX override pass-through | not-started | |
| 10.7 | Show the SAW/TOPSIS comparison in the ranking tab | not-started | |
| 10.8 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 11 | KPI ribbon, display currency, theme and accessibility, fragments | not-started | |
| 11.1 | Write failing KPI tests | not-started | |
| 11.2 | Write failing theme and accessibility tests | not-started | |
| 11.3 | Write failing fragment and layout smoke tests | not-started | |
| 11.4 | Write property test for display currency | not-started | |
| 11.5 | Implement display currency formatting | not-started | |
| 11.6 | Implement the KPI ribbon | not-started | |
| 11.7 | Apply theme, badges and fragments in charts and cards | not-started | |
| 11.8 | Wire the three-tier layout and display currency in the app | not-started | |
| 11.9 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 12 | Audit drawer and export | not-started | |
| 12.1 | Write failing audit and export tests | not-started | |
| 12.2 | Write failing audit smoke tests | not-started | |
| 12.3 | Write property test for the audit source list | not-started | |
| 12.4 | Write property test for the export round trip | not-started | |
| 12.5 | Implement the audit drawer content | not-started | |
| 12.6 | Implement JSON and CSV export | not-started | |
| 12.7 | Wire the audit drawer into the app | not-started | |
| 12.8 | Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |
| 13 | Concurrency, performance budget, CI, README and extension seams | not-started | |
| 13.1 | Write failing concurrency tests | not-started | |
| 13.2 | Write the performance budget test | not-started | |
| 13.3 | Write contract signature and schema coverage tests | not-started | |
| 13.4 | Write the Assumptions table consistency test | not-started | |
| 13.5 | Write CI, README and extension seam tests | not-started | |
| 13.6 | Write property test for service determinism | not-started | |
| 13.7 | Write the property coverage meta-test | not-started | |
| 13.8 | Create the GitHub Actions workflow | not-started | |
| 13.9 | Complete the README commands | not-started | |
| 13.10 | Append the extension seam table to `specs/00_INDEX_AND_AGENT_ROUTER.md` | not-started | |
| 13.11 | Fix concurrency and assumption findings | not-started | |
| 13.12 | Final checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | not-started | |

## Decisions Log
| Date | Decision | Rationale | Affects |
|---|---|---|---|
| 2026-11-06 | D-01: catalog numbers use `Sourced[T]` (value, source_id, tier, accessed, note); money uses `Money` | One provenance mechanism for JSON, contracts, validator and audit drawer (design.md "Key Design Decisions") | 8.3, 8.5, 12.3 |
| 2026-11-06 | D-02: a JSON number is covered if it or an ancestor object carries source_id + tier + accessed | Record-level provenance for benchmarks, fx.json, popularity and workload files | 8.3, 8.5, 14.1 |
| 2026-11-06 | D-03: catalog contracts use tuples only; lookup indexes stay private to the repository | Frozen models still allow mutation of inner lists and dicts | 39.3 |
| 2026-11-06 | D-04: EUR→USD conversion happens in the repository (`repo.catalog(fx_override)`), cached per rate | Engines never see EUR; FX override needs no change to fx.json | 12.3, 12.4, 39.2 |
| 2026-11-06 | D-05: engine tunables live in `settings.py` (pydantic-settings, `AI_TCO_*`) and reach engines as `EngineParameters` | Engines depend only on Domain_Contract arguments | 7.1, 9.5, 9.10, 20.6 |
| 2026-11-06 | D-06: quality scores are Benchmark_Records in `data/benchmarks/quality.json` | One measured-first path for performance and quality | 9.9, 10.8 |
| 2026-11-06 | D-07: utilization capacity fallback uses the stream limit U_max bounded by a per-node batch cap | Utilization must show idle capacity | 23.4 |
| 2026-11-06 | D-08: multi-node single-stream decode uses per-node bandwidth × α (no × N); aggregate capacity scales with N | Literal Req 20.1; calibration quantifies the error | 20.1, 23.1, 42 |
| 2026-11-06 | D-09: the 60-month timeline is anchored on an on-premise deployment | Req 26 defines break-even of on-premise against baselines | 26, 34.2, 35.4 |
| 2026-11-06 | D-10: Romania employer social tax = 2.25 % statutory CAM | Benefits are not a social tax | 13.6 |
| 2026-11-06 | D-11: CSV export downloads one ZIP with the two CSV files | `st.download_button` delivers one file per click (ledger C-012) | 36.5 |
| 2026-11-06 | D-12: one helper `scripts/verify.py` runs focus tests, ruff, mypy, Validate_CLI and the full suite | One command line per task that works in PowerShell 5.1 and bash | 4.3, 41.2 |
| 2026-11-07 | Accepted open point: Task 5 combines the Workload and Sizing engines | The Workload_Engine has no visible output alone and Req 6.2 needs a demo step | Task 5, 6.2 |
| 2026-11-07 | Accepted open point: CSV export is one ZIP with two CSVs | See D-11 and ledger C-012 | 36.5 |
| 2026-11-07 | Accepted open point: multi-node decode follows Req 20.1 literally | See D-08 and ledger C-011; calibration report quantifies the error | 20.1, 42 |
| 2026-11-07 | Task 1 adds a placeholder Dashboard (`ui/app.py`: title "AI TCO DSS", caption "Catalog not loaded yet") and the README Dashboard command | The Dashboard must start after every task | 6.3, 6.4, Task 1 |
| 2026-11-07 | Spec files were untracked at relocation, so Req 1.5 applies. The layout test checks `git log --follow` only once commits exist; the content baseline is the first committed version, or the staged version before the first commit | The user moved and staged the files; sessions never commit | 1.4, 1.5, 1.10, Task 1.1 |
| 2026-11-07 | The CLAUDE.md original hash is taken over the text with CRLF→LF and trailing newlines removed | Windows checkouts use CRLF (core.autocrlf), CI uses LF | 5.2, Task 1.2 |
| 2026-11-07 | The toolchain test runs `uv lock --check --offline` | The suite must pass without network access | 2.1, 2.2, 41.8 |
| 2026-11-07 | Ruff: line length 100, rules E, F, W, I, B, UP, SIM, RUF; `*.md` excluded | Ruff 0.17 formats Python blocks inside Markdown and would rewrite the spec documents | 1.10, 2.3, 2.4 |
| 2026-11-07 | The relocation script aborts every move when any target conflicts | Task 1.7 requires the conflict check before any change | 1.11 |
| 2026-11-07 | The prior-conversation check in tasks.md ignores phrases inside double quotes and does not list the bare words "prior conversation" | Task 1.2 quotes the phrases as examples and uses "prior conversation" to name the check itself | 4.4, Task 1.2 |
| 2026-11-07 | The offline guard blocks every non-loopback `socket.connect`; loopback (127.0.0.1, ::1, localhost) stays allowed | Windows asyncio builds its internal socket pair through a loopback connect, which AppTest needs; loopback is not network access | 41.8, Task 1.4 |

## Changelog
| Date | Task | Files created or modified |
|---|---|---|
| 2026-11-07 | 1 | created: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `scripts/verify.py`, `scripts/relocate_specs.py`, `.kiro/steering/project-rules.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `src/ai_tco_dss/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/{domain,catalog,engines,decision,services,ui}/__init__.py`, `src/ai_tco_dss/ui/app.py`, `tests/conftest.py`, `tests/unit/test_repository_layout.py`, `tests/unit/test_toolchain.py`, `tests/unit/test_session_artefacts.py`, `tests/unit/test_relocate_specs.py`, `tests/unit/test_offline_guard.py`, `tests/integration/test_app_smoke.py`; modified: `README.md` (commands), `CLAUDE.md` (appended `## Project Rules`) |

## Known Deviations
| Deviation | Ledger entries |
|---|---|
| Rental GPU is RTX PRO 6000 Max-Q; sizing reuses the workstation item | C-009 |
| Multi-node single-stream decode ignores the per-node bandwidth gain of tensor parallelism (Req 20.1 applied literally) | C-011 |
| CSV export delivers one ZIP with two CSV files instead of two downloads | C-012 |

## Next Step
Task 2 — Domain contracts and schema export

## Next Session Prompt
```text
You are continuing the AI TCO DSS MVP (TUM thesis, Python 3.12, uv). Read these files first, in order:
1. CLAUDE.md
2. progress.md
3. .kiro/specs/ai-tco-dss-mvp/requirements.md
4. .kiro/specs/ai-tco-dss-mvp/design.md
5. .kiro/specs/ai-tco-dss-mvp/tasks.md
Then execute task 2 "Domain contracts and schema export" from tasks.md, and only that task.
Task_Scope (identical to tasks.md):
  Load: `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Glossary", § "Requirement 7: Domain Contracts", § "Requirement 12: Currency and FX Conversion", § "Requirement 40: Extension Seams for Post-MVP Features"; `design.md` § "Domain base (`domain/base.py`)", § "Settings (`settings.py`)", § "Engine call convention", § "Data Models" (all subsections), § "Error Handling", § "Correctness Properties" › "Property 1" and "Property 6"; `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (whole file); `specs/07_DATA_CORRECTIONS.md` § "Contract Deviations"
  Modify: `src/ai_tco_dss/domain/`, `src/ai_tco_dss/settings.py`, `pyproject.toml`, `uv.lock`, `schemas/`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_contracts.py`, `tests/unit/test_schema_export.py`, `tests/property/strategies.py`, `tests/property/test_contract_props.py`
  Verify: uv run python scripts/verify.py tests/unit/test_contracts.py tests/unit/test_schema_export.py tests/property/test_contract_props.py
Work test-first, change only Task_Scope files, run the task's verification command (it must exit 0),
then update progress.md (Task Status, Current Status, Changelog, Next Step) and rewrite
this prompt for the next not-started task before reporting completion.
Stage changed files with git add; do not commit or push.
```
