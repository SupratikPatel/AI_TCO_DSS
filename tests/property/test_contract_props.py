"""Property tests for the Domain_Contracts and money helpers."""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import BaseModel
from strategies import contract_classes, for_contract

from ai_tco_dss.domain.money import eur_to_usd, usd_to_eur


# Feature: ai-tco-dss-mvp, Property 1: Contract JSON round trip
@pytest.mark.parametrize("cls", contract_classes(), ids=lambda c: c.__name__)
@settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(data=st.data())
def test_property_1_contract_json_round_trip(cls: type[BaseModel], data: st.DataObject) -> None:
    """Property 1 (Req 7.11): JSON serialisation then validation reproduces the instance."""
    instance = data.draw(for_contract(cls))
    assert cls.model_validate_json(instance.model_dump_json()) == instance


# Feature: ai-tco-dss-mvp, Property 6: FX round trip
@given(
    amount=st.floats(min_value=0, max_value=1e12, allow_nan=False),
    rate=st.floats(min_value=0.5, max_value=2.0, allow_nan=False),
)
def test_property_6_fx_round_trip(amount: float, rate: float) -> None:
    """Property 6 (Req 12.7): USD→EUR→USD with the same rate stays within 0.01 USD."""
    assert abs(eur_to_usd(usd_to_eur(amount, rate), rate) - amount) <= 0.01
