# Task 13 web cutover review

Task 13 retires the Streamlit runtime and serves the existing React UI and FastAPI
on one production origin. No numerical engines, domain contracts, catalog entries,
frontend components, styling or screenshot baselines changed.

Test-first evidence: new acceptance checks failed on the absent production factory,
CI, combined web verification, Streamlit retirement and extension-seam table. The
production-process test failed to start before implementation. Existing service
concurrency and warm recommendation budgets passed without numerical changes.
A test-fixture error initially placed the FX override inside financials; corrected
to the existing Scenario field before testing concurrency.

The mixed TCO/AppTest check was first extracted to a separate temporary UI test;
105 TCO/performance/UI checks passed before retirement. Only the four AppTest cases
(three smoke cases and that separated TCO widget case) were removed. The pure
performance_rows helper moved from cards.py into formatting.py, preserving its
assertions. Pure Python chart/theme/formatting and all numeric/property/calibration
regressions remain. Three boundary-test parameters disappear with the three deleted
adapter modules. Streamlit and 20 now-unused transitive packages leave the lock.

New coverage exercises ten distinct real scenarios with simultaneous thread starts,
exact field-by-field sequential/concurrent equality, unchanged shared catalog,
concurrent API clients, 100 generated deterministic recommendation scenarios and
five warm recommendations with median <500 ms. Two isolated browser contexts
verify independent user counts and display currencies and initial ranking <5 s.
Production tests check SPA routes, hashed JS/CSS, API/docs/errors, missing build,
path traversal, cache headers, process termination and release of its port.
The launcher test also occupies the API port, checks sibling cleanup and proves the
unrelated port owner survives. The initial custom raw HTTP test server hung on a
connection; replaced it with Node's HTTP server and explicit connection cleanup.

Combined verification runs Python/API/ruff/format/mypy/catalog and npm
types/lint/components/drift/build/browser/launcher checks, reports all failures,
and returns nonzero on any failing stage. Browser checks run the built production
server and stop before launcher tests. CI uses the reviewed Windows Chromium
platform and separate locked Python/web/browser install steps. Remote Actions
execution requires the author to commit/push; no commit or push was made here.

Fresh staged-checkout evidence: exported the Git index to a new temporary directory
with no .venv/node_modules/dist; uv sync --locked, npm ci, npm run build,
API-type drift and all three launcher/production-process tests passed. This
rehearses a clean checkout without touching unrelated untracked files.
Bash launcher uses the same npm/uv paths; the runtime rehearsal was on Windows.

The unchanged basic Plotly bundle remains 1.46 MB raw /480 KB gzip. Explicit
<1.6 MB raw /512 KB gzip initial-JS budgets prevent silent growth. Vite's advisory
is retained and quantified; compression is a deployment proxy responsibility.
No empirical accuracy or public multi-user hosting claim follows from local budgets.

The author restored/staged thesis notes and bibliography in separate work during
this task. Those files, their untracked tests and pre-existing administrative
status changes are preserved. Numerical refinement (C-035–C-040) and .kiro
relocation remain deferred. Final verification results are recorded in progress.md.

Final combined verification: 733 Python passed /3 calibration xfailed, 28 component
tests, 60 production Chromium checks and 3 separate launcher/production checks all
pass. Ruff/format, strict mypy, catalog, frontend type/lint/build/OpenAPI drift pass.
Both themes at 1280/1440/768/390 CSS px match unchanged reviewed baselines. No
remaining functional or administrative gate; the author-restored thesis files pass.
