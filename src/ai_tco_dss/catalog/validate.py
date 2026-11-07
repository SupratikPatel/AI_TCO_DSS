"""Validate_CLI: ``uv run ai-tco-validate [--root DIR]`` (design.md § "Validate_CLI").

Runs every check over every file, prints one line per error
(``path: field_path: message``) and the total, and exits 1; on success prints the
per-type file counts and exits 0.
"""

import argparse
import sys
from pathlib import Path

from ai_tco_dss.catalog import loading

REPOSITORY_DATA_ROOT = Path(__file__).resolve().parents[3] / "data"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the catalog under the data root.")
    parser.add_argument("--root", type=Path, default=Path("data"), help="data directory")
    parser.add_argument(
        "--mvp",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="check MVP_Catalog completeness (default: only for the repository data/ root)",
    )
    args = parser.parse_args(argv)
    root: Path = args.root
    mvp: bool = args.mvp if args.mvp is not None else root.resolve() == REPOSITORY_DATA_ROOT
    report = loading.load_catalog(root, mvp=mvp)
    if report.errors:
        for error in report.errors:
            print(f"{(root / error.file).as_posix()}: {error.field}: {error.message}")
        count = len(report.errors)
        print(f"{count} error" if count == 1 else f"{count} errors")
        return 1
    c = report.counts
    print(
        f"Validated {c['hardware']} hardware, {c['model']} model, {c['benchmark']} benchmark, "
        f"{c['reference']} reference files: 0 errors"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
