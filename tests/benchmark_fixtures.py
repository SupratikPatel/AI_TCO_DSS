"""Explicit synthetic execution facts; these are not empirical catalog evidence."""

from ai_tco_dss.domain.benchmark_conditions import BenchmarkConditions


def conditions(**changes):
    return BenchmarkConditions.model_validate(
        {
            "nodes": 1,
            "accelerator_memory_gb": 64,
            "system_ram_gb": 0,
            "runtime": "test-runtime",
            "runtime_version": "1",
            "model_revision": "test-revision",
            "kv_precision": "FP16",
            "optimized_backend": True,
            "prompt_cache_hit_rate": 0.5,
            "quantization": "uniform-INT4",
            "speculative_mode": "none",
            "speculative_config": "disabled",
            "concurrency": 5,
            "protocol": "single-request-decode",
            "cache_state": "cold",
            "residency": "resident",
            "output_tokens": 3750,  # default 1,500 output tokens * medium thinking (2.5)
            **changes,
        }
    )
