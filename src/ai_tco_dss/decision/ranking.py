"""Six-criterion SAW, missing data and deterministic explanations (Req 29)."""

from functools import cmp_to_key
from math import isfinite

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
    elif inp.method != RankingMethod.SAW:
        error = "TOPSIS is deferred to Task 10; select SAW."
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
    raws = [_raw(c) for c in inp.feasible]
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
                    raw=x,
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
    return RankingResult(
        method=inp.method,
        weights_normalised=weight_contract,
        ranked=ranked,
        explanation=explanation.strip() if explanation else None,
        ranking_error=None,
    )
