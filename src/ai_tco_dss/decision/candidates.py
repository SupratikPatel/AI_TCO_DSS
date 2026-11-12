"""Pure deployment enumeration over one immutable catalog (Req 27)."""

from ai_tco_dss.decision.quality import quality_ratios, resolve_quality
from ai_tco_dss.domain import (
    ApiCostInput,
    ApiPerformanceInput,
    BenchmarkSet,
    CandidateEvaluation,
    CandidateInput,
    CandidateKind,
    CandidateSet,
    DeploymentMode,
    EngineParameters,
    FilterFailure,
    HardwareSpec,
    HybridCostInput,
    LicenseType,
    Metric,
    ModelSpec,
    PerformanceInput,
    PerformanceResult,
    PrecisionFormat,
    QualityScore,
    RentalCostInput,
    SizingInput,
    TcoInput,
    ValueOrigin,
    WorkloadInput,
)
from ai_tco_dss.domain.errors import EngineInputError, UnknownIdentifierError
from ai_tco_dss.engines import compute_performance, compute_tco, compute_workload, size_deployment
from ai_tco_dss.engines.baselines import api_monthly_cost, compute_hybrid_cost, compute_rental_cost
from ai_tco_dss.engines.performance import compute_api_performance

BITS = (
    (PrecisionFormat.FP16, 16),
    (PrecisionFormat.BF16, 16),
    (PrecisionFormat.FP8, 8),
    (PrecisionFormat.INT8, 8),
    (PrecisionFormat.INT4, 4),
    (PrecisionFormat.INT3, 3),
    (PrecisionFormat.INT2, 2),
)
EMPTY_PERFORMANCE = PerformanceResult(
    decode_tps=None, prefill_tps=None, ttft_s=None, effective_tps=None, warnings=(), traces=()
)


def precisions(hw: HardwareSpec, model: ModelSpec) -> tuple[PrecisionFormat, ...]:
    return tuple(
        sorted(
            set(hw.supported_native_precisions) | {p.precision for p in model.calibrated_weights_gb}
        )
    )


def archetype(hw: HardwareSpec) -> str:
    if hw.deployment_mode == DeploymentMode.PER_SEAT_WORKSTATION:
        return "Sovereign Per-Seat Workstation"
    if hw.deployment_mode in (
        DeploymentMode.TIERED_OFFLOAD_APPLIANCE,
        DeploymentMode.HETEROGENEOUS_ROUTED_APPLIANCE,
        DeploymentMode.WIRELESS_EGPU_APPLIANCE,
    ):
        return "Heterogeneous Modality / Scavenged Rig"
    return "Sovereign Centralized Server / PD-Disagg"


def generate_candidates(inp: CandidateInput, params: EngineParameters) -> CandidateSet:
    catalog, scenario = inp.catalog, inp.scenario
    use_case = next((u for u in catalog.use_cases if u.id == scenario.decision.use_case), None)
    if use_case is None:
        raise UnknownIdentifierError("use case", scenario.decision.use_case)
    ratios = quality_ratios(catalog, params)
    models = sorted(catalog.models, key=lambda m: m.id)
    open_models = [m for m in models if m.type == "open-weights"]
    api_models = [m for m in models if m.type == "commercial-api"]
    reference = next(
        (
            m
            for m in models
            if m.id
            == (
                scenario.decision.reference_api_model_id
                or catalog.baseline_defaults.reference_api_model_id
            )
        ),
        None,
    )
    quality = {m.id: resolve_quality(catalog, m.id, use_case, ratios, params) for m in models}
    popularity = {e.model_id: e.value for e in catalog.popularity.entries}
    workloads = {
        m.id: compute_workload(
            WorkloadInput(profile=scenario.workload, model=m, harnesses=catalog.harnesses), params
        )
        for m in models
    }
    benchmarks = {
        (h.id, m.id): BenchmarkSet(
            records=tuple(
                b for b in catalog.benchmarks if b.hardware_id == h.id and b.model_id == m.id
            )
        )
        for h in catalog.hardware
        for m in open_models
    }
    alternatives = tuple(
        m.name for m in open_models if m.license_type in (LicenseType.MIT, LicenseType.APACHE_2)
    )
    # Hardware is part of the key: rental host RAM/mode can differ from purchased hardware.
    cache: dict[tuple[HardwareSpec, str, PrecisionFormat, int, float], CandidateEvaluation] = {}

    def common(model: ModelSpec) -> dict[str, object]:
        score = quality[model.id]
        notes: tuple[str, ...] = (score.fallback_note,) if score and score.fallback_note else ()
        if model.id not in popularity:
            notes += (
                f"Popularity not available for {model.id}; using 0 "
                f"(snapshot {catalog.popularity.snapshot_date}, {catalog.popularity.source_id}).",
            )
        return dict(
            model_id=model.id,
            quality=score,
            popularity=popularity.get(model.id, 0.0),
            notes=notes,
            model_max_context_tokens=model.max_context_length.value,
            api_has_eu_endpoint=bool(model.eu_pinned_endpoint and model.eu_pinned_endpoint.value),
        )

    def local(
        hw: HardwareSpec,
        model: ModelSpec,
        precision: PrecisionFormat,
        nodes: int,
        demand_share: float = 1.0,
    ) -> CandidateEvaluation:
        key = (hw, model.id, precision, nodes, demand_share)
        if key in cache:
            return cache[key]
        cid = f"onprem:{hw.id}:{nodes}x:{model.id}:{precision.value}"
        sizing = None
        perf = None
        tco = None
        failures: tuple[FilterFailure, ...] = ()
        notes: tuple[str, ...] = ()
        try:
            sizing = size_deployment(
                SizingInput(
                    hardware=hw,
                    model=model,
                    precision=precision,
                    requested_nodes=nodes,
                    options=scenario.sizing,
                    profile=scenario.workload,
                    license_alternatives=alternatives,
                ),
                params,
            )
            if sizing.is_feasible:
                perf = compute_performance(
                    PerformanceInput(
                        hardware=hw,
                        model=model,
                        precision=precision,
                        sizing=sizing,
                        workload=workloads[model.id],
                        profile=scenario.workload,
                        options=scenario.sizing,
                        benchmarks=benchmarks[(hw.id, model.id)],
                    ),
                    params,
                )
            tco = compute_tco(
                TcoInput(
                    hardware=hw,
                    nodes=nodes,
                    sizing=sizing,
                    performance=perf or EMPTY_PERFORMANCE,
                    workload=workloads[model.id],
                    profile=scenario.workload,
                    financials=scenario.financials,
                    tariffs=catalog.tariffs,
                    hubs=catalog.hubs,
                    benchmarks=benchmarks[(hw.id, model.id)],
                    demand_share=demand_share,
                    options=scenario.sizing,
                    cloud_ttft_s=reference.api_ttft_s.value
                    if reference and reference.api_ttft_s
                    else None,
                ),
                params,
            )
        except EngineInputError as exc:
            failures = (
                FilterFailure(
                    name="engine_input", measured=str(exc), threshold="valid engine inputs"
                ),
            )
            notes = (str(exc),)
        agreement = sizing.token_agreement_rate if sizing else None
        support = max(
            0.0,
            min(hw.lifecycle_clocks.software_support_years.value, params.risk_support_years_cap),
        )
        risk = params.risk_weight_support * (
            1 - support / params.risk_support_years_cap
        ) + params.risk_weight_fidelity * (
            1 - (agreement if agreement is not None else params.risk_missing_agreement)
        )
        fields = common(model)
        fields["notes"] = tuple(fields["notes"]) + notes  # type: ignore[arg-type]
        result = CandidateEvaluation.model_validate(
            dict(
                candidate_id=cid,
                kind=CandidateKind.ONPREM,
                label=f"{hw.name} x {nodes} + {model.name} {precision.value}",
                archetype=archetype(hw),
                hardware_id=hw.id,
                nodes=nodes,
                precision=precision,
                rental_id=None,
                api_model_id=None,
                local_candidate_id=None,
                sizing=sizing,
                performance=perf,
                tco=tco,
                capex=tco.capex.value if tco else 0.0,
                monthly_cost=tco.monthly_opex_total if tco else 0.0,
                cost_60m=tco.cost_60m if tco else 0.0,
                price_origin=tco.capex.origin
                if tco
                else ValueOrigin(origin="formula", source_ids=(hw.street_price.source_id,)),
                risk=max(0.0, min(1.0, risk)),
                utilization=tco.utilization if tco else None,
                eu_compliant=sizing.eu_commercial_license_valid if sizing else False,
                failures=failures,
                **fields,
            )
        )
        cache[key] = result
        return result

    onprem = [
        local(hw, model, precision, nodes)
        for hw in sorted(catalog.hardware, key=lambda h: h.id)
        for nodes in sorted(set(hw.valid_node_counts.value) & {1, 2, 4, 8})
        for model in open_models
        for precision in precisions(hw, model)
    ]

    def api(model: ModelSpec, force_eu: bool = False) -> CandidateEvaluation:
        assert model.api_prices is not None
        endpoint = bool(model.eu_pinned_endpoint and model.eu_pinned_endpoint.value)
        eu = force_eu or (scenario.financials.strict_eu_sovereignty and endpoint)
        cost = None
        perf = None
        failures: tuple[FilterFailure, ...] = ()
        fields = common(model)
        try:
            cost = api_monthly_cost(
                ApiCostInput(
                    model_id=model.id,
                    workload=workloads[model.id],
                    profile=scenario.workload,
                    prices=model.api_prices,
                    eu_pinned=eu,
                    gateway_fee_usd=catalog.baseline_defaults.gateway_fee_per_month.value,
                ),
                params,
            )
            perf = compute_api_performance(
                ApiPerformanceInput(
                    model=model, workload=workloads[model.id], profile=scenario.workload
                ),
                params,
            )
        except EngineInputError as exc:
            failures = (
                FilterFailure(
                    name="engine_input", measured=str(exc), threshold="valid engine inputs"
                ),
            )
            fields["notes"] = (*fields["notes"], str(exc))  # type: ignore[misc]
        return CandidateEvaluation.model_validate(
            dict(
                candidate_id=f"api:{model.id}",
                kind=CandidateKind.API,
                label=f"{model.name} ({'EU-pinned' if eu and endpoint else 'global'} API)",
                archetype="Baseline C" if eu else "Baseline B",
                hardware_id=None,
                nodes=None,
                precision=None,
                rental_id=None,
                api_model_id=model.id,
                local_candidate_id=None,
                sizing=None,
                performance=perf,
                tco=None,
                capex=0.0,
                monthly_cost=cost.monthly.value if cost else 0.0,
                cost_60m=60 * cost.monthly.value if cost else 0.0,
                price_origin=cost.monthly.origin
                if cost
                else ValueOrigin(
                    origin="formula", source_ids=(model.api_prices.input_per_1m.source_id,)
                ),
                risk=params.risk_weight_support * params.risk_api_lockin,
                utilization=None,
                eu_compliant=endpoint or not scenario.financials.strict_eu_sovereignty,
                failures=failures,
                **fields,
            )
        )

    apis = [api(m) for m in api_models]
    rentals = []
    for rental in sorted(catalog.rentals, key=lambda r: r.id):
        original = next((h for h in catalog.hardware if h.id == rental.gpu_hardware_id), None)
        if original is None:
            raise UnknownIdentifierError("hardware", rental.gpu_hardware_id)
        nodes = rental.gpu_count.value
        # Sizing multiplies per-node host RAM by nodes. Rental RAM describes the entire server.
        hw = original.model_copy(
            update={
                "deployment_mode": DeploymentMode.CLOUD_RENTAL,
                "system_ram_total_installed_gb": rental.system_ram_total_installed_gb.model_copy(
                    update={"value": rental.system_ram_total_installed_gb.value / nodes}
                ),
            }
        )
        for model in open_models:
            options = [local(hw, model, p, nodes) for p in precisions(hw, model)]
            fits = [c for c in options if c.sizing and c.sizing.is_feasible and c.tco]
            peak_fits = [
                c
                for c in fits
                if c.sizing
                and c.sizing.max_concurrent_users >= scenario.workload.peak_concurrent_requests
            ]
            chosen = (
                min(
                    peak_fits or fits,
                    key=lambda c: (
                        -dict(BITS)[PrecisionFormat(str(c.precision))],
                        str(c.precision),
                    ),
                )
                if fits
                else min(
                    options,
                    key=lambda c: (
                        c.sizing.weights.value if c.sizing else float("inf"),
                        str(c.precision),
                    ),
                )
            )
            personnel = dict(chosen.tco.monthly_opex)["personnel"] if chosen.tco else 0.0
            rental_cost = None
            rental_failures = chosen.failures
            rental_notes = chosen.notes
            try:
                rental_cost = compute_rental_cost(
                    RentalCostInput(rental=rental, personnel_monthly_usd=personnel), params
                )
            except EngineInputError as exc:
                rental_failures += (
                    FilterFailure(
                        name="engine_input", measured=str(exc), threshold="valid rental costs"
                    ),
                )
                rental_notes += (str(exc),)
            agreement = chosen.sizing.token_agreement_rate if chosen.sizing else None
            risk = (
                params.risk_weight_support * params.risk_rental_lifecycle
                + params.risk_weight_fidelity
                * (1 - (agreement if agreement is not None else params.risk_missing_agreement))
            )
            rentals.append(
                chosen.model_copy(
                    update={
                        "candidate_id": f"rental:{rental.id}:{model.id}",
                        "kind": CandidateKind.RENTAL,
                        "label": f"{rental.name} + {model.name} {chosen.precision}",
                        "archetype": "Dedicated EU Cloud GPU",
                        "rental_id": rental.id,
                        "capex": 0.0,
                        "monthly_cost": rental_cost.monthly_usd + personnel if rental_cost else 0.0,
                        "cost_60m": rental_cost.cost_60m if rental_cost else 0.0,
                        "price_origin": rental_cost.origin if rental_cost else chosen.price_origin,
                        "failures": rental_failures,
                        "notes": rental_notes,
                        "risk": risk,
                    }
                )
            )
    # Choose the cheapest local component that passes all constraints at its routed demand.
    from ai_tco_dss.decision.filters import apply_hard_filters
    from ai_tco_dss.domain import FilterInput

    routed = [
        c.model_copy(
            update={
                "utilization": c.utilization * scenario.financials.local_offload_ratio
                if c.utilization is not None
                else None
            }
        )
        for c in onprem
    ]
    eligible_ids = {
        c.candidate_id
        for c in apply_hard_filters(
            FilterInput(candidates=tuple(routed), scenario=scenario, use_case=use_case), params
        ).feasible
    }
    feasible_local = [
        c
        for c in onprem
        if c.sizing
        and c.sizing.is_feasible
        and c.tco
        and not c.failures
        and c.candidate_id in eligible_ids
    ]
    hybrids = []
    warnings: tuple[str, ...] = ()
    if not feasible_local:
        warnings = (
            "No Hybrid_Split could be formed because no feasible on-premise deployment exists.",
        )
    else:
        anchor = min(
            feasible_local,
            key=lambda c: (c.cost_60m, c.hardware_id, c.nodes, c.model_id, c.precision),
        )
        assert anchor.tco is not None
        r = scenario.financials.local_offload_ratio
        for model in api_models:
            remote = api(model, force_eu=True)
            hybrid_cost = compute_hybrid_cost(
                HybridCostInput(
                    local=anchor.tco, api_c_monthly_usd=remote.monthly_cost, local_offload_ratio=r
                ),
                params,
            )
            # Full fixed local cost; only demanded local token share is reduced.
            assert anchor.precision is not None and anchor.nodes is not None
            part = local(
                next(h for h in catalog.hardware if h.id == anchor.hardware_id),
                next(m for m in open_models if m.id == anchor.model_id),
                anchor.precision,
                anchor.nodes,
                demand_share=r,
            )
            parts = (part, remote)
            score = _hybrid_quality(anchor.quality, remote.quality, r)
            perf = _hybrid_performance(anchor.performance, remote.performance, r)
            notes = tuple(dict.fromkeys((*anchor.notes, *remote.notes)))
            hybrids.append(
                anchor.model_copy(
                    update={
                        "candidate_id": f"hybrid:{anchor.candidate_id}+{model.id}",
                        "kind": CandidateKind.HYBRID,
                        "label": f"{anchor.label} + {model.name} ({r:.0%} local)",
                        "archetype": "Hybrid Split",
                        "api_model_id": model.id,
                        "api_has_eu_endpoint": remote.api_has_eu_endpoint,
                        "local_candidate_id": anchor.candidate_id,
                        "components": parts,
                        "capex": hybrid_cost.capex_usd,
                        "monthly_cost": hybrid_cost.monthly_usd,
                        "cost_60m": hybrid_cost.cost_60m,
                        "price_origin": ValueOrigin(
                            origin="formula",
                            source_ids=tuple(
                                dict.fromkeys(
                                    (
                                        *anchor.price_origin.source_ids,
                                        *remote.price_origin.source_ids,
                                    )
                                )
                            ),
                        ),
                        "performance": perf,
                        "quality": score,
                        "risk": r * anchor.risk + (1 - r) * remote.risk,
                        "popularity": r * anchor.popularity + (1 - r) * remote.popularity,
                        "utilization": part.utilization,
                        "eu_compliant": anchor.eu_compliant and remote.api_has_eu_endpoint,
                        "notes": notes,
                    }
                )
            )
    return CandidateSet(candidates=tuple((*onprem, *apis, *rentals, *hybrids)), warnings=warnings)


def _hybrid_quality(
    local: QualityScore | None, remote: QualityScore | None, r: float
) -> QualityScore | None:
    if local is None or remote is None:
        return None
    return local.model_copy(
        update={
            "value": r * local.value + (1 - r) * remote.value,
            "origin": ValueOrigin(
                origin="formula",
                source_ids=tuple(
                    dict.fromkeys((*local.origin.source_ids, *remote.origin.source_ids))
                ),
            ),
            "fallback_note": " ".join(n for n in (local.fallback_note, remote.fallback_note) if n)
            or None,
        }
    )


def _hybrid_performance(
    local: PerformanceResult | None, remote: PerformanceResult | None, r: float
) -> PerformanceResult:
    def mean(name: str) -> Metric | None:
        a = getattr(local, name) if local else None
        b = getattr(remote, name) if remote else None
        if a is None or b is None:
            return None
        return Metric(
            value=r * a.value + (1 - r) * b.value,
            unit=a.unit,
            origin=ValueOrigin(
                origin="formula",
                source_ids=tuple(dict.fromkeys((*a.origin.source_ids, *b.origin.source_ids))),
            ),
        )

    return PerformanceResult(
        decode_tps=mean("decode_tps"),
        prefill_tps=mean("prefill_tps"),
        ttft_s=mean("ttft_s"),
        effective_tps=mean("effective_tps"),
        warnings=(),
        traces=(),
    )
