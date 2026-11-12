# Stitch web UI design contract

Decision date: 2026-11-07. The author rejected the Streamlit approximation. Implement
these references in a dedicated React/TypeScript frontend with full CSS/layout
control, connected to Python services through FastAPI. This is an acceptance
reference, not a suggestion to apply a few colours to a generic dashboard.
Read [the migration plan](09_WEB_FRONTEND_MIGRATION.md) and Requirement 43.

## Canonical Stitch resources

Project: `projects/12247395809959632226` - AI TCO Decision Dashboard.

| Screen | Screen ID | Role |
|---|---|---|
| TCO light | 2b49b16649ff4d66a9ce09206ede2ff5 | Canonical desktop shell and chart/table layout |
| TCO dark | 01e280423d614d30bb7b5af1f83640d4 | Dark appearance counterpart |
| Ranking | 8630bdf57aa340e0acb5765e9065c589 | Recommendation card, ranking table, rejected list |
| Memory fit | cff160e18cbe4ad3b7689fb170e0b87f | Pairing controls, memory bars, detail cards |
| Audit dark | f9fbe84561b5418384aa720d8be2f799 | Audit typography and formula/source panels |
| Expert validation | 1a362749fca6433ba9a64bc017c46794 | Expanded controls and inline validation |
| Empty/error | 82cb868b8dc84b4fb2915443cba04181 | Empty result visual treatment; separate empty vs error semantics |
| Chart variants | 02d402dd234840b298535ed66fb8be06 | Timeline hover and alternate chart states |
| Style guide | 2d5ba913f855478c8853bb60e47a0ff7 | Design tokens and component examples |
| EUR dark | 6d0ecc014fbe4fc3b93de1d35b7897fe | Currency and dark-mode reference |
| Loading dark | 1d7faea473ce4805ab89c61876e65f16 | Loading state |
| Catalog error dark | bae4f7105e3947b0b89ee53f339d3935 | Catalog failure state |

Stitch MCP authentication worked during the design review. Use its file-download
capability to export screenshot and HTML resources; record metadata in design/stitch/.
Choose canonical screenshots above when the generated design-system prose and
individual screens differ. Preserve the source exports to make visual comparisons
repeatable. All twelve canonical exports now live in `design/stitch/`; its manifest
records nominal and downloaded image sizes. See `design/stitch/TOKENS.md`,
`design/stitch/REVIEW.md` and `design/stitch/comparison.html` for implementation
tokens, real-browser evidence and normalized side-by-side comparisons.

## Required visual structure

Task 11 presentation evidence is recorded in `frontend/TASK11_REVIEW.md` and
`frontend/presentation-comparison.html`. Shared rank-one KPIs, two-decimal monetary
displays, C-004 chart styles, explicit missing/compliance/OOM states and keyboard
access are checked in both themes at 1280/1440/768/390 CSS px. Control borders are
stronger than the canonical export for contrast; tablet chart/accounting panels
stack. Dark black traces retain the C-004 colour with a CSS contrast outline.
The Task 11 screenshots refresh the shared presentation in the earlier baselines;
Tasks 8-10 behavior is preserved. Audit/export is implemented; see frontend/TASK12_REVIEW.md.

- Compact full-height left scenario sidebar, product identity, Normal/Expert switch,
  scenario controls and currency selection. Expert parameters are hidden in Normal.
- Slim project header and five aligned KPI cards with consistent meanings: recommended
  architecture, break-even, monthly savings, effective speed/TTFT, utilization.
- Ranking, Memory fit and 60-month TCO tabs, with an obvious selected tab.
- TCO: grouped input toolbar, interactive chart beside cost breakdown, legible legend
  and explicit utilization warning. Match relative widths and whitespace to the source.
- Ranking: top recommendation explanation, dense aligned table, expandable rejected
  candidates with measured values and thresholds. Support long names without clipping.
- Memory: segment bars, usable-memory thresholds, text OOM/eviction badges and pairing
  details. Audit/export stays reachable without a permanently oversized overlay.
- Inter interface typography, JetBrains Mono for quantitative/code labels, tabular
  numeric alignment, restrained borders, rounded panels and consistent spacing.
- Light and dark themes must each be deliberately designed and verified. Use semantic
  surface/text/border tokens. Chart archetypes retain ledger C-004 styles; any change
  to their meanings requires an explicit documented decision.

Use shadcn/ui as editable accessible primitives. Reproduce the Stitch component
proportions and treatment rather than accepting the library's default appearance.
Use working icons, controls, hover/focus states and responsive behavior. Account,
feedback and project-persistence features are not required just because their icons
appear in generated screens; avoid decorative controls that pretend to work.

## Data and semantics

Keep the existing Python contracts and calculations. All live values must come
through the API. Normal mode uses SAW; TOPSIS is Expert-only. Sovereignty is a hard
filter, not a replacement for the popularity criterion. Missing quality is explicit.
Do not copy generated mockup hardware/model names, source IDs, scores or formulas.

NPV/WACC discounting, P95 statistics, certification claims, cryptographic verification,
additional catalog records and generated executive reports need separate requirements.
An infeasible ranking is not a server failure. Changing weights cannot fix hard
filters. Baseline D is output market value, not a purchasable deployment option.

## Visual sign-off

Capture real-browser screenshots at 1280 CSS px against the canonical source, then
check 1440, 768 and 390 CSS px. Check both themes, all tabs, loading, validation,
empty and error states, keyboard access and readable chart/table text. Record
intentional deviations and evidence. Passing Python, API or component tests cannot
substitute for visual comparison. If browser tooling is unavailable, visual sign-off
remains pending and the frontend must not be reported as visually complete.
