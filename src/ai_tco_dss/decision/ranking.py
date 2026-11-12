"""Six-criterion SAW/TOPSIS, missing data and deterministic explanations (Req 29-30)."""

from functools import cmp_to_key
from math import hypot, isfinite

from ai_tco_dss.domain import (
    CandidateEvaluation,
    Criterion,
    CriterionScore,
    CriterionWeights,
    EngineParameters,
    RankedCandidate,
    RankingInput,
    RankingMethod,
    RankingResult,
)


def _raw(c: CandidateEvaluation) -> tuple[float | None, ...]:
    perf = c.performance
    return (
        c.cost_60m,
        c.quality.value if c.quality else None,
        perf.effective_tps.value if perf and perf.effective_tps else None,
        perf.ttft_s.value if perf and perf.ttft_s else None,
        c.risk,
        c.popularity,
    )


def rank_candidates(inp: RankingInput, params: EngineParameters) -> RankingResult:
    weights = tuple(getattr(inp.weights, criterion.value) for criterion in Criterion)
    invalid = [c.value for c, w in zip(Criterion, weights, strict=True) if not isfinite(w) or w < 0]
    error = None
    if invalid or not isfinite(sum(weights)) or sum(weights) <= 0:
        error = "Invalid weights: " + (
            ", ".join(invalid) if invalid else "weight sum must be finite and > 0"
        )
    if error:
        return RankingResult(
            method=inp.method,
            weights_normalised=None,
            ranked=(),
            explanation=None,
            ranking_error=error,
        )
    norm_weights = tuple(w / sum(weights) for w in weights)
    weight_contract = CriterionWeights(
        **dict(zip((c.value for c in Criterion), norm_weights, strict=True))
    )
    originals = [_raw(c) for c in inp.feasible]
    raws = [
        tuple(
            min(x, inp.tps_target)
            if j == 2 and x is not None and inp.tps_target is not None
            else max(x, inp.ttft_target)
            if j == 3 and x is not None and inp.ttft_target is not None
            else x
            for j, x in enumerate(row)
        )
        for row in originals
    ]
    ranges = [tuple(x for row in raws if (x := row[j]) is not None) for j in range(6)]
    rows = []
    for candidate, raw in zip(inp.feasible, raws, strict=True):
        criteria = []
        for j, (criterion, x, weight) in enumerate(zip(Criterion, raw, norm_weights, strict=True)):
            values = ranges[j]
            normalised = 0.0
            if x is not None and values:
                lo, hi = min(values), max(values)
                assert lo is not None and hi is not None
                normalised = (
                    1.0 if hi == lo else ((hi - x) if j in (0, 3, 4) else (x - lo)) / (hi - lo)
                )
            criteria.append(
                CriterionScore(
                    criterion=criterion,
                    raw=_raw(candidate)[j],
                    missing=x is None,
                    normalised=normalised,
                    weight=weight,
                    contribution=weight * normalised,
                )
            )
        rows.append(
            RankedCandidate(
                rank=1,
                saw_rank=1,
                evaluation=candidate,
                saw_score=sum(c.contribution for c in criteria),
                criteria=tuple(criteria),
                topsis_closeness=None,
                d_plus=None,
                d_minus=None,
                topsis_rank=None,
            )
        )

    def compare(a: RankedCandidate, b: RankedCandidate) -> int:
        if abs(a.saw_score - b.saw_score) > 1e-9:
            return -1 if a.saw_score > b.saw_score else 1
        ka = (a.evaluation.cost_60m, a.evaluation.candidate_id)
        kb = (b.evaluation.cost_60m, b.evaluation.candidate_id)
        return (ka > kb) - (ka < kb)

    ranked = tuple(
        row.model_copy(update={"rank": i, "saw_rank": i})
        for i, row in enumerate(sorted(rows, key=cmp_to_key(compare)), 1)
    )
    if inp.method == RankingMethod.TOPSIS and ranked:
        # Missing values use the worst observed raw value (design § Decision pipeline).
        columns = []
        for j, values in enumerate(ranges):
            worst = (max(values) if j in (0, 3, 4) else min(values)) if values else 0.0
            column = tuple(x if (x := row[j]) is not None else worst for row in raws)
            norm = hypot(*column)
            columns.append(tuple(norm_weights[j] * x / norm if norm else 0.0 for x in column))
        ideal = tuple(min(col) if j in (0, 3, 4) else max(col) for j, col in enumerate(columns))
        anti = tuple(max(col) if j in (0, 3, 4) else min(col) for j, col in enumerate(columns))
        distances = {}
        for i, candidate in enumerate(inp.feasible):
            plus = hypot(*(columns[j][i] - ideal[j] for j in range(6)))
            minus = hypot(*(columns[j][i] - anti[j] for j in range(6)))
            distances[candidate.candidate_id] = (
                plus,
                minus,
                minus / (plus + minus) if plus + minus else 1.0,
            )
        rows = []
        for row in ranked:
            plus, minus, closeness = distances[row.evaluation.candidate_id]
            rows.append(
                row.model_copy(
                    update={"d_plus": plus, "d_minus": minus, "topsis_closeness": closeness}
                )
            )
        ranked = tuple(
            row.model_copy(update={"rank": i, "topsis_rank": i})
            for i, row in enumerate(
                sorted(
                    rows,
                    key=lambda row: (
                        -float(row.topsis_closeness or 0),
                        row.evaluation.cost_60m,
                        row.evaluation.candidate_id,
                    ),
                ),
                1,
            )
        )
    explanation = None
    if ranked:
        top = ranked[0]
        contributions = sorted(top.criteria, key=lambda c: -c.contribution)[:2]
        explanation = (
            f"{top.evaluation.label} ranks first. Largest contributions: "
            + ", ".join(f"{c.criterion.value} {c.contribution:.3f}" for c in contributions)
            + "."
        )
        explanation += " " + " ".join(top.evaluation.notes)
        if inp.method == RankingMethod.TOPSIS:
            explanation = (
                f"{top.evaluation.label} ranks first by TOPSIS "
                f"closeness {top.topsis_closeness:.3f} "
                f"(D+ {top.d_plus:.3f}, D- {top.d_minus:.3f}; SAW rank {top.saw_rank}). "
                "SAW contributions are shown for comparison. " + " ".join(top.evaluation.notes)
            )
    if explanation and (inp.tps_target is not None or inp.ttft_target is not None):
        explanation += " Performance scores saturate at the requested TPS and TTFT targets."
    return RankingResult(
        method=inp.method,
        weights_normalised=weight_contract,
        ranked=ranked,
        explanation=explanation.strip() if explanation else None,
        ranking_error=None,
    )
