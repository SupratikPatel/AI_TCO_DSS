---
inclusion: manual
---

# Legacy Streamlit maintenance only

The author rejected the Streamlit approximation on 2026-11-07. The target frontend
is React/TypeScript with Vite, Tailwind and shadcn/ui, connected to Python via FastAPI.
Read `specs/09_WEB_FRONTEND_MIGRATION.md` and Requirement 43. Do not use this file as
an instruction to style the legacy UI or constrain the web design to native widgets.

Use the developing-with-streamlit skill only if deliberately maintaining existing
Streamlit code while the migration is underway. Preserve numeric regressions when
retiring mixed AppTest/calculation test files. Retire this legacy guidance at cutover.
