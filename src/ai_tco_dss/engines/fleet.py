"""Necessary fleet resource bounds under ideal balance; no scheduler or SLA prediction."""

import math
from fractions import Fraction

from ai_tco_dss.domain.fleet import FleetSizingInput, FleetSizingResult


def plan_fleet(inp: FleetSizingInput) -> FleetSizingResult:
    """Keep independent replicas distinct from GPUs used by each model replica.

    Independent resource ceilings do not establish joint placement feasibility.
    Unknown constraints stay visible even when another resource supplies a bound.
    A known zero capacity with positive demand has no finite solution.
    """
    unresolved: list[str] = []
    impossible: list[str] = []

    def bound(demand: float | None, capacity: float | None, name: str) -> int | None:
        if demand is None:
            unresolved.append("required_output_tps")
            return None
        if demand == 0:
            return 0
        if capacity is None:
            unresolved.append(name)
            return None
        if capacity == 0:
            impossible.append(name)
            return None
        # Preserve decimal input boundaries and avoid float-division overflow.
        return math.ceil(Fraction(str(demand)) / Fraction(str(capacity)))

    capacity = inp.capacity
    peak = bound(inp.peak_concurrent_requests, capacity.request_slots, "request_slots")
    retained = bound(
        inp.retained_sessions, capacity.retained_session_slots, "retained_session_slots"
    )
    output = bound(inp.required_output_tps, capacity.aggregate_output_tps, "aggregate_output_tps")
    known = [value for value in (peak, retained, output) if value is not None]
    active = None if impossible or not known else max(known)
    total = None if active is None else active + inp.spare_replicas
    return FleetSizingResult(
        replicas_for_peak=peak,
        replicas_for_retention=retained,
        replicas_for_output=output,
        minimum_active_replicas_lower_bound=active,
        total_replicas_lower_bound=total,
        total_gpus_lower_bound=None if total is None else total * capacity.gpus_per_replica,
        unresolved=tuple(unresolved),
        impossible=tuple(impossible),
        capacity_basis=capacity.capacity_basis,
        source_ids=capacity.source_ids,
        limitation=(
            "Independent resource bounds are necessary, not sufficient: ideal balance and "
            "additive output capacity do not validate joint memory placement, session affinity, "
            "arrival bursts, queueing, task quality or loaded latency."
        ),
    )
