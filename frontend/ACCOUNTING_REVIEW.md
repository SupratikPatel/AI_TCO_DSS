# TCO accounting explanation review

Author-requested follow-up to Task 13 (2026-11-09), prompted by the cost-matrix
screenshot. Ledger C-044 records the author-approved correction to the old Requirement 23.6
financial inference. The existing USD engine results, rankings, simulator independence and
export contracts are preserved. Only the engine's low-utilization warning text
changes; it reports a percentage and asks for an actual cost comparison rather
than predicting that APIs are cheaper.

The TCO API now adds a typed accounting explanation to the exact independent
simulator projection. The original candidate/timeline/baselines remain field-for-field
equal to project_tco. No new endpoint/request, client financial arithmetic or
ranking-selected audit lookup is involved. Explanation FX, resale status, source
inputs and traces travel with the retained successful result even when newer edits
or requests fail. Non-on-premise projections do not mislabel retained local cost
traces as deployment accounting.

Each row opens a keyboard-operable full-width disclosure with its equation,
substituted inputs, USD result, source references, provenance tiers and access dates.
The catalog's unverified hardware price is explicitly labelled as an assumption,
rather than implying a measured or verified quotation. USD equations remain USD
when monetary table cells display EUR. Monetary subtotals and comparisons are
computed in Python. Six components are counted once; cash/economic subtotals are
explanatory and the full model still includes opportunity/productivity assumptions.
Resale is a separate deduction, with before/after text from the successful request.
NIM/wait disabled states and no-eviction-risk states explain zero values separately.
Baseline C identifies the model, residency surcharge, gateway, sources and 60-month
cost. Savings and existing timeline break-even describe this simulator's anchor.

Default reproduction: CapEx $71,456.00; monthly cash $3,680.23; modeled economic
costs $267.96; total monthly $3,948.19; TCO $308,347.20. Baseline C totals
$325,669.51, yielding $17,322.31 savings and break-even in month 49 under these
assumptions despite 4.7% utilization. Full-precision values produce the TCO;
multiplying rounded monthly displays can differ by cents. Low-demand coverage also
checks the opposite comparison (API cheaper, no crossing), without changing the
utilization warning into a financial verdict.

Test-first: six Python cases first failed on absent accounting; the new component
suite first failed on the missing component. Browser acceptance caught the intended
TCO screenshot change before baseline updates. A mistaken EUR fixture expectation
was corrected against the actual full-precision USD/FX calculation. Existing API
parity assertions still compare every original projection field and additionally
check the new explanation's identity. The warning regression now requires percentage
formatting and neutral comparison language.

Visual review uses the canonical Stitch typography, palette and desktop proportions
from design/stitch/TOKENS.md and the existing TCO references. Eight new calculation
disclosure captures cover both themes at 1280/1440/768/390 CSS px. The eight existing
TCO full-page captures are refreshed for the added rows; other baselines remain
unchanged. Mobile numbers, long source references and formulas wrap within the
panel; tablet stacks the accounting below the chart. The larger accounting panel
is intentional progressive disclosure of the author's requested explanations.

Final checks and handoff are recorded in progress.md. No commit or push.

Final combined verification exits 0: 739 Python passed /3 calibration xfailed,
30 frontend tests, 69 Chromium checks and 3 separate launcher/production checks.
Ruff/format, strict mypy, catalog validation and web type/lint/build/type drift pass.
The final full browser run uses the reviewed snapshots without updating them.
