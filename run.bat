@echo off
rem Start the React UI and Python API. Double-click or run: run.bat
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

where node >nul 2>nul
if errorlevel 1 (
    echo Node.js is not installed. Install Node.js 22.12 or newer from https://nodejs.org/
    echo Then open a new terminal and run run.bat again.
    pause
    exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo npm is not available. Reinstall Node.js with npm included.
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

if not exist "node_modules\vite\bin\vite.js" (
    echo Installing the web dependencies...
    call npm.cmd ci --no-audit --no-fund
    if errorlevel 1 (
        echo Installing the web dependencies failed. See the messages above.
        pause
        exit /b 1
    )
)

echo Starting AI TCO DSS at http://127.0.0.1:5173
echo Keep this window open. Press Ctrl+C to stop the UI and API.
call npm.cmd run dev -- --open
if errorlevel 1 (
    echo The application stopped. See the messages above for any startup errors.
    pause
    exit /b 1
)
