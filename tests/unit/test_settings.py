"""Engine settings: context-match tolerance, δ_ctx breakpoints, calibration tolerances
(Req 9.5, 9.10, 20.6, 42.2)."""

import pytest

from ai_tco_dss.domain import BenchmarkMetric
from ai_tco_dss.domain.errors import ConfigurationError
from ai_tco_dss.settings import Settings, load_engine_parameters

TOLERANCE_ENV = "AI_TCO_CONTEXT_MATCH_TOLERANCE"
BREAKPOINTS_ENV = "AI_TCO_DELTA_CTX_BREAKPOINTS"


def test_req_9_5_default_context_match_tolerance_is_0_25() -> None:
    assert Settings().context_match_tolerance == 0.25
    assert load_engine_parameters().context_match_tolerance == 0.25


@pytest.mark.parametrize("value", ["0", "1", "0.5"])
def test_req_9_5_tolerance_range_ends_are_accepted(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv(TOLERANCE_ENV, value)
    assert load_engine_parameters().context_match_tolerance == float(value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_req_9_10_tolerance_outside_0_1_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch, value: float
) -> None:
    monkeypatch.setenv(TOLERANCE_ENV, str(value))
    with pytest.raises(ConfigurationError) as exc:
        load_engine_parameters()
    assert exc.value.setting == "context_match_tolerance"
    assert exc.value.value == value
    assert "context_match_tolerance" in str(exc.value)
    assert str(value) in str(exc.value)


def test_req_20_6_delta_ctx_breakpoints_have_their_defaults() -> None:
    assert load_engine_parameters().delta_ctx_breakpoints == (
        (8_192, 1.00),
        (32_768, 0.89),
        (131_072, 0.60),
        (262_144, 0.50),
        (1_048_576, 0.40),
    )


@pytest.mark.parametrize(
    "value",
    [
        "[[32768, 0.89], [8192, 1.0]]",  # contexts not increasing
        "[[8192, 0.8], [32768, 0.9]]",  # factor increases with the context
        "[]",  # no breakpoint
    ],
)
def test_req_20_6_invalid_delta_ctx_breakpoints_raise_configuration_error(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv(BREAKPOINTS_ENV, value)
    with pytest.raises(ConfigurationError) as exc:
        load_engine_parameters()
    assert exc.value.setting == "delta_ctx_breakpoints"


def test_req_42_2_calibration_tolerances_default_30_and_50_percent() -> None:
    tolerances = dict(load_engine_parameters().calibration_tolerance_pct)
    assert tolerances == {BenchmarkMetric.DECODE_TPS: 30.0, BenchmarkMetric.PREFILL_TPS: 50.0}
