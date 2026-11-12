"""Thesis notes and BibTeX export (user-requested, outside the MVP requirements).

Guards `scripts/export_bib.py`, the generated `thesis/references.bib` and the citation
keys used in `thesis/thesis_notes.md`.
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "export_bib.py"
SOURCES = ROOT / "data" / "sources.json"
THESIS = ROOT / "thesis"
NOTES = THESIS / "thesis_notes.md"
REFERENCES = THESIS / "references.bib"
LITERATURE = THESIS / "literature.bib"
CHAPTERS = (
    "1 Introduction",
    "2 Background",
    "3 Requirements",
    "4 Design",
    "5 Implementation",
    "6 Evaluation",
    "7 Limitations",
    "8 Future work",
)
CITATION = re.compile(r"\[@[^\]]+\]")
CITE_KEY = re.compile(r"@([A-Za-z0-9_\-:.]*[A-Za-z0-9_\-])")
BIB_KEY = re.compile(r"^@\w+\{([^,\s]+),", re.MULTILINE)


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("export_bib", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sources() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
    return data


def _source(**changes: Any) -> dict[str, Any]:
    base = {
        "source_id": "TEST-1",
        "title": "A title",
        "url": "https://example.org/a_b%20c",
        "reference": None,
        "publisher": "Publisher",
        "tier": "official",
    }
    return {**base, **changes}


def _keys(text: str) -> list[str]:
    return BIB_KEY.findall(text)


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


# --- export_bib.py ------------------------------------------------------------------------


def test_one_entry_per_source_keyed_by_source_id() -> None:
    sources = _sources()
    text = _module().to_bibtex(sources)
    keys = _keys(text)
    assert len(keys) == len(sources)
    assert sorted(keys) == sorted(s["source_id"] for s in sources)
    assert keys == sorted(keys)


def test_latex_special_characters_are_escaped_outside_urls() -> None:
    text = _module().to_bibtex(
        [_source(title="R&D 50% of_cost #1 $2 {x}", publisher="A & B", reference="see x_y")]
    )
    assert r"R\&D 50\% of\_cost \#1 \$2 \{x\}" in text
    assert r"{{A \& B}}" in text
    assert r"see x\_y" in text
    assert r"\url{https://example.org/a_b%20c}" in text


def test_tier_url_and_reference_fields() -> None:
    text = _module().to_bibtex(
        [
            _source(source_id="WITH-URL", tier="community"),
            _source(
                source_id="WITH-REF", url=None, reference="BDEW report 2026", tier="assumption"
            ),
        ]
    )
    with_url, with_ref = text.split("@misc{WITH-URL,")[1], text.split("@misc{WITH-REF,")[1]
    with_ref = with_ref.split("@misc{")[0]
    assert "keywords = {community}" in with_url
    assert "howpublished = {\\url{https://example.org/a_b%20c}}" in with_url
    assert "keywords = {assumption}" in with_ref
    assert "note = {BDEW report 2026}" in with_ref
    assert "howpublished" not in with_ref.split("@misc{WITH-URL")[0]


def test_export_is_deterministic(tmp_path: Path) -> None:
    out_a, out_b = tmp_path / "a.bib", tmp_path / "b.bib"
    assert _run("--out", str(out_a)).returncode == 0
    assert _run("--out", str(out_b)).returncode == 0
    assert out_a.read_bytes() == out_b.read_bytes()
    assert out_a.read_bytes().endswith(b"\n") and b"\r\n" not in out_a.read_bytes()


@pytest.mark.parametrize("missing", ["source_id", "title", "publisher"])
def test_malformed_source_fails_naming_the_source(tmp_path: Path, missing: str) -> None:
    bad = _source(source_id="BROKEN-7")
    bad[missing] = "" if missing != "source_id" else None
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({"sources": [_source(), bad]}), encoding="utf-8")
    result = _run("--sources", str(sources), "--out", str(tmp_path / "x.bib"))
    assert result.returncode == 1
    assert missing in result.stderr
    if missing != "source_id":
        assert "BROKEN-7" in result.stderr
    assert not (tmp_path / "x.bib").exists()


# --- thesis files -------------------------------------------------------------------------


def test_references_bib_is_up_to_date() -> None:
    """Run `uv run python scripts/export_bib.py` after changing data/sources.json."""
    expected = _module().to_bibtex(_sources())
    assert REFERENCES.read_text(encoding="utf-8") == expected


def test_notes_have_all_chapters_and_the_update_log() -> None:
    text = NOTES.read_text(encoding="utf-8")
    headings = [line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")]
    for chapter in CHAPTERS:
        assert any(h.startswith(chapter) for h in headings), chapter
    assert any(h.startswith("Update log") for h in headings)


def test_every_citation_key_resolves() -> None:
    known = set(_keys(REFERENCES.read_text(encoding="utf-8")))
    known |= set(_keys(LITERATURE.read_text(encoding="utf-8")))
    text = NOTES.read_text(encoding="utf-8")
    cited = {key for group in CITATION.findall(text) for key in CITE_KEY.findall(group)}
    assert cited, "the notes cite no source"
    assert sorted(cited - known) == []


def test_literature_entries_have_a_verification_url() -> None:
    """Every hand-added academic reference carries a DOI or url checked online."""
    text = LITERATURE.read_text(encoding="utf-8")
    entries = re.split(r"^@", text, flags=re.MULTILINE)[1:]
    for entry in entries:
        key = entry.split("{", 1)[1].split(",", 1)[0]
        assert re.search(r"^\s*(doi|url)\s*=", entry, re.MULTILINE), key
