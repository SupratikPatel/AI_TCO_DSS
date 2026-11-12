"""Derive searchable text and table cells without executing source-page code."""

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if self.skip:
            return
        if tag in ("p", "div", "li", "h1", "h2", "h3", "tr", "br"):
            self.parts.append("\n")
        if tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in ("th", "td"):
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if self.skip:
            return
        if tag in ("td", "th") and self.cell is not None:
            if self.row is not None:
                self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.table is not None and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
            if self.cell is not None:
                self.cell.append(data)


if __name__ == "__main__":
    tables = {}
    for path in ROOT.glob("*.html"):
        reader = Reader()
        reader.feed(path.read_text(encoding="utf-8"))
        lines = [" ".join(s.split()) for s in "".join(reader.parts).splitlines()]
        path.with_suffix(".text.txt").write_text(
            "\n".join(s for s in lines if s) + "\n", encoding="utf-8"
        )
        tables[path.name] = reader.tables
    (ROOT / "source_tables.json").write_text(json.dumps(tables, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: len(v) for k, v in tables.items()}))
