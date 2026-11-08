# Task 9 browser and reference review

Reviewed 2026-11-08 against `design/stitch/8630bdf57aa340e0acb5765e9065c589.png`
and the Task 8 shell tokens. [Side-by-side comparison](ranking-comparison.html).
Screenshots are real Playwright Chromium, Windows, DPR 1.

The Ranking tab now opens by default. It follows the reference's bordered recommendation
card with blue leading rule, icon, contribution chips and right-aligned aggregate score;
dense selected-row table; collapsed rejected-candidate section; and audit footer.
The shared five-card ribbon, 280 px rail, compact header, Inter/JetBrains Mono fonts,
spacing and light/dark tokens remain consistent with the canonical TCO shell.

Real defaults produce **36 admissible and 637 rejected candidates**. The leading result
is RTX Pro 6000 Blackwell 96 GB x4 + DeepSeek V4.1 Flash INT4, SAW 0.817 (rounded).
No generated mockup result, benchmark, TOPSIS score or sovereignty criterion is copied.
Normal mode exposes use case, active users and preset, plus display currency. Expert
values are ignored on returning to Normal. Full Expert controls remain Task 10.

The new ranking screenshots cover 1280/1440/768/390 CSS px in both themes under
`tests/ranking.spec.ts-snapshots/`. Review checks full candidate names, selected states,
readable values and no page-level overflow. The dense ranking/contribution tables scroll
within their panels, including on mobile. Tablet/mobile stack the scenario rail above
the workspace. Long KPI names grow the ribbon; final KPI density remains Task 11.

Intentional differences: SAW replaces the reference's TOPSIS in Normal mode; the six
specified criteria replace its invented sovereignty criterion; eight ranking rows and
ten rejections per page keep the full catalog navigable. All candidates and all failed
filters remain reachable. Selecting a row displays raw, normalized, weight and
contribution values from Python. The reference's fabricated compliance/certification
and report controls are omitted. Audit/downloads remain explicitly deferred to Task 12.

Browser flows verify real use-case/preset/user changes, inline invalid-user retention,
display-only EUR, selection, complete rejection reasons, server-error clearing, empty
results, delayed response cancellation, and memory/ranking request independence.
Component tests additionally cover Normal defaults ignoring prior Expert fields and
the shared request lifecycle. Existing memory/TCO snapshots were refreshed because
their shared KPI ribbon now describes the real recommendation.

Reproduce with `npm run test:browser`; run `npm run test:launcher` separately because
both use ports 5173/8000. Other checks: `npm run typecheck`, `npm run lint`,
`npm run build`, `npm test`, `npm run types:check`. The build retains the existing
Plotly bundle-size advisory; bundle/performance work remains Task 13.

Final verification: **23 browser tests pass**, including all eight new ranking screenshot
baselines and existing memory/TCO comparisons. Seven component tests and all frontend
checks pass; the launcher check passes separately. Python focus: 49 passed. Full Python:
**703 passed, 3 calibration xfailed, 3 missing-thesis-document failures**. The three
failures are unchanged and remain outside Task 9. Warm recommend median: 0.247 s over
five runs. Task 9's administrative completion gate remains in progress under Project Rule 8.
