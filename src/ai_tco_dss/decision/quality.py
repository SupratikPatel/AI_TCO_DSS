"""Measured-first use-case quality and catalog-derived AA scaling (Req 29/31)."""

from statistics import median

from ai_tco_dss.domain import (
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkSet,
    Catalog,
    EngineParameters,
    QualityScore,
    UseCaseSpec,
    ValueOrigin,
)
from ai_tco_dss.engines.resolver import select_benchmark


def measured_quality(
    catalog: Catalog, model_id: str, metric: BenchmarkMetric, params: EngineParameters
) -> QualityScore | None:
    record = select_benchmark(
        BenchmarkQuery(
            records=BenchmarkSet(
                records=tuple(r for r in catalog.benchmarks if r.model_id == model_id)
            ),
            metric=metric,
            model_id=model_id,
            hardware_id=None,
            precision=None,
            target_context=None,
            tolerance=params.context_match_tolerance,
        )
    )
    if record is None:
        return None
    return QualityScore(
        value=record.value,
        benchmark=metric,
        origin=ValueOrigin(origin="measured", source_ids=(record.source_id,)),
        fallback_note=None,
    )


def _ratio_pairs(
    catalog: Catalog, metric: BenchmarkMetric, params: EngineParameters
) -> tuple[tuple[QualityScore, QualityScore], ...]:
    pairs = []
    for model_id in sorted({r.model_id for r in catalog.benchmarks}):
        aa = measured_quality(catalog, model_id, BenchmarkMetric.AA_INDEX_V5, params)
        score = measured_quality(catalog, model_id, metric, params)
        if aa is not None and aa.value > 0 and score is not None:
            pairs.append((aa, score))
    return tuple(pairs)


def quality_ratios(catalog: Catalog, params: EngineParameters) -> dict[BenchmarkMetric, float]:
    ratios = {BenchmarkMetric.AA_INDEX_V5: 1.0}
    for metric in (BenchmarkMetric.TERMINAL_BENCH, BenchmarkMetric.SWE_BENCH):
        values = [score.value / aa.value for aa, score in _ratio_pairs(catalog, metric, params)]
        ratios[metric] = median(values) if len(values) >= 2 else params.aa_ratio_default
    return ratios


def resolve_quality(
    catalog: Catalog,
    model_id: str,
    use_case: UseCaseSpec,
    ratios: dict[BenchmarkMetric, float],
    params: EngineParameters,
) -> QualityScore | None:
    score = measured_quality(catalog, model_id, use_case.matching_benchmark, params)
    if score is not None:
        return score
    if use_case.second_choice_benchmark is not None:
        score = measured_quality(catalog, model_id, use_case.second_choice_benchmark, params)
        if score is not None:
            return score.model_copy(
                update={
                    "fallback_note": (
                        f"Fallback benchmark: {score.benchmark.value} ({score.value:g})."
                    )
                }
            )
    aa = measured_quality(catalog, model_id, BenchmarkMetric.AA_INDEX_V5, params)
    if aa is None:
        return None
    ratio = ratios[use_case.matching_benchmark]
    value = max(0.0, min(100.0, aa.value * ratio))
    pairs = _ratio_pairs(catalog, use_case.matching_benchmark, params)
    sources = aa.origin.source_ids
    if len(pairs) >= 2:
        sources = tuple(
            dict.fromkeys(
                (
                    *sources,
                    *(
                        source
                        for pair in pairs
                        for score in pair
                        for source in score.origin.source_ids
                    ),
                )
            )
        )
    return QualityScore(
        value=value,
        benchmark=BenchmarkMetric.AA_INDEX_V5,
        origin=ValueOrigin(origin="formula", source_ids=sources),
        fallback_note=(
            f"Fallback benchmark aa_index_v5: {aa.value:g} * ratio {ratio:g} = "
            f"{value:g} on {use_case.matching_benchmark.value} scale "
            "(clipped to [0, 100])."
        ),
    )
