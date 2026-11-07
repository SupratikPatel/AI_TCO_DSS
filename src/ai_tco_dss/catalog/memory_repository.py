"""In-memory Catalog_Repository holding an already-built Catalog (tests, later a DB)."""

from pathlib import Path

from ai_tco_dss.catalog.fx import convert_catalog
from ai_tco_dss.catalog.json_repository import read_workload_file
from ai_tco_dss.domain import Catalog, WorkloadProfile


class InMemoryCatalogRepository:
    def __init__(self, catalog: Catalog, workload: WorkloadProfile) -> None:
        self._catalog = catalog
        self._workload = workload

    def catalog(self, fx_override: float | None = None) -> Catalog:
        if fx_override is None:
            return self._catalog
        return convert_catalog(self._catalog, fx_override, is_override=True)

    def load_workload(self, path: Path | None = None) -> WorkloadProfile:
        """The held default Workload_Profile, or the profile of the workload file `path`."""
        return self._workload if path is None else read_workload_file(path)
