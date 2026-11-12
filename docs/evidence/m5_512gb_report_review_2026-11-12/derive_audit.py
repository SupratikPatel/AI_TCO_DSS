"""Offline source reconciliation. Never execute generated answers or external code."""

import ast
import gzip
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def plain(raw):
    parser = Text()
    parser.feed(raw)
    return " | ".join(parser.parts)


def write(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


manifest = json.loads(source("manifest.json"))
for entry in manifest["files"]:
    raw = (ROOT / entry["path"]).read_bytes()
    assert len(raw) == entry["bytes"], entry["path"]
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"], entry["path"]

performance = []
for path in sorted((ROOT / "omlx").glob("*.html")):
    if path.name.startswith("leaderboard"):
        continue
    raw = path.read_text(encoding="utf-8")
    text = plain(raw)
    metric = re.search(
        r"Performance \| ([^|]+) \| tokens \| ([\d,.]+) \| PP tok/s \| ([\d,.]+)"
        r" \| TG tok/s \| ([\d,.]+) \| TTFT \(ms\) \| ([\d,.]+) \| Peak mem \(GB\)", text
    )
    software = re.search(
        r"Software \| oMLX \| ([^|]+) \| macOS \| ([^|]+) \| Context \| ([\d,]+)", text
    )
    assert metric and software, path.name
    settings = json.loads(html.unescape(re.search(r"<pre[^>]*>(.*?)</pre>", raw, re.S)[1]))
    resources = {}
    for name in ("Peak footprint", "MLX active peak", "MLX cache peak", "System used peak", "System wired peak", "Total RAM"):
        found = re.search(re.escape(name) + r" \| ([\d,.]+) GB", text)
        if found:
            resources[name] = float(found[1].replace(",", ""))
    batches = []
    if "Batching Results | " in text:
        section = text.split("Batching Results | ", 1)[1].split("Acceleration | ", 1)[0]
        batches = [{"batch_size": int(n), "aggregate_tg_tps": float(rate.replace(",", ""))}
                   for n, rate in re.findall(r"(\d+)× \| ([\d,.]+) \| [\d.]+×", section)]
    performance.append({
        "path": path.relative_to(ROOT).as_posix(),
        "model": plain(re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)[1]),
        "headline_context_label": metric[1], "reported_context_tokens": int(software[3].replace(",", "")),
        "reported_pp_tps": float(metric[2].replace(",", "")), "reported_tg_tps": float(metric[3]),
        "reported_ttft_s": float(metric[4]) / 1000, "selected_peak_mem_gb": float(metric[5]),
        "runtime": software[1], "macos": software[2], "resources_gb": resources,
        "model_settings": settings, "batching": batches,
        "actual_output_count_independently_established": None, "live_kv_dtype": None,
        "cache_hit_fraction": None, "strict_admission": False,
        "note": "Context is the record's reported field, not independently checked tokenizer output. Settings are not event logs.",
    })

expected = {"mkzszvig": (1000, 714), "ybmeme01": (1319, 1238),
            "qvlxvz1i": (164, 132), "6b3p2k87": (164, 148)}
quality = []
for key, counts in expected.items():
    rows = json.loads(gzip.decompress((ROOT / "quality" / (key + "-raw.json.gz")).read_bytes()))
    correct = sum(row["correct"] is True for row in rows)
    assert (len(rows), correct) == counts
    assert len({row["id"] for row in rows}) == len(rows)
    categories = defaultdict(lambda: {"total": 0, "correct": 0})
    for row in rows:
        if "category" in row:
            categories[row["category"]]["total"] += 1
            categories[row["category"]]["correct"] += row["correct"] is True
    failures = [row for row in rows if not row["correct"]]
    raw = source("quality/" + key + ".html")
    quality.append({
        "record_id": key, "questions": len(rows), "correct": correct, "failed": len(failures),
        "score_percent": correct / len(rows) * 100, "categories": dict(categories),
        "failed_finish_reasons": dict(Counter(row.get("finish_reason", "unrecorded") for row in failures)),
        "model_settings": json.loads(html.unescape(re.search(r"<pre[^>]*>(.*?)</pre>", raw, re.S)[1])),
        "failure_ids": [row["id"] for row in failures],
        "method": "Recount published correct flags only; no generated code execution or independent regrading.",
        "limitations": "Different hardware/settings/artifact labels; no controlled causal comparison or production quality import.",
    })

raw = source("apple/mlx-distributed.html")
page = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)[1])
body = page["props"]["pageProps"]["posts"][0]["body"]
apple_tables = {}
for name in ("table2", "table3"):
    section = re.search(r'<Figure id="' + name + r'".*?</Figure>', body, re.S)[0]
    apple_tables[name] = [
        {"context_label": context, "columns": ast.literal_eval(columns), "rows": ast.literal_eval(rows)}
        for context, columns, rows in re.findall(
            r"title: '([^']+)',\s*columns: (\[.*?\]),\s*rows: (\[.*?\n\s*\])", section, re.S
        )
    ]
    assert len(apple_tables[name]) == 2

offers = []
for path in ("apple/store-512-1tb.html", "apple/store-512-16tb.html"):
    raw = source(path)
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', raw, re.S):
        data = json.loads(block)
        if isinstance(data, dict) and data.get("offers"):
            offers.append({"path": path, "name": data.get("name"), "offers": data["offers"]})
assert len(offers) == 2

write("review_audit.json", {
    "review_date": "2026-11-12", "manifest_file_count": len(manifest["files"]),
    "offers": offers, "omlx_performance": performance, "quality_raw_recounts": quality,
    "quality_questions_recounted": sum(row["questions"] for row in quality),
    "apple_ml_tables": apple_tables,
    "quality_artifact_repository_revision": json.loads(source("quality/ista-api.json"))["sha"],
    "primary_gaps": ["Five simultaneous 131072-token requests", "Eight resident agent sessions",
                     "Exact INT2/INT3 artifact tool reliability under target workload",
                     "Historical performance event/build/weight/KV/cache manifests"],
    "strict_comparable_observations": 0, "existing_excluded_observations": 13,
    "strict_mape": None, "production_changes": False,
    "fetch_limits": {"reddit_json": "403", "reddit_image": "403", "youtube_caption_response": "200 but zero bytes"},
})
write("integrity_verification.json", {
    "manifest_files_verified": len(manifest["files"]),
    "sha256_and_lengths_match": True,
    "response_status_counts": dict(Counter(str(row.get("status", "input")) for row in manifest["files"])),
    "empty_responses": [row["path"] for row in manifest["files"] if row["bytes"] == 0],
})
print(json.dumps({"source_files_verified": len(manifest["files"]), "performance_records": len(performance),
                  "quality_questions_recounted": sum(row["questions"] for row in quality),
                  "apple_table_contexts": {k: len(v) for k, v in apple_tables.items()}}))
