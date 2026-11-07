"""JSON-file Catalog_Repository (Req 11.1, 11.2, 11.10, 12.3, 12.4, 14.3, 14.7, 39.1 to 39.3)."""

import json
import threading
from pathlib import Path

from pydantic import ValidationError

from ai_tco_dss.catalog import loading
from ai_tco_dss.catalog.fx import convert_catalog
from ai_tco_dss.domain import Catalog, WorkloadProfile
from ai_tco_dss.domain.errors import CatalogLoadError, WorkloadFileError

DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[3] / "data"
MAX_OVERRIDE_CATALOGS = 8

_lock = threading.Lock()
_default_repository: "JsonCatalogRepository | None" = None


class JsonCatalogRepository:
    """Loads `root` once at construction; raises `CatalogLoadError` with every error."""

    def __init__(self, root: Path) -> None:
        self.root = root
        report = loading.load_catalog(root)
        if report.catalog is None or report.workload is None:
            raise CatalogLoadError(
                tuple(((root / e.file).as_posix(), e.field, e.message) for e in report.errors)
            )
        self._default = convert_catalog(
            report.catalog, report.catalog.fx.eur_to_usd, is_override=False
        )
        self._workload = report.workload
        self._overrides: dict[float, Catalog] = {}

    def catalog(self, fx_override: float | None = None) -> Catalog:
        if fx_override is None:
            return self._default
        with _lock:
            cached = self._overrides.get(fx_override)
            if cached is None:
                if len(self._overrides) >= MAX_OVERRIDE_CATALOGS:
                    self._overrides.pop(next(iter(self._overrides)))
                cached = convert_catalog(self._default, fx_override, is_override=True)
                self._overrides[fx_override] = cached
            return cached

    def load_workload(self, path: Path | None = None) -> WorkloadProfile:
        return self._workload if path is None else read_workload_file(path)


def read_workload_file(path: Path) -> WorkloadProfile:
    """The Workload_Profile of one workload JSON file (Req 14.3, 14.7).

    Fields the file omits take `WorkloadProfile` defaults. Raises `WorkloadFileError`
    naming the path and each failing field if the file is missing, is not valid JSON or
    fails `WorkloadFile` validation.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkloadFileError(path, ()) from exc
    try:
        return loading.WorkloadFile.model_validate(data).profile
    except ValidationError as exc:
        fields = tuple(dict.fromkeys(loading.field_path(tuple(e["loc"])) for e in exc.errors()))
        raise WorkloadFileError(path, fields) from exc


def get_default_repository() -> JsonCatalogRepository:
    """The process-wide repository on `data/`, built once under a lock (Req 39.1, 39.2)."""
    global _default_repository
    if _default_repository is None:
        with _lock:
            if _default_repository is None:
                _default_repository = JsonCatalogRepository(DEFAULT_DATA_ROOT)
    return _default_repository
