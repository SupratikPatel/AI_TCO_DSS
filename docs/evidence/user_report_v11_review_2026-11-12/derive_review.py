"""Reconcile archived evidence only; no network, inference or production writes.

Run from the workspace root: uv run python docs/evidence/
user_report_v11_review_2026-11-12/derive_review.py
External archived harnesses are inspected as text, never imported or executed.
"""

import hashlib
import html
import json
import math
import re
from collections import Counter
from pathlib import Path
from statistics import median

from ai_tco_dss.engines.performance import delta_ctx
from ai_tco_dss.settings import load_engine_parameters

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


manifest = read(ROOT / "manifest.json")
integrity = []
for entry in manifest["files"]:
    data = (ROOT / entry["path"]).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert len(data) == entry["bytes"] and digest == entry["sha256"], entry["path"]
    integrity.append({"path": entry["path"], "bytes": len(data), "sha256": digest})

cells = []
for date in ("2026-11-04-m5-max-flash-next", "2026-10-25-m5-max"):
    runs = []
    for path in sorted((ROOT / "kapitsa/bench/results" / date / "results").glob("*.json")):
        data = read(path)
        phases = {}
        for phase in ("decode", "decode_greedy"):
            responses = data[phase]
            calculated = median(row["decode_tps"] for row in responses)
            reported = data[phase + "_summary"]["median_tps"]
            assert round(calculated, 2) == reported
            assert len(responses) == 5
            assert all(row["completion_tokens"] == 512 for row in responses)
            phases[phase] = {
                "samples": len(responses), "actual_output_tokens": 512,
                "median_window_tps_unrounded": calculated,
                "reported_median_window_tps": reported,
                "rate_methods": dict(Counter(row["rate"]["rate_method"] for row in responses)),
                "reported_median_full_decode_tps": data[phase + "_summary"].get("median_tps_e2e"),
            }
        prefills = []
        for row in data["prefill"]:
            rate = row["prompt_tokens"] / row["ttft_s"]
            assert math.isclose(rate, row["prefill_tps"], rel_tol=1e-12)
            prefills.append({key: row.get(key) for key in (
                "target", "prompt_tokens", "ttft_s", "prefill_tps", "cold_cached_tokens", "timings"
            )})
        sweeps = [row for point in data.get("sweep", {}).get("runs", []) for row in point["runs"]]
        for row in sweeps:
            assert math.isclose(row["prompt_tokens"] / row["ttft_s"], row["prefill_tps"], rel_tol=1e-12)
        runs.append({
            "path": path.relative_to(ROOT).as_posix(), "harness": data["harness"],
            "phases": phases, "cold_prefill": prefills,
            "sweep_request_count": len(sweeps),
            "sweep_actual_output_counts": dict(Counter(str(row["completion_tokens"]) for row in sweeps)),
            "sweep_actual_prompt_range": [min(row["prompt_tokens"] for row in sweeps),
                                          max(row["prompt_tokens"] for row in sweeps)] if sweeps else None,
            "source_flags": data.get("flags"), "source_invalid": data.get("invalid"),
            "weight_file_manifest": data["provenance"]["weights"],
        })
    cells.append({
        "date": date, "runs": runs,
        "median_of_reported_run_medians": {
            phase: median(run["phases"][phase]["reported_median_window_tps"] for run in runs)
            for phase in ("decode", "decode_greedy")
        },
        "prefill_metric": "client prompt_tokens / TTFT; not isolated input-processing timing",
        "decode_metric": "middle window; chars approximation when stream events do not equal tokens",
        "strict_admission": False,
    })

settings = []
for path in sorted((ROOT / "omlx").glob("*.html")):
    blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", path.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 1
    raw = json.loads(html.unescape(re.sub(r"<[^>]*>", "", blocks[0])))
    settings.append({
        "path": path.relative_to(ROOT).as_posix(), "raw_model_settings": raw,
        "raw_request_event_log": False,
        "actual_output_tokens": None, "live_kv_dtype": None,
        "interpretation": "Settings/caps are not actual token counts. Disabled TurboQuant does not establish FP16.",
        "strict_admission": False,
    })

params = load_engine_parameters()
depths = [0, 4096, 16384, 32768, 65536, 131072, 262144]
observed = [33.0, 30.7, 27.9, 24.8, 23.0, 17.0, 10.9]
prefill = [966, 776, 456, 324, 241, 154, 80]
shape = []
for depth, tps, pp in zip(depths, observed, prefill, strict=True):
    factor = delta_ctx(depth, params.delta_ctx_breakpoints) / delta_ctx(0, params.delta_ctx_breakpoints)
    anchored = observed[0] * factor
    shape.append({
        "occupied_depth": depth, "source_tg128_tps": tps, "source_incremental_pp512_tps": pp,
        "observed_normalized_rate": tps / observed[0], "engine_normalized_factor": factor,
        "baseline_anchored_tps": anchored, "anchored_overprediction_percent": (anchored / tps - 1) * 100,
    })

write("review_audit.json", {
    "review_date": "2026-11-12", "source_file_count": len(integrity),
    "remote_source_count": sum("url" in entry for entry in manifest["files"]),
    "review_scope": "Delta from first report; previous twelve-row audit retained, no repeated acquisition.",
    "kapitsa": cells, "omlx": settings,
    "heretik_context_shape": {
        "source": "heretik.html", "engine_parameters": params.model_dump(mode="json"),
        "engine_helper": "src/ai_tco_dss/engines/performance.py:delta_ctx",
        "rows": shape, "strict_admission": False, "coefficient_fitting": False,
        "limitations": [
            "Post-inspection conditional shape diagnostic, not blind validation or full-formula prediction.",
            "Observed 33 tok/s at depth zero is the normalization anchor; amplitude is not predicted.",
            "One run per depth; mixed GGUF quantization and n-gram mmap differ from resident uniform-bit formula.",
            "Only delta_ctx shape is compared. No strict MAPE and no causal attribution of the discrepancy.",
            "pp512 is incremental at occupied depth; 28-minute full-fill figure is integrated estimate.",
        ],
    },
    "macstories_corrections": {
        "source": "../user_report_review_2026-11-12/macstories-response.html",
        "quant_order": ["oQ4e", "oQ5e", "oQ6e", "oQ8e"],
        "misattributed_m3_ultra_code_tps": [103.9, 97.3, 96.6, 89.1],
        "correct_m5_ultra_prose_tps": [111.6, 100.0, 95.2, 86.8],
        "correct_m5_ultra_code_tps": [142.9, 132.6, 122.8, 119.0],
        "m5_loading_peak_gb": [134, 153, 101, 130],
        "m5_answering_peak_gb": [155, 179, 156, 187],
        "qualification": "Q4 prose retest nine runs, code three; Q6/Q8 embedding tables on SSD. Memory is sampled process footprint.",
    },
    "remaining": {
        "m5_ultra_512gb_measurements": None, "m5_max_five_128k_request_logs": None,
        "strict_comparable_observations": 0, "existing_excluded_observations": 13, "strict_mape": None,
        "production_changes": False,
    },
})
write("integrity_verification.json", {"manifest_files_verified": len(integrity), "files": integrity})
print(json.dumps({"verified_files": len(integrity), "cells": len(cells),
                  "coding_responses": sum(phase["samples"] for cell in cells for run in cell["runs"] for phase in run["phases"].values()),
                  "cold_prefills": sum(len(run["cold_prefill"]) for cell in cells for run in cell["runs"]),
                  "sweep_requests": sum(run["sweep_request_count"] for cell in cells for run in cell["runs"]),
                  "context_shape": shape[-2:]}))
