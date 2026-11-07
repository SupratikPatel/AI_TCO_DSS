"""Catalog contracts (design.md § "Catalog contracts"). Collections are tuples (D-03)."""

from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

from ai_tco_dss.domain.base import Contract, IsoDate, Money, Sourced, SourceTier
from ai_tco_dss.domain.enums import (
    AttentionMechanism,
    BenchmarkMetric,
    DeploymentMode,
    ElectricityTariffTier,
    EuEngineeringHub,
    HarnessType,
    InterconnectType,
    LicenseType,
    MemoryArchitecture,
    PrecisionFormat,
    PresetId,
    UseCaseId,
)
from ai_tco_dss.domain.scenario import CriterionWeights


class SourceEntry(Contract):
    source_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str | None = None
    reference: str | None = None
    publisher: str = Field(min_length=1)
    tier: SourceTier

    @model_validator(mode="after")
    def _url_or_reference(self) -> Self:
        if not (self.url or "").strip() and not (self.reference or "").strip():
            raise ValueError("a source needs a non-empty url or reference")
        return self


class LifecycleClocks(Contract):
    software_support_years: Sourced[float]
    resale_value_retention_3yr: Sourced[float]
    cuda_or_rocm_status: Literal["active-flagship", "supported", "deprecated-legacy"]
    requires_nvidia_nim_license: bool = False
    warning_notes: str | None = None

    @field_validator("resale_value_retention_3yr")
    @classmethod
    def _retention_range(cls, value: Sourced[float]) -> Sourced[float]:
        if not 0.0 <= value.value <= 1.0:
            raise ValueError("resale_value_retention_3yr must be in [0, 1]")
        return value


class CablingKit(Contract):
    nodes: int = Field(ge=1, le=8)
    price: Money


class HardwareSpec(Contract):
    id: str = Field(min_length=1)
    name: str
    vendor: str
    deployment_mode: DeploymentMode
    memory_architecture: MemoryArchitecture
    interconnect: InterconnectType
    supported_native_precisions: tuple[PrecisionFormat, ...]
    valid_node_counts: Sourced[tuple[int, ...]]
    gpus_per_unit: Sourced[int]
    advertised_memory_gb: Sourced[float]
    os_reserved_memory_ratio: Sourced[float] | None = None
    tuned_max_usable_memory_gb: Sourced[float] | None = None
    linux_max_usable_memory_gb: Sourced[float] | None = None
    system_ram_offload_gb: Sourced[float] | None = None
    system_ram_total_installed_gb: Sourced[float] | None = None
    memory_bandwidth_gbs: Sourced[float]
    base_prefill_tps_at_32k: Sourced[float] | None = None
    prefill_tps_at_1m: Sourced[float] | None = None
    idle_watts: Sourced[float]
    load_watts: Sourced[float]
    street_price: Money
    msrp: Money | None = None
    datacenter_multiplier: Sourced[float]
    cabling_kits: tuple[CablingKit, ...] = ()
    lifecycle_clocks: LifecycleClocks


class PrecisionValue(Contract):
    precision: PrecisionFormat
    value: Sourced[float]


class ApiPrices(Contract):
    input_per_1m: Money
    output_per_1m: Money
    cache_read_per_1m: Money


class ModelSpec(Contract):
    id: str = Field(min_length=1)
    name: str
    family: str
    type: Literal["open-weights", "commercial-api"]
    license_type: LicenseType = LicenseType.APACHE_2
    architecture: Literal["dense", "moe"]
    attention_mechanism: AttentionMechanism = AttentionMechanism.STANDARD_MHA_GQA
    total_parameters_billions: Sourced[float] | None = None
    active_parameters_billions: Sourced[float] | None = None
    calibrated_weights_gb: tuple[PrecisionValue, ...] = ()
    token_agreement_rates: tuple[PrecisionValue, ...] = ()
    num_layers: Sourced[int] | None = None
    active_kv_layer_ratio: Sourced[float] | None = None
    num_kv_heads: Sourced[int] | None = None
    head_dim: Sourced[int] | None = None
    max_context_length: Sourced[int]
    supports_builtin_mtp: bool = False
    open_weights_output_price_per_1m: Money | None = None
    api_prices: ApiPrices | None = None
    eu_pinned_endpoint: Sourced[bool] | None = None
    api_decode_tps: Sourced[float] | None = None
    api_ttft_s: Sourced[float] | None = None

    @model_validator(mode="after")
    def _api_fields(self) -> Self:
        if self.type == "commercial-api" and self.api_prices is None:
            raise ValueError("commercial-api models need api_prices")
        if self.type == "open-weights":
            for name in ("api_prices", "eu_pinned_endpoint"):
                if getattr(self, name) is not None:
                    raise ValueError(f"{name} is only allowed for commercial-api models")
        return self


class BenchmarkRecord(Contract):
    metric: BenchmarkMetric
    value: float
    model_id: str = Field(min_length=1)
    hardware_id: str | None = None
    precision: PrecisionFormat | None = None
    context_tokens: int | None = Field(default=None, ge=1)
    engine: str | None = None
    source_id: str = Field(min_length=1)
    tier: SourceTier
    accessed: IsoDate
    note: str | None = None


class RentalSpec(Contract):
    id: str = Field(min_length=1)
    name: str
    provider: str
    region: str
    gpu_hardware_id: str
    gpu_count: Sourced[int]
    system_ram_total_installed_gb: Sourced[float]
    monthly_price: Money
    setup_fee: Money


class ElectricityTariff(Contract):
    id: ElectricityTariffTier
    price_per_kwh: Money


class StaffingHub(Contract):
    id: EuEngineeringHub
    base_salary: Money
    employer_social_tax_pct: Sourced[float]
    recruiting_delay_months: Sourced[int]


class HarnessEntry(Contract):
    id: HarnessType
    scaffolding_tokens_per_turn: Sourced[int]


class UseCaseSpec(Contract):
    id: UseCaseId
    label: str
    matching_benchmark: BenchmarkMetric
    second_choice_benchmark: BenchmarkMetric | None = None
    quality_floor: Sourced[float]


class PresetSpec(Contract):
    id: PresetId
    weights: CriterionWeights
    source_id: str = Field(min_length=1)
    tier: SourceTier
    accessed: IsoDate


class PopularityEntry(Contract):
    model_id: str
    value: float = Field(ge=0)


class PopularitySnapshot(Contract):
    snapshot_date: IsoDate
    source_id: str = Field(min_length=1)
    tier: SourceTier
    accessed: IsoDate
    entries: tuple[PopularityEntry, ...]


class SubscriptionPlan(Contract):
    id: str
    name: str
    price_per_seat_month: Money


class BaselineDefaults(Contract):
    plans: tuple[SubscriptionPlan, ...]
    default_plan_id: str
    gateway_fee_per_month: Money
    reference_api_model_id: str


class FxRate(Contract):
    eur_to_usd: float = Field(gt=0)
    rate_date: IsoDate
    source_id: str = Field(min_length=1)
    tier: SourceTier
    accessed: IsoDate


class Catalog(Contract):
    sources: tuple[SourceEntry, ...]
    hardware: tuple[HardwareSpec, ...]
    models: tuple[ModelSpec, ...]
    benchmarks: tuple[BenchmarkRecord, ...]
    rentals: tuple[RentalSpec, ...]
    tariffs: tuple[ElectricityTariff, ...]
    hubs: tuple[StaffingHub, ...]
    harnesses: tuple[HarnessEntry, ...]
    use_cases: tuple[UseCaseSpec, ...]
    presets: tuple[PresetSpec, ...]
    popularity: PopularitySnapshot
    baseline_defaults: BaselineDefaults
    fx: FxRate
    fx_active_rate: float = Field(gt=0)
    fx_is_override: bool
