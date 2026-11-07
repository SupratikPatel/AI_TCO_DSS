"""Relocate the original specification files into ``specs/`` (Requirement 1).

Usage: ``uv run python scripts/relocate_specs.py [--root PATH]``

- Tracked files are moved with ``git mv`` (history is kept, Req 1.4).
- Untracked files are moved and then added under the new path (Req 1.5).
- If any target already exists while its source is present, nothing is changed
  and the conflicting path is reported (Req 1.11).
- Old file names in ``specs/`` are replaced with the new names (Req 1.9).

The script is idempotent: with no source left and no old name in ``specs/`` it
changes nothing.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Original workspace-root name -> new name under specs/ (Req 1.1, 1.2).
RELOCATIONS = {
    "index_agent_router.md": "00_INDEX_AND_AGENT_ROUTER.md",
    "workload_profiler_physical_sizing_engine (1).md": "01_WORKLOAD_AND_PHYSICS_ENGINE.md",
    "financial_tco_eu_finops_cross_border_personnel_arbitrage (1).md": (
        "02_TCO_FINOPS_AND_EU_COMPLIANCE.md"
    ),
    "2026_calibrated_hardware_model_intelligence_seed_catalog (1).md": (
        "03_CALIBRATED_2026_SEED_DATA.md"
    ),
    "pydantic_v2_core_schemas_contracts (1).md": "04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md",
    "visualization_ux_standards_phased_execution_plan (1).md": (
        "05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md"
    ),
    "research_sources_benchmark_evidence (1).md": "06_RESEARCH_SOURCES.md",
}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


def _name_variants(old: str) -> tuple[str, str]:
    """The old name with the ' (1)' suffix first, then without it."""
    plain = old.replace(" (1).md", ".md")
    return plain.replace(".md", " (1).md"), plain


def _sources(root: Path) -> dict[str, Path]:
    """Old name -> existing source path at the root (either name variant)."""
    found = {}
    for old in RELOCATIONS:
        for variant in _name_variants(old):
            if (root / variant).is_file():
                found[old] = root / variant
                break
    return found


def _move(root: Path, source: Path, target: Path) -> None:
    rel_source = source.relative_to(root).as_posix()
    rel_target = target.relative_to(root).as_posix()
    target.parent.mkdir(parents=True, exist_ok=True)
    if _git(root, "ls-files", "--error-unmatch", rel_source).returncode == 0:
        _git(root, "mv", rel_source, rel_target).check_returncode()
        print(f"git mv {rel_source} -> {rel_target}")
    else:
        shutil.move(source, target)
        print(f"moved {rel_source} -> {rel_target}")


def _replace_references(specs: Path) -> list[Path]:
    """Replace every old file name in specs/ with its new name; return changed files."""
    changed = []
    for path in sorted(p for p in specs.rglob("*") if p.is_file()):
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        for old, new in RELOCATIONS.items():
            for variant in _name_variants(old):
                updated = updated.replace(variant, new)
        if updated != text:
            path.write_bytes(updated.encode("utf-8"))
            changed.append(path)
    return changed


def relocate(root: Path) -> int:
    specs = root / "specs"
    sources = _sources(root)
    conflicts = [specs / RELOCATIONS[old] for old in sources if (specs / RELOCATIONS[old]).exists()]
    if conflicts:
        for target in conflicts:
            print(f"conflict: target already exists: {target.relative_to(root).as_posix()}")
        print("No files were changed.")
        return 1

    moved = []
    for old, source in sources.items():
        target = specs / RELOCATIONS[old]
        _move(root, source, target)
        moved.append(target)

    changed = _replace_references(specs) if specs.is_dir() else []
    to_add = sorted({p.relative_to(root).as_posix() for p in [*moved, *changed]})
    if to_add:
        _git(root, "add", "--", *to_add).check_returncode()
    for path in changed:
        print(f"updated references in {path.relative_to(root).as_posix()}")
    if not moved and not changed:
        print("Nothing to relocate.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--root", type=Path, default=default_root, help="repository root")
    args = parser.parse_args(argv)
    return relocate(args.root.resolve())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
