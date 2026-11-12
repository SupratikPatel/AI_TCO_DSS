---
inclusion: manual
---

# Streamlit retirement record

Task 13 retired the Streamlit app/cards/session-state adapter, AppTest checks,
configuration and dependency after verifying React equivalents. There is no legacy
product launcher. Pure chart/theme/formatting references under ui/ remain for Python
regression tests and do not require Streamlit.

Use specs/09_WEB_FRONTEND_MIGRATION.md, Requirement 43 and frontend/TASK13_REVIEW.md
for the active web workflow. Preserve numeric tests when changing reference helpers.
Do not reinstall Streamlit or restore styling work as part of routine web maintenance.
