"""Service_Layer orchestration: `catalog_overview`, `load_workload`, `size` and
`project_tco`."""

import re
from pathlib import Path

from ai_tco_dss.catalog import CatalogRepository, get_default_repository
from ai_tco_dss.decision import apply_hard_filters, generate_candidates, rank_candidates
from ai_tco_dss.domain import (
    BaselineDInput,
    BaselineInput,
    BaselineResult,
    BenchmarkMetric,
    BenchmarkQuery,
    BenchmarkSet,
    CandidateEvaluation,
    CandidateInput,
    CandidateKind,
    Catalog,
    CatalogItem,
    CatalogOverview,
    DeploymentMode,
    EngineParameters,
    FilterInput,
    FxInfo,
    HardwareSpec,
    HybridCostInput,
    LicenseType,
    ModelSpec,
    PerformanceInput,
    PerformanceResult,
    PrecisionFormat,
    QualityScore,
    RankingInput,
    Recommendation,
    RecommendRequest,
    RentalCostInput,
    Scenario,
    ScenarioRequest,
    ScenarioResult,
    SizeRequest,
    SizeResult,
    SizingInput,
    SizingResult,
    TcoInput,
    TcoProjection,
    TcoRequest,
    TimelineInput,
    ValueOrigin,
    WorkloadInput,
    WorkloadProfile,
    WorkloadResult,
)
from ai_tco_dss.domain.errors import EngineInputError, UnknownIdentifierError
from ai_tco_dss.engines import (
    compute_baselines,
    compute_performance,
    compute_tco,
    compute_workload,
    select_benchmark,
    size_deployment,
)
from ai_tco_dss.engines.baselines import (
    compute_baseline_d,
    compute_hybrid_cost,
    compute_rental_cost,
    compute_timeline,
)
from ai_tco_dss.settings import load_engine_parameters

OPEN_LICENSES = (LicenseType.APACHE_2, LicenseType.MIT)


def _repository(repo: CatalogRepository | None) -> CatalogRepository:
    return repo if repo is not None else get_default_repository()


def catalog_overview(
    *, repo: CatalogRepository | None = None, fx_override: float | None = None
) -> CatalogOverview:
    """Counts, selectable items and FX info for the start page and the sidebar (Req 6.1)."""
    repository = _repository(repo)
    catalog = repository.catalog(fx_override)
    return CatalogOverview(
        counts=(
            ("hardware", len(catalog.hardware)),
            ("models", len(catalog.models)),
            ("rentals", len(catalog.rentals)),
            ("benchmarks", len(catalog.benchmarks)),
            ("sources", len(catalog.sources)),
        ),
        hardware=tuple(CatalogItem(id=h.id, label=h.name) for h in catalog.hardware),
        models=tuple(CatalogItem(id=m.id, label=m.name) for m in catalog.models),
        use_cases=tuple(CatalogItem(id=u.id.value, label=u.label) for u in catalog.use_cases),
        presets=tuple(CatalogItem(id=p.id.value, label=p.id.value) for p in catalog.presets),
        hubs=tuple(CatalogItem(id=h.id.value, label=h.id.value) for h in catalog.hubs),
        tariffs=tuple(CatalogItem(id=t.id.value, label=t.id.value) for t in catalog.tariffs),
        default_active_users=repository.load_workload().active_users,
        fx=FxInfo(
            rate=catalog.fx_active_rate,
            source_id=catalog.fx.source_id,
            rate_date=catalog.fx.rate_date,
            is_override=catalog.fx_is_override,
        ),
    )


def load_workload(
    path: Path | None = None, *, repo: CatalogRepository | None = None
) -> WorkloadProfile:
    """The Workload_Profile of `path` (None: the Default_Workload_File) (Req 14.3, 14.7).

    Raises `WorkloadFileError` naming the path and each failing field.
    """
    return _repository(repo).load_workload(path)


def _hardware(catalog: Catalog, hardware_id: str) -> HardwareSpec:
    found = next((h for h in catalog.hardware if h.id == hardware_id), None)
    if found is None:
        raise UnknownIdentifierError("hardware", hardware_id)
    return found


def _model(catalog: Catalog, model_id: str) -> ModelSpec:
    found = next((m for m in catalog.models if m.id == model_id), None)
    if found is None:
        raise UnknownIdentifierError("model", model_id)
    return found


def _pair_benchmarks(catalog: Catalog, hardware_id: str, model_id: str) -> BenchmarkSet:
    """The per-call index of design.md: records of one (model_id, hardware_id) pair."""
    return BenchmarkSet(
        records=tuple(
            r for r in catalog.benchmarks if r.model_id == model_id and r.hardware_id == hardware_id
        )
    )


def _quality(
    catalog: Catalog, model_id: str, metric: BenchmarkMetric, params: EngineParameters
) -> QualityScore | None:
    """Measured quality score of a model, without hardware or context (Req 9.9)."""
    records = tuple(r for r in catalog.benchmarks if r.model_id == model_id)
    record = select_benchmark(
        BenchmarkQuery(
            records=BenchmarkSet(records=records),
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


def _deployment(
    catalog: Catalog,
    scenario: Scenario,
    hardware: HardwareSpec,
    model: ModelSpec,
    precision: PrecisionFormat,
    nodes: float,
    params: EngineParameters,
) -> tuple[WorkloadResult, SizingResult, PerformanceResult | None]:
    """Workload, sizing and (for feasible pairings) performance of one deployment."""
    workload = compute_workload(
        WorkloadInput(profile=scenario.workload, model=model, harnesses=catalog.harnesses), params
    )
    alternatives = tuple(
        m.name
        for m in catalog.models
        if m.type == "open-weights" and m.license_type in OPEN_LICENSES
    )
    sizing = size_deployment(
        SizingInput(
            hardware=hardware,
            model=model,
            precision=precision,
            requested_nodes=nodes,
            options=scenario.sizing,
            profile=scenario.workload,
            license_alternatives=alternatives,
        ),
        params,
    )
    performance = None
    if sizing.is_feasible:
        performance = compute_performance(
            PerformanceInput(
                hardware=hardware,
                model=model,
                precision=precision,
                sizing=sizing,
                workload=workload,
                profile=scenario.workload,
                options=scenario.sizing,
                benchmarks=_pair_benchmarks(catalog, hardware.id, model.id),
            ),
            params,
        )
    return workload, sizing, performance


def size(request: SizeRequest, *, repo: CatalogRepository | None = None) -> SizeResult:
    """Sizing, workload, performance and the AA v5 score of one hardware-model pairing for
    View 1 (Req 38.1, 38.7, 38.8). Performance is computed for feasible pairings only.
    """
    request = SizeRequest.model_validate(request)
    catalog = _repository(repo).catalog(request.scenario.fx_override)
    hardware = _hardware(catalog, request.hardware_id)
    model = _model(catalog, request.model_id)
    params = load_engine_parameters()
    workload, sizing, performance = _deployment(
        catalog, request.scenario, hardware, model, request.precision, request.nodes, params
    )
    return SizeResult(
        sizing=sizing,
        performance=performance,
        workload=workload,
        aa_index_v5=_quality(catalog, model.id, BenchmarkMetric.AA_INDEX_V5, params),
    )


def _baselines(catalog: Catalog, scenario: Scenario, params: EngineParameters) -> BaselineResult:
    """Baselines A to C for the reference API model and the selected plan (Req 24)."""
    defaults = catalog.baseline_defaults
    ref_model = _model(
        catalog, scenario.decision.reference_api_model_id or defaults.reference_api_model_id
    )
    plan_id = scenario.financials.subscription_plan_id or defaults.default_plan_id
    plan = next((p for p in defaults.plans if p.id == plan_id), None)
    if plan is None:
        raise UnknownIdentifierError("subscription plan", plan_id)
    workload_ref = compute_workload(
        WorkloadInput(profile=scenario.workload, model=ref_model, harnesses=catalog.harnesses),
        params,
    )
    return compute_baselines(
        BaselineInput(
            workload_ref=workload_ref,
            profile=scenario.workload,
            ref_model=ref_model,
            plan=plan,
            gateway_fee_usd=defaults.gateway_fee_per_month.value,
            financials=scenario.financials,
        ),
        params,
    )


ONPREM_ID = re.compile(r"^onprem:([^:]+):(\d+)x:([^:]+):([^:]+)$")
ONPREM_ID_FORMAT = (
    "onprem:{hardware_id}:{nodes}x:{model_id}:{precision} "
    "(rental, API and hybrid candidates are added by Tasks 8 and 9)"
)
NO_PERFORMANCE = PerformanceResult(
    decode_tps=None, prefill_tps=None, ttft_s=None, effective_tps=None, warnings=(), traces=()
)


def _parse_onprem_id(candidate_id: str) -> tuple[str, int, str, PrecisionFormat]:
    match = ONPREM_ID.match(candidate_id)
    if match is None:
        raise EngineInputError("candidate_id", ONPREM_ID_FORMAT, candidate_id)
    hardware_id, nodes, model_id, precision = match.groups()
    try:
        return hardware_id, int(nodes), model_id, PrecisionFormat(precision)
    except ValueError as exc:
        allowed = ", ".join(p.value for p in PrecisionFormat)
        raise EngineInputError("precision", allowed, candidate_id) from exc


def _archetype(hardware: HardwareSpec) -> str:
    """Spec 05 §2.2 archetype of an on-premise deployment (design.md archetype mapping)."""
    if hardware.deployment_mode == DeploymentMode.PER_SEAT_WORKSTATION:
        return "Sovereign Per-Seat Workstation"
    if hardware.deployment_mode in (
        DeploymentMode.HETEROGENEOUS_ROUTED_APPLIANCE,
        DeploymentMode.WIRELESS_EGPU_APPLIANCE,
        DeploymentMode.TIERED_OFFLOAD_APPLIANCE,
    ):
        return "Heterogeneous Modality / Scavenged Rig"
    return "Sovereign Centralized Server / PD-Disagg"


def _project_onprem(request: TcoRequest, *, repo: CatalogRepository | None = None) -> TcoProjection:
    """TCO of one on-premise candidate plus Baselines A to C for View 2 and the audit drawer
    (Req 13.7, 22-26, 38.7, 38.8), anchored on the explicitly selected deployment."""
    request = TcoRequest.model_validate(request)
    scenario = request.scenario
    catalog = _repository(repo).catalog(scenario.fx_override)
    hardware_id, nodes, model_id, precision = _parse_onprem_id(request.candidate_id)
    hardware = _hardware(catalog, hardware_id)
    model = _model(catalog, model_id)
    params = load_engine_parameters()
    workload, sizing, performance = _deployment(
        catalog, scenario, hardware, model, precision, nodes, params
    )
    baselines = _baselines(catalog, scenario, params)
    ref_model = _model(catalog, baselines.reference_model_id)
    tco = compute_tco(
        TcoInput(
            hardware=hardware,
            nodes=nodes,
            sizing=sizing,
            performance=performance or NO_PERFORMANCE,
            workload=workload,
            profile=scenario.workload,
            financials=scenario.financials,
            tariffs=catalog.tariffs,
            hubs=catalog.hubs,
            benchmarks=_pair_benchmarks(catalog, hardware.id, model.id),
            cloud_ttft_s=ref_model.api_ttft_s.value if ref_model.api_ttft_s else None,
        ),
        params,
    )
    candidate = CandidateEvaluation(
        candidate_id=request.candidate_id,
        kind=CandidateKind.ONPREM,
        label=f"{hardware.name} x {nodes} + {model.name} {precision.value}",
        archetype=_archetype(hardware),
        hardware_id=hardware.id,
        nodes=nodes,
        model_id=model.id,
        precision=precision,
        rental_id=None,
        api_model_id=None,
        local_candidate_id=None,
        sizing=sizing,
        performance=performance,
        tco=tco,
        capex=tco.capex.value,
        monthly_cost=tco.monthly_opex_total,
        cost_60m=tco.cost_60m,
        price_origin=tco.capex.origin,
        quality=None,
        risk=0.0,
        popularity=0.0,
        utilization=tco.utilization,
        eu_compliant=sizing.eu_commercial_license_valid,
        failures=(),
        notes=("quality, risk and popularity are set by the Decision_Engine (Task 9)",),
    )
    rental = next((r for r in catalog.rentals if r.id == "hetzner-gex63"), None)
    if rental is None:
        rental = next(iter(catalog.rentals), None)
    if rental is None:
        raise EngineInputError("rentals", "at least one EU rental for the comparison")
    rental_cost = compute_rental_cost(
        RentalCostInput(rental=rental, personnel_monthly_usd=dict(tco.monthly_opex)["personnel"]),
        params,
    )
    hybrid = compute_hybrid_cost(
        HybridCostInput(
            local=tco,
            api_c_monthly_usd=baselines.c_monthly.value,
            local_offload_ratio=scenario.financials.local_offload_ratio,
        ),
        params,
    )
    baseline_d = compute_baseline_d(
        BaselineDInput(
            performance=performance,
            utilization=tco.utilization,
            profile=scenario.workload,
            model=model,
            infeasible_reason=sizing.oom_reason if not sizing.is_feasible else None,
        ),
        params,
    )
    timeline = compute_timeline(
        TimelineInput(
            anchor_candidate_id=candidate.candidate_id,
            onprem=tco,
            include_resale=scenario.financials.include_resale_value,
            baselines=baselines,
            baseline_d=baseline_d,
            rental=rental_cost,
            hybrid=hybrid,
            hybrid_api_model_id=ref_model.id,
            decode_tps=performance.decode_tps if performance else None,
            open_output_price=model.open_weights_output_price_per_1m,
        ),
        params,
    )
    return TcoProjection(candidate=candidate, timeline=timeline, baselines=baselines)


def recommend(
    request: RecommendRequest, *, repo: CatalogRepository | None = None
) -> Recommendation:
    """Enumerate, filter and rank using one repository snapshot (Req 27-29/38)."""
    request = RecommendRequest.model_validate(request)
    catalog = _repository(repo).catalog(request.scenario.fx_override)
    return _recommend(catalog, request.scenario, load_engine_parameters())


def _recommend(catalog: Catalog, scenario: Scenario, params: EngineParameters) -> Recommendation:
    preset = next((p for p in catalog.presets if p.id == scenario.decision.preset), None)
    use_case = next((u for u in catalog.use_cases if u.id == scenario.decision.use_case), None)
    if preset is None:
        raise UnknownIdentifierError("preset", scenario.decision.preset)
    if use_case is None:
        raise UnknownIdentifierError("use case", scenario.decision.use_case)
    if scenario.decision.reference_api_model_id:
        _model(catalog, scenario.decision.reference_api_model_id)
    candidates = generate_candidates(CandidateInput(catalog=catalog, scenario=scenario), params)
    filtered = apply_hard_filters(
        FilterInput(candidates=candidates.candidates, scenario=scenario, use_case=use_case), params
    )
    ranking = rank_candidates(
        RankingInput(
            feasible=filtered.feasible,
            weights=scenario.decision.weights or preset.weights,
            method=scenario.decision.method,
        ),
        params,
    )
    return Recommendation(
        use_case=scenario.decision.use_case,
        method=ranking.method,
        weights_normalised=ranking.weights_normalised,
        ranked=ranking.ranked,
        rejected=filtered.rejected,
        explanation=ranking.explanation,
        ranking_error=ranking.ranking_error,
        warnings=candidates.warnings,
    )


def _anchor(recommendation: Recommendation) -> str | None:
    if recommendation.ranked:
        top = recommendation.ranked[0].evaluation
        if top.kind == CandidateKind.ONPREM:
            return top.candidate_id
    all_candidates = (*[r.evaluation for r in recommendation.ranked], *recommendation.rejected)
    hybrid = next((c for c in all_candidates if c.kind == CandidateKind.HYBRID), None)
    return hybrid.local_candidate_id if hybrid else None


def evaluate_scenario(
    request: ScenarioRequest, *, repo: CatalogRepository | None = None
) -> ScenarioResult:
    """Complete scenario plus the on-premise timeline anchor of design D-09."""
    request = ScenarioRequest.model_validate(request)
    repository = _repository(repo)
    scenario = request.scenario
    catalog = repository.catalog(scenario.fx_override)
    recommendation = _recommend(catalog, scenario, load_engine_parameters())
    anchor_id = _anchor(recommendation)
    projection = (
        _project_onprem(TcoRequest(scenario=scenario, candidate_id=anchor_id), repo=repository)
        if anchor_id
        else None
    )
    return ScenarioResult(
        scenario=scenario,
        recommendation=recommendation,
        baselines=projection.baselines
        if projection
        else _baselines(catalog, scenario, load_engine_parameters()),
        timeline=projection.timeline if projection else None,
        fx_rate=catalog.fx_active_rate,
        fx_source_id=catalog.fx.source_id,
        fx_rate_date=catalog.fx.rate_date,
        fx_is_override=catalog.fx_is_override,
        sources=catalog.sources,
        warnings=recommendation.warnings,
    )


def project_tco(request: TcoRequest, *, repo: CatalogRepository | None = None) -> TcoProjection:
    """Project any generated candidate; preserve the independent on-premise simulator."""
    request = TcoRequest.model_validate(request)
    repository = _repository(repo)
    result = recommend(RecommendRequest(scenario=request.scenario), repo=repository)
    candidates = (*[r.evaluation for r in result.ranked], *result.rejected)
    candidate = next((c for c in candidates if c.candidate_id == request.candidate_id), None)
    if candidate is None:
        if request.candidate_id.startswith("onprem:"):
            return _project_onprem(request, repo=repository)
        if not request.candidate_id.startswith(("api:", "rental:", "hybrid:")):
            raise EngineInputError("candidate_id", "onprem:, api:, rental: or hybrid: identifier")
        raise UnknownIdentifierError("candidate", request.candidate_id)
    anchor_id = (
        candidate.candidate_id if candidate.kind == CandidateKind.ONPREM else _anchor(result)
    )
    projection = (
        _project_onprem(
            TcoRequest(scenario=request.scenario, candidate_id=anchor_id), repo=repository
        )
        if anchor_id
        else None
    )
    return TcoProjection(
        candidate=candidate,
        timeline=projection.timeline if projection else None,
        baselines=projection.baselines
        if projection
        else _baselines(
            repository.catalog(request.scenario.fx_override),
            request.scenario,
            load_engine_parameters(),
        ),
    )
