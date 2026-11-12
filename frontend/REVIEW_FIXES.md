# Post-MVP review follow-up

2026-11-10. Author-requested recommendation review and correctness fixes.

The first recommendation waits for Apply scenario. Normal controls update an already-applied scenario; Expert edits remain explicit submissions. The setup text directs users to workload and budget inputs. Downloads remain unavailable before application.

Performance scoring now stops rewarding extra speed or lower latency after the configured targets are met. Expert mode can restore the earlier policy. Actual metrics remain unchanged in the table and export. The 60-month budget is a hard filter, including aggregate hybrid cost. Labels explain OpenRouter usage and staffing savings; cost comparison and missing API evidence are visible beside results.

Backend regressions cover requested context, API-reference latency cost parity, 744-hour bounds, backend-sensitive eviction loss, formula provenance, eligible hybrid anchors, budget filtering, explicit excess-performance preference and changed-catalog audit rejection. Catalog fingerprints protect against mixing a retained result with a different catalog. This is not a complete archived replay system.

Existing browser flows now explicitly apply their first scenario. Snapshot changes reflect new controls, wording, scoring and warnings, with no baseline tolerance relaxation. The setup capture, mobile Expert layout and desktop audit were visually inspected; automated coverage includes both themes and 1280/1440/768/390 widths. The final combined verifier runs against these reviewed baselines without updates.

No independent performance measurements or procurement quotations were added. See docs/RECOMMENDATION_REVIEW.md, docs/REVOLUT_CASE_STUDY.md and progress.md for results and remaining empirical work.

Final checks: 750 Python passed / 3 calibration xfailed, 31 frontend tests, 70 browser checks and 3 launcher checks. All static/build checks pass. A test-format correction and an unchanged-baseline recheck resolved the initial combined-run failures; the final full browser rerun passed without updates.
