"""Session-continuity artefacts (Requirements 3, 4, 5, 6.2, 41.1, 41.2)."""

import hashlib
import re
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = ROOT / ".kiro" / "specs" / "ai-tco-dss-mvp"
PROGRESS = ROOT / "progress.md"
CLAUDE = ROOT / "CLAUDE.md"
STEERING = ROOT / ".kiro" / "steering" / "project-rules.md"
LEDGER = ROOT / "specs" / "07_DATA_CORRECTIONS.md"

# SHA-256 of CLAUDE.md before "## Project Rules" was appended, computed over the
# text with CRLF normalised to LF and trailing newlines removed (Req 5.2).
CLAUDE_ORIGINAL_SHA256 = "b03ae728d17d8b716f6f064d9b566b0891c9369819d225ad0c4b54d640f45235"

PROGRESS_SECTIONS = [
    "Current Status",
    "Task Status",
    "Decisions Log",
    "Changelog",
    "Known Deviations",
    "Next Step",
    "Next Session Prompt",
]
STATUSES = {"not-started", "in-progress", "done", "blocked"}
PROMPT_FILE_ORDER = ["CLAUDE.md", "progress.md", "requirements.md", "design.md", "tasks.md"]
TASK_FIELDS = ["Load", "Modify", "Covers", "Verify", "Demo"]
LEDGER_SECTIONS = [
    "Entries",
    "Contract Deviations",
    "Okabe-Ito Archetype Mapping",
    "Calibration Known Deviations",
    "Assumptions",
]
CONVERSATION_PHRASES = [
    "as discussed",
    "earlier chat",
    "previous chat",
    "previous conversation",
    "as agreed earlier",
    "as mentioned earlier",
]
SPEC_DOCS = {"requirements.md", "design.md", "tasks.md"}

# Files and directories that exist before Task 1 starts (Req 4.7).
PRE_TASK_1_PATHS = {
    "CLAUDE.md",
    "README.md",
    "LICENSE",
    ".kiro/specs/ai-tco-dss-mvp/requirements.md",
    ".kiro/specs/ai-tco-dss-mvp/design.md",
    ".kiro/specs/ai-tco-dss-mvp/tasks.md",
    "specs/00_INDEX_AND_AGENT_ROUTER.md",
    "specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md",
    "specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md",
    "specs/03_CALIBRATED_2026_SEED_DATA.md",
    "specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md",
    "specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md",
    "specs/06_RESEARCH_SOURCES.md",
    "data/",
    "data/benchmarks/",
    "data/catalog/",
    "data/catalog/hardware/",
    "data/catalog/models/",
    "data/reference/",
    "data/workloads/",
    "src/",
    "src/ai_tco_dss/",
    "src/ai_tco_dss/domain/",
    "src/ai_tco_dss/catalog/",
    "src/ai_tco_dss/engines/",
    "src/ai_tco_dss/decision/",
    "src/ai_tco_dss/services/",
    "src/ai_tco_dss/ui/",
    "tests/",
    "tests/unit/",
    "tests/calibration/",
    "tests/property/",
    "tests/integration/",
}

TASK_LINE = re.compile(r"^(?P<indent>\s*)- \[.\]\*? (?P<id>\d+(?:\.\d+)?)\.? (?P<title>.+?)\s*$")
FIELD_LINE = re.compile(r"^\s*- \*\*(?P<name>Load|Modify|Covers|Verify|Demo):\*\* (?P<value>.+)$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LEDGER_ID = re.compile(r"\bC-\d{3}\b")


# --------------------------------------------------------------------------- helpers


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _tasks_section() -> list[str]:
    lines = _read(SPEC_DIR / "tasks.md").split("\n")
    start = lines.index("## Tasks")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    return lines[start + 1 : end]


def _tasks() -> list[tuple[str, str]]:
    """All (task id, title) pairs of tasks.md in document order."""
    result = []
    for line in _tasks_section():
        match = TASK_LINE.match(line)
        if match:
            result.append((match["id"], match["title"]))
    return result


def _top_level_blocks() -> dict[str, dict[str, str]]:
    """Top-level task id -> {field name: field value} plus the raw block text."""
    blocks: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in _tasks_section():
        match = TASK_LINE.match(line)
        if match and not match["indent"]:
            current = match["id"]
            blocks[current] = {"_text": line}
            continue
        if current is None:
            continue
        blocks[current]["_text"] += "\n" + line
        field = FIELD_LINE.match(line)
        if field and not line.startswith("    "):
            blocks[current][field["name"]] = field["value"]
    return blocks


def _requirement_ids() -> set[str]:
    ids: set[str] = set()
    current: str | None = None
    for line in _read(SPEC_DIR / "requirements.md").split("\n"):
        heading = re.match(r"^### Requirement (\d+):", line)
        if heading:
            current = heading.group(1)
            continue
        if line.startswith("## "):
            current = None
        criterion = re.match(r"^(\d+)\. ", line)
        if current and criterion:
            ids.add(f"{current}.{criterion.group(1)}")
    return ids


def _backticked(value: str) -> list[str]:
    return re.findall(r"`([^`]+)`", value)


def _load_paths(value: str) -> list[str]:
    without_headings = re.sub(r'"[^"]*"', "", value)
    paths = []
    for token in _backticked(without_headings):
        paths.append(f".kiro/specs/ai-tco-dss-mvp/{token}" if token in SPEC_DOCS else token)
    return paths


def _sections(text: str) -> dict[str, list[str]]:
    """Level-2 sections outside fenced code blocks, in document order."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            current = line[3:].strip()
            assert current not in sections, f"duplicate heading: {current}"
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = [line.strip() for line in lines if line.strip().startswith("|")]
    body = [row for row in rows[1:] if not re.match(r"^\|[\s:|-]+\|$", row)]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in body]


def _progress_sections() -> dict[str, list[str]]:
    return _sections(_read(PROGRESS))


def _status_rows() -> list[list[str]]:
    return _table_rows(_progress_sections()["Task Status"])


def _statuses() -> dict[str, str]:
    return {row[0]: row[2] for row in _status_rows()}


def _task_ref(task_id: str) -> re.Pattern[str]:
    return re.compile(rf"\b[Tt]ask {re.escape(task_id)}(?!\.?\d)")


def _prompt_block() -> list[str]:
    lines = _progress_sections()["Next Session Prompt"]
    fences = [i for i, line in enumerate(lines) if line.startswith("```")]
    assert len(fences) == 2, "Next Session Prompt must contain exactly one fenced block"
    return lines[fences[0] + 1 : fences[1]]


def _numbered_items(lines: list[str]) -> list[tuple[int, str]]:
    items = []
    for line in lines:
        match = re.match(r"^(\d+)\. (.+)$", line.strip())
        if match:
            items.append((int(match.group(1)), match.group(2).strip()))
    return items


def _claude_rules() -> list[tuple[int, str]]:
    return _numbered_items(_sections(_read(CLAUDE))["Project Rules"])


def _steering_rules() -> list[tuple[int, str]]:
    lines = _read(STEERING).split("\n")
    closing = lines.index("---", 1)
    return _numbered_items(lines[closing + 1 :])


def _ledger_ids() -> set[str]:
    entries = _sections(_read(LEDGER))["Entries"]
    return {row[0] for row in _table_rows(entries) if LEDGER_ID.fullmatch(row[0])}


# --------------------------------------------------------------------------- progress.md


def test_req_3_1_progress_headings_in_order() -> None:
    assert list(_progress_sections()) == PROGRESS_SECTIONS


def test_req_3_2_one_status_row_per_task_id() -> None:
    row_ids = [row[0] for row in _status_rows()]
    assert len(row_ids) == len(set(row_ids)), "duplicate task ids"
    assert set(row_ids) == {task_id for task_id, _ in _tasks()}


def test_req_3_2_status_titles_match_tasks_md() -> None:
    titles = dict(_tasks())
    for row in _status_rows():
        assert row[1] == titles[row[0]], f"title mismatch for task {row[0]}"


def test_req_3_2_status_values_and_dates() -> None:
    for row in _status_rows():
        assert len(row) == 4, row
        task_id, _, status, completed = row
        assert status in STATUSES, f"task {task_id}: {status}"
        if status == "done":
            assert ISO_DATE.match(completed), f"task {task_id}: {completed!r}"
            date.fromisoformat(completed)
        else:
            assert completed == "", f"task {task_id} has a date but is {status}"


def test_req_3_3_changelog_entries() -> None:
    task_ids = {task_id for task_id, _ in _tasks()}
    rows = _table_rows(_progress_sections()["Changelog"])
    for row in rows:
        assert len(row) == 3, row
        assert ISO_DATE.match(row[0]), row
        assert row[1] in task_ids, row
        assert row[2], row
    done_top_level = [
        task_id
        for task_id, status in _statuses().items()
        if status == "done" and "." not in task_id
    ]
    for task_id in done_top_level:
        assert any(row[1] == task_id for row in rows), f"no changelog entry for task {task_id}"


def test_req_3_4_decisions_log_rows() -> None:
    rows = _table_rows(_progress_sections()["Decisions Log"])
    assert rows
    for row in rows:
        assert len(row) == 4, row
        assert ISO_DATE.match(row[0]), row
        assert all(cell for cell in row[1:]), row


def test_req_3_5_known_deviations_reference_ledger() -> None:
    lines = _progress_sections()["Known Deviations"]
    text = "\n".join(lines)
    if "No deviations are recorded" in text:
        return
    ledger_ids = _ledger_ids()
    rows = _table_rows(lines)
    assert rows
    for row in rows:
        ids = LEDGER_ID.findall(" ".join(row))
        assert ids, f"deviation without ledger id: {row}"
        assert set(ids) <= ledger_ids, f"unknown ledger ids in {row}"


def _expected_next_ids() -> tuple[str | None, set[str]]:
    statuses = _statuses()
    order = [task_id for task_id, _ in _tasks()]
    first_not_started = next((t for t in order if statuses[t] == "not-started"), None)
    resumable = {t for t in order if statuses[t] in {"in-progress", "blocked"}}
    return first_not_started, resumable


def _named_task(lines: list[str]) -> str | None:
    match = re.search(r"\b[Tt]ask (\d+(?:\.\d+)?)", "\n".join(lines))
    return match.group(1) if match else None


def test_req_3_3_3_7_next_step_names_next_task() -> None:
    first_not_started, resumable = _expected_next_ids()
    lines = _progress_sections()["Next Step"]
    if first_not_started is None:
        assert "No not-started task remains" in "\n".join(lines)
        return
    assert _named_task(lines) in {first_not_started} | resumable


def test_req_4_1_prompt_is_one_block_of_at_most_50_lines() -> None:
    assert len(_prompt_block()) <= 50


def test_req_4_1_prompt_lists_files_in_order() -> None:
    text = "\n".join(_prompt_block())
    positions = [text.find(name) for name in PROMPT_FILE_ORDER]
    assert all(pos >= 0 for pos in positions), positions
    assert positions == sorted(positions)


def test_req_3_6_4_1_4_2_prompt_names_next_step_task_and_scope() -> None:
    block = _prompt_block()
    text = "\n".join(block)
    first_not_started, resumable = _expected_next_ids()
    if first_not_started is None:
        assert "No not-started task remains" in text
        for task_id in resumable:
            assert _task_ref(task_id).search(text), task_id
        return
    next_step = _named_task(_progress_sections()["Next Step"])
    assert next_step is not None
    assert _task_ref(next_step).search(text)
    block_fields = _top_level_blocks()[next_step.split(".")[0]]
    for item in block_fields["Load"].split("; "):
        assert item.strip() in text, f"Load item missing: {item}"
    for item in block_fields["Modify"].split(", "):
        assert item.strip() in text, f"Modify item missing: {item}"


def test_req_4_5_prompt_has_no_placeholders() -> None:
    text = "\n".join(_prompt_block())
    assert not re.search(r"<[^<>\n]*>", text)
    assert "TODO" not in text
    assert "TBD" not in text


# --------------------------------------------------------------------------- tasks.md


def test_req_4_3_6_2_every_task_has_scope_lines() -> None:
    for task_id, fields in _top_level_blocks().items():
        for name in TASK_FIELDS:
            assert fields.get(name), f"task {task_id} lacks {name}"


def test_req_4_3_verify_is_one_command() -> None:
    for task_id, fields in _top_level_blocks().items():
        commands = _backticked(fields["Verify"])
        assert len(commands) == 1, task_id
        assert commands[0].startswith("uv run python scripts/verify.py"), task_id
        assert "&&" not in commands[0] and ";" not in commands[0], task_id


def test_req_4_3_requirement_ids_exist() -> None:
    known = _requirement_ids()
    text = "\n".join(_tasks_section())
    referenced: list[str] = []
    for fields in _top_level_blocks().values():
        referenced += [i.strip() for i in fields["Covers"].split(",")]
    for group in re.findall(r"_Requirements: ([\d., ]+)_", text):
        referenced += [i.strip() for i in group.split(",")]
    for group in re.findall(r"\*\*Validates: Requirements ([\d., ]+)\*\*", text):
        referenced += [i.strip() for i in group.split(",")]
    assert referenced
    unknown = sorted({i for i in referenced if i not in known})
    assert unknown == []


def _is_covered(path: str, allowed: set[str]) -> bool:
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allowed)


def test_req_4_7_load_paths_exist_before_the_task() -> None:
    allowed = set(PRE_TASK_1_PATHS)
    for task_id, fields in _top_level_blocks().items():
        for path in _load_paths(fields["Load"]):
            assert _is_covered(path, allowed), f"task {task_id}: {path}"
        allowed |= set(_backticked(fields["Modify"]))


def test_req_4_4_no_reference_to_prior_conversation() -> None:
    # Quoted phrases are mentions (e.g. the examples in task 1.2), not references.
    text = re.sub(r'"[^"\n]*"', "", "\n".join(_tasks_section())).lower()
    for phrase in CONVERSATION_PHRASES:
        assert phrase not in text, phrase


# --------------------------------------------------------------------------- Project Rules


def test_req_5_1_one_project_rules_heading() -> None:
    lines = _read(CLAUDE).split("\n")
    assert [line for line in lines if line.startswith("## Project Rules")] == ["## Project Rules"]


def test_req_5_2_original_claude_content_unchanged() -> None:
    text = _read(CLAUDE)
    prefix = text[: text.index("## Project Rules")].rstrip("\n")
    assert hashlib.sha256(prefix.encode("utf-8")).hexdigest() == CLAUDE_ORIGINAL_SHA256


def test_req_5_1_project_rules_is_last_section() -> None:
    sections = list(_sections(_read(CLAUDE)))
    assert sections[-1] == "Project Rules"


def test_req_5_4_eight_numbered_rules() -> None:
    rules = _claude_rules()
    assert [number for number, _ in rules] == list(range(1, 9))


@pytest.mark.parametrize(
    ("number", "keywords"),
    [
        (1, ["start of every session", "progress.md"]),
        (2, ["test-first", "failure"]),
        (3, ["Provenance_Record", "source_id", "Source_Tier", "ISO 8601"]),
        (4, ["measured value", "formula value"]),
        (5, ["USD", "default currency"]),
        (6, ["Task_Scope"]),
        (7, ["07_DATA_CORRECTIONS.md", "old value", "new value", "sources", "decision date"]),
        (8, ["progress.md", "Next Session Prompt", "zero failures"]),
    ],
)
def test_req_5_4_41_1_41_2_rule_content(number: int, keywords: list[str]) -> None:
    text = dict(_claude_rules())[number]
    for keyword in keywords:
        assert keyword in text, f"rule {number} lacks {keyword!r}"


def test_req_5_3_steering_front_matter() -> None:
    lines = _read(STEERING).split("\n")
    assert lines[0] == "---"
    closing = lines.index("---", 1)
    assert "inclusion: always" in lines[1:closing]


def test_req_5_5_5_6_steering_rules_identical() -> None:
    assert _steering_rules() == _claude_rules()


# --------------------------------------------------------------------------- ledger


def test_req_3_5_ledger_sections() -> None:
    headings = list(_sections(_read(LEDGER)))
    for name in LEDGER_SECTIONS:
        assert any(h.startswith(name) for h in headings), name


def test_ledger_entries_c001_to_c015() -> None:
    assert {f"C-{n:03d}" for n in range(1, 16)} <= _ledger_ids()
