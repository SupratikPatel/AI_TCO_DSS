"""Measured-first resolver (Req 9.3 to 9.6, 9.9, 9.10; design.md § "Measured-first resolver").

Pure: the result depends only on the `BenchmarkQuery` contract.
"""

from ai_tco_dss.domain import TIER_RANK, BenchmarkQuery, BenchmarkRecord
from ai_tco_dss.domain.errors import ConfigurationError


def _matches(record: BenchmarkRecord, query: BenchmarkQuery) -> bool:
    if (record.metric, record.model_id, record.hardware_id, record.precision) != (
        query.metric,
        query.model_id,
        query.hardware_id,
        query.precision,
    ):
        return False
    target = query.target_context
    if target is None:
        return True
    tokens = record.context_tokens
    return tokens is not None and abs(tokens - target) <= query.tolerance * target


def select_benchmark(query: BenchmarkQuery) -> BenchmarkRecord | None:
    """The one matching record (highest tier, latest access, closest context, lowest
    source_id), or None if no record matches metric, model, hardware, precision and
    the context-match tolerance. Quality queries pass `target_context=None`."""
    if not 0.0 <= query.tolerance <= 1.0:
        raise ConfigurationError("context_match_tolerance", query.tolerance)
    target = query.target_context

    def key(record: BenchmarkRecord) -> tuple[int, int, int, str]:
        distance = abs(record.context_tokens - target) if target and record.context_tokens else 0
        return (-TIER_RANK[record.tier], -record.accessed.toordinal(), distance, record.source_id)

    candidates = [r for r in query.records.records if _matches(r, query)]
    return min(candidates, key=key) if candidates else None
