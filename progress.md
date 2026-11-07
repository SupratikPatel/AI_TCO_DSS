# Progress — AI TCO DSS MVP

## Current Status
Tasks 1 to 7 done (2026-11-07). Task 7 added the TCO_Engine (`engines/tco.py`: `compute_tco`, `resale_value`, `classify_utilization`), the Baseline_Engine for Baselines A–D (`engines/baselines.py`: `api_monthly_cost`, `compute_baselines`, `compute_baseline_d`), the Service_Layer function `project_tco` (on-premise candidate ids `onprem:{hw}:{n}x:{model}:{precision}`, `timeline=None`), `ui/formatting.py` (`viability_badge`, `tco_cost_rows`) and the View 2 tab with the `timeline_card` Simulator_Card (`@st.fragment`, `render_counts["timeline"]`). Demo checked with a headless app through the agent API: RTX Pro 6000 96GB × 4 + gpt-oss-120b INT4 shows CapEx 71,456.00 USD, the six OpEx components (energy 112.66, personnel 3,567.57, NIM 0, capital opportunity 267.96, wait penalty 0, eviction loss 0 USD/month), Utilization 4.7 % with badge `idle capacity warning` (aggregate 2,779 tok/s `formula`), Baselines A 5,000.00 (non-compliant: both reasons), B 4,479.84 and C 5,427.83 USD/month and a compliance tax delta of 427.83 USD; switching the staffing hub to `de-munich-hq` raises personnel OpEx to 6,771.57 USD/month (60-month TCO 308,347 → 500,588 USD). Baselines A/B/C and the delta equal the design.md reference values (the catalog still has the spec 03 Sonnet prices $2 / $0.10 / $10). The full suite has 615 passing tests and 3 xfailed; `ai-tco-validate` reports 0 errors. Files are staged with `git add`, not committed. Task 8 (EU rental, hybrid split, 60-month timeline and View 2 chart) is next.

Open points for the author from Task 7: Req 22.3 limits H_active to 730 h while the Workload_Profile allows 744 h, so profiles above 730 h get no on-premise TCO (C-038, requirement change proposal). `TcoInput` lacks `SizingOptions`, so the target context is derived from the sizing result and the eviction wait time ignores β_backend (C-039); Baseline C does not list the gateway-fee source id because the baseline inputs carry the fee as a float (C-040); both have contract change proposals. No hardware item has a cabling kit, so multi-node CapEx has no switch cost. `project_tco` fills `quality=None`, `risk=0.0` and `popularity=0.0` with a note until the Decision_Engine of Task 9 computes them. During the demo one cold server start logged a plotly/pandas "partially initialized module" error in the unchanged View 1 chart; it did not reproduce on a second cold start or in three fresh sessions.

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

## Next Step
Task 8 — EU rental, hybrid split, 60-month timeline and View 2 chart

## Next Session Prompt
```text
You are continuing the AI TCO DSS MVP (TUM thesis, Python 3.12, uv). Read these files first, in order:
1. CLAUDE.md
2. progress.md
3. .kiro/specs/ai-tco-dss-mvp/requirements.md
4. .kiro/specs/ai-tco-dss-mvp/design.md
5. .kiro/specs/ai-tco-dss-mvp/tasks.md
Then execute task 8 "EU rental, hybrid split, 60-month timeline and View 2 chart" from tasks.md, and only that task.
Task_Scope (identical to tasks.md):
  Load: `CLAUDE.md` § "Project Rules"; `progress.md` (whole file); `requirements.md` § "Requirement 25: EU Dedicated Rental and Hybrid Split", § "Requirement 26: 60-Month Timeline and Break-Even", § "Requirement 35: Views 1 and 2", § "Requirement 37: Visual Accessibility and UI Architecture"; `design.md` § "Key Design Decisions", § "Baseline_Engine (`engines/baselines.py`)", § "Service Layer (`services/`)", § "Dashboard (`ui/`)", § "Okabe-Ito archetype mapping (`ui/theme.py`, ledger entry C-004)", § "Correctness Properties" › "Baselines, rental, hybrid and timeline" and "Dashboard and export"; `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` § "Baseline C: EU-Sovereign Metered Enterprise API & Dedicated EU Cloud Rental", § "2.7 Sovereign On-Premise 60-Month TCO Integration Formula"; `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` § "2.2 Semantic, Colorblind-Safe Financial Palette (Okabe-Ito / IBCS Aligned)", § "3. The Six Interactive Plotly Views (`src/ui/charts.py`)"; `src/ai_tco_dss/engines/`; `src/ai_tco_dss/services/`; `src/ai_tco_dss/ui/`
  Modify: `src/ai_tco_dss/engines/baselines.py`, `src/ai_tco_dss/services/__init__.py`, `src/ai_tco_dss/services/scenario_service.py`, `src/ai_tco_dss/ui/charts.py`, `src/ai_tco_dss/ui/theme.py`, `src/ai_tco_dss/ui/cards.py`, `specs/07_DATA_CORRECTIONS.md`, `progress.md`, `tests/unit/test_timeline.py`, `tests/unit/test_charts.py`, `tests/property/test_baseline_props.py`, `tests/property/test_ui_props.py`
  Verify: uv run python scripts/verify.py tests/unit/test_timeline.py tests/unit/test_charts.py tests/property/test_baseline_props.py tests/property/test_ui_props.py
Work test-first, change only Task_Scope files, run the task's verification command (it must exit 0),
then update progress.md (Task Status, Current Status, Changelog, Next Step) and rewrite
this prompt for the next not-started task before reporting completion.
Stage changed files with git add; do not commit or push.
Before creating or changing any Streamlit code (src/ai_tco_dss/ui/ or AppTest tests),
activate the developing-with-streamlit skill (see .kiro/steering/streamlit-ui.md).
```
