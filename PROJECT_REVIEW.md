# MVP Project Review

**Review date:** 2026-11-10  
**Scope:** `progress.md`, implementation plan, corrections ledger, Python engines and services, API, frontend, tests, deployment setup and thesis notes.  
**Review type:** Read-only project assessment; no source changes were made.

## Implementation follow-up (2026-11-10)

The findings below are the original review snapshot. Implementation details and remaining evidence gaps are recorded in [Recommendation engine follow-up](docs/RECOMMENDATION_REVIEW.md). Code now addresses requested context, reference-latency parity, monthly-hour bounds, eviction backend factor, eligible hybrid selection, derived metric origins, catalog fingerprint checking, explicit initial submission, performance scoring capped at user targets and total-cost budgets. External calibration, benchmark coverage, verified network costs and custom-license modeling remain evidence/model work; no measurements were fabricated.

## Overall assessment

The MVP is substantially complete and well engineered, with a strong architecture and broad automated coverage. It is a solid foundation for a functional demonstration. Before relying on its recommendations as decision evidence, prioritize correctness and numerical validation. The review reproduced two important calculation/validation issues and found material limitations in comparison data and modeling assumptions.

Passing tests establish conformance to the implemented rules; they do not establish that every rule or catalog input accurately represents real deployments.

## Verification results

The combined verifier reported **all steps passed**, matching the current `progress.md` completion counts.

| Check | Result |
|---|---:|
| Python tests | 739 passed, 3 expected calibration failures |
| Frontend tests | 30 passed |
| Chromium browser checks | 69 passed |
| Launcher and production-process checks | 3 passed |
| Ruff, formatting, strict mypy | Passed |
| Catalog validation | Passed |
| Frontend typecheck, lint, generated-type consistency, build | Passed |

Browser checks passed without updating screenshots. The build retained its known bundle-size advisory; the Python suite emitted a test-client deprecation warning. PowerShell's logging wrapper returned a nonzero status after capturing native stderr, although the verifier itself reported every stage passing. The test counts include the untracked thesis tests present in this checkout; ensure intended release contents include them if those counts are part of the completion claim.

## What is working well

- Python remains the numerical authority; FastAPI provides the application boundary and React handles presentation.
- Immutable domain contracts, input validation and generated TypeScript types reduce mismatches between the client and service.
- The frontend handles stale requests, obsolete exports and independent simulator results carefully. Currency conversions retain the FX rate associated with the original result.
- Test coverage includes unit, property, integration, concurrency, browser, screenshot and launcher checks.
- Accounting explanations and the corrections ledger make formulas and assumptions more inspectable.

Preserve this architecture and verification approach while addressing the findings below.

## Findings and recommendations

### 1. High: requested context is not checked against model context limits

I changed the target context to **1,000,000 tokens** in a default-derived scenario. The engine returned **19 ranked candidates; 9 had model context limits below the requested target**. For example, some Qwen entries have a 262,144-token model limit.

The implementation checks memory capacity and a fixed 128K context floor, but it does not reject a candidate whose advertised maximum is below the user's requested context. Relevant code: `src/ai_tco_dss/engines/sizing.py` and `src/ai_tco_dss/decision/filters.py`.

**Recommendation:** Add a requested-context constraint for owned, rental, API and hybrid candidates. Distinguish model context support from memory fit, and cover the model limit and the first value above it with regression tests.

### 2. High: ranking and timeline costs can disagree when API latency is available

Candidate generation omits `cloud_ttft_s`, while the independent TCO projection supplies the reference API model's latency. When wait-time penalties are enabled, the two paths can calculate different costs. This is hidden by the current catalog's missing API latency values.

With a controlled in-memory catalog setting the reference API latency to **2 seconds**, I reproduced:

| Calculation for the same deployment | 60-month cost |
|---|---:|
| Ranking evaluation | $424,459.20 |
| Scenario timeline | $371,241.20 |
| Difference | **$53,218.00** |

Relevant code: `src/ai_tco_dss/decision/candidates.py` and `src/ai_tco_dss/services/scenario_service.py`.

**Recommendation:** Centralize TCO input construction and require ranking, projection, accounting and timeline totals to agree for the same deployment and assumptions.

### 3. High: the default comparison excludes all API candidates because performance data is missing

The default admissible set contains 23 owned-infrastructure candidates and 13 rentals, but no APIs or hybrids. All four API candidates lack throughput and latency values, so they fail the default minimum-TPS and maximum-TTFT filters. This behavior is documented in `progress.md`.

Rejecting alternatives with unknown performance can be reasonable, but the winner is then only the winner among candidates with sufficient data. It does not show that owned infrastructure is better than the available APIs.

**Recommendation:** Add comparable API measurements and show a clear evidence-coverage explanation, such as “API alternatives excluded because performance evidence is unavailable.” Distinguish missing evidence from measured failure.

### 4. High: numerical calibration is the largest limitation on recommendation credibility

I independently reproduced the calibration report:

| Measure | Result |
|---|---:|
| Decode observations | 6 |
| Decode MAPE | **252.0%** |
| Worst decode error | **1,378.3%** |
| Prefill observations | 1 |
| Prefill MAPE | 0%, but circular |

The worst case predicts about 68 TPS against 4.6 TPS measured. The sole prefill observation repeats the catalog value used by the calculation, so the perfect error score is not independent validation. Measured-first lookup helps when a matching measurement exists; it does not validate predictions for other contexts, configurations or deployments. See entries C-035 through C-037 in `specs/07_DATA_CORRECTIONS.md`.

**Recommendation:** Build an independent benchmark dataset that records hardware configuration, node count, runtime, quantization, context, concurrency and speculative mode. Prioritize offload and multi-node behavior. Report errors by deployment category with sample counts and measurement coverage.

### 5. Medium-high: hybrid enumeration can discard alternatives before considering them

The generator chooses one cheapest local anchor before applying all hard filters, then builds hybrids around that anchor. In the default scenario, the selected local component has quality **51.5**, below the required **55**. Every generated hybrid therefore fails the local quality requirement, aside from the separate API performance-data gap.

Relevant code: `src/ai_tco_dss/decision/candidates.py`.

**Recommendation:** Consider multiple eligible local anchors, or clearly define the feature as one illustrative hybrid comparison. Apply constraints at the intended local demand share before selecting anchors.

### 6. Medium: documented contract gaps affect modeled results

These were deferred while completing the application, but warrant resolution:

- **Active hours:** the workload contract accepts 744 hours; owned-infrastructure TCO rejects values above 730. A 744-hour default-derived scenario produced no ranked options.
- **Eviction costs:** disabling the optimized backend does not apply its slowdown factor to eviction wait costs. The ledger identifies an approximately 28.6× understatement of this wait-time component.
- **Networking costs:** missing cabling or switch kits are treated as zero, including for multi-node deployments.
- **License representation:** custom licenses are stored as MIT, while the interface uses a broad “Compliant” label.

See `specs/07_DATA_CORRECTIONS.md` for the underlying entries and proposals.

**Recommendation:** Reconcile the contracts and formulas, represent unknown costs explicitly, and use precise compliance labels such as “Passes configured license and endpoint checks.”

### 7. Medium: provenance should distinguish measurements from derived estimates

A calculated TTFT inherits the origin of its prefill input. With a synthetic measured prefill input, I reproduced a **calculated 20-second TTFT labeled “measured.”** This is an intentional rule documented in `progress.md` and implemented in `src/ai_tco_dss/engines/performance.py`; I recommend changing it because a measured input does not make a derived output a direct measurement.

Audit provenance is also resolved against the current catalog. After catalog changes, an older result can therefore be paired with newer explanatory inputs. See `src/ai_tco_dss/services/audit_export.py`.

**Recommendation:** Label derived values as formulas while retaining measurement source IDs. Export an engine version, catalog identifier or hash, and the relevant input snapshot.

### 8. Medium: completion documentation and release contents need consolidation

The current status and task-status table say all tasks are complete, but older “administrative completion gate” text remains in the current-status section. The implementation-plan checkboxes remain unchecked. The thesis notes also say Streamlit retirement, combined verification and Task 13 are future work, despite their completion elsewhere.

Some thesis support files remain untracked, including `tests/unit/test_thesis_notes.py`, `scripts/export_bib.py` and `thesis/references.bib`. The 739-test result includes the untracked thesis tests.

**Recommendation:** Keep the historical record, but identify one authoritative current status. Confirm the intended release contents and run the clean-checkout verification against those contents.

## Product and thesis improvements

The interface is coherent; targeted changes should be sufficient:

- Rename **“Monthly savings”** to **“Monthly staffing savings.”** The value is Munich-versus-Romania personnel savings and can be mistaken for deployment savings.
- Show measurement coverage and major assumptions beside the recommendation, not only inside the audit drawer.
- Add a compact comparison of leading alternatives covering cost, capability, evidence quality and exclusion reasons.
- Add scenario save/import for repeatable evaluations.
- Consider loading Plotly only when needed. The roughly 480 KB gzip initial JavaScript bundle passes its current budget, so this ranks below numerical correctness.

For the thesis, prioritize a reproducible evaluation study: vary workload, context, staffing, prices and ranking weights; report changes in feasibility and the preferred alternative; compare predictions with independent measurements; and preserve exact scenario and catalog snapshots. Include sensitivity to missing data and candidate composition. Agreement between SAW and TOPSIS, or deterministic results, does not establish recommendation robustness.

I did not independently reverify every external price, benchmark source or license page during this review; those remain a separate data-validation task.

## Recommended sequence

| Priority | Work | Evidence of completion |
|---|---|---|
| 1 | Fix requested-context validation and inconsistent wait-cost inputs | The reproduced cases become regression tests |
| 2 | Revisit hybrid selection and resolve active-hours/backend gaps | Boundary and cross-path consistency checks |
| 3 | Improve API and local benchmark coverage | Independent calibration report with coverage |
| 4 | Add provenance snapshots and ranking sensitivity | Reproducible exported scenario evaluations |
| 5 | Consolidate documentation and release files | Clean-checkout verification of intended release |

**Conclusion:** Keep the MVP architecture and UI. Make validated decision behavior the next milestone. The project is in good shape for a functional demonstration, but address the context-limit defect, latent cost inconsistency and incomplete comparison evidence before making strong claims about which deployment an organization should choose.
