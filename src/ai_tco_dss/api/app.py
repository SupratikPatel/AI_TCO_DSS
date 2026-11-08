"""Stateless, same-origin FastAPI boundary (Requirement 43)."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ai_tco_dss import services
from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    CatalogOverview,
    DecisionOptions,
    EnterpriseFinancials,
    Scenario,
    SizeRequest,
    SizeResult,
    SizingOptions,
    TcoProjection,
    TcoRequest,
    WorkloadProfile,
)
from ai_tco_dss.domain.base import Contract
from ai_tco_dss.domain.errors import (
    CatalogLoadError,
    ConfigurationError,
    EngineInputError,
    UnknownIdentifierError,
    WorkloadFileError,
)

logger = logging.getLogger(__name__)


class ApiError(Contract):
    code: str
    message: str
    fields: tuple[str, ...] = ()


class Health(Contract):
    status: str = "ok"


class SimulationOptions(Contract):
    open_model_ids: tuple[str, ...]
    node_counts: tuple[tuple[str, tuple[int, ...]], ...]


app = FastAPI(
    title="AI TCO DSS",
    version="0.1.0",
    responses={status: {"model": ApiError} for status in (404, 422, 500, 503)},
)


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """Safe public errors; detailed configuration/catalog failures stay in server logs."""
    fields: tuple[str, ...] = ()
    status, code, message = 500, "server_error", "Calculation failed. Please retry."
    if isinstance(exc, UnknownIdentifierError):
        status, code, message = 404, "unknown_identifier", str(exc)
    elif isinstance(exc, (RequestValidationError, ValidationError)):
        status, code, message = 422, "validation_error", "Check the listed input fields."
        fields = tuple(".".join(map(str, e["loc"])) for e in exc.errors())
    elif isinstance(exc, EngineInputError):
        status, code, message, fields = 422, "input_error", str(exc), (exc.field,)
    elif isinstance(exc, CatalogLoadError):
        status, code, message = 503, "catalog_error", "Catalog unavailable. Check server logs."
    elif isinstance(exc, (ConfigurationError, WorkloadFileError)):
        status, code, message = 503, "configuration_error", "Server configuration unavailable."
    if status >= 500:
        logger.error("%s %s", request.url.path, code, exc_info=exc)
    return JSONResponse(
        status_code=status,
        content=ApiError(code=code, message=message, fields=fields).model_dump(mode="json"),
    )


# Register known errors explicitly so Starlette handles them before its server-error middleware.
for error_type in (
    RequestValidationError,
    ValidationError,
    UnknownIdentifierError,
    EngineInputError,
    CatalogLoadError,
    ConfigurationError,
    WorkloadFileError,
):
    app.add_exception_handler(error_type, handle_error)


@app.get("/api/v1/health", response_model=Health)
def health() -> Health:
    return Health()


@app.get("/api/v1/catalog", response_model=CatalogOverview)
def catalog() -> CatalogOverview:
    return services.catalog_overview()


@app.get("/api/v1/workloads/default", response_model=WorkloadProfile)
def default_workload() -> WorkloadProfile:
    return services.load_workload()


@app.get("/api/v1/scenario/default", response_model=Scenario)
def default_scenario() -> Scenario:
    """Centralize existing domain defaults rather than copying them into TypeScript."""
    return Scenario(
        workload=services.load_workload(),
        financials=EnterpriseFinancials(),
        sizing=SizingOptions(),
        decision=DecisionOptions(),
    )


@app.get("/api/v1/options", response_model=SimulationOptions)
def options() -> SimulationOptions:
    catalog = get_default_repository().catalog()
    return SimulationOptions(
        open_model_ids=tuple(m.id for m in catalog.models if m.type == "open-weights"),
        node_counts=tuple((h.id, h.valid_node_counts.value) for h in catalog.hardware),
    )


@app.post("/api/v1/size", response_model=SizeResult)
def size(request: SizeRequest) -> SizeResult:
    return services.size(request)


@app.post("/api/v1/scenario/validate", response_model=Scenario)
def validate_scenario(scenario: Scenario) -> Scenario:
    return scenario


@app.post("/api/v1/tco", response_model=TcoProjection)
def tco(request: TcoRequest) -> TcoProjection:
    return services.project_tco(request)
