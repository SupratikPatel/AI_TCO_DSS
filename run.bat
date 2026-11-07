@echo off
rem Start the AI TCO DSS Dashboard (Windows). Double-click or run: run.bat
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv is not installed. Install it with:
    echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo Then open a new terminal and run run.bat again.
    pause
    exit /b 1
)

rem Create or update .venv exactly as pinned in uv.lock (downloads Python 3.12 if needed).
uv sync --locked
if errorlevel 1 (
    echo Installing the dependencies failed. See the messages above.
    pause
    exit /b 1
)

set "URL=http://localhost:8501"
echo Starting the Dashboard at %URL%  (press Ctrl+C to stop)
rem Headless mode skips Streamlit's first-run e-mail prompt; open the browser ourselves.
start "" /b cmd /c "timeout /t 4 /nobreak >nul & start %URL%"
uv run streamlit run src/ai_tco_dss/ui/app.py --server.headless true --server.port 8501 %*
