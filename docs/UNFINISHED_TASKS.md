# Unfinished calibration and recommendation work

**Week-break checkpoint, 2026-11-12:** resume from
[SESSION_HANDOFF_2026-11-12.md](SESSION_HANDOFF_2026-11-12.md) and progress.md's saved
prompt. The enterprise review and bounded planner are delivered; U-07's next phase
is explicit complete-replica deployment/cost/state placement before recommendation
integration. Core empirical U-02 through U-06 and remaining U-07/U-08 gaps stay open.
Do not repeat completed reviews or passed suites merely to restart after the break.

**Latest enterprise report / implementation checkpoint, 2026-11-12:** read
[the new review](ENTERPRISE_REPORT_REVIEW_2026-11-12.md) and
[the bounded fleet scope](FLEET_PLANNING_SCOPE_2026-11-12.md).
The supplied evidence_report.md is preserved unchanged; named companion JSON files
are absent. Twenty-four new source/input/excerpt/member hashes and ten reused files
verify. C-076 through C-083 correct primary-source contradictions; earlier C-071/C-074
still apply. Implemented an opt-in complete-replica resource lower-bound planner,
with explicit spares and unknown/zero handling; it is not wired into recommendations
and does not prove SLA/placement feasibility. Focused fleet/purity: 30 passed.
Full Python: native exit 0, 858 passed, 13 skipped, 3 historical xfails.
Proof: .enterprise-report-python.log / .enterprise-report-python-exit.json.
No catalog, current engine 0.1.4 behavior, coefficients or capacity-policy change.
Strict coverage stays zero / 13 existing exclusions / MAPE n/a. U-02 through U-08
remain open; U-07 has a delivered planning primitive, not a deployed fleet/router.
Reuse prior browser/launcher checks. Preserve staging/unrelated work and logs;
never commit or push.

**Latest enterprise/router analysis, 2026-11-12:** read
[ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md](ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md)
for the author's 1050-user observation and two supplied posts. Reproduced no admission
at 1050 with enterprise defaults and the saved self-managed profile: last eligible
candidate has formula capacity 1010.5049 users, not a 1000-user input cap. The domain
and frontend accept 100000. The USD 100000 CapEx cap and missing API latency evidence
also constrain results; presets run after hard filters. Eight new scenarios and two
budget-only counterfactuals are saved separately. Revolut's shared fleet and Pi's
adaptive routing expose explicit replica/scheduler/router gaps beyond the existing
static Hybrid Split. Six primary responses are hashed; the report contains the
focused external-agent fetch request. No production changes or passed app/browser
reruns; capacity policy and strict calibration status remain unchanged. Continue the
latest 512 GB evidence review for core calibration. Preserve all staging/unrelated
files and logs; never commit or push.

**Latest 512 GB evidence checkpoint, 2026-11-12:** read
[M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md](M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md)
after the saved handoff/backlog. Official Apple specs and dated USD 22299 (1 TB) /
29799 (16 TB) offers now verify the 36-core CPU / 80-core GPU / 512 GB target.
Thirteen acquired oMLX records report 512 GB; Qwen Q6 at 131072 input reports
28.250 s TTFT / 102.3 TPS with fixed MTP depth 3. Apple supplies independent 512 GB
native-precision measurements. Four original quality logs reconcile 2647 questions.
A new archive preserves the input and 42 remote responses, including explicit blocked/
empty captures. C-070 through C-075 correct six report interpretations. Earlier
statements that no 512 GB measurements were acquired are historical and superseded.
Five simultaneous 128K requests, eight resident sessions and exact low-bit tool
validity remain missing in inspected evidence. No 512 GB catalog/shared-serving
implementation, production import, coefficient or capacity-policy change. Strict
coverage remains zero / 13 existing exclusions / MAPE n/a; no U task closed.
Reuse existing engine 0.1.4 verification and all archives. No benchmark machine;
preserve staging/unrelated files and logs; never commit or push.

**Latest v1.1 report checkpoint, 2026-11-12:** read
[YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md](YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md)
first after the saved handoff/backlog. A separate 34-file archive preserves the revised
input and 33 new primary remote files. Reconciled 60 Kapitsa coding responses,
12 cold prompt/TTFT records and 36 sweep requests; oMLX JSON is settings, not request
events. Added a conditional Heretik context-shape diagnostic (128K +16.5%, 256K
+51.4% overprediction after anchoring the baseline), not strict MAPE or fitting.
C-065 through C-069 correct M3-as-M5 attribution, loading-memory phase, unsupported
FP16 cache, forward-meter interpretation and integrated full-fill timing. No M5 Ultra
512 GB measurements or Max five-request / 128K logs acquired. Strict coverage remains
zero / 13 existing exclusions / MAPE n/a; no production data/code, coefficients,
capacity policy or task status changed. Reuse prior engine 0.1.4 verification and all
archives. No benchmark machine available; preserve staging/unrelated files, never
commit or push.

**Author's hardware scope, 2026-11-12: M5 Macs only.** The 512 GB target is
**Mac Studio M5 Ultra 512 GB**. Do not add or recommend M3 Macs, acquire more M3
purchase evidence, or substitute M3 Ultra 512 GB measurements for M5 performance.
Preserve M3 results inside original source archives as historical context. Existing
M5 catalog entries stay in scope. The latest 512 GB review verifies configuration,
two US offers and qualified performance; catalog/shared-serving implementation
and the requested concurrent workload remain unfinished.

**Latest checkpoint - supplied report reviewed:**
[YOUTUBE_EVIDENCE_REPORT_REVIEW_2026-11-12.md](YOUTUBE_EVIDENCE_REPORT_REVIEW_2026-11-12.md)
and its machine-readable audit assess all twelve headline rows. The user's input
and 23 new remote files are hashed in a separate archive. Primary sources confirm
M5 Max non-MTP rates, DGX serving/concurrency, separate Mac-mini workload summaries
and Requesty production API statistics. This materially improves external evidence
coverage, while C-061 through C-064 correct supplied-report interpretations. Exact
M5 Max 5 x 128K loaded performance and artifact-specific tool quality remain absent;
original raw run identities/logs are still required for strict calibration. Coverage
stays zero comparable observations / 13 exclusions / MAPE n/a. Engine 0.1.4,
coefficients, production data and capacity policy are unchanged; no U task closed.

**Latest resume checkpoint, 2026-11-12:** read
[the run-fact continuation](U02_RUN_FACTS_CONTINUATION_2026-11-12.md). A separate
34-file archive adds twelve Qwen 27B raw llama-bench rows (including isolated
prefill), two historical harness snapshots, dataset history and three Strata
operator reports/comments with partial same-run storage inputs. All 36 raw timing
records / 108 samples reconcile with the saved source summaries. The published
history does not recover `1025283-dirty` or live MLX cache dtype; dynamic GGUF
quantization prevents uniform-bit calibration. Offload summaries lack raw manifests
and transfer/compute overlap. Coverage remains zero, 13 exclusions, MAPE n/a.
No production code/data changed or task was marked complete. The simultaneous
capacity policy and passed engine 0.1.4 verification remain settled. The next step
is original run bundles or controlled measurements as specified in the new report;
do not reacquire the saved archives. The author confirmed **no benchmark machine
is available**. A supplemental seven-response API search archive retains six 404s
and a whole-task HolmesGPT report; no comparable raw API events were acquired.
No paid calls/inference performed. These are evidence blockers, not measured failures.

Updated 2026-11-11 after the author reported that the previous handoff caused a new session to stop with "everything done".

**Restart here:** [current handoff — 2026-11-11](SESSION_HANDOFF_2026-11-11.md).

Latest continuation: [U-02 acquired primary material and diagnostics](U02_PUBLIC_EVIDENCE_ACQUISITION.md)
retains 35 hashed source files. Original run metadata remains missing and strict
coverage remains zero. The author chose **Require simultaneous capacity**; the
[U-05 policy change](PEAK_CAPACITY_POLICY.md) implements `peak_capacity`, peak-aware
rental precision selection and engine 0.1.4. New sensitivity outputs are saved
separately from the original engine 0.1.3 evidence. Final combined verification of engine 0.1.4 passed with native exit 0: 836 Python
passed, 13 skips, 3 historical xfails; 31 frontend tests, 72 no-update browser checks,
3 launcher checks. Reuse `.u02-u05-final.log` / `.u02-u05-final-exit.json`. Earlier
U-09 verification remains complete for its snapshot. The author requested a saved
handoff; resume only on a new instruction.
U-05 still needs quantized quality and loaded-serving measurements. Do not repeat
the archived acquisition or original reports without new evidence or changed inputs.
U-01/C-058 corrections and U-09 verification are complete. Resume the remaining U-02
acquisition using the existing evidence matrix, then continue U-03 through U-06.
Their evidence/modeling gaps remain open even where an audit or sensitivity report
has already been delivered. U-07/U-08 are separate follow-ups. The older handoff is
historical; do not restart U-01 or repeat passed checks just to resume.

**The broader calibration task is NOT complete.** Cost-accounting fixes and evidence-eligibility safeguards are implemented. There are still **zero comparable calibration observations**, 13 excluded observations and three historical numerical xfails. Passing software tests does not establish accurate performance predictions or reliable deployment recommendations.

The author resumed implementation on 2026-11-11. U-01 policy, regression fixes and final full Python verification are complete (819 passed, 13 skipped, 3 historical xfails); see [matching policy](BENCHMARK_MATCHING_POLICY.md). U-02 has an initial [evidence matrix](BENCHMARK_EVIDENCE_MATRIX.md) and [HTTP probe results](evidence/benchmark_metadata_probe_2026-11-11.json), but usable independent observations remain unavailable. Do not ask the author to restate the task or announce that calibration is done.

## Core unfinished work, in execution order

2026-11-11 continuation: C-058 adds output-volume matching and local-formula
applicability guards (seven failing regressions corrected; engine 0.1.3).
The [one-user sensitivity/API coverage report](ONE_USER_SENSITIVITY_AND_API_COVERAGE.md)
and its saved 11 scenarios deliver the modeled U-05 comparison and U-06 coverage
audit. Quantization-specific quality, loaded-serving latency and API measurements
remain unresolved. In particular, monthly capacity is not a peak-concurrency SLA:
the current formulas can admit a configuration with fewer KV slots than requested
peak requests. Do not interpret invariant peak sensitivity as measured invariance.
Final combined verification is complete: native exit 0, 826 Python passed, 13 skipped,
3 historical xfails; 31 frontend tests, 71 browser checks without updates, 3 launcher
checks. Evidence: `.calibration-followup-final.log` / `.calibration-followup-final-exit.json`.

- [x] **U-01: Review the new matching/eligibility implementation against the original goal.** Inspect `domain/benchmark_conditions.py`, `engines/resolver.py`, `engines/performance.py` and `services/calibration_report.py`. Determine which conditions are actually necessary for each metric and deployment. In particular, assess the universal completeness requirement, the app-specific optimized-backend flag, concurrency semantics, and the relationship between actual prompt length, formula context and configured capacity. These are review questions, not already-proven defects. Completion: document a metric-specific matching policy and add regressions for any demonstrated errors, preserving meaningful exclusions. Do not simply relax requirements to make existing records pass.

- [ ] **U-02: Recover or acquire usable benchmark evidence.** Resolve the missing MacStories KV/runtime facts where primary evidence permits; investigate the linked model-revision 404 without claiming its contents were verified. Establish the Strata decode prompt, exact build, runtime, speculative mode and protocol independently of its separate prefill observations. Keep unknowns unknown. Completion: a source-backed evidence matrix showing measured, inferred and missing facts for each observation, with explicit eligibility decisions. If a source cannot resolve a fact, record that blocker and identify the controlled measurement required; do not invent a value.

- [ ] **U-03: Perform actual independent calibration.** Build comparable resident decode and prefill observations, including the Mac configurations relevant to the recommendation. Avoid calibrating prefill against the same catalog value used by the formula. Evaluate predictions by deployment and metric with sample counts, error distributions and validation evidence separate from fitting data. Completion: a reproducible report with genuinely comparable results, numerical failures and coverage gaps; explain remaining uncertainty. The current MAPE of n/a and removal of unsuitable comparisons from MAPE do not satisfy this task. Change coefficients only when supported by evidence; retain historical discrepancy records.

- [ ] **U-04: Address offload performance modeling.** The unsafe VRAM-only fallback was removed, but no validated replacement was implemented. Obtain a matched measured path or develop a tier-aware model using supported residency, execution placement and transfer inputs. Completion: compare its predictions against independent offload observations and report deployment limits. If evidence is unavailable, retain unavailable performance and mark this task unresolved; do not declare the offload model fixed merely because unsupported predictions are suppressed.

- [ ] **U-05: Validate the one-user recommendation beyond accounting.** The author chose **Require simultaneous capacity**; C-060 / engine 0.1.4 implements the peak-memory rule, and [the updated policy/sensitivity report](PEAK_CAPACITY_POLICY.md) is delivered. Do not re-ask that policy question. The $6,143.30 INT2 winner still uses formula performance and a model-level quality fallback. Defaults remain eight retained agents and five peak requests. Exact INT2/INT3 artifact quality/tool reliability and loaded TTFT/throughput still need measurements. Memory capacity is necessary but does not validate loaded latency. Preserve the historical engine 0.1.3 report; use the separate engine 0.1.4 evidence for current admission decisions. Do not force a Mac to win, infer full-precision quality for INT2, or silently reduce requirements.

- [ ] **U-06: Improve comparison coverage for APIs.** API alternatives currently fail performance filters because matching latency/throughput evidence is missing. Acquire comparable measurements or make the unresolved comparison boundary explicit. Completion: report API measurement coverage and distinguish missing evidence from measured failure; do not interpret a local winner as proof it beats excluded APIs.

## Explicit follow-ups, separate from the core calibration correction

- [ ] **U-07: Shared Mac serving and catalog coverage.** Existing M5 Macs are per-seat workstations. The author restricted Mac options to M5; the 512 GB target is Mac Studio M5 Ultra 512 GB, with its own verified configuration, price and performance evidence. M3 is historical evidence only and must not be added as a purchase option or used to validate M5 performance. A shared M5 inference server needs its own deployment option and validated concurrency/capacity; a 512 GB M5 entry and shared serving were not implemented. Do not invent prices or assume one Mac serves all users. Shared-serving scope remains separate from this hardware-generation choice.
  Enterprise follow-up analysed in docs/ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md: distinguish replicas from model-parallel nodes, model shared fleet capacity/arrival bursts and evaluate adaptive routing separately from static local/API ratios. The 1050-user empty result is reproduced under saved defaults and is not an input cap. This is a documented modeling/catalog scope gap; no fleet, router or scheduling feature was implemented and no existing peak-capacity policy was changed.

- [ ] **U-08: Other known catalog/model limitations.** Verified hardware/networking quotes and accurate custom-license representation remain follow-ups from the project review. Preserve their ledger entries; assess them separately from the completed cost-accounting changes.
- [x] **U-09: Final verification of the C-058 / engine 0.1.3 snapshot.** Focused regressions passed; affected schema/API types regenerated. A single final combined `scripts/verify.py` run returned captured native exit 0: 826 Python passed, 13 skipped, 3 historical xfails; 31 frontend tests; 71 no-update browser checks; 3 launcher checks; lint/format, strict mypy, catalog validation, types/lint/build/API drift pass. No screenshots changed. Re-run appropriate checks after future substantive changes. This completes software verification for this snapshot, not U-02 through U-06 empirical/modeling work. The later C-060 / engine 0.1.4 change also has a final combined native-exit-0 result: 836 Python passed, 13 skipped, 3 historical xfails; 31 frontend tests, 72 browser checks without updates, 3 launcher checks. Logs: `.u02-u05-final.log` and `.u02-u05-final-exit.json`.

### U-07 delivered subset and next boundary (2026-11-12)

The opt-in `domain/fleet.py` / `engines/fleet.py` primitive now computes independent
complete-replica resource lower bounds with caller-declared spares. It separates
peak requests, retained sessions and aggregate output demand, preserving unknowns
and impossible zero-capacity cases. See [the explicit scope](FLEET_PLANNING_SCOPE_2026-11-12.md)
and [the new report review](ENTERPRISE_REPORT_REVIEW_2026-11-12.md). This subset has
30 focused fleet/purity passes and full Python exit 0 (858 passed / 13 skips /
3 historical xfails); it does not integrate fleets into current recommendations.
Next: define deployment/cost/state-placement semantics and acquire matched load/SLA
evidence before candidate/API/UI integration. Adaptive routing still needs task-class
and load traces, cache/retry/classifier costs and task success. Published Jev policy
source is now pinned; Julien's extension identity remains unknown. Do not reuse
AgentX session-tree counts as simultaneous resident request slots. Shared 512 GB M5
catalog/serving, exact low-bit validity and EU request-event logs remain open.

## Already completed: do not redo

- Explained the old ~$300K result: hardware was charged once; five years of 0.5 operations FTE dominated costs.
- Added the author-approved Self-managed purchase-and-electricity option and literal cost-only Cheapest preset, retaining enterprise assumptions and hard filters.
- Added prompt/execution metadata, strict evidence matching, explicit exclusions, historical observation preservation and offload fallback suppression.
- Recorded corrections C-054 through C-056, regenerated schemas/types/bibliography and preserved three historical numerical xfails.
- Verified the saved implementation: 772 Python passed, 13 calibration skips, 3 expected historical xfails; 31 frontend unit tests; 3 launcher tests. Browser coverage passed across 70 tests in the final full run plus the reviewed OOM screenshot's targeted rerun. These are software checks, not empirical calibration.

## Cost-conscious resume procedure

Read `progress.md`, `SESSION_HANDOFF_2026-11-11.md` and this file, then the matching policy, evidence matrix and sensitivity report. U-01/C-058 and U-09 are complete; continue U-02 from its concrete acquisition requirements without repeating the saved review, reports or passing checks. Reuse saved findings and logs. Do not repeat the original cost investigation, redo the UI, or rerun expensive suites without changes. If external evidence blocks one item, report the precise missing information and continue independent authorized work. Preserve staged/unrelated files and never commit or push.
