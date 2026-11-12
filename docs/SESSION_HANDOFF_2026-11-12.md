# Restart checkpoint after the November 12 work

Saved at the author's request before a week-long break. Stop substantive work at
this checkpoint; resume only when the author returns. `progress.md` remains the
first file to read. This is the current handoff; November 10/11 handoffs and their
verification results are preserved as history. No commit or push was performed.

## Exact restart point

The enterprise report review and the bounded fleet-planning primitive are complete
for their stated scope. Do not repeat those reviews or their passed checks simply
to resume. Read these next:

1. [Unfinished backlog](UNFINISHED_TASKS.md).
2. [Enterprise report review](ENTERPRISE_REPORT_REVIEW_2026-11-12.md).
3. [Fleet implementation scope](FLEET_PLANNING_SCOPE_2026-11-12.md).
4. [Enterprise scale/router analysis](ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md).
5. [M5 Ultra 512 GB evidence review](M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md).
6. [Metric matching policy](BENCHMARK_MATCHING_POLICY.md).

Then inspect `src/ai_tco_dss/domain/fleet.py`, `src/ai_tco_dss/engines/fleet.py` and
`tests/unit/test_fleet.py` for the next U-07 phase. `plan_fleet` is an opt-in pure
function; it does not participate in recommendation ranking, API endpoints or UI.
It computes conditional integer resource bounds from caller-declared capacities
of one complete replica. Requests, retained sessions, output demand and GPUs per
replica stay separate. Explicit spares are required. Missing capacity is unknown;
positive demand with zero capacity has no finite solution. A necessary bound is
not sufficient placement, SLA or task-quality evidence. A measured test rate is
not automatically a proven maximum capacity.

Next concrete work: scope deployment/cost/state-placement semantics for complete
replicas before integrating fleet candidates, API contracts or UI. Identify which
cost terms repeat per replica versus per employee or shared fleet, how retained
state is placed and which resource/SLA claims are established versus conditional.
Preserve unknown load/placement facts; do not turn a lower bound into an admitted
fleet. Continue implementation and regression verification where existing evidence
and policy support it. If a dependency is unavailable, record the exact missing
field and continue independent authorized backlog work instead of repeating the
completed review or asking the author to restate the project.

Adaptive routing is separately scoped: task classes, capability/data policy, local
load signal, classifier overhead/bypass, affinity, cache loss, retries, escalation,
API rate limits, success and per-path cost require explicit representation and
matched evidence. Jev's pinned source establishes policy behavior, not Julien's
personal router or measured savings. Do not silently import its default thresholds
or reinterpret the current static Hybrid Split as adaptive routing.

## Evidence state to preserve

- The supplied `evidence_report.md` is preserved unchanged in
  `docs/evidence/enterprise_report_review_2026-11-12/`. SHA-256:
  `2e82d5087bbb2b14d08c58d079a1f32da9db7368a439c9b7c7ec5115dfa46361`.
  Its named companion JSON files were absent. They are not prerequisites to resuming
  independent work, and their reported hashes do not establish acquired artifacts.
- That archive verifies 24 new source/input/excerpt/member files and ten reused
  files. All 24 new staged source blobs match the manifest hashes. Preserve original
  source whitespace and encodings. The Petronella direct downloads are 403 bodies;
  primary-page web excerpts are separate files. Downloaded code was not executed.
- C-076 through C-083 correct new report contradictions. Reuse C-071/C-074 for
  repeated M5 memory and Sushi denominator errors; do not edit supplied reports.
- The inspected Revolut slide confirms Together AI Dedicated Model Inference and
  reported fleet/tuning results. Replica layout and actual contract invoice remain
  unknown. AgentX concurrency is live session trees, not simultaneous HTTP requests.
- M5 Ultra 512 GB configuration, dated US offers and qualified measurements are
  verified in the previous archive. Five occupied 128K requests and eight retained
  M5 sessions remain unverified. The 12-request M5 DeepSeek release summary does not
  supply that workload's context/memory identity. M3 remains historical only.
- Exact uniform INT2/INT3 tool quality and matched EU 32K/128K API request-event
  evidence remain missing. Strict calibration is **zero comparable observations /
  13 existing exclusions / MAPE n/a**. No coefficients or observations were imported.

## Settled decisions and operating constraints

- There is no 1,000-user input cap. The saved 1,050-user failure is already explained:
  formula capacity 1010.5049 under saved defaults, plus CapEx and API evidence limits.
  Reuse the eight user-count scenarios and two budget counterfactuals.
- Keep valid filters and ranking rules. Do not force any deployment to win.
- Simultaneous resident peak capacity is decided and implemented (C-060, engine
  0.1.4). Do not re-ask or relax it. Memory capacity does not prove loaded latency.
- Mac purchase options are M5 only. No benchmark machine is available. Do not rent
  hardware, run paid inference, download weights or guess measurements.
- Preserve staged changes, unrelated files, all source archives and diagnostic logs.
  Stage only relevant changes. Never commit or push unless the author explicitly
  changes that instruction. No background work or scheduled action was arranged.

## Verification already completed

- New fleet/purity checks: **30 passed**. Tests first failed on the absent primitive;
  two further regressions reproduced decimal ceiling inflation and finite-ratio
  overflow before correction with exact decimal-ratio arithmetic.
- Full current Python suite: **858 passed, 13 skipped, 3 historical xfails**, native
  exit 0, 252.33 seconds. Root proof: `.enterprise-report-python.log` and
  `.enterprise-report-python-exit.json`.
- All **33 continuity checks** pass. Scoped Ruff/format pass for `src`, `tests`,
  `scripts` and the new archive's scripts. Strict mypy passes all 47 source files.
  Review links, archive hashes and npm SHA-512 integrity pass.
- Root-wide Ruff still reports **41 pre-existing findings** in three earlier
  evidence derivation scripts. Those archived files were preserved. An unscoped
  staged whitespace check also flags intentionally preserved source bytes and
  earlier staged material; the current code/continuity/scoped-document check passes.
  Do not describe this as a new all-green combined verifier.
- Reuse the unchanged engine 0.1.4 combined proof: `.u02-u05-final.log` and
  `.u02-u05-final-exit.json`, native exit 0, 836 Python passes, 31 frontend tests,
  72 no-update browser checks and three launcher checks. Current additions have
  no recommendation/frontend path; those suites were not repeated.

Byte-preserved copies of the latest Python proof, the prior combined proof and
the current lint limitation are saved with hashes under
`docs/verification/session_checkpoint_2026-11-12/`. The root logs remain in place.
Documentation-only break preparation does not justify another full suite.

## Git and restart materials

The index already contains accumulated changes from earlier sessions, including
application/frontend work, research archives and bibliography/thesis files. Nothing
was unstaged, discarded, committed or pushed. The suggested detailed message in
[COMMIT_MESSAGE_2026-11-12.txt](COMMIT_MESSAGE_2026-11-12.txt) describes the accumulated
implementation/research checkpoint; it is text for the author, not an instruction
to execute a commit. Existing unrelated staging remains intact.

The complete next-session prompt is in `progress.md` and mirrored in
[START_NEXT_SESSION_2026-11-12.txt](START_NEXT_SESSION_2026-11-12.txt).
Reinspect working-tree changes, processes and listeners on return; old PIDs are not
restart commands. Revalidate time-sensitive external claims only when needed for
new work. No development server or browser handoff is promised by this checkpoint.
