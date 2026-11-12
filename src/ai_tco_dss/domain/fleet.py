"""Opt-in fleet resource bounds; separate from single-deployment recommendation contracts."""

from pydantic import Field

from ai_tco_dss.domain.base import Contract


class ReplicaCapacity(Contract):
    """Caller-established resource ceilings of one complete, workload-matched replica.

    Request slots mean simultaneous resident inference requests, not employee seats,
    workflow/session trees or a configured scheduler limit. Output TPS excludes input
    tokens and covers the complete replica, not each GPU or individual stream.
    The caller must establish these meanings; this contract cannot verify a source.
    """

    gpus_per_replica: int = Field(ge=1)
    request_slots: int | None = Field(default=None, ge=0)
    retained_session_slots: int | None = Field(default=None, ge=0)
    aggregate_output_tps: float | None = Field(default=None, ge=0)
    capacity_basis: str = Field(min_length=1)
    source_ids: tuple[str, ...] = Field(min_length=1)


class FleetSizingInput(Contract):
    capacity: ReplicaCapacity
    peak_concurrent_requests: int = Field(ge=0)
    retained_sessions: int = Field(ge=0)
    required_output_tps: float | None = Field(default=None, ge=0)
    spare_replicas: int = Field(ge=0)


class FleetSizingResult(Contract):
    replicas_for_peak: int | None
    replicas_for_retention: int | None
    replicas_for_output: int | None
    minimum_active_replicas_lower_bound: int | None
    total_replicas_lower_bound: int | None
    total_gpus_lower_bound: int | None
    unresolved: tuple[str, ...]
    impossible: tuple[str, ...]
    capacity_basis: str
    source_ids: tuple[str, ...]
    limitation: str
