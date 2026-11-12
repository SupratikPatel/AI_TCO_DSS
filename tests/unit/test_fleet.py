"""Independent resource bounds for complete serving replicas (U-07 scope)."""

import pytest
from pydantic import ValidationError

from ai_tco_dss.domain.fleet import FleetSizingInput, ReplicaCapacity
from ai_tco_dss.engines.fleet import plan_fleet


def capacity(**changes: object) -> ReplicaCapacity:
    return ReplicaCapacity.model_validate(
        dict(
            gpus_per_replica=8,
            request_slots=16,
            retained_session_slots=40,
            aggregate_output_tps=400.0,
            capacity_basis="Synthetic joint-deployment resource ceilings; not an observed run",
            source_ids=("synthetic-test",),
        )
        | changes
    )


def demand(**changes: object) -> FleetSizingInput:
    return FleetSizingInput.model_validate(
        dict(
            capacity=capacity(),
            peak_concurrent_requests=33,
            retained_sessions=80,
            required_output_tps=800.0,
            spare_replicas=1,
        )
        | changes
    )


def test_independent_replicas_do_not_snap_three_to_four_or_multiply_capacity_by_gpus() -> None:
    result = plan_fleet(demand())
    assert result.replicas_for_peak == 3
    assert result.replicas_for_retention == 2
    assert result.replicas_for_output == 2
    assert result.minimum_active_replicas_lower_bound == 3
    assert result.total_replicas_lower_bound == 4
    assert result.total_gpus_lower_bound == 32
    assert result.unresolved == ()
    assert result.source_ids == ("synthetic-test",)
    assert "necessary" in result.limitation


@pytest.mark.parametrize(("peak", "expected"), [(0, 0), (16, 1), (17, 2), (48, 3)])
def test_integer_capacity_boundaries(peak: int, expected: int) -> None:
    result = plan_fleet(
        demand(
            peak_concurrent_requests=peak,
            retained_sessions=0,
            required_output_tps=0,
            spare_replicas=0,
        )
    )
    assert result.minimum_active_replicas_lower_bound == expected


def test_retained_sessions_and_output_demand_can_independently_dominate() -> None:
    assert plan_fleet(demand(retained_sessions=201)).minimum_active_replicas_lower_bound == 6
    assert plan_fleet(demand(required_output_tps=2000.1)).minimum_active_replicas_lower_bound == 6


def test_decimal_output_capacity_does_not_create_an_extra_replica() -> None:
    result = plan_fleet(
        demand(capacity=capacity(aggregate_output_tps=0.01), required_output_tps=0.14)
    )
    assert result.replicas_for_output == 14


def test_finite_extreme_output_ratio_does_not_overflow() -> None:
    result = plan_fleet(
        demand(capacity=capacity(aggregate_output_tps=1e-300), required_output_tps=1e300)
    )
    assert result.replicas_for_output == 10**600


def test_unknown_capacity_preserves_known_lower_bounds_and_reports_gaps() -> None:
    result = plan_fleet(demand(capacity=capacity(request_slots=None, aggregate_output_tps=None)))
    assert result.replicas_for_peak is None
    assert result.replicas_for_output is None
    assert result.minimum_active_replicas_lower_bound == 2
    assert result.unresolved == ("request_slots", "aggregate_output_tps")


def test_unknown_output_demand_is_not_replaced_with_employee_seats_or_zero() -> None:
    result = plan_fleet(demand(required_output_tps=None))
    assert result.replicas_for_output is None
    assert result.unresolved == ("required_output_tps",)


@pytest.mark.parametrize(
    "field", ["request_slots", "retained_session_slots", "aggregate_output_tps"]
)
def test_positive_demand_with_zero_capacity_has_no_finite_fleet(field: str) -> None:
    result = plan_fleet(demand(capacity=capacity(**{field: 0})))
    assert result.minimum_active_replicas_lower_bound is None
    assert result.total_replicas_lower_bound is None
    assert result.total_gpus_lower_bound is None
    assert result.impossible == (field,)


def test_zero_demand_needs_no_capacity_and_spares_are_explicit() -> None:
    result = plan_fleet(
        demand(
            capacity=capacity(
                request_slots=None, retained_session_slots=0, aggregate_output_tps=None
            ),
            peak_concurrent_requests=0,
            retained_sessions=0,
            required_output_tps=0,
            spare_replicas=2,
        )
    )
    assert result.minimum_active_replicas_lower_bound == 0
    assert result.total_replicas_lower_bound == 2
    assert result.total_gpus_lower_bound == 16
    assert result.unresolved == ()


@pytest.mark.parametrize(
    "changes",
    [
        {"gpus_per_replica": 0},
        {"request_slots": -1},
        {"request_slots": 1.5},
        {"aggregate_output_tps": float("nan")},
        {"aggregate_output_tps": float("inf")},
        {"source_ids": ()},
        {"capacity_basis": ""},
    ],
)
def test_invalid_capacity_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        capacity(**changes)


def test_spares_must_be_supplied_and_results_are_immutable_and_deterministic() -> None:
    payload = demand().model_dump()
    payload.pop("spare_replicas")
    with pytest.raises(ValidationError):
        FleetSizingInput.model_validate(payload)
    result = plan_fleet(demand())
    assert plan_fleet(demand()) == result
    with pytest.raises(ValidationError):
        result.total_gpus_lower_bound = 0
