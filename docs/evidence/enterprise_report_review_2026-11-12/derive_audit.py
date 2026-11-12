"""Offline review derivation. Does not execute acquired code or make network calls."""

import base64
import hashlib
import json
from pathlib import Path

from ai_tco_dss.domain.fleet import FleetSizingInput, ReplicaCapacity
from ai_tco_dss.engines.fleet import plan_fleet

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    manifest = load(ROOT / "manifest.json")
    integrity = []
    for entry in manifest["files"]:
        if "sha256" not in entry:
            continue
        body = (ROOT / entry["path"]).read_bytes()
        assert len(body) == entry["bytes"], entry["path"]
        assert hashlib.sha256(body).hexdigest() == entry["sha256"], entry["path"]
        integrity.append(entry["path"])
    reused = []
    for entry in manifest["reused_files"]:
        body = (REPO / entry["path"]).read_bytes()
        assert hashlib.sha256(body).hexdigest() == entry["sha256"], entry["path"]
        assert len(body) == entry["bytes"], entry["path"]
        reused.append(entry["path"])
    npm = load(ROOT / "jev-npm.json")
    digest = base64.b64encode(
        hashlib.sha512((ROOT / "jev-2.0.0.tgz").read_bytes()).digest()
    ).decode()
    assert "sha512-" + digest == npm["dist"]["integrity"]
    tables = load(ROOT / "source_tables.json")
    h100 = tables["backboard-h100.html"]
    # Preserve the publisher's denominator, rather than importing total-token TPS as output.
    h100_output_per_gpu = [float(row[1].replace(",", "")) for row in h100[3][1:]]
    h100_output_8gpu_derived = [round(x * 8, 1) for x in h100_output_per_gpu]
    h100_output_8gpu_reported = [float(x) for x in h100[5][2][1:]]
    # The page rounds per-GPU and whole-node tables independently. Keep both.
    assert h100_output_8gpu_reported == [168, 262, 396, 554, 726]
    assert tables["backboard-glm.html"][1][1][1:3] == ["3.24 s", "357.50 s"]
    assert tables["backboard-glm.html"][1][2][1:3] == ["61.20 s", "504.90 s"]

    synthetic_input = FleetSizingInput(
        capacity=ReplicaCapacity(
            gpus_per_replica=8,
            request_slots=16,
            retained_session_slots=40,
            aggregate_output_tps=400,
            capacity_basis="Synthetic example; all capacities assumed",
            source_ids=("synthetic-example",),
        ),
        peak_concurrent_requests=33,
        retained_sessions=80,
        required_output_tps=800,
        spare_replicas=1,
    )
    # 32 workflows is not a proven resident-request-slot count. Leave it unknown.
    partial_input = FleetSizingInput(
        capacity=ReplicaCapacity(
            gpus_per_replica=8,
            aggregate_output_tps=370,
            capacity_basis="Observed 370 TPS treated as a hypothetical planning ceiling, "
            "not a proven maximum. Backboard GLM-5.3 sustained-admission summary; "
            "30-minute window plus drain, BF16, 8 B200, "
            "32 workflows; incomplete workload manifest",
            source_ids=("backboard-glm.html",),
        ),
        peak_concurrent_requests=33,
        retained_sessions=80,
        required_output_tps=1000,
        spare_replicas=0,
    )
    # Demand and transferability to multiple replicas are hypothetical in both examples.
    cases = [
        {"input": inp.model_dump(mode="json"), "result": plan_fleet(inp).model_dump(mode="json")}
        for inp in (synthetic_input, partial_input)
    ]
    audit = {
        "integrity": {
            "new_files_verified": integrity,
            "reused_files_verified": reused,
            "npm_sha512_verified": True,
        },
        "companion_probes": manifest["companion_probes"],
        "shared_serving": {
            "glm": {
                "source": "backboard-glm.html",
                "gpus": 8,
                "precision": "BF16",
                "sustained": {
                    "workflows": 32,
                    "admission_window_s": 1800,
                    "aggregate_output_tps": [370.0, 74.9],
                    "ttft_p50_s": [3.24, 357.5],
                    "ttft_p90_s": [61.2, 504.9],
                    "median_generation_tps": [15.8, 7.7],
                    "admitted": [462, 116],
                    "completed": [461, 96],
                },
                "burst": {
                    "offered_workflows": 96,
                    "concurrency_workflows": 32,
                    "aggregate_output_tps": [165.5, 63.5],
                    "ttft_p50_s": [1.63, 16.4],
                    "ttft_p90_s": [58.3, 481.0],
                },
                "strict_admission": False,
                "reason": "Missing exact run-linked manifests; "
                "concurrent/queueing workload not represented by resident formula",
            },
            "h100": {
                "source": "backboard-h100.html",
                "publication": "2026-11-06",
                "concurrency_kind": "live session trees, not simultaneous HTTP requests",
                "gpus": 8,
                "precisions": ["BF16", "FP8"],
                "backboard_p90_ttft_s": [0.78, 0.74, 0.86, 1.01, 1.41],
                "backboard_p90_interactivity_tps": [209, 156.3, 147, 100.4, 71.6],
                "backboard_output_tps_per_gpu": h100_output_per_gpu,
                "backboard_8gpu_output_tps_derived": h100_output_8gpu_derived,
                "backboard_8gpu_output_tps_reported": h100_output_8gpu_reported,
                "strict_admission": False,
            },
            "petronella": {
                "primary_web_excerpts": "petronella-web-excerpts.json",
                "direct_download_status": 403,
                "deepseek_61_349_583_hardware": "4 RTX PRO 6000 Blackwell Max-Q, not H200",
                "gb300_fast_path_precision": "MXFP4 experts (official checkpoint), "
                "Al-ENGR v20 pin-hot-experts plus RTX PRO 6000 peer; not uniform NVFP4",
                "ttft_from_prefill_not_admitted": True,
                "qwen_gb10_values": "Confirmed published 2/4/8-unit throughput; "
                "model-parallel pools, not independent replica counts",
            },
        },
        "router": {
            "package": npm["_id"],
            "git_head": npm["gitHead"],
            "api": "route(request, ctx), not resolve(context)",
            "classifier_provider_vs_adapter_api": "typesafe vs typesafe-system-one",
            "julien_personal_extension_identity": None,
            "load_aware_bypass_validated": False,
            "live_accuracy_latency_quality_cost_validated": False,
            "synthtraces_head": load(ROOT / "synthtraces-head.json")["sha"],
            "synthtraces_role": "local simulated user and remote coding agent; not router eval",
        },
        "m5": {
            "reused_512gb_record": "2zvzoy8b",
            "ttft_s": 28.25,
            "decode_tps": 102.3,
            "five_128k_requests": None,
            "eight_retained_sessions": None,
            "new_release_m5_deepseek_12_request_aggregate_tps": [56.3, 125.7],
            "new_release_memory_and_context_for_12_request_test": None,
            "exact_uniform_int2_int3_tool_quality": None,
            "sushi_94_denominator": "182/194 points, not 94/100 scenarios",
        },
        "api": {
            "matched_eu_32k_128k_request_logs": None,
            "openai_sol_standard_input_output_cache": [2, 10, 0.1],
            "openai_sol_long_input_output_cache_derived": [4, 15, 0.2],
            "openai_sol_regional_uplift": 0.10,
            "gemini31_vertex_regions": ["global"],
            "gemini31_report_2m_context_not_accepted": True,
            "etuki_4k_us_batch_edge_not_matched_eu_streaming": True,
        },
        "fleet_examples": cases,
        "calibration": {
            "new_production_imports": 0,
            "strict_coverage": 0,
            "existing_exclusions": 13,
            "mape": None,
        },
    }
    (ROOT / "review_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "new_verified": len(integrity),
                "reused_verified": len(reused),
                "fleet_examples": len(cases),
                "strict_coverage": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
