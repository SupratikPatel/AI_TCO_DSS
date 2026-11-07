"""Service_Layer orchestration: `catalog_overview`, `load_workload` and `size` (Task 5)."""

from pathlib import Path

from ai_tco_dss.catalog import CatalogRepository, get_default_repository
from ai_tco_dss.domain import (
    Catalog,
    CatalogItem,
    CatalogOverview,
    FxInfo,
    HardwareSpec,
    LicenseType,
    ModelSpec,
    SizeRequest,
    SizeResult,
    SizingInput,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.domain.errors import UnknownIdentifierError
from ai_tco_dss.engines import compute_workload, size_deployment
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


def size(request: SizeRequest, *, repo: CatalogRepository | None = None) -> SizeResult:
    """Sizing and workload of one hardware-model pairing for View 1 (Req 38.1, 38.7, 38.8).

    Performance and the AA v5 score are added in Task 6 (`None` until then).
    """
    request = SizeRequest.model_validate(request)
    catalog = _repository(repo).catalog(request.scenario.fx_override)
    hardware = _hardware(catalog, request.hardware_id)
    model = _model(catalog, request.model_id)
    params = load_engine_parameters()
    scenario = request.scenario
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
            precision=request.precision,
            requested_nodes=request.nodes,
            options=scenario.sizing,
            profile=scenario.workload,
            license_alternatives=alternatives,
        ),
        params,
    )
    return SizeResult(sizing=sizing, performance=None, workload=workload, aa_index_v5=None)
