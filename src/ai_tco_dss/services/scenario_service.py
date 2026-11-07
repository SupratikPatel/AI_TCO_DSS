"""Service_Layer orchestration. Task 3 provides `catalog_overview` only."""

from ai_tco_dss.catalog import CatalogRepository, get_default_repository
from ai_tco_dss.domain import CatalogItem, CatalogOverview, FxInfo


def catalog_overview(
    *, repo: CatalogRepository | None = None, fx_override: float | None = None
) -> CatalogOverview:
    """Counts, selectable items and FX info for the start page and the sidebar (Req 6.1)."""
    repository = repo if repo is not None else get_default_repository()
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
