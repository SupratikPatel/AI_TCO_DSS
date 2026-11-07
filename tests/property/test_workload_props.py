"""Property tests for the Workload_Engine (Properties 9 and 10)."""

from functools import cache

import pytest
from hypothesis import given
from hypothesis import strategies as st
from strategies import for_contract

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import (
    HarnessEntry,
    HarnessType,
    ModelSpec,
    Sourced,
    SourceTier,
    ThinkingEffortPreset,
    WorkloadInput,
    WorkloadProfile,
)
from ai_tco_dss.engines.workload import compute_workload
from ai_tco_dss.settings import load_engine_parameters

PARAMS = load_engine_parameters()
REL = 1e-9
# Oracle constants, taken from requirements.md (Req 15.1 to 15.5), not from settings.py.
MU = {
    ThinkingEffortPreset.NONE: 1.0,
    ThinkingEffortPreset.LOW: 1.5,
    ThinkingEffortPreset.MEDIUM: 2.5,
    ThinkingEffortPreset.EXTRA_HIGH: 4.94,
}
BOUNDS = {
    "active_users": 100_000,
    "daily_requests_per_user": 10_000,
    "avg_input_tokens": 1_000_000,
    "avg_output_tokens": 200_000,
}


@cache
def _base_model() -> ModelSpec:
    return next(m for m in get_default_repository().catalog().models if m.id == "qwen-3-8-27b")


def _harnesses(tokens: list[int]) -> tuple[HarnessEntry, ...]:
    return tuple(
        HarnessEntry(
            id=harness,
            scaffolding_tokens_per_turn=Sourced[int](
                value=value, source_id="T", tier=SourceTier.ASSUMPTION, accessed="2026-11-07"
            ),
        )
        for harness, value in zip(HarnessType, tokens, strict=True)
    )


HARNESS_TOKENS = st.lists(
    st.integers(min_value=0, max_value=200_000),
    min_size=len(HarnessType),
    max_size=len(HarnessType),
)
FAMILIES = st.sampled_from(["Claude", "Qwen", "GPT", "claude", "DeepSeek"])


# Feature: ai-tco-dss-mvp, Property 9: Workload formulas
@given(profile=for_contract(WorkloadProfile), tokens=HARNESS_TOKENS, family=FAMILIES)
def test_property_9_workload_formulas(
    profile: WorkloadProfile, tokens: list[int], family: str
) -> None:
    """Property 9 (Req 14.4, 15.1, 15.2, 15.3, 15.4, 15.5, 15.7): results equal the formulas."""
    model = _base_model().model_copy(update={"family": family})
    harnesses = _harnesses(tokens)
    result = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=harnesses), PARAMS
    )

    by_id = {h.id: h.scaffolding_tokens_per_turn.value for h in harnesses}
    custom = profile.harness_type == HarnessType.CUSTOM_LEAN
    s_harness = (
        profile.custom_scaffolding_tokens
        if custom and profile.custom_scaffolding_tokens is not None
        else by_id[profile.harness_type]
    )
    s_eff = s_harness * (1 - (0.75 if profile.mcp_code_mode_pruning else 0.0))
    tau = 1.30 if family == "Claude" else 1.00
    t_in = (profile.avg_input_tokens + s_eff) * tau
    t_out = profile.avg_output_tokens * tau
    out_think = t_out * MU[profile.thinking_effort_preset]
    kappa = 1.0 + profile.mega_session_ratio * 2.8
    nu = 2.0 if profile.has_verification_agent_layer else 1.0
    requests = (
        profile.active_users * profile.daily_requests_per_user * profile.working_days_per_month
    )

    assert result.monthly_requests == requests
    assert result.tau == tau
    assert result.s_effective == pytest.approx(s_eff, rel=REL, abs=1e-9)
    assert result.t_in_hat == pytest.approx(t_in, rel=REL)
    assert result.t_out_hat == pytest.approx(t_out, rel=REL)
    assert result.out_think == pytest.approx(out_think, rel=REL)
    assert result.kappa_mega == pytest.approx(kappa, rel=REL)
    assert 1.0 <= result.kappa_mega <= 3.8
    assert result.nu_verify == nu
    assert result.monthly_tokens == pytest.approx(
        requests * (t_in + out_think) * kappa * nu, rel=REL
    )
    assert result.monthly_output_demand == pytest.approx(requests * out_think * nu, rel=REL)


# Feature: ai-tco-dss-mvp, Property 10: Workload monotonicity
@given(
    profile=for_contract(WorkloadProfile),
    tokens=HARNESS_TOKENS,
    family=FAMILIES,
    field=st.sampled_from(sorted(BOUNDS)),
    delta=st.integers(min_value=1, max_value=1_000_000),
)
def test_property_10_workload_monotonicity(
    profile: WorkloadProfile, tokens: list[int], family: str, field: str, delta: int
) -> None:
    """Property 10 (Req 15.6): raising users, requests, T_in or T_out never lowers volume."""
    model = _base_model().model_copy(update={"family": family})
    harnesses = _harnesses(tokens)
    larger = profile.model_copy(update={field: min(getattr(profile, field) + delta, BOUNDS[field])})
    before = compute_workload(
        WorkloadInput(profile=profile, model=model, harnesses=harnesses), PARAMS
    )
    after = compute_workload(
        WorkloadInput(profile=larger, model=model, harnesses=harnesses), PARAMS
    )
    assert after.monthly_tokens >= before.monthly_tokens
