"""Workload_Engine: effective token volume (Req 14.4, 15.1 to 15.8; design.md § "Workload_Engine").

Pure: the result depends only on the `WorkloadInput` contract and `EngineParameters`.
"""

from ai_tco_dss.domain import (
    EngineParameters,
    HarnessType,
    WorkloadInput,
    WorkloadResult,
)
from ai_tco_dss.domain.errors import EngineInputError

CLAUDE_FAMILY = "Claude"


def _scaffolding_tokens(inp: WorkloadInput) -> float:
    """S_harness: the custom-lean value of the profile if set, else the harness table value."""
    profile = inp.profile
    if (
        profile.harness_type == HarnessType.CUSTOM_LEAN
        and profile.custom_scaffolding_tokens is not None
    ):
        tokens = profile.custom_scaffolding_tokens
    else:
        entry = next((h for h in inp.harnesses if h.id == profile.harness_type), None)
        if entry is None:
            raise EngineInputError("harness_type", "a harness listed in harnesses.json")
        tokens = entry.scaffolding_tokens_per_turn.value
    if tokens < 0:
        raise EngineInputError("S_harness", ">= 0 scaffolding tokens", profile.harness_type.value)
    return float(tokens)


def compute_workload(inp: WorkloadInput, params: EngineParameters) -> WorkloadResult:
    """Monthly requests and effective token volume of one Workload_Profile and model."""
    profile = inp.profile
    thinking = dict(params.thinking_multipliers)
    if profile.thinking_effort_preset not in thinking:
        raise EngineInputError("thinking_effort_preset", "none, low, medium or extra-high")

    monthly_requests = (
        profile.active_users * profile.daily_requests_per_user * profile.working_days_per_month
    )
    r_prune = params.mcp_prune_ratio if profile.mcp_code_mode_pruning else 0.0
    s_effective = _scaffolding_tokens(inp) * (1 - r_prune)
    tau = params.claude_tokenizer_inflation if inp.model.family == CLAUDE_FAMILY else 1.0
    t_in_hat = (profile.avg_input_tokens + s_effective) * tau
    t_out_hat = profile.avg_output_tokens * tau
    out_think = t_out_hat * thinking[profile.thinking_effort_preset]
    kappa_mega = 1.0 + profile.mega_session_ratio * params.mega_session_slope
    nu_verify = 2.0 if profile.has_verification_agent_layer else 1.0
    return WorkloadResult(
        monthly_requests=monthly_requests,
        s_effective=s_effective,
        t_in_hat=t_in_hat,
        t_out_hat=t_out_hat,
        out_think=out_think,
        kappa_mega=kappa_mega,
        nu_verify=nu_verify,
        tau=tau,
        monthly_tokens=monthly_requests * (t_in_hat + out_think) * kappa_mega * nu_verify,
        monthly_output_demand=monthly_requests * out_think * nu_verify,
    )
