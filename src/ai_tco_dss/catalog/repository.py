"""Catalog_Repository port: the only way the Service_Layer obtains Catalog data (Req 38.3)."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from ai_tco_dss.domain import Catalog, WorkloadProfile


@runtime_checkable
class CatalogRepository(Protocol):
    def catalog(self, fx_override: float | None = None) -> Catalog:
        """The USD Catalog at the file rate, or at `fx_override` USD per EUR."""
        ...

    def load_workload(self, path: Path | None = None) -> WorkloadProfile:
        """The Workload_Profile of `path`; None means `data/workloads/default.json`."""
        ...
