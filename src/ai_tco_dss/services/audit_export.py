"""Audit transport and exports of an existing result, without recalculating it (Req 36)."""

import csv
import hashlib
import io
import zipfile
from typing import Literal

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.catalog.repository import CatalogRepository
from ai_tco_dss.domain import ApiCostInput, CandidateEvaluation, ScenarioResult, WorkloadInput
from ai_tco_dss.domain.base import Contract, FormulaTrace, IsoDate, Metric, SourceTier
from ai_tco_dss.domain.catalog import SourceEntry
from ai_tco_dss.domain.errors import EngineInputError, UnknownIdentifierError
from ai_tco_dss.domain.requests import FxInfo
from ai_tco_dss.engines.baselines import api_monthly_cost
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

PERFORMANCE_NAMES = ("decode_tps", "prefill_tps", "ttft_s", "effective_tps", "prefill_1m_minutes")


class AuditRequest(Contract):
    result: ScenarioResult
    candidate_id: str


class ExportRequest(Contract):
    result: ScenarioResult
    currency: Literal["USD", "EUR"] = "USD"


class AuditProvenance(Contract):
    path: str
    tier: SourceTier
    accessed: IsoDate
    value: str | None = None
    unit: str | None = None


class AuditSource(SourceEntry):
    provenance: tuple[AuditProvenance, ...]


class AuditFormula(Contract):
    section: str
    trace: FormulaTrace
    input_units: str = ""


class AuditResult(Contract):
    candidate_id: str
    formulas: tuple[AuditFormula, ...]
    performance: dict[str, Metric | None]
    sources: tuple[AuditSource, ...]
    fx: FxInfo


def candidate_audit(request: AuditRequest, *, repo: CatalogRepository | None = None) -> AuditResult:
    """Keep the supplied evaluation's exact traces; resolve its catalog input provenance."""
    result = request.result
    candidate = next(
        (
            r.evaluation
            for r in result.recommendation.ranked
            if r.evaluation.candidate_id == request.candidate_id
        ),
        None,
    )
    if candidate is None:
        raise UnknownIdentifierError("ranked candidate", request.candidate_id)
    catalog = (repo or get_default_repository()).catalog(result.scenario.fx_override)
    if (
        result.catalog_fingerprint
        and result.catalog_fingerprint
        != hashlib.sha256(catalog.model_dump_json().encode()).hexdigest()
    ):
        raise EngineInputError(
            "catalog_fingerprint", "Recalculate this scenario: its catalog snapshot has changed."
        )
    provenance: dict[str, list[AuditProvenance]] = {}
    origins: set[str] = set()

    def collect(value: object, path: str) -> None:
        if isinstance(value, Contract):
            collect(value.model_dump(mode="json"), path)
        elif isinstance(value, dict):
            if "source_id" in value and "accessed" in value and "tier" in value:
                provenance.setdefault(str(value["source_id"]), []).append(
                    AuditProvenance(
                        path=path,
                        tier=value["tier"],
                        accessed=value["accessed"],
                        value=(
                            f"{value['value']:.2f}"
                            if "currency" in value
                            else str(value["value"])
                            if "value" in value
                            else None
                        ),
                        unit=value.get("currency"),
                    )
                )
            origins.update(value.get("source_ids", []))
            for key, child in value.items():
                collect(child, f"{path}.{key}")
        elif isinstance(value, (tuple, list)):
            for index, child in enumerate(value):
                collect(child, f"{path}[{index}]")

    formulas: list[AuditFormula] = []

    def deployment_costs(c: CandidateEvaluation, prefix: str) -> None:
        """Trace costs absent from the engine's local TcoResult; keep the displayed results."""
        capex_symbolic, capex_inputs = "CapEx = 0 (no purchased hardware)", "0 USD"
        setup = 0.0
        if c.kind == "rental":
            rental = next(r for r in catalog.rentals if r.id == c.rental_id)
            setup = rental.setup_fee.value
            personnel = dict(c.tco.monthly_opex)["personnel"] if c.tco else 0.0
            if c.tco:
                formulas.extend(
                    AuditFormula(section=prefix + "cost", trace=t)
                    for t in c.tco.traces
                    if t.name == "personnel"
                )
            monthly_symbolic = "monthly cost = rental price + personnel"
            monthly_inputs = f"{rental.monthly_price.value:.2f} USD + {personnel:.2f} USD"
            # The rental's host RAM is a server total; expose the same per-node sizing input.
            if rental.system_ram_total_installed_gb and c.nodes:
                formulas.append(
                    AuditFormula(
                        section=prefix + "sizing",
                        trace=FormulaTrace(
                            name="rental_ram_per_node",
                            symbolic="host RAM per node = server RAM / nodes",
                            substituted=(
                                f"{rental.system_ram_total_installed_gb.value} GB / {c.nodes} nodes"
                            ),
                            result=rental.system_ram_total_installed_gb.value / c.nodes,
                            unit="GB/node",
                        ),
                    )
                )
        elif c.kind == "hybrid":
            local, remote = c.components
            ratio = result.scenario.financials.local_offload_ratio
            capex_symbolic, capex_inputs = "CapEx = local CapEx", f"{local.capex:.2f} USD"
            monthly_symbolic = "monthly cost = full local OpEx + (1-r) * EU API monthly cost"
            monthly_inputs = (
                f"{local.monthly_cost:.2f} USD + (1 - {ratio}) * {remote.monthly_cost:.2f} USD"
            )
        else:
            model = next(m for m in catalog.models if m.id == c.model_id)
            assert model.api_prices is not None
            params = load_engine_parameters()
            profile = result.scenario.workload
            workload = compute_workload(
                WorkloadInput(profile=profile, model=model, harnesses=catalog.harnesses), params
            )
            pinned = c.archetype == "Baseline C"
            gateway = catalog.baseline_defaults.gateway_fee_per_month.value if pinned else 0.0
            cost = api_monthly_cost(
                ApiCostInput(
                    model_id=model.id,
                    workload=workload,
                    profile=profile,
                    prices=model.api_prices,
                    eu_pinned=pinned,
                    gateway_fee_usd=gateway,
                ),
                params,
            )
            prices = model.api_prices
            formulas.append(
                AuditFormula(
                    section=prefix + "cost",
                    trace=FormulaTrace(
                        name="per_request",
                        symbolic=(
                            "per_request = [T_in*(1-cache)*P_in + "
                            "T_in*cache*P_cache + out_think*P_out]/1e6"
                        ),
                        substituted=(
                            f"[{workload.t_in_hat} tokens * "
                            f"(1 - {profile.prompt_cache_hit_rate}) * "
                            f"{prices.input_per_1m.value:.2f} USD/Mtok + "
                            f"{workload.t_in_hat} tokens * {profile.prompt_cache_hit_rate} * "
                            f"{prices.cache_read_per_1m.value:.2f} USD/Mtok + "
                            f"{workload.out_think} tokens * "
                            f"{prices.output_per_1m.value:.2f} USD/Mtok]/1e6"
                        ),
                        result=cost.per_request_usd,
                        unit="USD/request",
                    ),
                )
            )
            monthly_symbolic = (
                "monthly cost = requests * per_request * kappa * nu * (1-0.5*batch)"
                " * residency multiplier + gateway fee"
            )
            monthly_inputs = (
                f"{workload.monthly_requests} requests/month * "
                f"{cost.per_request_usd} USD/request * "
                f"{workload.kappa_mega} * {workload.nu_verify} * "
                f"(1 - 0.5 * {profile.batch_api_eligible_ratio}) * {1.10 if pinned else 1.0}"
                f" + {gateway:.2f} USD/month"
            )
        for name, symbolic, substituted, value, unit in (
            ("capex", capex_symbolic, capex_inputs, c.capex, "USD"),
            ("monthly_cost", monthly_symbolic, monthly_inputs, c.monthly_cost, "USD/month"),
            (
                "cost_60m",
                "TCO(60) = CapEx + setup fee + 60 * monthly cost",
                f"{c.capex:.2f} USD + {setup:.2f} USD + 60 months * {c.monthly_cost:.2f} USD/month",
                c.cost_60m,
                "USD",
            ),
        ):
            formulas.append(
                AuditFormula(
                    section=prefix + "cost",
                    trace=FormulaTrace(
                        name=name,
                        symbolic=symbolic,
                        substituted=substituted,
                        result=value,
                        unit=unit,
                    ),
                )
            )

    def visit(c: CandidateEvaluation, prefix: str = "") -> None:
        collect(c, f"{prefix}evaluation")
        for section in ("sizing", "performance", "tco"):
            actual = getattr(c, section)
            # Rental/hybrid retain a local TcoResult, not their deployment's accounting.
            if actual and (section != "tco" or c.kind == "onprem"):
                formulas.extend(
                    AuditFormula(
                        section=prefix + section,
                        trace=t,
                        input_units={
                            "sizing": "Memory: GB; KV/token: bytes/token; context: tokens; "
                            "parameters: billions; precision: bits; nodes/users: counts.",
                            "performance": "Bandwidth: GB/s; active parameters: billions; "
                            "precision: bits; throughput: tok/s; latency: seconds; "
                            "prefill time: minutes; cache/scaling factors: ratios.",
                            "tco": "Prices/CapEx: USD; OpEx: USD/month; salary: USD/year; "
                            "power: W; time: hours/month; tariff: USD/kWh; "
                            "FTE/ratios: dimensionless; employer tax: percent.",
                        }[section],
                    )
                    for t in actual.traces
                )
        for name, items, identifier in (
            ("hardware", catalog.hardware, c.hardware_id),
            ("model", catalog.models, c.model_id),
            ("rental", catalog.rentals, c.rental_id),
        ):
            item = next((i for i in items if i.id == identifier), None)
            if item:
                collect(item, prefix + name)
        if c.kind != "onprem":
            deployment_costs(c, prefix)
        elif c.tco:
            formulas.append(
                AuditFormula(
                    section=prefix + "cost",
                    trace=FormulaTrace(
                        name="monthly_opex_total",
                        symbolic="monthly OpEx = " + " + ".join(k for k, _ in c.tco.monthly_opex),
                        substituted=" + ".join(f"{v:.2f} USD/month" for _, v in c.tco.monthly_opex),
                        result=c.tco.monthly_opex_total,
                        unit="USD/month",
                    ),
                )
            )
        if c.kind == "hybrid":
            r = result.scenario.financials.local_offload_ratio
            for name in PERFORMANCE_NAMES:
                metric = getattr(c.performance, name) if c.performance else None
                parts = [
                    getattr(p.performance, name) if p.performance else None for p in c.components
                ]
                if metric and len(parts) == 2 and all(parts):
                    a, b = parts
                    assert a is not None and b is not None
                    formulas.append(
                        AuditFormula(
                            section=prefix + "performance",
                            trace=FormulaTrace(
                                name=name,
                                symbolic="metric = r * local + (1-r) * remote",
                                substituted=(
                                    f"{r} * {a.value} {a.unit} + {1 - r} * {b.value} {b.unit}"
                                ),
                                result=metric.value,
                                unit=metric.unit,
                            ),
                        )
                    )
        for index, component in enumerate(c.components):
            visit(component, f"component {index + 1} / ")

    visit(candidate)
    scenario = result.scenario
    for name, item in (
        ("fx", catalog.fx),
        ("popularity", catalog.popularity),
        ("gateway fee", catalog.baseline_defaults.gateway_fee_per_month),
        ("harness", next(h for h in catalog.harnesses if h.id == scenario.workload.harness_type)),
        (
            "tariff",
            next(t for t in catalog.tariffs if t.id == scenario.financials.electricity_tariff_tier),
        ),
    ):
        collect(item, name)
    for hub in catalog.hubs:
        if hub.id in (
            scenario.financials.engineering_hub_location,
            "de-munich",
            "ro-cluj-bucharest",
        ):
            collect(hub, f"hub.{hub.id}")
    # Origin IDs may reference fallback/measurement records outside the selected model.
    for index, record in enumerate(catalog.benchmarks):
        if record.source_id in origins:
            collect(record, f"benchmark[{index}]")
    sources = []
    for source in result.sources:
        records = provenance.get(source.source_id, [])
        if source.source_id in origins or records:
            sources.append(
                AuditSource(**source.model_dump(), provenance=tuple(dict.fromkeys(records)))
            )
    return AuditResult(
        candidate_id=candidate.candidate_id,
        formulas=tuple(formulas),
        sources=tuple(sources),
        performance={
            name: getattr(candidate.performance, name) if candidate.performance else None
            for name in PERFORMANCE_NAMES
        },
        fx=FxInfo(
            rate=result.fx_rate,
            source_id=result.fx_source_id,
            rate_date=result.fx_rate_date,
            is_override=result.fx_is_override,
        ),
    )


def csv_zip(request: ExportRequest) -> bytes:
    """One ranking CSV and all seven timeline series, converted with this result's FX."""
    result, currency = request.result, request.currency
    if result.timeline is None:
        raise EngineInputError("timeline", "a completed 60-month scenario timeline is required")
    rate = result.fx_rate if currency == "EUR" else 1.0
    criteria = ("tco_60m", "quality", "effective_tps", "ttft", "risk", "popularity")
    ranking = io.StringIO(newline="")
    writer = csv.writer(ranking, lineterminator="\n")
    writer.writerow(
        (
            "rank",
            "candidate_id",
            f"tco_60m_{currency}",
            *criteria[1:],
            "aggregate_score",
            "method",
            "saw_score",
            "saw_rank",
            "topsis_rank",
        )
    )
    for row in result.recommendation.ranked:
        raw = {c.criterion.value: c.raw for c in row.criteria}
        score = row.topsis_closeness if result.recommendation.method == "topsis" else row.saw_score
        writer.writerow(
            (
                row.rank,
                row.evaluation.candidate_id,
                raw["tco_60m"] / rate if raw["tco_60m"] is not None else None,
                *(raw[k] for k in criteria[1:]),
                score,
                result.recommendation.method,
                row.saw_score,
                row.saw_rank,
                row.topsis_rank,
            )
        )
    timeline = io.StringIO(newline="")
    writer = csv.writer(timeline, lineterminator="\n")
    fields = tuple(type(result.timeline.points[0]).model_fields)
    writer.writerow(("month", *(f"{key}_{currency}" for key in fields[1:])))
    for point in result.timeline.points:
        writer.writerow(
            (
                point.month,
                *(
                    getattr(point, k) / rate if getattr(point, k) is not None else None
                    for k in fields[1:]
                ),
            )
        )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in (("ranking", ranking.getvalue()), ("timeline", timeline.getvalue())):
            # Stable metadata makes the same result produce byte-identical archives.
            info = zipfile.ZipInfo(f"{name}_{currency}.csv", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content.encode("utf-8"))
    return output.getvalue()
