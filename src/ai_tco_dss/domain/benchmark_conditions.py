"""Execution facts shared by observed benchmarks and requested deployments.

Unknown facts stay null. Zero host RAM explicitly denotes unified/device-only memory.
All observation fields inherit their BenchmarkRecord's source, tier and access date.
"""

from typing import Literal

from pydantic import Field

from ai_tco_dss.domain.base import Contract
from ai_tco_dss.domain.enums import PrecisionFormat, SpeculativeMode


class BenchmarkConditions(Contract):
    nodes: int | None = Field(None, ge=1)
    accelerator_memory_gb: float | None = Field(None, gt=0)
    system_ram_gb: float | None = Field(None, ge=0)
    runtime: str | None = Field(None, min_length=1)
    runtime_version: str | None = Field(None, min_length=1)
    model_revision: str | None = Field(None, min_length=1)
    quantization: str | None = Field(None, min_length=1)
    kv_precision: PrecisionFormat | None = None
    optimized_backend: bool | None = None
    prompt_cache_hit_rate: float | None = Field(None, ge=0, le=1)
    speculative_mode: SpeculativeMode | None = None
    speculative_config: str | None = Field(None, min_length=1)
    concurrency: int | None = Field(None, ge=1)
    protocol: str | None = Field(None, min_length=1)
    cache_state: str | None = Field(None, min_length=1)
    residency: Literal["resident", "offload"] | None = None
    output_tokens: int | None = Field(None, ge=1)

    def missing_fields(self) -> tuple[str, ...]:
        return tuple(name for name in type(self).model_fields if getattr(self, name) is None)
