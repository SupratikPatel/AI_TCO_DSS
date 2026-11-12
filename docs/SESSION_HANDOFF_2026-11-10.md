# Paused session handoff - 2026-11-10

**Historical checkpoint:** the authoritative restart instructions are now in
[SESSION_HANDOFF_2026-11-11.md](SESSION_HANDOFF_2026-11-11.md). Its current U-02 starting
point and completed U-09 verification supersede older instructions on this page.

**Latest 2026-11-11 continuation:** C-058 query-output and calibration-applicability guards are fixed; engine 0.1.3. Final single combined verifier native exit 0: 826 Python passed, 13 skipped, 3 historical xfails; 31 frontend tests; 71 browser checks without snapshot updates; 3 launcher checks. See .calibration-followup-final.log/.calibration-followup-final-exit.json. U-09 complete for this snapshot; U-02 through U-06 remain empirically/modeling-unfinished. New docs/ONE_USER_SENSITIVITY_AND_API_COVERAGE.md plus 11 exact saved scenarios distinguish quantization, latency/agent sensitivity, missing API data and the unresolved peak-load/queueing boundary. Dev server restored directly with node scripts/dev.mjs, session 26682/API PID 10320 at observation; health ok and frontend 200. Reinspect current state, do not assume PIDs. No browser tab controlled. All relevant changes staged, no commit/push. Resume from progress.md; historical statements below are checkpoints superseded by the latest status.

**2026-11-11 resume:** U-01 is complete: policy/fixes and final full Python verification (819 passed, 13 skipped, 3 xfailed, exit 0) are saved in progress.md/.u01-python.log. The authoritative current matching policy is docs/BENCHMARK_MATCHING_POLICY.md (C-057), superseding this historical checkpoint's universal completeness rule. U-02 started with docs/BENCHMARK_EVIDENCE_MATRIX.md and saved model-revision HTTP probes. Continue from progress.md and docs/UNFINISHED_TASKS.md; do not redo the completed investigation. Calibration still has zero comparable observations.

User explicitly paused because the connection was interrupted and the session consumed too many credits. Stop work; resume only on a new user instruction. Do not repeat the investigation or rerun passed suites without a new change or specific concern.

**Correction added 2026-11-11: this is a saved implementation checkpoint, not completion of the broader calibration task.** The prior "housekeeping only" wording was too strong. Read [UNFINISHED_TASKS.md](UNFINISHED_TASKS.md): independent calibration, a validated offload model and evidence-backed recommendation validation remain unfinished. Zero comparable observations means calibration has not yet been achieved. On a request to resume, start U-01 and continue the original task; do not stop after reporting that existing tests pass.

## Outcome already implemented

- Root cause of the one-user $308,347.20 result: $71,456 hardware once, about $214,054 staffing (0.5 operations FTE for five years), $6,760 electricity, $16,078 capital opportunity cost. No repeated hardware purchase bug.
- Cheapest previously weighted cost only 50%; it now uses cost-only preset weights after hard filters. Expert custom weights remain an explicit override. No Mac-specific preference was added.
- User explicitly chose: "Yes-use self-managed for my comparison." A visible Cost assumptions selector now supports Enterprise and Self-managed in Normal/Expert. Self-managed owned hardware includes purchase once plus power at PUE 1; excludes staffing, NIM, economic wait/eviction/capital costs and resale. Enterprise inputs are retained.
- One user / Agentic coding / Cheapest / Self-managed, otherwise defaults: M5 Max 128 GB + Qwen 3.8 Flash Next INT2 ranks first at $6,143.30 ($5,693.03 hardware + $450.27 electricity over 60 months). M5 Ultra 256 GB options cost $11,443.83. These are current catalog/formula estimates, including a quality fallback, not verified performance of those exact configurations.
- Both SAW and TOPSIS cheapest results and timeline parity were checked. Existing workload defaults still require eight agents, five peak requests, 128K context, >=20 effective TPS and <=15 s TTFT; changing users alone does not change those inputs.
- Ranking now exposes selected candidate purchase, monthly electricity, monthly staffing and total monthly costs.

## Benchmark/calibration work already implemented

- New domain/benchmark_conditions.py contract. BenchmarkRecord retains legacy context_tokens and adds actual prompt_tokens, configured_context_tokens, conditions and uncertainty_reasons. SizingOptions adds explicit performance_prompt_tokens and benchmark_conditions.
- Resolver requires prompt and complete matching execution facts: hardware memory/node configuration, runtime/version, model revision, exact quantization, KV precision, optimized backend, cache fraction/state, speculative mode/configuration, concurrency, output length, protocol and residency. Quality matching stays independent. Scenario settings override contradictory condition hints.
- Offload deployments no longer receive a VRAM-bandwidth-only fallback. Missing comparable evidence produces unavailable performance/capacity, not validated throughput.
- All six legacy decode observations retained with uncertainty; unchanged original copy in docs/evidence/legacy_decode_observations.json. Added five separate MacStories prompt-series rows and a separate maintainer-reported Strata 4.7 TPS row. No 70% multiplier or invented PCIe/NVMe assumptions, no coefficient tuning.
- MacStories 256 GB M5 versus 512 GB M3 attribution preserved. 60.6 TPS at 130522 prompt tokens, output 512, cold/no-reuse, MTP depth 3, oMLX 0.7.0.dev2. Exact revision is recorded as linked by the article; direct Hugging Face revision fetch returned 404. Unknown KV/optimized-backend facts remain null.
- Calibration report exports all observations and exclusions with reasons and separates numerical outcomes. Current independent coverage: zero comparable decode/prefill rows, 12 decode + 1 prefill exclusions, MAPE n/a. This is NOT improved calibration accuracy.
- Three original numerical discrepancies remain strict historical diagnostic xfails in tests/calibration/test_historical_deviations.py. Original observation tests skip with eligibility reasons. Synthetic tests verify matched success, mismatches, exclusions and numerical failures.
- Engine result version is 0.1.2. Schemas/API types, source registry and bibliography (79 sources) regenerated. Ledger C-054 through C-056 and new contract rows recorded.

## Verification completed; do not repeat unnecessarily

- Final full Python: 772 passed, 13 skipped (ineligible calibration observations), 3 expected historical xfails, 0 failures/errors. Log: .calibration-full-pass.log; 430 seconds. It finished before the pause checkpoint. An earlier full run had one missing-ledger-row gate; corrected, targeted contracts 34 passed, then this successful full rerun.
- Ruff, format, strict mypy, catalog validation, TypeScript typecheck, ESLint, types:check and production build pass. Known Vite size advisory and test-client deprecation warning remain.
- Frontend unit tests: 31 passed (.calibration-frontend.log).
- Browser: first update run 71 passed; cosmetic fixes refreshed 37 targeted visual checks. Final no-update full run: 70 passed and one stale OOM screenshot failed. Actual OOM image was reviewed and copied to its baseline; that entire test then passed WITHOUT snapshot updates (.calibration-browser-oom.log). Thus all 71 cases passed across final full + targeted rerun. Do NOT claim a subsequent single full 71/71 or combined verify.py exit-0 run.
- Launcher/production checks: 3 passed (.calibration-launcher.log).
- Reviewed all 48 affected/new captures via six contact sheets, plus full/cropped desktop/mobile self-managed images and OOM actual; compared the existing Stitch ranking reference. Fixed clipped cost-selector labels and bad separators. Temporary QA images remain in .calibration-qa/.
- Logs .calibration-*.log are this session's untracked diagnostic artifacts; keep them until useful evidence is no longer needed. No further tests are running.

## Runtime and browser state

- Original development server on 5173/8000 was temporarily stopped for browser/launcher tests and restored with hidden `node scripts/dev.mjs`, parent PID 27184 at restoration. Health endpoint returned ok. Reinspect current PIDs if needed; never assume these remain current.
- Restored server logs: %TEMP%/ai-tco-calibration-dev.stdout.log and .stderr.log.
- Browser connector host unavailable; native Computer Use returned "Computer Use was not approved to use Comet". No attempt to bypass it. CUA completion summary was sent. User was told to use 1 user -> Self-managed -> Cheapest -> Apply scenario at http://127.0.0.1:5173. We did NOT set their live browser tab.

## Resume point

1. Read progress.md, docs/UNFINISHED_TASKS.md, this handoff and docs/CALIBRATION_AND_COST_REVIEW.md. The cost fixes and eligibility safeguards are implemented; actual empirical calibration is unfinished.
2. On the author's next resume request, start U-01: review whether matching conditions are appropriate for each metric/deployment, then proceed through the evidence and modeling tasks. Do not repeat completed cost/UI work or treat passing software tests as numerical validation.
3. U-02 through U-06 cover missing source metadata, independent calibration, offload modeling, quantization-sensitive one-user recommendations and API comparison coverage. These are substantive unfinished tasks, not optional housekeeping. Keep unresolved evidence explicit and do not tune for green tests.
4. Preserve all relevant staged changes and unrelated untracked .gitkeep/.config.kiro files. Never commit or push. Shared Mac serving, a verified 512 GB catalog entry and other catalog follow-ups are separately identified in U-07/U-08. Verification and cost-conscious sequencing are in U-09 and the resume procedure.

Detailed technical review and cost explanation: docs/CALIBRATION_AND_COST_REVIEW.md. Original primary sources are registered as MACSTORIES-M5-2026 and STRATA-DEEPSEEK41.
