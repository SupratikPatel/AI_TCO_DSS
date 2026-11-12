# Simultaneous peak capacity — U-05, 2026-11-11

The author selected **Require simultaneous capacity**: five peak requests require
five resident request slots at the requested target context. Engine 0.1.4 adds the
`peak_capacity` hard filter alongside the existing monthly-utilization filter.
A three-slot deployment now reports `3 resident request slots`, threshold
`>= 5 simultaneous requests at target context`, even at low monthly utilization.
Unknown sizing cannot establish capacity. Equality passes.

Scope: `decision/filters.py`, rental precision selection in `decision/candidates.py`,
engine metadata in `domain/results.py`, affected generated schema/API types,
`tests/unit/test_peak_capacity.py`, the rental-selection oracle in `test_decision.py`,
the changed admission-count assertion in `tests/integration/test_concurrency_performance.py`,
the browser acceptance check and 22 affected ranking/Expert/self-managed snapshots,
saved policy sensitivity results, correction ledger
and continuity/evidence reports. This author choice extends historical Req 28.1's
monthly-only users-served condition; it does not change sizing or cost equations.

The local rule applies to on-premise deployments, rentals and hybrid local components.
The existing component recursion carries the complete reason into hybrid rejection
and anchor selection. A rental chooses the highest precision that covers the peak
when one exists; otherwise it retains a diagnostic memory-fit candidate, rejected by
the new rule. Commercial APIs have no local-memory sizing and remain outside this
filter; their missing performance evidence remains explicit.

The full scenario peak applies to each evaluated local service. Existing per-seat
workstations are not pooled into a shared service, and the peak is not divided by
active users or the average hybrid local-cost share. No enforced peak routing split
exists to justify that reduction. Multi-node `max_concurrent_users` already represents
the sized deployment; it is not multiplied by node count a second time. Retained
agents remain a separate eviction assumption. No queueing allowance or latency
coefficient was added. Loaded latency and quantization-specific quality still need
measurements; U-05 remains open for those empirical requirements.

## Changed modeled outcomes

The original 11-case engine 0.1.3 evidence is preserved. Because policy changed, the
same inputs were evaluated once for
[`peak_capacity_sensitivity_2026-11-11.json`](evidence/peak_capacity_sensitivity_2026-11-11.json),
which records exact scenarios, parameters, catalog fingerprint, winners, Mac rows
and every peak-capacity rejection. These are model outputs, not measurements.

| Scenario | Admitted | Winner | 60-month USD |
|---|---:|---|---:|
| Baseline, peak 5 / context 128K | 44 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Context 64K | 50 | Max 128 / Qwen 27B INT3 | 6,143.30 |
| Context 256K | 31 | DGX Spark / Flash-Next INT2 | 8,330.83 |
| Peak 1 | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Peak 2 | 42 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Peak 10 | 35 | DGX Spark / Flash-Next INT2 | 8,330.83 |
| One retained agent | 45 | Max 128 / Qwen 27B INT3 | 6,143.30 |
| Sixteen retained agents | 40 | DGX Spark / Flash-Next INT2 | 8,330.83 |
| Maximum TTFT 5 s | 29 | RTX Pro 6000 / Qwen 27B FP8 | 19,272.25 |
| Maximum TTFT 30 s | 44 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Both performance filters unset | 104 | Strix Halo / Qwen 27B INT3 | 4,250.75 |

The baseline Max INT2 has six modeled slots and still qualifies on memory; the
equally priced three-slot INT3 alternative is rejected. At 256K, Max INT2 has three
slots, so it fails the unchanged five-request requirement. At peak ten, six slots
are also insufficient. These are capacity decisions, not measured throughput failures.
Candidate counts need not be monotonic: rental enumeration chooses one highest-bit
capacity-fitting precision per rental/model, which can change its performance-filter
outcome when the requested peak changes.

## Verification

Seven new unit regressions failed before implementation (two boundary passes already
held). Focused post-fix decision/review coverage: 52 passed, including equality, missing
sizing, independent monthly load, API exemption, rental selection, hybrid recursion
and the real one-user three-slot regression. The initial full suite had 835 passes
and one obsolete admission-count assertion; that expectation now records 35 admitted
and 638 rejected, with the timing threshold unchanged. The paginated browser reason
check passes. Twenty targeted browser checks passed while refreshing 22 visually
reviewed snapshots for changed counts/rows/scores; no frontend layout code changed.
Final combined verification passed with native exit 0: 836 Python passed, 13 skipped, 3 historical xfails; 31 frontend tests, 72 browser checks without snapshot updates, 3 launcher checks. Lint/format, strict mypy, catalog validation, frontend types/lint/build and API drift pass. Proof: `.u02-u05-final.log` and `.u02-u05-final-exit.json`. U-09's earlier engine 0.1.3 result remains historical proof for that earlier snapshot. Calibration remains unfinished.
