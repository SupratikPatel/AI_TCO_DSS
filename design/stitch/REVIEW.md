# Task 8 browser and reference review

Reviewed 2026-11-08 in real Playwright Chromium on Windows, device scale factor 1.
Canonical assets were exported through the connected Stitch MCP, project
12247395809959632226. All twelve HTML files, screenshots and design-system JSON
are preserved. See `manifest.json` for resource names, retrieval date, nominal
screen sizes and actual downloaded raster dimensions.

The light/dark TCO JPEGs are 1920 px wide despite nominal 2560 px screen metadata.
Compare them at 1280 CSS px (scale 2/3); the PNG memory reference is normalized
from its recorded width. `comparison.html` places normalized references beside
the implementation without changing the exported originals.

## Visual findings

- The 1280 px light/dark TCO implementation reproduces the 280 px scenario rail,
  64 px project header, five aligned KPI cards, selected tab treatment, grouped
  simulator toolbar, chart/accounting split, legend, warning and audit footer.
- Inter/JetBrains Mono are served locally. Borders, radii, spacing and semantic
  surface tokens follow the actual canonical screens. Dark mode uses the screen's
  inline dark override rather than the conflicting global design prose.
- Screenshots cover TCO and memory in both themes at 1280, 1440, 768 and 390 CSS px.
  Desktop retains the fixed rail; tablet/mobile reflows scenario controls above
  the workspace, with stacked content on mobile. Automated checks confirm no
  document-level horizontal overflow. Dense timeline data scrolls inside its panel.
- Full names are repeated in the anchor/pairing heading and wrap without clipping.
  Accounting rows and legend names remain readable. The reference's clipped table
  is expanded so every cost component is visible, increasing total page height.
- Memory uses real segmented Python results, usable-capacity markers, pairing
  details and explicit OOM/eviction text. Its one selected pairing is the Task 8
  service slice, replacing the source's invented multi-pair results.
- Keyboard arrow/Home/End tab navigation, visible focus and labelled inputs work.
  Review caught and fixed primary-button hover contrast. Loading preserves the
  shell; catalog errors offer retry; calculation errors preserve and identify the
  last valid result. Infeasible memory is a successful result with an OOM message.

## Intentional scope and semantic differences

- Live Python values replace all generated numbers and sources. For the default
  RTX PRO 6000 ×4 / gpt-oss-120b INT4 anchor, break-even versus C is month 49,
  not the generated month 19. This session did not recalibrate those estimates.
- The recommendation KPI and Ranking tab clearly await Task 9. No invented score,
  recommendation or rejection explanation is presented. Five KPI meanings remain
  stable when switching tabs and refer to the selected TCO anchor.
- Normal hides Expert controls. Available Expert financial settings affect the
  Python scenario; weights, TOPSIS and FX overrides remain Tasks 9–10.
- No NPV/WACC toggle, certification, cryptographic claim, account or feedback
  control is simulated. Audit/download controls are disabled with Task 12 text.
- EUR converts displayed money only. Requests and Python results remain USD.
  Rental/hybrid timelines are reused. Baseline D is labelled output market value;
  absent series are omitted from chart and legend.
- Task 11 retains the full chart-semantic/KPI/accessibility polish scope, including
  more detailed break-even markers, utilization shading, memory annotations and
  final review of all three completed tabs. Task 13 owns production serving,
  bundle/performance work, CI and Streamlit retirement.

## Reproduction and evidence

From the root, after `uv sync --locked`, `npm ci` and `npx playwright install chromium`:

- `npm run dev` → Vite 5173 + API 8000, same-origin development proxy.
- `npm run test:browser` → real API/browser interactions and reviewed raster checks.
- Baselines: `frontend/tests/web.spec.ts-snapshots/` (Windows Chromium DPR 1).
- `npm run test:launcher` verifies startup, proxy and release of both ports.
- `npm test` verifies primitives, currency formatting and stale/error request state.
- `npm run typecheck`, `npm run lint`, `npm run build`, `npm run types:check` pass.
- API/direct-service parity and error tests pass. Python ruff, format, strict mypy
  and catalog validation pass. The full Python run reports **652 passed, 3 xfailed,
  3 failed**; failures are solely missing `thesis/thesis_notes.md` and
  `thesis/literature.bib` in pre-existing unrelated tests. Those tests are unchanged.

Visual review is complete for the Task 8 foundation and size/TCO slice. This is
not sign-off for the later ranking/audit or complete web cutover. The overall
Task 8 status remains in progress only because Project Rule 8 requires a full
zero-failure Python suite; the unrelated thesis files were not fabricated.
