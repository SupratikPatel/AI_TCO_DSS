# AI TCO DSS

React/TypeScript, Vite, Tailwind and shadcn UI over FastAPI and Python services.
Ranking, Normal/Expert controls, independent memory/TCO simulators, audit and JSON/CSV
ZIP downloads are implemented. All sizing, financial and ranking math stays in Python.

## Clean checkout

Install Git, uv and Node.js 22.12+ (with npm). From the repository root:

```sh
uv sync --locked
npm ci
```

Start both services: `npm run dev`. Open http://127.0.0.1:5173.
Vite proxies /api to FastAPI at 127.0.0.1:8000. Ctrl+C stops both owned children;
a child startup failure stops the sibling. Keep these ports free.
No environment activation or credentials are required; catalog data is local.

Windows: double-click `run.bat`. macOS/Linux/Git Bash: `bash run.sh`.
Both sync the locked Python environment, install web dependencies on first use,
start the web app and open the browser. After a lockfile change, run `npm ci` again.
PowerShell installations blocking npm.ps1 can use `npm.cmd` and `npx.cmd`.

## Production on one origin

```sh
npm run build
npm run start
```

Open http://127.0.0.1:8000. FastAPI serves frontend/dist and /api/v1 on the same
origin; Node and Vite are not production servers. The launcher binds loopback.
For a hosted deployment use `uv run uvicorn ai_tco_dss.api.production:create_app
--factory --host 0.0.0.0 --port 8000` behind a TLS reverse proxy and access controls.
Run from this checkout's root: catalog data, schema files and the web bundle are
checkout assets, not a standalone wheel. Set AI_TCO_WEB_DIST to an absolute build
path if needed. Startup fails with build instructions when index.html is missing.
API docs: /docs; OpenAPI: /openapi.json. Unknown API paths and missing assets return
404 rather than app HTML. Client routes fall back to index.html. Hashed Vite assets
cache for one year; index.html revalidates. Rebuild before restarting after UI edits.
The API holds no browser scenario/session state; each worker loads its own immutable
catalog. No authentication, shared project storage or internet-facing service is implied.

## Verification

Install the test browser once: `npx playwright install chromium`.
One combined entry point: `uv run python scripts/verify.py` (optional focus test paths
may follow). It runs focus tests, ruff/format, strict mypy, catalog validation, full
Python/API/property/calibration tests, web types/lint/components/OpenAPI drift/build,
Chromium flows/screenshots, then launcher and production-process tests. Every stage
runs even after failures; any failing stage makes the command fail. Browser servers
stop before launcher tests, which share ports 5173/8000. Do not run them concurrently.

Individual commands: `uv run pytest`, `npm run typecheck`, `npm run lint`, `npm test`,
`npm run types:check`, `npm run build`, `npm run test:browser`, `npm run test:launcher`.
Generate transport types with `npm run types:generate` after API schema changes.
Browser checks run the built same-origin production app (run `npm run build` first
when invoking browser checks alone). CI uses Python 3.12, Node 22 and Windows Chromium because the reviewed raster
baselines are Windows/DPR 1. It runs the same combined command on push and PR.
Review screenshot changes against design/stitch before deliberately updating them;
never regenerate baselines merely to obtain green tests. Both themes at
1280/1440/768/390 CSS px and prior state/currency/export invariants remain covered.

Python tests disable external network access. Performance acceptance measures five
warm real-catalog recommendations (median <500 ms); concurrency compares ten distinct
scenarios sequentially and across ten threads, including concurrent API clients.
These are local budgets, not production load guarantees. Keep this check separate
from other CPU-heavy test processes.

The prior missing-thesis gate was resolved by separately staged author work during
Task 13. The thesis files and their tests are preserved. Three calibration xfails
remain tied to C-035/C-036; functional implementation does not establish empirical
numerical accuracy. See progress.md and specs/07_DATA_CORRECTIONS.md.

The basic Plotly/React bundle measures about 1.46 MB raw / 480 KB gzip. The build
retains Vite's size advisory; production-process tests enforce <1.6 MB raw /512 KB
gzip for initial JavaScript. This is a measured regression budget, not a claim of
small first-load transfer. Configure compression at the reverse proxy; the gzip
measurement is a build-size check. Browser acceptance additionally budgets two
independent initial ranking sessions at <5 seconds on the test machine.

## Catalog, numerical validation and extension points

- Validate provenance/catalog: `uv run ai-tco-validate`.
- Calibration report: `uv run ai-tco-calibrate` (writes reports/calibration.csv).
- JSON Schema export: `uv run ai-tco-schemas`.
- USD is canonical; display EUR changes presentation only. Expert FX overrides
  legitimately change EUR-derived USD inputs. Retained projections keep original FX.
- See [extension seams](specs/00_INDEX_AND_AGENT_ROUTER.md#extension-seams-post-mvp),
  [migration contract](specs/09_WEB_FRONTEND_MIGRATION.md) and
  [visual reviews](frontend/TASK12_REVIEW.md).

Streamlit's adapter, AppTest checks, config and runtime dependency were retired in
Task 13 after the React equivalents passed. The single mixed TCO/AppTest test was
separated before retirement; all numeric TCO/performance tests remain. Pure Python
Plotly chart/theme/formatting references under ui/ remain for regression testing;
they do not import Streamlit or launch a product UI. Historical spec discussions
of fragments and Streamlit layouts describe the retired prototype.
Numerical calibration refinement and .kiro relocation remain deferred.
