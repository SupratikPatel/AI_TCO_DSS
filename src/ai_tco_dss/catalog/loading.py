"""Catalog loading and validation shared by the Validate_CLI and the repository.

`load_catalog(root)` reads every file under `root` (the `data/` directory), runs all
checks of design.md § "Validate_CLI" without stopping at the first error, and
returns a `LoadReport`. The Catalog is built only when no error was found.
"""

import json
import math
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from ai_tco_dss.domain import (
    BaselineDefaults,
    BenchmarkMetric,
    BenchmarkRecord,
    Catalog,
    Contract,
    ElectricityTariff,
    ElectricityTariffTier,
    EuEngineeringHub,
    FxRate,
    HardwareSpec,
    HarnessEntry,
    HarnessType,
    IsoDate,
    ModelSpec,
    PopularitySnapshot,
    PresetId,
    PresetSpec,
    RentalSpec,
    SourceEntry,
    SourceTier,
    StaffingHub,
    UseCaseId,
    UseCaseSpec,
    WorkloadProfile,
)

YOUTUBE_ID = re.compile(r"^YT-\d{2}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIERS = {t.value for t in SourceTier}
CONTEXT_METRICS = {
    BenchmarkMetric.DECODE_TPS,
    BenchmarkMetric.PREFILL_TPS,
    BenchmarkMetric.AGGREGATE_TPS,
    BenchmarkMetric.TTFT_S,
}
REQUIRED_RENTALS = ("hetzner-gex63", "hetzner-gex430")
QUALITY_METRICS = {
    BenchmarkMetric.AA_INDEX_V5,
    BenchmarkMetric.TERMINAL_BENCH,
    BenchmarkMetric.SWE_BENCH,
}

# MVP_Catalog (Req 10.1, 10.3 to 10.5); checked only in MVP mode (Req 10.11).
MVP_OPEN_MODELS = (
    "gemma-4-12b",
    "qwen-3-8-27b",
    "qwen-3-6-35b-a3b",
    "gpt-oss-120b",
    "qwen-3-8-flash-next",
    "glm-5-3-flash",
    "deepseek-v4-1-flash",
    "kimi-k3-1-pro",
)
MVP_API_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5", "gpt-6-1", "gemini-3-1-pro")
MVP_NODE_COUNTS: dict[str, tuple[int, ...]] = {
    "rtx-5060-ti-16gb": (1,),
    "rtx-5070-strata-64gb": (1,),
    "mac-mini-m5-pro-64gb": (1,),
    "mac-studio-m5-max-128gb": (1,),
    "mac-studio-m5-ultra-256gb": (1,),
    "amd-strix-halo-128gb": (1,),
    "dgx-spark-128gb": (1, 2, 4),
    "rtx-pro-6000-96gb": (1, 4, 8),
    "h100-80gb-sxm": (8,),
}
GPT_OSS_PARAMETERS = {"total_parameters_billions": 117.0, "active_parameters_billions": 5.1}

# Presets (Req 32.1 to 32.5)
CRITERIA = ("tco_60m", "quality", "effective_tps", "ttft", "risk", "popularity")
PRESET_DOMINANT = {"cheapest": "tco_60m", "most-capable": "quality", "popular": "popularity"}
WEIGHT_SUM_TOLERANCE = 1e-6


def preset_violations(preset_id: str, weights: Mapping[str, float]) -> list[str]:
    """Rule violations of one preset weight vector (Req 32.1 to 32.5); empty if valid."""
    if set(weights) != set(CRITERIA):
        return [f"preset {preset_id} needs exactly the six weights {', '.join(CRITERIA)}"]
    problems = [
        f"preset {preset_id}: weight {name} = {value} outside [0, 1]"
        for name, value in weights.items()
        if not 0.0 <= value <= 1.0
    ]
    total = sum(weights.values())
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=WEIGHT_SUM_TOLERANCE):
        problems.append(f"preset {preset_id}: weights sum to {total}, not 1 +/- 1e-6")
    if preset_id == "best-fit":
        if not all(value > 0 for value in weights.values()):
            problems.append("preset best-fit: every weight must be > 0")
    elif preset_id in PRESET_DOMINANT:
        top = PRESET_DOMINANT[preset_id]
        if not all(weights[top] > weights[c] for c in CRITERIA if c != top):
            problems.append(f"preset {preset_id}: {top} must have the strictly largest weight")
    return problems


def popularity_violations(entries: Sequence[tuple[str, float]]) -> list[tuple[int, str]]:
    """(entry index, message) per negative value or repeated `model_id` (Req 32.8)."""
    problems: list[tuple[int, str]] = []
    first: dict[str, int] = {}
    for index, (model_id, value) in enumerate(entries):
        if value < 0:
            problems.append((index, f"popularity of {model_id} is negative ({value})"))
        if model_id in first:
            problems.append(
                (index, f"duplicate model_id {model_id} (first at entries[{first[model_id]}])")
            )
        else:
            first[model_id] = index
    return problems


# --------------------------------------------------------------------------- file contracts


class SourcesFile(Contract):
    sources: tuple[SourceEntry, ...]


class BenchmarkFile(Contract):
    records: tuple[BenchmarkRecord, ...]


class ElectricityFile(Contract):
    tariffs: tuple[ElectricityTariff, ...]


class StaffingFile(Contract):
    hubs: tuple[StaffingHub, ...]


class HarnessFile(Contract):
    harnesses: tuple[HarnessEntry, ...]


class UseCaseFile(Contract):
    use_cases: tuple[UseCaseSpec, ...]


class RentalFile(Contract):
    rentals: tuple[RentalSpec, ...]


class PresetFile(Contract):
    presets: tuple[PresetSpec, ...]


class WorkloadFile(Contract):
    source_id: str
    tier: SourceTier
    accessed: IsoDate
    profile: WorkloadProfile


REFERENCE_FILES: dict[str, type[BaseModel]] = {
    "fx.json": FxRate,
    "electricity.json": ElectricityFile,
    "staffing_hubs.json": StaffingFile,
    "harnesses.json": HarnessFile,
    "use_cases.json": UseCaseFile,
    "rentals.json": RentalFile,
    "presets.json": PresetFile,
    "popularity.json": PopularitySnapshot,
    "baselines.json": BaselineDefaults,
}
WORKLOAD_FILE = "workloads/default.json"


# --------------------------------------------------------------------------- report


@dataclass(frozen=True)
class CatalogError:
    file: str  # path relative to the data root, POSIX separators
    field: str  # field path, or "line:column" for JSON parse errors
    message: str


@dataclass
class LoadReport:
    root: Path
    errors: list[CatalogError] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    catalog: Catalog | None = None
    workload: WorkloadProfile | None = None

    def add(self, file: str, field_path: str, message: str) -> None:
        if any(e.file == file and e.field == field_path for e in self.errors):
            return  # one line per file and field; the first, most specific message wins
        self.errors.append(CatalogError(file, field_path, message))


# --------------------------------------------------------------------------- helpers


def field_path(loc: tuple[int | str, ...]) -> str:
    out = ""
    for part in loc:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}" if out else str(part)
    return out


def _entry_label(raw: Any, loc: tuple[int | str, ...]) -> str:
    """` (entry <id>)` for errors inside a list entry that has an id."""
    if len(loc) >= 2 and isinstance(loc[0], str) and isinstance(loc[1], int):
        items = raw.get(loc[0]) if isinstance(raw, dict) else None
        if isinstance(items, list) and loc[1] < len(items) and isinstance(items[loc[1]], dict):
            item = items[loc[1]]
            for key in ("id", "source_id", "model_id"):
                if isinstance(item.get(key), str):
                    return f" ({key} {item[key]})"
    return ""


def _has_provenance(node: dict[str, Any]) -> bool:
    return all(key in node for key in ("source_id", "tier", "accessed"))


def _numbers(node: Any, path: str, covered: bool) -> Iterator[tuple[str, bool]]:
    """Yield (field path, covered) for every JSON number (not bool) in the tree."""
    if isinstance(node, dict):
        covered = covered or _has_provenance(node)
        for key, value in node.items():
            yield from _numbers(value, f"{path}.{key}" if path else key, covered)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _numbers(value, f"{path}[{index}]", covered)
    elif isinstance(node, int | float) and not isinstance(node, bool):
        yield path, covered


def uncovered_number_paths(tree: Any) -> list[str]:
    """Field paths of numbers without a covering Provenance_Record (design D-02)."""
    return [path for path, covered in _numbers(tree, "", False) if not covered]


def _provenance_nodes(node: Any, path: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (path, dict) for every object that carries a `source_id`."""
    if isinstance(node, dict):
        if "source_id" in node:
            yield path, node
        for key, value in node.items():
            yield from _provenance_nodes(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _provenance_nodes(value, f"{path}[{index}]")


def _join(path: str, name: str) -> str:
    return f"{path}.{name}" if path else name


# --------------------------------------------------------------------------- loader


class _Loader:
    def __init__(self, root: Path, today: date, mvp: bool) -> None:
        self.root = root
        self.today = today
        self.mvp = mvp
        self.report = LoadReport(root)
        self.raw: dict[str, Any] = {}

    # -- step 1: parse ----------------------------------------------------------------

    def parse(self, rel: str) -> Any:
        path = self.root / rel
        if not path.is_file():
            self.report.add(rel, "", "file is missing")
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.report.add(rel, f"{exc.lineno}:{exc.colno}", f"invalid JSON: {exc.msg}")
            return None
        except (OSError, UnicodeDecodeError) as exc:
            self.report.add(rel, "", f"cannot read file: {exc}")
            return None
        self.raw[rel] = data
        return data

    def json_files(self, folder: str) -> list[str]:
        directory = self.root / folder
        if not directory.is_dir():
            self.report.add(folder, "", "directory is missing")
            return []
        return [f"{folder}/{p.name}" for p in sorted(directory.glob("*.json")) if p.is_file()]

    # -- step 2: provenance coverage --------------------------------------------------

    def check_coverage(self, rel: str) -> None:
        for path in uncovered_number_paths(self.raw[rel]):
            self.report.add(rel, path, "numeric value lacks Provenance_Record")

    # -- step 5: provenance rules -----------------------------------------------------

    def check_provenance(self, rel: str, registry: dict[str, SourceTier]) -> None:
        for path, node in _provenance_nodes(self.raw[rel], ""):
            self._check_record(rel, path, node, registry)

    def _check_record(
        self, rel: str, path: str, node: dict[str, Any], registry: dict[str, SourceTier]
    ) -> None:
        source_id = node.get("source_id")
        tier = node.get("tier")
        if not isinstance(source_id, str) or not source_id:
            self.report.add(rel, _join(path, "source_id"), "source_id must be a non-empty string")
            return
        if source_id not in registry:
            self.report.add(
                rel,
                _join(path, "source_id"),
                f"unknown source_id {source_id} (not in sources.json)",
            )
        if tier not in TIERS:
            self.report.add(
                rel, _join(path, "tier"), f"invalid tier {tier!r}; allowed: {sorted(TIERS)}"
            )
        elif YOUTUBE_ID.match(source_id) and tier != SourceTier.COMMUNITY:
            self.report.add(
                rel, _join(path, "tier"), f"source {source_id} must have tier community, got {tier}"
            )
        elif source_id in registry and tier != registry[source_id]:
            self.report.add(
                rel,
                _join(path, "tier"),
                f"tier {tier} does not match registry tier {registry[source_id].value} "
                f"of {source_id}",
            )
        if YOUTUBE_ID.match(source_id) and node.get("note") != "single-source":
            self.report.add(
                rel, _join(path, "note"), f"values from {source_id} need note 'single-source'"
            )
        self._check_date(rel, _join(path, "accessed"), node.get("accessed"))

    def _check_date(self, rel: str, path: str, value: Any) -> None:
        if not isinstance(value, str) or not ISO_DATE.match(value):
            self.report.add(rel, path, f"date {value!r} must be ISO 8601 YYYY-MM-DD")
            return
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            self.report.add(rel, path, f"date {value!r} must be ISO 8601 YYYY-MM-DD")
            return
        if parsed > self.today:
            self.report.add(rel, path, f"access date {value} is in the future")

    # -- step 3: contract validation --------------------------------------------------

    def validate[M: BaseModel](self, rel: str, contract: type[M]) -> M | None:
        data = self.raw.get(rel)
        if data is None:
            return None
        try:
            return contract.model_validate(data)
        except ValidationError as exc:
            for error in exc.errors():
                loc = tuple(error["loc"])
                self.report.add(rel, field_path(loc), error["msg"] + _entry_label(data, loc))
            return None

    # -- run --------------------------------------------------------------------------

    def run(self) -> LoadReport:
        report = self.report
        hardware_files = self.json_files("catalog/hardware")
        model_files = self.json_files("catalog/models")
        benchmark_files = self.json_files("benchmarks")
        reference_files = [f"reference/{name}" for name in REFERENCE_FILES]
        data_files = [*hardware_files, *model_files, *benchmark_files, *reference_files]
        data_files.append(WORKLOAD_FILE)

        self.parse("sources.json")
        for rel in data_files:
            self.parse(rel)
        report.counts = {
            "hardware": len(hardware_files),
            "model": len(model_files),
            "benchmark": len(benchmark_files),
            "reference": len(reference_files),
        }

        registry = self._registry()
        for rel in data_files:
            if rel in self.raw:
                self.check_coverage(rel)
                self.check_provenance(rel, registry)
                self.check_benchmarks_raw(rel)

        sources = self.validate("sources.json", SourcesFile)
        hardware = [h for rel in hardware_files if (h := self._item(rel, HardwareSpec))]
        models = [m for rel in model_files if (m := self._item(rel, ModelSpec))]
        benchmarks = [b for rel in benchmark_files if (b := self.validate(rel, BenchmarkFile))]
        refs = {name: self.validate(f"reference/{name}", c) for name, c in REFERENCE_FILES.items()}
        workload = self.validate(WORKLOAD_FILE, WorkloadFile)

        self.check_duplicate_ids(hardware_files + model_files)
        hardware_ids = {h.id for h in hardware}
        model_ids = {m.id for m in models}
        self.check_benchmark_references(benchmark_files, hardware_ids, model_ids)
        self.check_quality_scores(benchmark_files)
        self.check_reference_rules(refs, hardware_ids, model_ids)
        if self.mvp:
            self.check_mvp(hardware_files + model_files, hardware, models)

        if report.errors or sources is None or workload is None:
            return report
        report.workload = workload.profile
        report.catalog = self._build(sources, hardware, models, benchmarks, refs)
        return report

    def _registry(self) -> dict[str, SourceTier]:
        rel = "sources.json"
        raw = self.raw.get(rel)
        registry: dict[str, SourceTier] = {}
        entries = raw.get("sources") if isinstance(raw, dict) else None
        if not isinstance(entries, list):
            if raw is not None:
                self.report.add(rel, "sources", "sources must be a list")
            return registry
        seen: dict[str, int] = {}
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not isinstance(entry.get("source_id"), str):
                continue
            source_id = entry["source_id"]
            if source_id in seen:
                self.report.add(
                    rel,
                    f"sources[{index}].source_id",
                    f"duplicate source_id {source_id} (first at sources[{seen[source_id]}])",
                )
                continue
            seen[source_id] = index
            tier = entry.get("tier")
            if tier in TIERS:
                registry[source_id] = SourceTier(tier)
                if YOUTUBE_ID.match(source_id) and tier != SourceTier.COMMUNITY:
                    self.report.add(
                        rel, f"sources[{index}].tier", f"source {source_id} must be community"
                    )
        return registry

    def _item[M: HardwareSpec | ModelSpec](self, rel: str, contract: type[M]) -> M | None:
        item = self.validate(rel, contract)
        expected = Path(rel).stem
        if item is not None and item.id != expected:
            self.report.add(
                rel, "id", f"file name {expected}.json does not match declared id {item.id}"
            )
        return item

    def check_duplicate_ids(self, files: list[str]) -> None:
        declared: dict[str, list[str]] = {}
        for rel in files:
            raw = self.raw.get(rel)
            if isinstance(raw, dict) and isinstance(raw.get("id"), str):
                declared.setdefault(raw["id"], []).append(rel)
        for item_id, paths in declared.items():
            if len(paths) > 1:
                self.report.add(
                    paths[0], "id", f"duplicate id {item_id} declared in {', '.join(paths)}"
                )

    def check_benchmarks_raw(self, rel: str) -> None:
        raw = self.raw.get(rel)
        if not rel.startswith("benchmarks/") or not isinstance(raw, dict):
            return
        records = raw.get("records")
        if not isinstance(records, list):
            return
        for index, record in enumerate(records):
            if not isinstance(record, dict) or record.get("metric") not in CONTEXT_METRICS:
                continue
            tokens = record.get("context_tokens")
            if not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 1:
                self.report.add(
                    rel,
                    f"records[{index}].context_tokens",
                    f"metric {record['metric']} needs context_tokens >= 1, got {tokens!r}",
                )

    def check_benchmark_references(
        self, files: list[str], hardware_ids: set[str], model_ids: set[str]
    ) -> None:
        for rel in files:
            raw = self.raw.get(rel)
            records = raw.get("records") if isinstance(raw, dict) else None
            if not isinstance(records, list):
                continue
            for index, record in enumerate(records):
                if not isinstance(record, dict):
                    continue
                model_id = record.get("model_id")
                if isinstance(model_id, str) and model_id not in model_ids:
                    self.report.add(
                        rel, f"records[{index}].model_id", f"unknown model_id {model_id}"
                    )
                hardware_id = record.get("hardware_id")
                if isinstance(hardware_id, str) and hardware_id not in hardware_ids:
                    self.report.add(
                        rel, f"records[{index}].hardware_id", f"unknown hardware_id {hardware_id}"
                    )

    def check_quality_scores(self, files: list[str]) -> None:
        """Quality scores lie in [0, 100]; in MVP mode 0 is rejected (absent, not 0; Req 10.8)."""
        for rel in files:
            raw = self.raw.get(rel)
            records = raw.get("records") if isinstance(raw, dict) else None
            if not isinstance(records, list):
                continue
            for index, record in enumerate(records):
                if not isinstance(record, dict) or record.get("metric") not in QUALITY_METRICS:
                    continue
                value = record.get("value")
                if not isinstance(value, int | float) or isinstance(value, bool):
                    continue
                path = f"records[{index}].value"
                label = f"{record['metric']} of {record.get('model_id')}"
                if not 0 <= value <= 100:
                    self.report.add(rel, path, f"{label} = {value} outside [0, 100]")
                elif self.mvp and value == 0:
                    self.report.add(
                        rel, path, f"{label} is 0; leave an unavailable score absent (Req 10.8)"
                    )

    def check_mvp(
        self, files: list[str], hardware: list[HardwareSpec], models: list[ModelSpec]
    ) -> None:
        """MVP_Catalog completeness (Req 10.1 to 10.5, 10.11)."""
        for folder, ids in (
            ("catalog/hardware", tuple(MVP_NODE_COUNTS)),
            ("catalog/models", MVP_OPEN_MODELS + MVP_API_MODELS),
        ):
            for item_id in ids:
                rel = f"{folder}/{item_id}.json"
                if rel not in files:
                    self.report.add(rel, "id", f"missing MVP item {item_id} (requirements 10)")
        for item in hardware:
            expected = MVP_NODE_COUNTS.get(item.id)
            if expected is not None and tuple(sorted(item.valid_node_counts.value)) != expected:
                self.report.add(
                    f"catalog/hardware/{item.id}.json",
                    "valid_node_counts.value",
                    f"{item.id}: valid node counts must be {list(expected)} (requirements 10.5)",
                )
        for model in models:
            rel = f"catalog/models/{model.id}.json"
            if model.id in MVP_OPEN_MODELS:
                self._mvp_open_model(rel, model)
            elif model.id in MVP_API_MODELS:
                self._mvp_api_model(rel, model)

    def _mvp_open_model(self, rel: str, model: ModelSpec) -> None:
        for name in ("total_parameters_billions", "active_parameters_billions"):
            if getattr(model, name) is None:
                self.report.add(rel, name, f"{model.id}: parameter count {name} is missing")
        if model.id != "gpt-oss-120b":
            return
        if model.architecture != "moe":
            self.report.add(rel, "architecture", "gpt-oss-120b must be moe (requirements 10.2)")
        for name, expected in GPT_OSS_PARAMETERS.items():
            value = getattr(model, name)
            if value is not None and value.value != expected:
                self.report.add(
                    rel, f"{name}.value", f"gpt-oss-120b: {name} must be {expected} (req 10.2)"
                )

    def _mvp_api_model(self, rel: str, model: ModelSpec) -> None:
        if model.api_prices is None:
            return  # the contract already reports missing api_prices
        for name in ("input_per_1m", "output_per_1m", "cache_read_per_1m"):
            price = getattr(model.api_prices, name)
            path = f"api_prices.{name}"
            if price.value <= 0:
                self.report.add(rel, f"{path}.value", f"{model.id}: {name} must be > 0")
            if price.tier != SourceTier.OFFICIAL:
                self.report.add(
                    rel,
                    f"{path}.tier",
                    f"{model.id}: {name} needs a Provenance_Record with tier official",
                )

    def check_reference_rules(
        self, refs: dict[str, BaseModel | None], hardware_ids: set[str], model_ids: set[str]
    ) -> None:
        presets = refs["presets.json"]
        if isinstance(presets, PresetFile):
            self._presets(presets)
        self._popularity()
        electricity = refs["electricity.json"]
        if isinstance(electricity, ElectricityFile):
            self._electricity(electricity)
        hubs = refs["staffing_hubs.json"]
        if isinstance(hubs, StaffingFile):
            self._hubs(hubs)
        harnesses = refs["harnesses.json"]
        if isinstance(harnesses, HarnessFile):
            self._harnesses(harnesses)
        use_cases = refs["use_cases.json"]
        if isinstance(use_cases, UseCaseFile):
            self._use_cases(use_cases)
        rentals = refs["rentals.json"]
        if isinstance(rentals, RentalFile):
            self._rentals(rentals, hardware_ids)
        baselines = refs["baselines.json"]
        if isinstance(baselines, BaselineDefaults):
            self._baselines(baselines, model_ids)

    def _missing(self, rel: str, key: str, present: set[str], required: list[str]) -> None:
        for item_id in required:
            if item_id not in present:
                self.report.add(rel, key, f"missing entry {item_id}")

    def _presets(self, data: PresetFile) -> None:
        rel = "reference/presets.json"
        present = {p.id.value for p in data.presets}
        self._missing(rel, "presets", present, [p.value for p in PresetId])
        for i, preset in enumerate(data.presets):
            for message in preset_violations(preset.id.value, preset.weights.model_dump()):
                self.report.add(rel, f"presets[{i}].weights", message)
            if preset.tier != SourceTier.ASSUMPTION:
                self.report.add(
                    rel, f"presets[{i}].tier", f"preset {preset.id} must have tier assumption"
                )

    def _popularity(self) -> None:
        rel = "reference/popularity.json"
        raw = self.raw.get(rel)
        entries = raw.get("entries") if isinstance(raw, dict) else None
        if not isinstance(entries, list):
            return
        pairs = [
            (e["model_id"], float(e["value"]))
            for e in entries
            if isinstance(e, dict)
            and isinstance(e.get("model_id"), str)
            and isinstance(e.get("value"), int | float)
            and not isinstance(e.get("value"), bool)
        ]
        if len(pairs) != len(entries):
            return  # malformed entries are reported by the contract
        for index, message in popularity_violations(pairs):
            name = "value" if "negative" in message else "model_id"
            self.report.add(rel, f"entries[{index}].{name}", message)

    def _electricity(self, data: ElectricityFile) -> None:
        rel = "reference/electricity.json"
        present = {t.id.value for t in data.tariffs}
        self._missing(rel, "tariffs", present, [t.value for t in ElectricityTariffTier])
        for i, tariff in enumerate(data.tariffs):
            price = tariff.price_per_kwh
            if price.currency != "EUR":
                self.report.add(
                    rel, f"tariffs[{i}].price_per_kwh.currency", f"must be EUR ({tariff.id})"
                )
            if not 0 < price.value <= 1.0:
                self.report.add(
                    rel,
                    f"tariffs[{i}].price_per_kwh.value",
                    f"price {price.value} outside (0, 1.00] EUR/kWh (entry {tariff.id})",
                )

    def _hubs(self, data: StaffingFile) -> None:
        rel = "reference/staffing_hubs.json"
        self._missing(
            rel, "hubs", {h.id.value for h in data.hubs}, [h.value for h in EuEngineeringHub]
        )
        for i, hub in enumerate(data.hubs):
            if hub.base_salary.currency != "EUR":
                self.report.add(rel, f"hubs[{i}].base_salary.currency", f"must be EUR ({hub.id})")
            if hub.base_salary.value <= 0:
                self.report.add(
                    rel, f"hubs[{i}].base_salary.value", f"salary must be > 0 (entry {hub.id})"
                )
            if not 0 <= hub.employer_social_tax_pct.value <= 100:
                self.report.add(
                    rel,
                    f"hubs[{i}].employer_social_tax_pct.value",
                    f"tax rate must be within [0, 100] percent (entry {hub.id})",
                )
            if not 0 <= hub.recruiting_delay_months.value <= 24:
                self.report.add(
                    rel,
                    f"hubs[{i}].recruiting_delay_months.value",
                    f"recruiting delay must be within [0, 24] months (entry {hub.id})",
                )

    def _harnesses(self, data: HarnessFile) -> None:
        rel = "reference/harnesses.json"
        present = {h.id.value for h in data.harnesses}
        self._missing(rel, "harnesses", present, [h.value for h in HarnessType])
        for i, harness in enumerate(data.harnesses):
            tokens = harness.scaffolding_tokens_per_turn
            if tokens.value < 0:
                self.report.add(
                    rel,
                    f"harnesses[{i}].scaffolding_tokens_per_turn.value",
                    f"tokens must be >= 0 (entry {harness.id})",
                )
            if harness.id == HarnessType.CUSTOM_LEAN and tokens.tier != SourceTier.ASSUMPTION:
                self.report.add(
                    rel,
                    f"harnesses[{i}].scaffolding_tokens_per_turn.tier",
                    "custom-lean default must have tier assumption (entry custom-lean)",
                )

    def _use_cases(self, data: UseCaseFile) -> None:
        rel = "reference/use_cases.json"
        present = {u.id.value for u in data.use_cases}
        self._missing(rel, "use_cases", present, [u.value for u in UseCaseId])
        for i, use_case in enumerate(data.use_cases):
            if not 0 <= use_case.quality_floor.value <= 100:
                self.report.add(
                    rel,
                    f"use_cases[{i}].quality_floor.value",
                    f"quality floor must be within [0, 100] (entry {use_case.id})",
                )

    def _rentals(self, data: RentalFile, hardware_ids: set[str]) -> None:
        rel = "reference/rentals.json"
        self._missing(rel, "rentals", {r.id for r in data.rentals}, list(REQUIRED_RENTALS))
        for i, rental in enumerate(data.rentals):
            if rental.monthly_price.value <= 0:
                self.report.add(
                    rel,
                    f"rentals[{i}].monthly_price.value",
                    f"monthly price must be > 0 (entry {rental.id})",
                )
            if rental.gpu_count.value < 1:
                self.report.add(
                    rel,
                    f"rentals[{i}].gpu_count.value",
                    f"GPU count must be a positive integer (entry {rental.id})",
                )
            if rental.gpu_hardware_id not in hardware_ids:
                self.report.add(
                    rel,
                    f"rentals[{i}].gpu_hardware_id",
                    f"unknown hardware id {rental.gpu_hardware_id} (entry {rental.id})",
                )

    def _baselines(self, data: BaselineDefaults, model_ids: set[str]) -> None:
        rel = "reference/baselines.json"
        if data.default_plan_id not in {p.id for p in data.plans}:
            self.report.add(rel, "default_plan_id", f"unknown plan id {data.default_plan_id}")
        if data.reference_api_model_id not in model_ids:
            self.report.add(
                rel, "reference_api_model_id", f"unknown model_id {data.reference_api_model_id}"
            )

    def _build(
        self,
        sources: SourcesFile,
        hardware: list[HardwareSpec],
        models: list[ModelSpec],
        benchmarks: list[BenchmarkFile],
        refs: dict[str, Any],
    ) -> Catalog:
        fx: FxRate = refs["fx.json"]
        return Catalog(
            sources=tuple(sorted(sources.sources, key=lambda s: s.source_id)),
            hardware=tuple(sorted(hardware, key=lambda h: h.id)),
            models=tuple(sorted(models, key=lambda m: m.id)),
            benchmarks=tuple(r for f in benchmarks for r in f.records),
            rentals=tuple(sorted(refs["rentals.json"].rentals, key=lambda r: r.id)),
            tariffs=tuple(sorted(refs["electricity.json"].tariffs, key=lambda t: t.id.value)),
            hubs=tuple(sorted(refs["staffing_hubs.json"].hubs, key=lambda h: h.id.value)),
            harnesses=tuple(sorted(refs["harnesses.json"].harnesses, key=lambda h: h.id.value)),
            use_cases=tuple(sorted(refs["use_cases.json"].use_cases, key=lambda u: u.id.value)),
            presets=tuple(sorted(refs["presets.json"].presets, key=lambda p: p.id.value)),
            popularity=refs["popularity.json"],
            baseline_defaults=refs["baselines.json"],
            fx=fx,
            fx_active_rate=fx.eur_to_usd,
            fx_is_override=False,
        )


def load_catalog(root: Path, today: date | None = None, mvp: bool = False) -> LoadReport:
    """Read and check every file under `root`; build the (EUR) Catalog if error-free.

    `mvp=True` adds the MVP_Catalog completeness rules (Req 10.11); the Validate_CLI
    enables them for the repository `data/` root only.
    """
    return _Loader(root, today or date.today(), mvp).run()
