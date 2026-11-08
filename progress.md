# Progress — AI TCO DSS MVP

## Current Status

**Task 10 is functionally implemented and verified:** Python TOPSIS vector normalization, worst-observed missing-value imputation, distances/closeness, deterministic ties and paired SAW/TOPSIS ranks; complete Expert controls with catalog preset initialization, validated raw weights, method selection and FX overrides. Normal mode preserves use case/users/preset and ignores all Expert inputs. Validation and calculation responses cannot overwrite newer edits or mode transitions. No Streamlit code, catalog data or domain contracts changed.

Default TOPSIS uses the same **36 admissible / 637 rejected** candidates as SAW. RTX Pro 6000 Blackwell 96 GB x1 + Qwen 3.8 Flash Next INT2 leads with closeness **0.758** (SAW rank 9); the existing SAW leader remains unchanged. The API exposes preset weights through `/options`; TypeScript types are regenerated. Display currency never submits calculations or changes USD ranking/break-even. A valid FX override legitimately recalculates EUR-derived USD costs; retained TCO projections keep the rate associated with their successful request.

Task 10 validation: **38 Chromium checks**, including both themes at 1280/1440/768/390 CSS px and inline validation, plus nine frontend component/helper checks, typecheck/lint/build/types:check and separate launcher startup/proxy/cleanup pass. Independent NumPy reference and dominance properties pass. Focused TOPSIS/property/service/API checks: **34 passed**. `uv run python scripts/verify.py tests/unit/test_topsis.py` passes its focus, ruff/format, strict mypy and catalog validation; full suite: **713 passed, 3 calibration xfailed, 3 failures solely from the same missing thesis/thesis_notes.md and thesis/literature.bib**. See `frontend/TASK10_REVIEW.md`, `frontend/expert-comparison.html` and ten new browser screenshots. The existing Normal/memory/TCO screenshot baselines are unchanged.

The user explicitly authorized Task 10 implementation despite the unrelated completion gate, superseding the old Task 9 stopping point. Tasks 8-10 stay administratively in progress under Project Rule 8; Task 10.1-10.4 are done and 10.5 retains only that gate. **Next implementation: Task 11, web KPI/chart/theme/accessibility polish.** Audit/export remains Task 12. No commit or push was made; relevant changes are staged and unrelated untracked files are preserved.

Task 9 implementation is complete: deterministic candidates, all nine hard filters with complete rejection reasons, measured-first quality/fallback ratios, six-criterion SAW, explanations, recommend/evaluate services and FastAPI routes, and the actual Stitch Ranking screen with working Normal-mode controls. Python remains the numerical authority. Default inputs yield 36 admissible / 637 rejected candidates; the leading option is RTX Pro 6000 Blackwell 96 GB x4 + DeepSeek V4.1 Flash INT4 (SAW 0.817 rounded). TOPSIS is now implemented by Task 10 above.

The hybrid contract gap is resolved with explicit context/endpoint facts and component evaluations, with local utilization recomputed at the local demand share (C-042). Rental host RAM is divided per node only when constructing the sizing input, preserving the server total and keeping hardware configurations distinct in the local cache (C-043). The request explicitly authorizes the necessary extension to `domain/results.py` and three generated result schemas.

Task 9 validation: focused Python/API tests, SAW property tests, recursive contract round trips, strict mypy, ruff/format, catalog validation, frontend type/lint/build, seven component tests, OpenAPI drift and launcher startup/proxy/cleanup pass. Browser evidence covers both themes at 1280/1440/768/390 CSS px, real controls, all rejection reasons, empty/server/loading states, delayed stale responses and independent memory inputs. See `frontend/TASK9_REVIEW.md` and `frontend/ranking-comparison.html`. **Final verification:** `uv run python scripts/verify.py tests/unit/test_decision.py tests/integration/test_service_end_to_end.py` passes all 49 focused tests, ruff/format, strict mypy and catalog validation; its full suite reports **703 passed, 3 calibration xfailed, 3 failures solely from missing thesis/thesis_notes.md and thesis/literature.bib**. All **23 Chromium flows/screenshots**, seven component tests, frontend type/lint/build, OpenAPI drift and launcher checks pass. Five warm recommend calls have median **0.247 s**. The unrelated missing-thesis gate is retained without changing its tests.

Windows shortcut: double-click `run.bat` to sync Python dependencies, install web dependencies on first use, start the React UI/API and open the browser. Keep its console open; Ctrl+C stops both services. Updated at the author's request on 2026-11-08; launcher startup/proxy/cleanup verification passes.

Tasks 1–7 remain complete. **Task 8's React/TypeScript + Vite/Tailwind/shadcn foundation and FastAPI size/TCO vertical slice are implemented and visually verified.** Root `npm run dev` starts Vite at 127.0.0.1:5173 and Python at 127.0.0.1:8000, proxies API calls and terminates both children. Python remains the numerical authority; the existing rental/hybrid/timeline implementation is reused unchanged.

All twelve canonical Stitch screens have local HTML and screenshot exports, design-system JSON, a resource/dimension manifest and implementation tokens under `design/stitch/`. Real Chromium screenshots cover ranking/memory/TCO in both themes at 1280/1440/768/390 CSS px, plus loading/catalog-error/OOM states. See `design/stitch/REVIEW.md`, `comparison.html` and the Task 9 frontend review. The UI includes separate memory/TCO controls, real charts/tables, display-only EUR, validated scenario edits, stale-request protection, retained last-valid simulator results and explicit loading/error/infeasible states. Final chart/KPI polish and audit/downloads remain Tasks 11–12; production serving/CI and Streamlit retirement remain Task 13.

Task 8 verification: API/service parity and errors pass; frontend type/lint/build, generated-type drift, five component/state tests, browser flows/screenshots and launcher startup/proxy/cleanup pass. Python ruff/format, strict mypy and catalog validation pass. The required verification helper reaches the full suite: **652 passed, 3 calibration xfailed, 3 failed solely because thesis/thesis_notes.md and thesis/literature.bib are missing**. The three historical relocation failures caused by the already-approved web notices were resolved with an exact amendment whitelist that still compares the remaining original content. Unrelated thesis files/tests are preserved and not newly staged.

**Administrative completion gate:** Tasks 8/9/10 and subtasks 8.6/9.6/10.5 remain `in-progress` under CLAUDE.md Project Rule 8 (full pytest must have zero failures). No functional acceptance work remains for these implemented slices. Do not invent thesis documents or weaken their tests to satisfy the gate. Once the author restores those documents or explicitly changes that gate, rerun verification and close their administrative gates; the next implementation task is Task 11. Numerical-calibration issues and .kiro relocation remain deferred.

Open points for the author from Task 7: Req 22.3 limits H_active to 730 h while the Workload_Profile allows 744 h, so profiles above 730 h get no on-premise TCO (C-038, requirement change proposal). `TcoInput` lacks `SizingOptions`, so the target context is derived from the sizing result and the eviction wait time ignores β_backend (C-039); Baseline C does not list the gateway-fee source id because the baseline inputs carry the fee as a float (C-040); both have contract change proposals. No hardware item has a cabling kit, so multi-node CapEx has no switch cost. Task 9 now resolves quality, risk and popularity for generated `project_tco` candidates. During the demo one cold server start logged a plotly/pandas "partially initialized module" error in the unchanged View 1 chart; it did not reproduce on a second cold start or in three fresh sessions.

Task 6 summary: Task 6 added the measured-first resolver (`engines/resolver.py`, `select_benchmark`), the Performance_Engine (`engines/performance.py`: `compute_performance`, `compute_api_performance`, `delta_ctx`), a δ_ctx breakpoint check in `settings.py`, the Calibration_Report CLI (`services/calibration_report.py`, console script `ai-tco-calibrate`, writes `reports/calibration.csv`), the first decode and prefill Benchmark_Records (`data/benchmarks/decode.json` with 6 records, `prefill.json` with 1 record, all from the spec 06 YouTube summaries, tier `community`) and the performance table of the View 1 card. `size` now returns `PerformanceResult` for feasible pairings and the AA v5 `QualityScore`. Demo checked with a headless app through the agent API: Mac mini M5 Pro 64GB + Qwen 3.8-27B INT4 at 8 192 tokens shows decode 14.7 tok/s `measured (YT-18)`, prefill 1,200 tok/s, TTFT 20.0 s and effective TPS 13.6 tok/s `formula`, and the bar label "AA v5 20.1". `uv run ai-tco-calibrate` prints decode: 6 records, MAPE 252.0 % (dominated by the offload record C-036; the other five are 5.1 % to 59.3 %), prefill: 1 record, MAPE 0.0 % (circular, C-037). Three calibration cases are expected failures with ledger ids C-035 (Flash Next on M5 Ultra, 2 records) and C-036 (DeepSeek INT2 on Strata). After Task 6 the full suite had 512 passing tests and 3 xfailed.

Open points for the author from Task 6: the benchmark values come from the spec 06 summaries of the videos (not re-watched); unstated contexts are stored as 8,192 tokens and unstated precisions as INT4 (C-037, Assumptions). The gpt-oss-120b Strix Halo records (YT-02 46 TPS, YT-06 51.1 TPS) are not stored because an out-of-scope MVP test deletes that model from a data copy (C-037). Multi-node and speculative-decoding measurements cannot be stored until `BenchmarkRecord` gets `nodes` and `speculative_mode` fields (contract change proposal in C-037).

Task 5 summary: Task 5 added the Workload_Engine (`engines/workload.py`), the Sizing_Engine (`engines/sizing.py`), workload loading for other files (`load_workload(path)` in both repositories and as a Service_Layer function), the `size` service, and the View 1 tab with the memory-fit Simulator_Card (`ui/cards.py`, `@st.fragment`), the pure chart factory `memory_fit_figure` (`ui/charts.py`) and the Okabe-Ito constants (`ui/theme.py`). Demo checked with AppTest and a headless app through the agent API: Mac Studio M5 Max 128GB + Qwen 3.8 Flash Next INT4 at 8 192 tokens is infeasible against 103.04 GB usable (shortfall 10.3 GB) and shows `sudo sysctl iogpu.wired_limit_mb=117760`; with the Mac override the usable line moves to 115.00 GB and the pairing fits (U_max 7). Req 16.6 deviations are 0.04 GB and 0.00 GB (below 1.0 GB, no ledger entry). The design's tiered-offload pool formula contradicted Req 18.6 and was replaced (ledger C-034). After Task 5 the full suite had 424 passing tests.

Task 4 summary: Task 4 replaced the seed subset with the curated MVP catalog: 9 hardware files, 12 model files (8 open-weights, 4 commercial API), 14 quality Benchmark_Records, 6 EU rentals and updated reference data. Values were fetched on 2026-11-07 from vendor pages (NVIDIA, Apple, AMD, Anthropic, OpenAI, Google), Hugging Face model cards and `config.json`, Unsloth GGUF file sizes, the OpenRouter models API and rankings, Artificial Analysis (AA v5.0.1), Hetzner, Nebius, Fireworks, ECB and PwC tax summaries; `data/sources.json` now has 75 entries. Values without a web source (most hardware street prices, Apple configured prices, salaries, recruiting delays, some idle watts) stay `SPEC-03` / `assumption` and are listed in ledger C-032. The Validate_CLI has new MVP completeness rules (on by default only for the repository `data/` root, `--mvp` / `--no-mvp` to force), quality-score range checks, preset rules and popularity rules. At the user's request the rentals include other EU providers (Hetzner GEX131, Nebius RTX PRO 6000 and 8× H100, Fireworks 8× H100 Frankfurt); Deutsche Telekom, OVHcloud and Scaleway were researched but not added (ledger C-031). The start page therefore shows "Catalog: 9 hardware, 12 models, 6 rentals" instead of the "2 rentals" of the tasks.md demo. Open points for the author: the German employer tax ignores contribution ceilings (C-019), and Gemma 4 12B, gpt-oss-120b and Gemini 3.1 Pro have no quality score, so they fail every Quality_Floor (C-025). After Task 4 the full suite had 324 passing tests.

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
| 2 | Domain contracts and schema export | done | 2026-11-07 |
| 2.1 | Write failing unit tests for the contracts | done | 2026-11-07 |
| 2.2 | Write failing tests for the schema export | done | 2026-11-07 |
| 2.3 | Write property test for contract JSON round trip | done | 2026-11-07 |
| 2.4 | Write property test for FX round trip | done | 2026-11-07 |
| 2.5 | Implement domain base, enums, errors and money helpers | done | 2026-11-07 |
| 2.6 | Implement catalog and scenario contracts and `EngineParameters` | done | 2026-11-07 |
| 2.7 | Implement result, input and request contracts | done | 2026-11-07 |
| 2.8 | Implement the schema export command | done | 2026-11-07 |
| 2.9 | Record contract deviations in the ledger | done | 2026-11-07 |
| 2.10 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 3 | Catalog repository, Validate_CLI, seed subset and Dashboard skeleton | done | 2026-11-07 |
| 3.1 | Create the minimal fixture catalog and write failing Validate_CLI tests | done | 2026-11-07 |
| 3.2 | Write failing repository tests | done | 2026-11-07 |
| 3.3 | Write failing import-boundary tests | done | 2026-11-07 |
| 3.4 | Extend the smoke and layout tests | done | 2026-11-07 |
| 3.5 | Write property test for provenance coverage | done | 2026-11-07 |
| 3.6 | Write property test for validator fault reporting | done | 2026-11-07 |
| 3.7 | Write property test for repository FX conversion | done | 2026-11-07 |
| 3.8 | Implement catalog loading and FX conversion | done | 2026-11-07 |
| 3.9 | Implement the Validate_CLI | done | 2026-11-07 |
| 3.10 | Implement the repositories | done | 2026-11-07 |
| 3.11 | Write the seed data subset | done | 2026-11-07 |
| 3.12 | Implement `catalog_overview` and the Dashboard skeleton | done | 2026-11-07 |
| 3.13 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 4 | Curated MVP catalog with web-verified values | done | 2026-11-07 |
| 4.1 | Write failing MVP catalog tests | done | 2026-11-07 |
| 4.2 | Write failing reference data tests | done | 2026-11-07 |
| 4.3 | Write property test for preset and popularity validation | done | 2026-11-07 |
| 4.4 | Add MVP completeness, preset and popularity rules to the Validate_CLI | done | 2026-11-07 |
| 4.5 | Web-verify and write the nine hardware files | done | 2026-11-07 |
| 4.6 | Web-verify and write the eight open-weights model files and quality records | done | 2026-11-07 |
| 4.7 | Web-verify and write the four commercial API model files | done | 2026-11-07 |
| 4.8 | Web-verify and write the reference data | done | 2026-11-07 |
| 4.9 | Update the Corrections_Ledger for the curated data | done | 2026-11-07 |
| 4.10 | Checkpoint and progress update: Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 5 | Workload and Sizing engines, `size` service and View 1 card | done | 2026-11-07 |
| 5.1 | Write failing Workload_Engine tests | done | 2026-11-07 |
| 5.2 | Write failing Sizing_Engine tests | done | 2026-11-07 |
| 5.3 | Write failing engine purity tests | done | 2026-11-07 |
| 5.4 | Write failing View 1 chart tests | done | 2026-11-07 |
| 5.5 | Write property test for workload formulas | done | 2026-11-07 |
| 5.6 | Write property test for workload monotonicity | done | 2026-11-07 |
| 5.7 | Write property test for usable memory by architecture | done | 2026-11-07 |
| 5.8 | Write property test for the Mac default-split trap | done | 2026-11-07 |
| 5.9 | Write property test for weight and KV-per-token formulas | done | 2026-11-07 |
| 5.10 | Write property test for KV pool, concurrency and OOM | done | 2026-11-07 |
| 5.11 | Write property test for memory breakdown and eviction flag | done | 2026-11-07 |
| 5.12 | Write property test for memory monotonicity | done | 2026-11-07 |
| 5.13 | Write property test for node-count handling | done | 2026-11-07 |
| 5.14 | Write property test for quality, license and context flags | done | 2026-11-07 |
| 5.15 | Write property test for View 1 chart structure | done | 2026-11-07 |
| 5.16 | Implement the Workload_Engine and workload loading | done | 2026-11-07 |
| 5.17 | Implement the Sizing_Engine | done | 2026-11-07 |
| 5.18 | Implement the `size` service | done | 2026-11-07 |
| 5.19 | Implement the View 1 chart and card | done | 2026-11-07 |
| 5.20 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 6 | Performance engine, measured-first resolver and calibration | done | 2026-11-07 |
| 6.1 | Write failing Performance_Engine tests | done | 2026-11-07 |
| 6.2 | Write failing settings tests | done | 2026-11-07 |
| 6.3 | Write failing calibration tests and report tests | done | 2026-11-07 |
| 6.4 | Write property test for the measured-first resolver | done | 2026-11-07 |
| 6.5 | Write property test for performance formulas | done | 2026-11-07 |
| 6.6 | Write property test for decode monotonicity in bandwidth | done | 2026-11-07 |
| 6.7 | Write property test for the MoE dual-parameter law | done | 2026-11-07 |
| 6.8 | Write property test for the context degradation curve | done | 2026-11-07 |
| 6.9 | Write property test for latency invariants | done | 2026-11-07 |
| 6.10 | Write property test for calibration outcome classification | done | 2026-11-07 |
| 6.11 | Write property test for the calibration report builder | done | 2026-11-07 |
| 6.12 | Implement the measured-first resolver and settings checks | done | 2026-11-07 |
| 6.13 | Implement the Performance_Engine | done | 2026-11-07 |
| 6.14 | Implement the Calibration_Report CLI | done | 2026-11-07 |
| 6.15 | Extend the `size` service and View 1 card with performance | done | 2026-11-07 |
| 6.16 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 7 | TCO engine, utilization, Baselines A–D and `project_tco` | done | 2026-11-07 |
| 7.1 | Write failing TCO_Engine tests | done | 2026-11-07 |
| 7.2 | Write failing Baseline_Engine tests | done | 2026-11-07 |
| 7.3 | Write failing service validation test for edited reference data | done | 2026-11-07 |
| 7.4 | Write property test for on-premise cost components | done | 2026-11-07 |
| 7.5 | Write property test for the resale curve | done | 2026-11-07 |
| 7.6 | Write property test for TCO monotonicity | done | 2026-11-07 |
| 7.7 | Write property test for the utilization formula | done | 2026-11-07 |
| 7.8 | Write property test for utilization classification and viability badge | done | 2026-11-07 |
| 7.9 | Write property test for baseline formulas | done | 2026-11-07 |
| 7.10 | Write property test for Baseline C versus Baseline B | done | 2026-11-07 |
| 7.11 | Write property test for baselines growing with users | done | 2026-11-07 |
| 7.12 | Implement the TCO_Engine | done | 2026-11-07 |
| 7.13 | Implement Baselines A–D | done | 2026-11-07 |
| 7.14 | Implement `project_tco` and the View 2 cost table | done | 2026-11-07 |
| 7.15 | Update progress.md (Task Status, Current Status, Changelog, Next Step, Next Session Prompt for the next task) and run the verification command | done | 2026-11-07 |
| 8 | Stitch web foundation, FastAPI boundary and size/TCO vertical slice | in-progress | |
| 8.1 | Export canonical Stitch assets and record a screen manifest and design tokens | done | 2026-11-08 |
| 8.2 | Write failing API parity, error and web interaction tests | done | 2026-11-08 |
| 8.3 | Implement FastAPI catalog, default-workload, size and TCO endpoints with OpenAPI types | done | 2026-11-08 |
| 8.4 | Implement React shell, scenario controls and real memory/TCO panels matching Stitch | done | 2026-11-08 |
| 8.5 | Implement root npm run dev orchestration and frontend type/build/component/browser checks | done | 2026-11-08 |
| 8.6 | Run browser reference comparisons, verify Python and web checks, update progress and next prompt | in-progress | |
| 9 | Decision engine (SAW), use cases, presets and Normal-mode web recommendations | in-progress | |
| 9.1 | Write failing candidate, filter, quality, SAW and service tests | done | 2026-11-08 |
| 9.2 | Implement quality resolution, candidate enumeration and all hard filters | done | 2026-11-08 |
| 9.3 | Implement criterion normalization, ranking and explanations | done | 2026-11-08 |
| 9.4 | Expose recommend/evaluate through FastAPI and generate client types | done | 2026-11-08 |
| 9.5 | Build the Stitch ranking tab and Normal-mode flow with real result states | done | 2026-11-08 |
| 9.6 | Verify Python/API/frontend/browser checks and update progress | in-progress | |
| 10 | TOPSIS, Expert web controls and FX override | in-progress | |
| 10.1 | Write failing TOPSIS and Expert interaction tests | done | 2026-11-08 |
| 10.2 | Implement TOPSIS and service/API pass-through | done | 2026-11-08 |
| 10.3 | Implement Expert panels, weights and validated FX inputs | done | 2026-11-08 |
| 10.4 | Verify mode transitions, stale-response handling and currency invariants | done | 2026-11-08 |
| 10.5 | Run all applicable checks and update progress | in-progress | |
| 11 | Web KPI ribbon, chart semantics, responsive themes and accessibility | not-started | |
| 11.1 | Write interaction tests for KPI, theme, missing-data and currency states | not-started | |
| 11.2 | Complete shared KPI and display formatting components | not-started | |
| 11.3 | Complete chart styles and independent simulator state | not-started | |
| 11.4 | Verify responsive layout, keyboard access, contrast and loading/empty/error states against Stitch | not-started | |
| 11.5 | Record browser evidence and update progress | not-started | |
| 12 | Web audit drawer and JSON/CSV export | not-started | |
| 12.1 | Write failing audit-selection, source and export round-trip tests | not-started | |
| 12.2 | Implement audit result transport and drawer contents | not-started | |
| 12.3 | Implement JSON and display-currency CSV ZIP exports | not-started | |
| 12.4 | Verify browser downloads, empty states and selected-candidate behavior | not-started | |
| 12.5 | Run checks and update progress | not-started | |
| 13 | Web cutover, concurrency, performance, CI and documentation | not-started | |
| 13.1 | Write concurrency, performance, launcher and build/serving tests | not-started | |
| 13.2 | Add combined Python/API/frontend/browser verification and CI | not-started | |
| 13.3 | Separate numeric tests from legacy UI tests and retire Streamlit adapter/config/dependency | not-started | |
| 13.4 | Finalize same-origin production serving, launchers, README and extension seams | not-started | |
| 13.5 | Run clean-checkout and visual acceptance checks; update progress with the remaining numerical-validation backlog | not-started | |

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
| 2026-11-07 | Input and output contracts for the Baseline and Decision engines (`ApiCost`, `BaselineD`, `RentalCost`, `HybridCost`, `CandidateSet`, `FilteredCandidates`, `RankingResult` and their `*Input`s) are defined now as first drafts | The Modify lists of Tasks 7 to 9 do not include `src/ai_tco_dss/domain/`, and Req 7.1 needs every engine input and output to be a contract; a later field change must be recorded as a scope deviation | 7.1, Tasks 7, 8, 9 |
| 2026-11-07 | `IsoDate` accepts only `date` objects and `YYYY-MM-DD` strings | Pydantic lax mode would accept integers as Unix timestamps; Req 40.5 requires rejecting non-ISO dates | 8.3, 40.5 |
| 2026-11-07 | Defaults live in `settings.Settings`; bounds live in the `EngineParameters` contract. `load_engine_parameters` turns the first violation into `ConfigurationError(setting, value)` | One place for defaults and one for bounds (design D-05) | 9.10, Task 2.6 |
| 2026-11-07 | `PresetSpec` has an `accessed` field | `presets.json` in design.md "JSON file formats" carries `accessed`, which `extra="forbid"` would otherwise reject | 32.1, Task 2.6 |
| 2026-11-07 | Result contracts keep the spec 04 defaults (`oom_reason=None`, `context_eviction_risk=False`, `thunderbolt_mesh_cables=0`, etc.) | Avoids default deviations that serve no purpose (Req 7.7) | 7.7, Task 2.7 |
| 2026-11-07 | `SizeRequest.nodes` is a float with default 1.0; `CatalogOverview` uses `CatalogItem(id, label)` and `FxInfo(rate, source_id, rate_date, is_override)` | Non-integer node counts must reach the Req 18.7 engine check; design.md leaves the overview field types open | 18.7, 6.1, Task 2.7 |
| 2026-11-07 | Enums use `StrEnum` with the spec 04 member names and values | Same values as `(str, Enum)`; ruff UP042 prefers `StrEnum` | 7.7 |
| 2026-11-07 | Process note: the Task 2 tests were first run after `base`, `enums`, `errors` and `money` were already written. They still failed at import because no contract, settings or export code existed | Recorded for transparency (Project Rule 2) | 41.1, Task 2 |
| 2026-11-07 | The `data/` seed subset equals the test fixture `tests/fixtures/catalog_min/`: `mac-studio-m5-max-128gb`, `rtx-pro-6000-96gb`, `qwen-3-8-27b` and `claude-sonnet-5-5` (the reference API model that `baselines.json` must name). Unverified spec 03 numbers carry source `SPEC-03` with tier `assumption` | Task 3 adds no web-verified data; Task 4 replaces these values | 3.11, 8.3, Task 4 |
| 2026-11-07 | New registry entries: `SPEC-01`, `SPEC-02`, `SPEC-03` (tier `assumption`), `ECB-FX`, `HETZNER-GEX63`, `HETZNER-GEX430` (tier `official`). IND tiers by publisher type: IND-01, IND-02, IND-05 `third_party`; IND-03, IND-04, IND-06 to IND-09 `official`; IND-10 `community` | Req 8.2 rule; Task 4 re-checks it in its tests | 8.1, 8.2 |
| 2026-11-07 | The start page shows "Catalog: H hardware, M models, R rentals" plus the FX rate and source | Task 4's demo expects the rental count, and Task 4 may not modify `ui/` | 6.1, Task 4 |
| 2026-11-07 | The loader reports at most one error per (file, field path); the first, most specific message wins. A duplicate id is reported once, on the first file, and names every file | Avoids two lines for one fault (e.g. provenance and contract both rejecting an invalid tier) | 11.4, 11.5 |
| 2026-11-07 | `load_workload(path)` with a non-default path raises `NotImplementedError` until Task 5 | Task 5 owns `load_workload` (Req 14.7) | 14.7, Task 5 |
| 2026-11-07 | The GEX430 setup fee (EUR 3,599) and the rental system RAM values carry `ASSUMPTION-MVP` until Task 4 verifies them; `popularity.json` has an empty assumption snapshot | No verified source yet | 10.6, 32.6, Task 4 |
| 2026-11-07 | The optional property tests 3.5 to 3.7 (Properties 2, 3, 5) were written | Leaving them `not-started` would make them the next step in tasks.md order | 3.5, 3.6, 3.7 |
| 2026-11-07 | Added `run.bat`, `run.sh` and `.gitattributes` (LF for `*.sh`, CRLF for `*.bat`) outside any Task_Scope, at the user's explicit request. The scripts check for uv, run `uv sync --locked`, start Streamlit headless on port 8501 (which skips the first-run e-mail prompt) and open the browser. README is unchanged, so it still documents exactly one Dashboard command | One-click start for the thesis author; Req 6.3 limits README to one Dashboard command | 6.3, 6.4 |
| 2026-11-07 | Streamlit agent skill `developing-with-streamlit` installed (`uv run streamlit skills --yes`; global fallback to `~/.agents/skills` and `~/.claude/skills`, copied to `~/.kiro/skills`). At the user's request it is now mandatory before any Streamlit code change: new steering file `.kiro/steering/streamlit-ui.md` (`inclusion: always`), a non-numbered note appended to `CLAUDE.md` (existing lines and the eight rules unchanged), a "Streamlit skill" convention in `tasks.md` § "Overview", and two lines in the Next Session Prompt | The skill supplies reference docs matched to the installed Streamlit 1.67.0 for Tasks 5 to 12 (fragments, AppTest, caching, layout) | 5.2 (unchanged), 37.5, 37.6, Tasks 5 to 12 |
| 2026-11-07 | MVP completeness rules run only when `load_catalog(..., mvp=True)`; the Validate_CLI sets it automatically for the repository `data/` root (`--mvp` / `--no-mvp` override). `JsonCatalogRepository` keeps `mvp=False` | The fixture catalog must still validate (task 4.4); adding or removing catalog files must not stop the Dashboard (Req 11.2) | 10.11, 11.2 |
| 2026-11-07 | Quality scores outside [0, 100] are always errors; a score of 0 is an error in MVP mode | Req 10.8: an unavailable score stays absent instead of 0 | 10.8 |
| 2026-11-07 | Preset and popularity checks are the pure functions `loading.preset_violations` and `loading.popularity_violations`, also used by the Property 52 test | One rule implementation for the CLI and the property test | 32.8 |
| 2026-11-07 | Model ids: `gemma-4-12b`, `qwen-3-8-27b`, `qwen-3-6-35b-a3b`, `gpt-oss-120b`, `qwen-3-8-flash-next`, `glm-5-3-flash`, `deepseek-v4-1-flash`, `kimi-k3-1-pro`, `claude-opus-5-5`, `claude-sonnet-5-5`, `gpt-6-1` (GPT-6.1 Sol, the $2/$10 model of spec 03), `gemini-3-1-pro` (Gemini 3.1 Pro Preview). Hardware ids follow spec 03 §2 | Stable ids for later tasks | 10.1, 10.3, 10.4 |
| 2026-11-07 | `calibrated_weights_gb`: INT2/INT3/INT4/INT8 = Unsloth UD-Q2_K_XL / UD-Q3_K_XL / UD-Q4_K_XL / Q8_0 | This mapping reproduces the 111.3 GB Flash Next INT4 reference of Req 16.6 (ledger C-028) | 17.1, 16.6 |
| 2026-11-07 | `terminal_bench` = vendor-reported Terminal-Bench 2.x, `swe_bench` = SWE-bench Pro; frontier models report only Terminal-Bench 4.0 and use the scaled AA fallback | Scores of different benchmark versions are not comparable (ledger C-029) | 31.2, 31.4 |
| 2026-11-07 | Custom open-weights licenses (Qwen Community License 1.0, Kimi K3.1-Pro License) are stored as `MIT`; DGX Spark is stored as `discrete` memory | `LicenseType` and `MemoryArchitecture` lack fitting members and `domain/` is outside the Task 4 scope; contract change proposals in ledger C-015, C-017, C-024 | 10.7, 16.4, 19.2 |
| 2026-11-07 | Extra EU rentals (user request): only offers that map to a catalog GPU and one of its valid node counts are added; hourly prices × 730 h; USD prices stay USD | RentalSpec sizes a rental as `gpu_count` nodes of `gpu_hardware_id` (ledger C-031) | 13.5, 25.1 |
| 2026-11-07 | Baseline A default plan `claude-ultra` ($200); `claude-max` ($100) added | Anthropic renamed its plans (ledger C-018) | 24.1 |
| 2026-11-07 | `SizingResult` memory values (`usable_memory_gb`, `usable_memory_default_gb`, `kv_pool_gb`, `os_reserved`) cover all effective nodes. `usable_system_ram_gb` is the installed system RAM × N for discrete hardware and `None` for unified memory; the eviction check of unified hardware uses the per-node usable memory (design step 8). The View 1 chart draws a system RAM line only when the value is not `None` | Req 35.1 omits the line for hardware without a separate system RAM value; the chart takes only `SizeResult` | 17.11, 18.3, 35.1 |
| 2026-11-07 | Tiered-offload appliances: the Shelf takes the weights first, weights on device = max(0, weights − N × `system_ram_offload_gb`) | The design formula made every offloaded model OOM (ledger C-034) | 18.6 |
| 2026-11-07 | Infeasibility reasons (node count not valid, weight capacity exceeded, OOM shortfall) are joined with "; " in `oom_reason`; `U_max` is still computed when only the node count is invalid | `SizingResult` has one reason field; Req 18.8 needs a recorded reason | 17.6, 18.8 |
| 2026-11-07 | `size_deployment` rejects `commercial-api` models with `EngineInputError` naming the model id; the View 1 card shows the error as a warning and keeps the other pairings | API models have no weights to size; `CatalogOverview` lists all models | 38.2 |
| 2026-11-07 | New Service_Layer function `load_workload(path=None, *, repo=None)`; repositories share `read_workload_file(path)`. Missing or unparseable files raise `WorkloadFileError(path, ())`; validation failures list every field path (e.g. `profile.active_users`) | Req 14.3 and 14.7 address the Service_Layer; the Dashboard needs the default workload without importing `catalog` | 14.3, 14.7, 37.7 |
| 2026-11-07 | `size` returns `performance=None` and `aa_index_v5=None` until Task 6 | Task 5 demo: "AA labels show n/a until Task 6"; the measured-first resolver is Task 6 | 35.9, Task 6 |
| 2026-11-07 | The memory-fit card also has a Nodes control (1, 2, 4, 8; default 1) besides the inputs listed in design.md | H100 has valid node count {8} only and would always show infeasible at 1 node | 18.1, 35.1 |
| 2026-11-07 | View 1 uses Plotly although the Streamlit skill prefers Vega charts | Req 35.8 requires Plotly figure factories; Req 35.3 needs bar hatch patterns | 35.3, 35.8 |
| 2026-11-07 | Engine purity AST test: `engines/` may import `ai_tco_dss.domain` and `ai_tco_dss.engines`; `decision/` may also import `ai_tco_dss.decision` and the engines. `engines/__init__.py` uses a tuple `__all__` | Package `__init__` re-exports and the decision layer calling pure engines do not break Req 38.2 | 38.2 |
| 2026-11-07 | The optional property tests 5.5, 5.7 to 5.11 and 5.13 to 5.15 (Properties 9, 11 to 15, 17, 18, 54) were written | Same reason as for Tasks 3 and 4 | 5.5 to 5.15 |
| 2026-11-07 | `load_engine_parameters` also rejects δ_ctx breakpoints that are empty, not increasing in context or increasing in factor (`ConfigurationError("delta_ctx_breakpoints", value)`); `delta_ctx` (in `engines/performance.py`, engines may not import `settings`) interpolates linearly in log2(context), returns the first factor at or below the first breakpoint and the last factor above the last | Req 20.6 curve shape must hold for any configured breakpoints | 20.6 |
| 2026-11-07 | The decode formula inputs (bandwidth, `P_active`, bits, speculative mode) are validated even when a measured record matches | Req 20.7 rejects the combination; an invalid catalog item should not hide behind a measurement | 20.7 |
| 2026-11-07 | TTFT carries the origin of the prefill value it used (measured prefill record → TTFT `measured`); a matching `ttft_s` record replaces the formula TTFT as is (no eviction or cache adjustment) | Req 21.2 and 9.4 | 9.4, 21.2 |
| 2026-11-07 | Effective TPS uses `T_out × μ = out_think / τ` (no tokenizer inflation) and is clamped to decode TPS against rounding | design.md Performance_Engine and Req 21.4; Property 23 needs effective ≤ decode exactly | 21.4, 21.6 |
| 2026-11-07 | When no prefill value exists (21.7), the 1M-token prefill time is also not available even if `prefill_tps_at_1m` exists; measured speed values ≤ 0 raise `EngineInputError` | Literal Req 21.7; avoids division by zero | 21.5, 21.7 |
| 2026-11-07 | API performance (`compute_api_performance`) labels catalog `api_decode_tps` / `api_ttft_s` as `measured` with their source_id; all MVP API models have neither, so all values are `None` | Published third-party measurements; Req 29.12 treats missing values as missing criteria | 9.7, 29.12 |
| 2026-11-07 | `size` computes performance only for feasible pairings; the per-pair `BenchmarkSet` holds the records of the (model, hardware) pair; the AA v5 score is resolved for every pairing | design.md Service Layer and "Engine call convention" | 9.9, 21.1, 35.9 |
| 2026-11-07 | Calibration formula values use one node, `WorkloadProfile()` defaults and `SizingOptions` with the record's precision and context (defaults INT4 and 128,000 when absent); an infeasible sizing does not stop the comparison. The known-deviation key is (metric, model_id, hardware_id, source_id), so one ledger row can cover several contexts of one source | `BenchmarkRecord` has no node count or speculative mode | 42.1, 42.3 |
| 2026-11-07 | Calibration_Report prints measured, formula and APE with one decimal and MAPE with one decimal (`n/a` when no record); the CSV has one `summary` row per metric and one row per top-list record with the same strings; skipped records are printed with their reasons | Req 42.4, 42.5 ("same values and same rounding") | 42.4 to 42.7 |
| 2026-11-07 | Benchmark_Records from YouTube sources carry `note: "single-source"` (Validate_CLI rule); record details (assumed context, precision, hardware mapping) are in ledger C-037 instead of the note | The Validate_CLI requires exactly that note for YT values | 8.4, 9.1 |
| 2026-11-07 | The View 1 card shows the five performance values in an `st.table` (value with unit, origin with source_ids) and lists performance warnings under the sizing warnings; the pure helper `performance_rows` builds the table | Streamlit skill: `st.table` for small static tables, `alt=` on tables | 21.1, 21.5, 35.9 |
| 2026-11-07 | The optional property tests 6.4, 6.5, 6.8, 6.10 and 6.11 (Properties 4, 19, 22, 59, 60) were written | Same reason as for Tasks 3 to 5 | 6.4 to 6.11 |
| 2026-11-07 | `reports/.gitkeep` created; `.gitignore` already ignored `reports/*` except `.gitkeep`, so it is unchanged; `services/__init__.py` is unchanged (`calibration_report` is a CLI module, not a Service_Layer function) | No change needed | 42.5 |
| 2026-11-07 | TCO_Engine validation raises `EngineInputError` at the first out-of-range field (Req 22.12) and checks `currency == "USD"` on street price, cabling kits, the selected tariff and the selected, Munich and Romania hubs (field `<name>.currency`, Req 22.14). The Munich and Romania hubs must exist even when another hub is selected (Req 22.10) | One named field per error, as in the other engines | 22.10, 22.12, 22.14 |
| 2026-11-07 | `cost_60m = CapEx + 60 × monthly OpEx − resale(60)`, resale only when `include_resale_value` is true; `resale_value(capex, r, m)` is a public helper for Task 8 | Spec 02 §2.7 at m = 60; Req 26.4 default false | 22.9, 22.11, 26.4 |
| 2026-11-07 | Utilization helper `classify_utilization(u, demand, capacity, params)` returns (threshold flag, capacity-insufficient, warnings) for a defined Utilization; undefined Utilization (infeasible sizing, no decode TPS, capacity 0) gives threshold false, capacity-insufficient true and one "capacity could not be determined" warning | Exact boundaries 0.55 / 0.70 / 1.0 are testable without floating-point construction of a deployment | 23.5 to 23.8 |
| 2026-11-07 | Capacity formula fallback (design D-07) without `base_prefill_tps_at_32k` uses no compute cap; the capacity origin lists the decode, prefill and advertised-memory source_ids; a measured `aggregate_tps` record is multiplied by `units` for per-seat workstations | design.md TCO_Engine; one record measures one machine | 23.3, 23.4 |
| 2026-11-07 | The target context of the TCO_Engine is derived from the sizing result, the eviction wait time uses the prefill rate without β, and Baseline C omits the gateway-fee source id | `TcoInput` and the baseline inputs lack the fields and `domain/` is outside the Task 7 scope (ledger C-039, C-040) | 22.8, 23.3, 24.11 |
| 2026-11-07 | Baseline_Engine validation collects every offending field into one `EngineInputError` (`field` = comma-separated names: `input_per_1m`, `output_per_1m`, `cache_read_per_1m`, `gateway_fee_usd`, `r_cache`, `r_batch`, `thinking_multiplier` = out_think / T̂_out, `kappa_mega`, `nu_verify`, `active_hours_per_month`, `price_per_seat_month`); non-USD prices count as invalid. Baseline D is unavailable with a reason when the candidate is infeasible, has no effective TPS, has undefined Utilization or has no open-weights price | Req 24.10 names each field; Req 24.6 | 24.6, 24.10 |
| 2026-11-07 | `project_tco` accepts only on-premise ids `onprem:{hw}:{n}x:{model}:{precision}` (malformed ids and bad precisions raise `EngineInputError`, unknown hardware or models `UnknownIdentifierError`); baselines use `reference_api_model_id` or the catalog default and `subscription_plan_id` or the default plan; `cloud_ttft_s` = the reference API model's `api_ttft_s` (None in the MVP catalog). `quality`, `risk` and `popularity` are placeholders (`None`, 0.0, 0.0) with a note until Task 9; `archetype` follows the deployment mode | Candidate generation and the Decision_Engine are Task 9; the timeline is Task 8 | 13.7, 38.8, Task 8, Task 9 |
| 2026-11-07 | `size` and `project_tco` share the private helper `_deployment` (workload, sizing, performance) | Same pipeline for View 1 and View 2 | 38.1 |
| 2026-11-07 | The View 2 card composes the candidate id from hardware, nodes (1, 2, 4, 8), model and precision selectors (defaults RTX Pro 6000 × 4, gpt-oss-120b, INT4) plus a staffing-hub selectbox (default `ro-cluj-bucharest`), and shows the cost table with `st.table` (`tco_cost_rows`: Item, Value, Origin) and the TCO warnings. Values are USD; display currency is Task 11. Baseline A shows `[NON-COMPLIANT / BLOCKED]` with the reasons when ineligible | No candidate list exists before Task 9; `CatalogOverview` lacks model type and valid node counts, so API models or invalid node counts show a warning instead of a table | 34.3, 37.5, 37.6 |
| 2026-11-07 | Formula traces and labels use ASCII `*`, `-` and `x` instead of `×` and `−` | Ruff RUF001–RUF003 reject ambiguous Unicode; `pyproject.toml` is outside the Task 7 scope | 2.3 |
| 2026-11-07 | The AppTest check of the View 2 card (render count, cost table, hub change) lives in `tests/unit/test_tco.py` | `tests/integration/test_app_smoke.py` is outside the Task 7 scope | 37.6 |
| 2026-11-07 | The optional property tests 7.4, 7.5, 7.7, 7.8 and 7.9 (Properties 24, 25, 27, 28, 29) were written | Same reason as for Tasks 3 to 6 | 7.4 to 7.9 |

| 2026-11-07 | User prioritizes functional MVP before numerical refinement; Task 8 includes the Stitch-inspired wide chart/cost layout and light/dark theme, with scope extended to config, app, design reference and smoke tests | Stitch project 12247395809959632226 is a visual reference; existing contracts and ledger styles define behavior. See specs/08_MVP_DESIGN_REFERENCE.md for the agreed sequence | Task 8, Tasks 9-13 |

| 2026-11-07 | Replace Streamlit with React/TypeScript, Vite, Tailwind and shadcn/ui; use FastAPI over existing Python services. Promote Stitch fidelity to browser-verified acceptance; root npm run dev will start both processes | Author rejected the Streamlit approximation and accepted extra implementation work. Requirement 43 and specs/09_WEB_FRONTEND_MIGRATION.md supersede delivery-specific legacy instructions. Prior backend implementation remains reusable | Revised Tasks 8-13, Req 43 |

| 2026-11-08 | Task 8 adds Python scenario-default/validation and options metadata endpoints, editable shadcn primitives and a direct .venv process launcher | Defaults/valid node counts stay in Python; Vite proxies a stateless API; launcher cleanup is tested without depending on shell activation | 43.1, 43.2, 43.5, 43.7, 43.9 |
| 2026-11-08 | Historical relocation checks allow only the exact approved migration amendments; full Task 8 status stays in progress for missing thesis documents | Preserve original domain text and existing unrelated tests; prompt-order test follows the user/Project Rule 1 progress-first instruction; Project Rule 8 still requires a zero-failure full suite | 1.10, 41.2, Task 8.6 |

| 2026-11-08 | Task 9 resolves hybrid filtering using explicit component results/context/endpoint facts; rental server RAM is converted to a per-node sizing input. Scope extends to domain/results.py and generated result schemas, as required by the user's contract-gap instruction | Weighted averages cannot prove component feasibility; sizing multiplies host RAM by nodes. Recursive property generation now exercises nested component round trips without reducing assertions | C-042, C-043; Req 27-29, 38, 43 |
| 2026-11-08 | Ranking is the initial tab; Normal changes use Python defaults plus only use case/users/preset, with SAW preset weights. Shared KPIs now reference rank 1 rather than the independent TCO simulator | Real recommendation workflow; preserve simulator independence. Full Expert controls, TOPSIS and final KPI polish remain later tasks | Req 33, 34; Tasks 9-11 |

| 2026-11-08 | Task 10 proceeds despite the unrelated completion gate under explicit user authorization; Tasks 8-10 retain administrative in-progress status until the full suite has zero failures | The user supersedes the old Task 9 stopping point without weakening thesis tests or changing Project Rule 8 | Task 10, 41.2 |
| 2026-11-08 | Expert preset weights come from Python `/options`; drafts require Apply, validation requests cancel on edits/mode switches, and entry initializes preset weights plus SAW | No duplicated weight constants or stale validation commits; Normal always restores Python defaults except use case/users/preset | 30.1, 33.2-5, 43.5-7 |
| 2026-11-08 | Expert quantization selects KV precision for candidate sizing; ranking still enumerates all supported weight precisions, and independent simulator panels retain their weight selectors | Preserve Req 27's candidate set rather than introducing an unspecified precision filter | 27.2, 33.3 |
| 2026-11-08 | TOPSIS retains SAW criterion contributions with explicit comparison labels; each retained TCO projection uses the FX rate from its successful request | Avoid presenting SAW contributions as TOPSIS distances or revaluing stale USD costs at a newer FX rate | 12.4, 30.2-4, 43.7 |

## Changelog
| Date | Task | Files created or modified |
|---|---|---|
| 2026-11-07 | 1 | created: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `scripts/verify.py`, `scripts/relocate_specs.py`, `.kiro/steering/project-rules.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `src/ai_tco_dss/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/{domain,catalog,engines,decision,services,ui}/__init__.py`, `src/ai_tco_dss/ui/app.py`, `tests/conftest.py`, `tests/unit/test_repository_layout.py`, `tests/unit/test_toolchain.py`, `tests/unit/test_session_artefacts.py`, `tests/unit/test_relocate_specs.py`, `tests/unit/test_offline_guard.py`, `tests/integration/test_app_smoke.py`; modified: `README.md` (commands), `CLAUDE.md` (appended `## Project Rules`) |
| 2026-11-07 | 2 | created: `src/ai_tco_dss/domain/{base,enums,errors,money,catalog,scenario,results,inputs,requests,export_schemas}.py`, `schemas/*.json` (8 files), `tests/unit/test_contracts.py`, `tests/unit/test_schema_export.py`, `tests/property/strategies.py`, `tests/property/test_contract_props.py`; modified: `src/ai_tco_dss/domain/__init__.py`, `src/ai_tco_dss/settings.py`, `pyproject.toml` (console script `ai-tco-schemas`), `uv.lock`, `specs/07_DATA_CORRECTIONS.md` (Contract Deviations), `progress.md` |
| 2026-11-07 | 3 | created: `src/ai_tco_dss/catalog/{loading,fx,repository,json_repository,memory_repository,validate}.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/state.py`, `data/sources.json`, `data/catalog/README.md`, `data/catalog/hardware/{mac-studio-m5-max-128gb,rtx-pro-6000-96gb}.json`, `data/catalog/models/{qwen-3-8-27b,claude-sonnet-5-5}.json`, `data/benchmarks/quality.json`, `data/reference/{fx,electricity,staffing_hubs,harnesses,use_cases,rentals,presets,popularity,baselines}.json`, `data/workloads/default.json`, `tests/fixtures/catalog_min/**`, `tests/unit/test_validate_cli.py`, `tests/unit/test_repository.py`, `tests/unit/test_import_boundaries.py`, `tests/property/test_catalog_props.py`; modified: `src/ai_tco_dss/catalog/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/ui/app.py`, `pyproject.toml` (console script `ai-tco-validate`), `README.md` (validate command), `specs/07_DATA_CORRECTIONS.md` (C-016), `tests/unit/test_repository_layout.py`, `tests/integration/test_app_smoke.py`, `progress.md` |
| 2026-11-07 | 4 | created: `data/catalog/hardware/{rtx-5060-ti-16gb,rtx-5070-strata-64gb,mac-mini-m5-pro-64gb,mac-studio-m5-ultra-256gb,amd-strix-halo-128gb,dgx-spark-128gb,h100-80gb-sxm}.json`, `data/catalog/models/{gemma-4-12b,qwen-3-6-35b-a3b,gpt-oss-120b,qwen-3-8-flash-next,glm-5-3-flash,deepseek-v4-1-flash,kimi-k3-1-pro,claude-opus-5-5,gpt-6-1,gemini-3-1-pro}.json`, `tests/unit/test_mvp_catalog.py`, `tests/unit/test_reference_data.py`, `tests/property/test_preset_validator_props.py`; modified: `data/sources.json`, `data/catalog/hardware/{mac-studio-m5-max-128gb,rtx-pro-6000-96gb}.json`, `data/catalog/models/{qwen-3-8-27b,claude-sonnet-5-5}.json`, `data/benchmarks/quality.json`, `data/reference/{fx,electricity,staffing_hubs,rentals,popularity,baselines}.json`, `src/ai_tco_dss/catalog/loading.py`, `src/ai_tco_dss/catalog/validate.py`, `specs/07_DATA_CORRECTIONS.md` (C-001 to C-003, C-010, C-013 to C-016 updated; C-017 to C-033 added; Assumptions rows), `progress.md` |
| 2026-11-07 | 5 | created: `src/ai_tco_dss/engines/workload.py`, `src/ai_tco_dss/engines/sizing.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/theme.py`, `tests/unit/test_workload.py`, `tests/unit/test_sizing.py`, `tests/unit/test_engine_purity.py`, `tests/unit/test_charts.py`, `tests/property/test_workload_props.py`, `tests/property/test_sizing_props.py`, `tests/property/test_ui_props.py`; modified: `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/catalog/json_repository.py`, `src/ai_tco_dss/catalog/memory_repository.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md` (C-034), `progress.md` |
| 2026-11-07 | 6 | created: `src/ai_tco_dss/engines/resolver.py`, `src/ai_tco_dss/engines/performance.py`, `src/ai_tco_dss/services/calibration_report.py`, `data/benchmarks/decode.json`, `data/benchmarks/prefill.json`, `reports/.gitkeep`, `tests/unit/test_performance.py`, `tests/unit/test_settings.py`, `tests/unit/test_calibration_report.py`, `tests/calibration/test_calibration.py`, `tests/property/test_performance_props.py`, `tests/property/test_calibration_props.py`; modified: `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/settings.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `pyproject.toml` (console script `ai-tco-calibrate`), `README.md` (calibration command), `specs/07_DATA_CORRECTIONS.md` (C-035 to C-037, Calibration Known Deviations, Assumptions rows), `progress.md` |
| 2026-11-07 | 7 | created: `src/ai_tco_dss/engines/tco.py`, `src/ai_tco_dss/engines/baselines.py`, `src/ai_tco_dss/ui/formatting.py`, `tests/unit/test_tco.py`, `tests/unit/test_baselines.py`, `tests/property/test_tco_props.py`, `tests/property/test_baseline_props.py`, `tests/integration/test_service_validation.py`; modified: `src/ai_tco_dss/engines/__init__.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/cards.py`, `src/ai_tco_dss/ui/app.py`, `specs/07_DATA_CORRECTIONS.md` (C-038 to C-040, Assumptions rows), `progress.md` |

| 2026-11-07 | 8 | Added rental/hybrid/timeline engines, service orchestration, View 2 chart and controls, `.streamlit/config.toml`, design reference, timeline tests and chart/property/UI regressions; updated the Task 8 scope and Task 7 timeline expectation. Verification pending the unrelated missing thesis documents. |

| 2026-11-07 | 8 | Documentation-only migration planning: updated progress, README, agent/steering rules, MVP requirements/design/tasks, spec router/schema/UX authority notices and Stitch reference; added web migration contract and archived the previous task plan. No application code, dependencies or launch scripts changed. |

| 2026-11-08 | 8 | Implemented frontend/, root npm workspace/lock, scripts/dev.mjs + launcher test, OpenAPI export/type-drift scripts, src/ai_tco_dss/api/, Python dependencies/lock and API/foundation tests; exported all Stitch assets and visual review/comparison under design/stitch/; adapted exact approved-amendment handling in repository-layout tests; updated README, migration/reference docs, tasks and progress. Size/TCO browser slice verified; completion gate remains in progress only for three unrelated missing-thesis test failures. |

| 2026-11-08 | 8 | Author-requested Windows launcher update: run.bat now starts the React UI/API and opens the browser via scripts/dev.mjs --open; README updated. Startup/proxy/cleanup test passes. This explicitly requested launcher change extends the earlier Task 8 file scope to run.bat. |

| 2026-11-08 | 9 | Created decision/{candidates,filters,quality,ranking}.py; added recommend/evaluate orchestration and routes, result filter facts/components, regenerated three JSON schemas and frontend types; created Ranking.tsx, Normal scenario helper, decision/property/API/component/browser tests, recursive strategy support, reviewed screenshots/comparison and frontend/TASK9_REVIEW.md; updated services/API exports, shared app/KPIs/styles, legacy web expectations, ledger and progress. No commit or push. |
| 2026-11-08 | 10 | created: `tests/unit/test_topsis.py`, `frontend/src/components/ExpertControls.tsx`, `frontend/tests/expert.test.tsx`, `frontend/tests/expert.spec.ts`, ten `frontend/tests/expert.spec.ts-snapshots/*.png`, `frontend/TASK10_REVIEW.md`, `frontend/expert-comparison.html`; modified: `src/ai_tco_dss/decision/ranking.py`, `src/ai_tco_dss/api/app.py`, `tests/property/test_decision_props.py`, `frontend/src/{App.tsx,styles.css,lib/scenario.ts,components/Ranking.tsx,api/generated.ts}`, `progress.md`. Existing FX repository/service pass-through is reused and verified; no catalog/schema change or new data contradiction |

## Known Deviations
| Deviation | Ledger entries |
|---|---|
| Rental GPU is RTX PRO 6000 Max-Q; sizing reuses the workstation item | C-009 |
| Multi-node single-stream decode ignores the per-node bandwidth gain of tensor parallelism (Req 20.1 applied literally) | C-011 |
| CSV export delivers one ZIP with two CSV files instead of two downloads | C-012 |
| Recruiting delays are stored as whole months rounded up (8 / 7 / 3 / 4) instead of the spec 03 decimals | C-016 |
| Custom open-weights licenses of Qwen 3.8 Flash Next and Kimi K3.1 Pro are stored as `MIT` (no fitting `LicenseType` member) | C-015, C-017 |
| DGX Spark is sized as `discrete` memory (115.2 GB usable instead of ~118 GB) | C-024 |
| Gemma 4 12B, gpt-oss-120b and Gemini 3.1 Pro have no quality score and fail every Quality_Floor | C-025 |
| Start page shows 6 rentals instead of the 2 of the Task 4 demo (extra EU providers added at the user's request) | C-031 |
| Most hardware street prices stay spec 03 assumptions (not web-verified) | C-032 |
| Tiered-offload KV pool uses a Shelf-first weight placement instead of the design.md step 6 formula | C-034 |
| Decode formula overestimates Qwen 3.8 Flash Next on the M5 Ultra by 50–59 % (calibration xfail) | C-035 |
| Decode formula ignores the offload bandwidth of tiered-offload appliances (DeepSeek on Strata, APE 1,378 %, calibration xfail) | C-036 |
| Benchmark_Records use assumed context (8,192) and precision (INT4) where the source does not state them; multi-node, speculative-decoding and gpt-oss-120b records are not stored; prefill calibration is circular | C-037 |
| The TCO_Engine rejects profiles with more than 730 active hours per month although the Workload_Profile allows 744 | C-038 |
| The TCO_Engine derives the target context from the sizing result; the eviction wait time ignores β_backend | C-039 |
| Baseline C does not list the gateway-fee source id | C-040 |

| Hybrid and on-premise timelines share the resale adjustment to preserve the 100% local boundary | C-041 |
| Hybrid filtering requires explicit component facts and reduced local demand; rental host RAM is a server total | C-042, C-043 |

## Next Step
Task 11 - Web KPI ribbon, chart semantics, responsive themes and accessibility. Task 10 functionality and visual acceptance are complete; Tasks 8-10 retain only the unrelated administrative completion gate. Do not redo their implementation.

## Next Session Prompt
```text
Continue AI TCO DSS at C:\TUM\Thesis\AI_TCO_DSS.

Read progress.md first, then:
1. CLAUDE.md
2. specs/09_WEB_FRONTEND_MIGRATION.md
3. specs/08_MVP_DESIGN_REFERENCE.md
4. .kiro/specs/ai-tco-dss-mvp/requirements.md (12, 34, 35, 37, 43)
5. .kiro/specs/ai-tco-dss-mvp/design.md (Web delivery, Dashboard, chart semantics)
6. .kiro/specs/ai-tco-dss-mvp/tasks.md

Implement Task 11: Web KPI ribbon, chart semantics, responsive themes and accessibility.
Task_Scope:
  Load: `CLAUDE.md` section "Project Rules"; `progress.md` (whole file); `requirements.md` section "Requirement 43: Dedicated Web Frontend and Stitch Fidelity"; `design.md` section "Web delivery architecture (active)"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md`
  Modify: `frontend/`, `src/ai_tco_dss/api/`, `tests/`, `specs/08_MVP_DESIGN_REFERENCE.md`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`
  Verify: uv run python scripts/verify.py

Tasks 1-7 are done. Tasks 8-10 are implemented and browser-verified; do not redo them.
Tasks 8-10 stay administratively in progress under CLAUDE.md's zero-failure gate.
Task 10 was explicitly authorized despite that unrelated gate; its functionality is complete.
Full suite: 713 passed, 3 calibration xfailed, 3 failures solely from missing
thesis/thesis_notes.md and thesis/literature.bib. Do not invent files or weaken tests.
Task 10 focused TOPSIS/property/API/service checks: 34 passed. Frontend checks and
all 38 Chromium checks plus separate launcher checks pass. Review TASK10_REVIEW.md,
frontend/expert-comparison.html, frontend/TASK9_REVIEW.md and design/stitch/TOKENS.md.

Normal uses real Python SAW rankings (36 ranked / 637 rejected by default).
Expert initializes catalog preset weights and SAW; TOPSIS exposes paired ranks,
closeness and distances. Default TOPSIS leader is RTX Pro 6000 x1 + Qwen 3.8 Flash
Next INT2, C=0.758, SAW rank 9. Preserve the shared hard-filtered candidate set.
Expert KV precision applies to sizing; ranking compares all weight precisions.
FX accepts 0.50-2.00 with <=6 decimals; display currency never recomputes results.
Overrides can change USD costs of EUR inputs. Retained TCO keeps its own FX rate.
Preserve C-042 hybrid component/context/endpoint facts and reduced local demand,
and C-043 rental server-total RAM/per-node sizing. Keep calculations in Python.

Task 11 includes five consistent KPIs, monetary rounding/display/chart semantics,
themes, keyboard/contrast/loading/empty/error states and independent simulators.
Run npm typecheck/lint/build/test/types:check and test:browser in both themes at
1280/1440/768/390 CSS px; run test:launcher separately (shared ports 5173/8000).
run.bat and root npm run dev start the web UI/API. Freeze Streamlit work.
Audit/export remains Task 12; production/CI/Streamlit retirement remains Task 13.
Preserve staged and unrelated untracked work, including thesis files, export_bib.py,
.config.kiro and .gitkeep files. Stage only relevant changes. Do not commit or push.
Update progress.md and its next-session prompt after the work.
```
