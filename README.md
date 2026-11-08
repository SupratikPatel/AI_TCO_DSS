# AI_TCO_DSS

Enterprise AI infrastructure decision support for model fit, inference performance,
five-year costs and explained recommendations.

## Frontend migration status

The target product is a React/TypeScript web UI implementing the Google Stitch
design, backed by FastAPI and the existing Python services. Only the presentation
layer moves to TypeScript; the engines, catalog, validation and decision logic stay
in Python. The Streamlit prototype did not meet the intended visual standard.

Task 8 implements the web foundation and real size/TCO vertical slice. Memory fit
and 60-month costs call the existing Python services. Rankings, full Expert
weights, audit and downloads remain assigned to Tasks 9–12 and are labelled as
pending. Streamlit is retained until the Task 13 cutover.

See the [migration contract](specs/09_WEB_FRONTEND_MIGRATION.md),
[visual evidence](design/stitch/REVIEW.md) and
[task plan](.kiro/specs/ai-tco-dss-mvp/tasks.md).

## Working Python commands

Run from the repository root after `uv sync`:

- Tests: `uv run pytest`
- Python verification (focus test paths optional): `uv run python scripts/verify.py`
- Catalog validation: `uv run ai-tco-validate`
- Calibration report (writes reports/calibration.csv): `uv run ai-tco-calibrate`
- JSON Schema export: `uv run ai-tco-schemas`
- Legacy Dashboard: `uv run streamlit run src/ai_tco_dss/ui/app.py`

Double-click `run.bat` on Windows to start the web UI/API and open your browser.
It syncs Python dependencies and installs web dependencies on first run.
`run.sh` still starts the legacy prototype.

## Working web commands

- Install Python dependencies: `uv sync --locked`
- Install frontend dependencies from the root: `npm ci` (Node 22.12+; npm workspaces, one root lockfile).
- Start frontend and API together from the root: `npm run dev`.
- Open `http://127.0.0.1:5173`. Vite proxies `/api` to FastAPI at `127.0.0.1:8000`.
- Press Ctrl+C to stop both owned child processes. A startup failure also stops the other child. The launcher uses the `.venv` installed by uv and does not require activating it.
- API documentation: `http://127.0.0.1:8000/docs`; OpenAPI: `/openapi.json`.
- Frontend type check: `npm run typecheck`
- Frontend lint: `npm run lint`
- Frontend production bundle: `npm run build` (writes `frontend/dist`; production serving is finalized in Task 13).
- Component/state tests: `npm test`
- Install the test browser once: `npx playwright install chromium`
- Browser flows and screenshot comparisons: `npm run test:browser`
- Launcher startup, proxy and cleanup check (ports 5173/8000 must be free): `npm run test:launcher`
- Generate API types: `npm run types:generate`; drift check: `npm run types:check`.
- Task 8 Python checks: `uv run python scripts/verify.py tests/unit/test_api.py tests/integration/test_web_api.py tests/unit/test_web_foundation.py`

On PowerShell systems blocking npm.ps1, use `npm.cmd` / `npx.cmd` with the same
arguments. Python dependencies remain managed by uv. Numerical results remain USD;
EUR changes presentation only, using the dated catalog FX rate.

Playwright baselines live in `frontend/tests/web.spec.ts-snapshots/`. They were
reviewed on Windows Chromium at DPR 1. Review changes against the exported Stitch
screens before running `npm run test:browser -- --update-snapshots`; a generated
baseline alone does not establish fidelity. Other operating systems require their
own reviewed raster baselines. Vite reports a large Plotly bundle; bundle/performance
polish is deferred to the cutover work.

The complete Python suite still reports three unrelated failures because
`thesis/thesis_notes.md` and `thesis/literature.bib` are missing. These files and
their untracked tests were present as unrelated work at session start and are not
changed or staged by Task 8. Calibration has three documented expected failures.
