"""Archive public documentation only; never run downloaded code or inference."""

import concurrent.futures
import datetime
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "backboard-glm.html": "https://backboard.io/blog/glm-5-3-inference-throughput-vllm",
    "backboard-h100.html": "https://backboard.io/blog/qwen-flash-next-h100-full-precision",
    "backboard-27b.html": "https://backboard.io/blog/qwen3-8-27b-vllm-sglang-inference",
    "backboard-35b.html": "https://backboard.io/blog/qwen3-6-inference-throughput-vllm",
    "petronella-deepseek.html": "https://petronellatech.com/ai/llm-benchmarks/models/deepseek-v4-1-flash/",
    "petronella-qwen.html": "https://petronellatech.com/ai/llm-benchmarks/models/qwen3-8-flash-next/",
    "jev-package.html": "https://pi.dev/packages/@caph42/pi-jev-router",
    "jev-npm.json": "https://registry.npmjs.org/@caph42/pi-jev-router/2.0.0",
    "synthtraces-head.json": "https://api.github.com/repos/julien-c/synthtraces/commits/main",
    "omlx-releases.json": "https://api.github.com/repos/jundot/omlx/releases?per_page=20",
    "openai-sol.html": "https://developers.openai.com/api/docs/models/gpt-6.1-sol",
    "openai-data.html": "https://developers.openai.com/api/docs/guides/your-data",
    "anthropic-models.html": "https://platform.claude.com/docs/en/about-claude/models/overview",
    "anthropic-pricing.html": "https://platform.claude.com/docs/en/about-claude/pricing",
    "google-locations.html": "https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations",
    "google-gemini31.html": "https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-pro",
}


def acquire(item):
    name, url = item
    req = urllib.request.Request(url, headers={"User-Agent": "AI-TCO-evidence-review/1.0"})
    error = None
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body, status, resolved = response.read(), response.status, response.url
    except urllib.error.HTTPError as exc:
        body, status, resolved = exc.read(), exc.code, exc.url
        error = str(exc)
    except Exception as exc:
        return {"path": name, "url": url, "error": str(exc), "status": None}
    (ROOT / name).write_bytes(body)
    return {
        "path": name,
        "url": url,
        "resolved_url": resolved,
        "status": status,
        "retrieved_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "error": error,
    }


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(acquire, SOURCES.items()))
    original = Path("C:/Users/supra/Downloads/evidence_report.md")
    body = (ROOT / "evidence_report.md").read_bytes()
    assert body == original.read_bytes()
    rows.insert(
        0,
        {
            "path": "evidence_report.md",
            "source_path": str(original),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        },
    )
    companions = [
        "evidence_records.json",
        "ai_deployment_benchmark_evidence.json",
        "m5_ultra_512gb_benchmark_evidence.json",
    ]
    manifest = {
        "purpose": "New enterprise report verification; prior archives reused separately.",
        "files": rows,
        "companion_probes": [
            {"path": str(original.parent / n), "exists": (original.parent / n).exists()}
            for n in companions
        ],
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "files": [
                    {
                        "path": r["path"],
                        "status": r.get("status"),
                        "bytes": r.get("bytes"),
                        "error": r.get("error"),
                    }
                    for r in rows
                ],
                "companion_probes": manifest["companion_probes"],
            },
            indent=2,
        )
    )
