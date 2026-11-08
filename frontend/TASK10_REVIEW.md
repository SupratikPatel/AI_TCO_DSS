# Task 10 Expert and TOPSIS review

Reviewed 2026-11-08 against canonical Stitch Expert validation
`1a362749fca6433ba9a64bc017c46794`, Ranking `8630bdf57aa340e0acb5765e9065c589`,
and the light/dark tokens in `design/stitch/TOKENS.md`.
Open `expert-comparison.html` for the reference comparison and viewport evidence.

The compact 280 px scenario rail now includes staffing/tariff/PUE/FTE, constraint
switches, resale, local share, FX, TPS/TTFT, concurrency, context, quantization,
harness/pruning/thinking, budget, six weights and SAW/TOPSIS. Workload and ranking
sections can collapse; all controls remain reachable by scrolling the rail.
The tablet rail uses two columns; mobile uses normal page flow. The ranking table
scrolls within its focusable panel, with adjacent SAW rank, TOPSIS rank and
three-decimal closeness columns. Full candidate names wrap within a dedicated
275 px column. Both themes retain explicit labels, visible focus and text errors.

Intentional differences from generated examples: five specified KPIs replace the
reference's four invented ones; sovereignty stays a hard filter. Real catalog IDs,
quality/fallbacks, costs and results replace every mock value. The default TOPSIS
leader is RTX Pro 6000 x1 + Qwen 3.8 Flash Next INT2, closeness 0.758, SAW rank 9.
It uses exactly the same 36 admissible / 637 rejected candidates as SAW. The SAW
leader and its score remain unchanged. TOPSIS distances and closeness come from
Python; the contribution detail is explicitly labelled as SAW for comparison.

Precision semantics preserve Req 27 enumeration: ranking compares every supported
weight precision; the Expert quantization control sets KV precision for candidate
sizing. Each independent simulator retains its own weight precision selector.
The FX input is blank for the file rate, accepts 0.50-2.00 with at most six decimals,
and changes converted EUR input costs after Apply. Display currency never submits
a scenario or changes stored USD results/ranks/break-even. Each retained TCO
projection uses the rate from its successful request, including after a newer
projection fails. No catalog file is modified.

Preset weights are supplied by Python through `/options` and generated OpenAPI
types. Entering Expert initializes the selected preset and SAW. Returning to Normal
preserves use case/users/preset and ignores all Expert values. Expert inputs are
drafts until Apply; invalid FX, weights and server-validated inputs preserve the
active scenario. Validation requests are aborted on edits/mode switches; existing
calculation cancellation prevents older results replacing newer ones.

Verification: 15 new Chromium checks include both themes at 1280/1440/768/390 CSS
px, inline validation, actual payloads, method/preset/mode transitions, FX and USD
invariants, delayed validation and retained projections. The complete browser suite
contains 38 checks. Existing Normal/memory/TCO screenshot baselines are preserved.
Nine component/helper checks and frontend typecheck/lint/build/types:check pass.
The production build retains the existing Plotly bundle advisory (Task 13).
Python focus/API/property checks pass; full suite: 713 passed, 3 calibration xfailed,
3 unchanged failures from missing thesis/thesis_notes.md and thesis/literature.bib.
Task 10 remains administratively in progress under Project Rule 8.
Audit/export stays Task 12; final KPI/chart/currency-rounding polish stays Task 11.

Reproduce: `npm run test:browser`, `npm test`, `npm run typecheck`, `npm run lint`,
`npm run build`, `npm run types:check`. Run `npm run test:launcher` separately
because it shares ports 5173/8000 with the browser suite.
