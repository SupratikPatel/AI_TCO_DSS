# AI_TCO_DSS
AI Total cost of ownership design support system

## Commands

Run from the repository root after `uv sync`:

- Tests: `uv run pytest`
- Task verification (focus test paths are optional): `uv run python scripts/verify.py`
- Catalog validation: `uv run ai-tco-validate`
- Calibration report (writes `reports/calibration.csv`): `uv run ai-tco-calibrate`
- Dashboard: `uv run streamlit run src/ai_tco_dss/ui/app.py`
