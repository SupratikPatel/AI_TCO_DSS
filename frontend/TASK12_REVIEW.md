# Task 12 audit and export review

Reviewed 2026-11-09 against the canonical Stitch audit dark export
`f9fbe84561b5418384aa720d8be2f799`, the TCO light/dark shell and
`design/stitch/TOKENS.md`. [Visual comparison](audit-comparison.html).

The third tier starts collapsed. Its formula cards use the reference's raised
panels, dark code surfaces, quantitative typography and highlighted results.
Desktop uses two columns; tablet/mobile stack the cards and preserve complete
candidate names, formulas and source references. This is an inline disclosure,
so the workspace remains reachable without a permanent overlay. Reference-only
discounting, certification and cryptographic claims are omitted.

Ranking row buttons and the audit selector share selection. A successful new
scenario result defaults to rank one; tab, theme and display-currency changes
preserve selection. The independent memory and TCO simulators never supply the
audit/export result. The download description identifies the scenario timeline
anchor, including the existing D-09 fallback when necessary.

The stateless audit API accepts the displayed `ScenarioResult` and selected ID.
It retains the exact engine traces, supplies input-unit legends, exposes all five
performance values with their measured/formula origins, and resolves registry
titles, URLs/references, tiers and ISO access dates. Source IDs appear once, with
expandable field records and adjacent assumption badges. These records include
the selected hardware/model's catalog metadata; the UI labels that broader input
context explicitly. FX shows six decimals, original rate date/source, and file
versus Expert override. Missing metrics remain unavailable.

Rental and hybrid accounting have deployment-specific traces. Rental setup fees,
monthly rental/personnel and server-total RAM divided per node are explicit.
Hybrid traces show full local fixed costs, the remote API share and separate
component evaluations. Retained local TCO values are never presented as rental
or hybrid totals. The Python engines and C-042/C-043 calculations are unchanged.

JSON export validates and serializes the exact supplied `ScenarioResult` in USD;
it does not rerun evaluation. CSV export creates one deterministic ZIP with
`ranking_<CUR>.csv` and `timeline_<CUR>.csv`. Ranking includes every ranked
candidate, six raw criteria, method-appropriate aggregate score and paired ranks.
Timeline includes exactly months 1–60 and all seven series; unavailable series
cells are empty. Monetary column headers contain USD/EUR. Python converts CSV
money using the result's original FX rate and retains numeric precision for data
reuse. The UI continues to format monetary results to two decimals.

Pending/failed/ranking-error scenarios cannot expose retained results through
either download button. A valid empty result can still export its full JSON;
CSV requires a completed timeline. Audit requests and transfers cancel when
their result becomes obsolete. Server/download errors remain visible and retain
scenario inputs.

Test-first evidence: initial Python cases failed on absent audit/export routes;
component tests failed on the absent drawer; Chromium failed on the absent audit
disclosure. Additional deployment tests failed on generic accounting traces and
missing personnel/monthly-OpEx derivations before their implementation. Round-trip
coverage includes real Python service outputs under SAW/TOPSIS, generated user
counts and multiple FX values. Browser downloads compare JSON to the exact
evaluate response and ZIP bytes to the Python export endpoint.

Final verification: **59 Chromium checks** pass against the reviewed baselines,
**28 frontend tests** pass, and typecheck/lint/build/types:check pass. The launcher
startup/proxy/cleanup test passes separately after the browser server stops.
`uv run python scripts/verify.py` passes ruff/format, strict mypy and catalog
validation, then reports **728 passed, 3 calibration xfailed and the same three
failures solely from missing thesis/thesis_notes.md and thesis/literature.bib**.
All 11 new Python audit/export checks pass. Tasks 8-12 retain their administrative
in-progress gates. One snapshot-refresh attempt hit a Windows file-open error;
its targeted rerun and final full browser run passed without changing tests.
The currency-cancellation regression first failed on a stuck busy button, then
passed after tying download status to the transfer's cancellation signal.

Verification results are also recorded in `progress.md`. Reproduce with `npm test`,
`npm run typecheck`, `npm run lint`, `npm run build`, `npm run types:check`,
`npm run test:browser`, then separately `npm run test:launcher` after the browser
server stops. Python: `uv run python scripts/verify.py`.

No catalog, domain contract, engine or Streamlit file was changed. The existing
Plotly bundle-size advisory remains Task 13. The unrelated missing thesis files
continue to govern administrative completion under Project Rule 8.
