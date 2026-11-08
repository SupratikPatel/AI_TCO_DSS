"""All applicable hard filters, including each hybrid component (Req 28)."""

from ai_tco_dss.domain import (
    CandidateEvaluation,
    CandidateKind,
    EngineParameters,
    FilteredCandidates,
    FilterFailure,
    FilterInput,
)


def _failures(c: CandidateEvaluation, inp: FilterInput) -> tuple[FilterFailure, ...]:
    if c.kind == CandidateKind.HYBRID:
        if not c.components:
            return (
                FilterFailure(
                    name="engine_input",
                    measured="component evaluations not available",
                    threshold="local and API component evaluations required",
                ),
            )
        # One failure per rule, with all failing components identified.
        failures: dict[str, list[tuple[str, FilterFailure]]] = {}
        for part in c.components:
            for failure in _failures(part, inp):
                failures.setdefault(failure.name, []).append((part.candidate_id, failure))
        return tuple(
            FilterFailure(
                name=name,
                measured="; ".join(f"{cid}: {f.measured}" for cid, f in group),
                threshold="; ".join(dict.fromkeys(f.threshold for _, f in group)),
            )
            for name, group in failures.items()
        )
    profile, fin = inp.scenario.workload, inp.scenario.financials
    api = c.kind == CandidateKind.API
    sizing, perf = c.sizing, c.performance
    failures_list = list(c.failures)

    def check(name: str, ok: bool, measured: object, threshold: object) -> None:
        if not ok:
            failures_list.append(
                FilterFailure(
                    name=name,
                    measured=str(measured) if measured is not None else "not available",
                    threshold=str(threshold),
                )
            )

    if not api:
        check(
            "memory_fit",
            sizing is not None and sizing.is_feasible,
            sizing.is_feasible if sizing else None,
            True,
        )
        check(
            "eu_license",
            sizing is not None and sizing.eu_commercial_license_valid,
            sizing.eu_commercial_license_valid if sizing else None,
            True,
        )
    if api and fin.strict_eu_sovereignty:
        check(
            "eu_sovereignty",
            c.api_has_eu_endpoint,
            "no EU-pinned endpoint",
            "EU-pinned endpoint required",
        )
    tps = perf.effective_tps.value if perf and perf.effective_tps else None
    ttft = perf.ttft_s.value if perf and perf.ttft_s else None
    if profile.min_acceptable_tps is not None:
        check(
            "min_tps",
            tps is not None and tps >= profile.min_acceptable_tps,
            tps,
            f">= {profile.min_acceptable_tps:g} tok/s",
        )
    if profile.max_acceptable_ttft_seconds is not None:
        check(
            "max_ttft",
            ttft is not None and ttft <= profile.max_acceptable_ttft_seconds,
            ttft,
            f"<= {profile.max_acceptable_ttft_seconds:g} s",
        )
    if not api:
        check(
            "users_served",
            c.utilization is not None and c.utilization <= 1.0,
            c.utilization,
            "<= 1.0",
        )
    context_ok = (
        (c.model_max_context_tokens is not None and c.model_max_context_tokens >= 128000)
        if api
        else (sizing is not None and sizing.meets_128k_agentic_context_floor)
    )
    check(
        "context_128k",
        context_ok,
        c.model_max_context_tokens
        if api
        else (sizing.meets_128k_agentic_context_floor if sizing else None),
        ">= 128000 tokens" if api else True,
    )
    check(
        "quality_floor",
        c.quality is not None and c.quality.value >= inp.use_case.quality_floor.value,
        c.quality.value if c.quality else "not available",
        f">= {inp.use_case.quality_floor.value:g}",
    )
    if fin.max_capex_budget_usd is not None and c.kind == CandidateKind.ONPREM:
        check(
            "capex_budget",
            c.capex <= fin.max_capex_budget_usd,
            c.capex,
            f"<= {fin.max_capex_budget_usd:g} USD",
        )
    return tuple(failures_list)


def apply_hard_filters(inp: FilterInput, params: EngineParameters) -> FilteredCandidates:
    feasible: list[CandidateEvaluation] = []
    rejected: list[CandidateEvaluation] = []
    for candidate in inp.candidates:
        failures = _failures(candidate, inp)
        checked = candidate.model_copy(
            update={
                "failures": failures,
                "notes": candidate.notes
                + (("no quality score available",) if candidate.quality is None else ()),
                "eu_compliant": candidate.eu_compliant
                and not any(f.name in ("eu_license", "eu_sovereignty") for f in failures),
            }
        )
        (rejected if failures else feasible).append(checked)
    return FilteredCandidates(
        feasible=tuple(feasible),
        rejected=tuple(sorted(rejected, key=lambda c: (len(c.failures), c.candidate_id))),
    )
