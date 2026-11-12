"""One-line task verification (design.md D-12).

Usage: ``uv run python scripts/verify.py [focus test paths ...]``

Runs the focus tests, then ``ruff check``, ``ruff format --check``, ``mypy``, the
Validate_CLI (once ``ai-tco-validate`` is declared in ``pyproject.toml``) and the
full ``pytest`` suite and all web checks. Runs every step and reports all failures;
exits nonzero if any step failed.
Browser servers stop before launcher tests begin. Requires npm ci and Chromium.
"""

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE_SCRIPT = "ai-tco-validate"


def _validate_cli_declared() -> bool:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        scripts = tomllib.load(fh).get("project", {}).get("scripts", {})
    return VALIDATE_SCRIPT in scripts


def _steps(focus: list[str]) -> list[tuple[str, list[str]]]:
    python = sys.executable
    steps: list[tuple[str, list[str]]] = []
    existing = []
    for path in focus:
        if (ROOT / path).exists():
            existing.append(path)
        else:
            print(f"[verify] notice: focus path not found, skipped: {path}")
    if existing:
        steps.append(("focus tests", [python, "-m", "pytest", *existing]))
    steps += [
        ("ruff check", [python, "-m", "ruff", "check"]),
        ("ruff format --check", [python, "-m", "ruff", "format", "--check"]),
        ("mypy", [python, "-m", "mypy"]),
    ]
    if _validate_cli_declared():
        validate = shutil.which(VALIDATE_SCRIPT) or VALIDATE_SCRIPT
        steps.append(("validate", [validate]))
    steps.append(("full pytest", [python, "-m", "pytest"]))
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm") or "npm"
    steps.extend(
        (f"web {script}", [npm, "run", script])
        for script in (
            "typecheck",
            "lint",
            "test",
            "types:check",
            "build",
            "test:browser",
            "test:launcher",
        )
    )
    return steps


def main(argv: list[str]) -> int:
    failures = []
    for name, command in _steps(argv):
        print(f"[verify] step: {name}", flush=True)
        try:
            code = subprocess.run(command, cwd=ROOT, check=False).returncode
        except OSError as exc:
            print(f"[verify] cannot start {name}: {exc}", flush=True)
            code = 1
        if code != 0:
            print(f"[verify] FAILED: {name} (exit code {code})", flush=True)
            failures.append(name)
    if failures:
        print(f"[verify] failed steps: {', '.join(failures)}", flush=True)
        return 1
    print("[verify] all steps passed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
