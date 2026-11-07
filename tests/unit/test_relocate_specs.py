"""Spec relocation script (Req 1.4, 1.5, 1.9, 1.11)."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "relocate_specs.py"
GIT_IDENTITY = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *GIT_IDENTITY, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _relocate(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert _git(repo, "init", "-q").returncode == 0
    (repo / "README.md").write_text("readme\n", encoding="utf-8")
    assert _git(repo, "add", "README.md").returncode == 0
    assert _git(repo, "commit", "-q", "-m", "init").returncode == 0
    return repo


def test_req_1_4_tracked_file_moved_with_git_mv_keeps_history(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "index_agent_router.md").write_text("router content\n", encoding="utf-8")
    _git(repo, "add", "index_agent_router.md")
    _git(repo, "commit", "-q", "-m", "add router")
    original_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()

    result = _relocate(repo)
    assert result.returncode == 0, result.stdout + result.stderr

    new_rel = "specs/00_INDEX_AND_AGENT_ROUTER.md"
    assert not (repo / "index_agent_router.md").exists()
    assert (repo / new_rel).read_text(encoding="utf-8") == "router content\n"
    tracked = _git(repo, "ls-files").stdout.split("\n")
    assert new_rel in tracked
    assert "index_agent_router.md" not in tracked

    _git(repo, "commit", "-q", "-m", "relocate")
    history = _git(repo, "log", "--follow", "--format=%H", "--", new_rel).stdout.split()
    assert original_sha in history


def test_req_1_5_untracked_file_moved_and_added(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    old = "research_sources_benchmark_evidence (1).md"
    (repo / old).write_text("sources\n", encoding="utf-8")

    result = _relocate(repo)
    assert result.returncode == 0, result.stdout + result.stderr

    new_rel = "specs/06_RESEARCH_SOURCES.md"
    assert not (repo / old).exists()
    assert (repo / new_rel).read_text(encoding="utf-8") == "sources\n"
    assert _git(repo, "ls-files", "--error-unmatch", new_rel).returncode == 0


def test_req_1_9_cross_references_replaced(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "index_agent_router.md").write_text(
        "See `workload_profiler_physical_sizing_engine (1).md` and "
        "pydantic_v2_core_schemas_contracts.md.\n",
        encoding="utf-8",
    )

    result = _relocate(repo)
    assert result.returncode == 0, result.stdout + result.stderr

    text = (repo / "specs" / "00_INDEX_AND_AGENT_ROUTER.md").read_text(encoding="utf-8")
    assert text == (
        "See `01_WORKLOAD_AND_PHYSICS_ENGINE.md` and 04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md.\n"
    )


def test_req_1_11_existing_target_leaves_both_files_unchanged(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    source = repo / "index_agent_router.md"
    target = repo / "specs" / "00_INDEX_AND_AGENT_ROUTER.md"
    other = repo / "pydantic_v2_core_schemas_contracts (1).md"
    source.write_text("source\n", encoding="utf-8")
    other.write_text("other\n", encoding="utf-8")
    target.parent.mkdir()
    target.write_text("target\n", encoding="utf-8")

    result = _relocate(repo)

    assert result.returncode != 0
    assert "specs/00_INDEX_AND_AGENT_ROUTER.md" in (result.stdout + result.stderr).replace(
        "\\", "/"
    )
    assert source.read_text(encoding="utf-8") == "source\n"
    assert target.read_text(encoding="utf-8") == "target\n"
    # The conflict check runs before any change, so no other file moves either.
    assert other.exists()
    assert not (repo / "specs" / "04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md").exists()


def test_real_repository_is_a_no_op() -> None:
    status_before = _git(ROOT, "status", "--porcelain").stdout
    specs_before = {p.name: p.read_bytes() for p in (ROOT / "specs").iterdir() if p.is_file()}

    result = _relocate(ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    assert _git(ROOT, "status", "--porcelain").stdout == status_before
    specs_after = {p.name: p.read_bytes() for p in (ROOT / "specs").iterdir() if p.is_file()}
    assert specs_after == specs_before
