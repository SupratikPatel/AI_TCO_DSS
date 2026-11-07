#!/usr/bin/env bash
# Start the AI TCO DSS Dashboard (macOS, Linux, Git Bash). Run: ./run.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is not installed. Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Then open a new terminal and run ./run.sh again."
    exit 1
fi

# Create or update .venv exactly as pinned in uv.lock (downloads Python 3.12 if needed).
uv sync --locked

URL="http://localhost:8501"
echo "Starting the Dashboard at $URL  (press Ctrl+C to stop)"
# Headless mode skips Streamlit's first-run e-mail prompt; open the browser ourselves.
(
    sleep 4
    if command -v open >/dev/null 2>&1; then open "$URL"
    elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"
    elif command -v explorer.exe >/dev/null 2>&1; then explorer.exe "$URL"
    fi
) >/dev/null 2>&1 &
exec uv run streamlit run src/ai_tco_dss/ui/app.py --server.headless true --server.port 8501 "$@"
