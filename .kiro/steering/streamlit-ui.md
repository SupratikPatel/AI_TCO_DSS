---
inclusion: always
---

# Streamlit UI work

Before creating or changing any Streamlit code (any file under `src/ai_tco_dss/ui/`, or a test that uses `streamlit.testing.v1.AppTest`), activate the `developing-with-streamlit` skill and follow it. The skill finds the reference docs bundled with the installed Streamlit version, so the code matches that version.

- Most relevant references for this project: `performance.md` (Simulator_Cards with `@st.fragment`, `st.cache_data`, `st.cache_resource`), `testing.md` (AppTest), `session-state.md`, `layouts.md`, `dashboards.md`, `charts.md`, `theme.md`.
- If the skill is not available, read the bundled docs directly: `.venv/Lib/site-packages/streamlit/.agents/skills/developing-with-streamlit/SKILL.md` (Windows) or `.venv/lib/python3.12/site-packages/streamlit/.agents/skills/developing-with-streamlit/SKILL.md` (macOS, Linux), and the `references/` folder next to it.
- To reinstall the skill: run `uv run streamlit skills --yes`. On Windows without Developer Mode this installs globally to `~/.agents/skills` and `~/.claude/skills`; copy `developing-with-streamlit` from there to `~/.kiro/skills/` for Kiro.
- Project rules still apply: the Okabe-Ito palette and archetype styles of `specs/07_DATA_CORRECTIONS.md`, UI imports only from `ai_tco_dss.services`, `ai_tco_dss.domain` and `ai_tco_dss.ui`, and one `@st.fragment` per Simulator_Card.
