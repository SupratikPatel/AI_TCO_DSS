#!/usr/bin/env bash
# Start React/Vite and FastAPI from a locked checkout (macOS/Linux/Git Bash).
set -euo pipefail
cd "$(dirname "$0")"
command -v uv >/dev/null || { echo 'Install uv, then rerun ./run.sh'; exit 1; }
command -v node >/dev/null || { echo 'Install Node.js 22.12+ with npm, then rerun ./run.sh'; exit 1; }
command -v npm >/dev/null || { echo 'Install npm with Node.js'; exit 1; }
uv sync --locked
if [ ! -f node_modules/vite/bin/vite.js ]; then npm ci --no-audit --no-fund; fi
exec npm run dev -- --open "$@"
