# Task 11 presentation and accessibility review

Reviewed 2026-11-08 against the canonical Stitch TCO light/dark, ranking,
memory-fit and Expert exports in `design/stitch/`. Chromium on Windows, DPR 1,
1280/1440/768/390 CSS px. [Side-by-side review](presentation-comparison.html).

The shell retains the 280 px rail, 64 px header, Inter/JetBrains Mono typography,
five aligned desktop KPI cards and chart/accounting proportions. Tablet stacks
the chart and accounting panels and reflows the ribbon; mobile retains all five
cards and full names. Dense tables scroll inside labelled, keyboard-focusable
regions. The stronger input boundaries intentionally improve contrast over Stitch.

The single shared ribbon always describes rank one, regardless of active tab,
selected ranking row or independent simulator pairing. It distinguishes loading,
empty, failed and missing metrics, shows one-decimal utilization with text badges,
both monthly savings measures and the complete no-break-even wording. The empty
state button switches to Ranking, opens rejected candidates and focuses its summary.
The D-09 fallback on-premise comparison anchor is explicitly identified when it
differs from a non-on-premise winner; no new break-even formula is introduced.

All monetary KPIs, ranking/contribution/accounting/timeline tables, cost axes and
hover labels now use two decimals with $/€ symbols. Conversion is presentation only;
raw USD values and Python break-even/ranks are preserved. Retained TCO results keep
the successful request's FX rate. The existing FX-override and Normal-mode tests
continue to exercise their original behavior.

Chart trace colours use named Okabe-Ito constants in both themes and C-004 styles.
Black traces and thresholds retain black, with a CSS light outline in dark mode;
legend swatches sit on a neutral white backing. D adds diamond markers. Dash-dot
swatches are drawn as SVG rather than being collapsed into dotted CSS borders.
Computed series alone appear; eligible A is solid, blocked A is dashed and explicitly
non-compliant. Every returned crossing gets a `t*` marker except blocked A, and absent
crossings have text notes. The <70% warning shades the full plot. Chart and table
compliance/OOM labels remain understandable in greyscale. Hybrid timeline transport
does not include component compliance, so its legend directs the reader to component
evaluation rather than inferring a compliant result from a weighted average (C-042).

Memory charts preserve the five segment order, add eviction hatching and text,
show every supplied usable-memory/system-RAM threshold within the axis range, and
label AA v5 and token agreement or n/a. Exact segment/capacity values remain in the
adjacent text breakdown. Python determines fit; the summed bar is not a new test.

Keyboard checks cover skip-to-analysis, roving tabs/Home/End, rejected disclosure,
focusable scrolling data and native labelled controls. Browser contrast assertions
check visible KPI/field/help text at >=4.5:1 and input boundaries at >=3:1 in both
themes at every target width. Focus rings and reduced-motion styling are explicit.
The checks are targeted accessibility regressions, not a claim of complete WCAG certification.

Test-first evidence: the new suite first failed on the missing KPI component, then
on whole-unit money, chart palette/labels, absent-series/no-data and memory semantics.
The first new browser run failed on missing skip navigation. Existing tests were
retained; only monetary expectations and the ranking-error locator changed to match
the new two-decimal requirement and separate KPI/ranking error messages.

Run `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`,
`npm run types:check`, `npm run test:browser` and, after the browser server stops,
`npm run test:launcher`. Python: `uv run python scripts/verify.py`.
The Plotly bundle advisory remains Task 13. Audit drawer/downloads remain Task 12;
Streamlit and numerical engines/contracts/catalog files are unchanged.

Final results: **48 Chromium checks**, **25 frontend tests**, typecheck/lint/build,
OpenAPI type drift and the separately run launcher check pass. All 37 screenshot
baselines were reviewed and refreshed for the shared presentation. API/service focus:
13 passed (including four new SAW/TOPSIS/FX parity cases). The full Python verification
passes ruff/format, strict mypy and catalog validation, then reports **717 passed,
3 calibration xfailed and 3 failures solely from missing thesis/thesis_notes.md and
thesis/literature.bib**. No new data contradiction or numerical change was introduced.
Tasks 8-11 remain administratively in progress under Project Rule 8.

Scheduling note: the first Python run overlapped snapshot updates, causing the
unchanged relocation no-op test to observe repository status changing. It passes
with files held steady in the final full run. An early launcher attempt encountered
the browser's occupied port; its final separate run verifies startup, proxy and cleanup.
