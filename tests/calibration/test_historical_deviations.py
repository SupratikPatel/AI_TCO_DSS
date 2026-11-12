"""Preserved C-035/C-036 diagnostics under the OLD assumed conditions.

These xfails reproduce numerical failures, not matched-condition calibration.
The eligibility report excludes the incomplete observations instead of counting them as passes.
"""

import pytest
from tests.unit.test_performance import PARAMS, _inp

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import PrecisionFormat
from ai_tco_dss.engines.performance import _formula_decode


@pytest.mark.parametrize(
    "hardware_id,model_id,precision,context,measured",
    [
        ("mac-studio-m5-ultra-256gb", "qwen-3-8-flash-next", "INT4", 8192, 108),
        ("mac-studio-m5-ultra-256gb", "qwen-3-8-flash-next", "INT4", 131072, 61),
        ("rtx-5070-strata-64gb", "deepseek-v4-1-flash", "INT2", 8192, 4.6),
    ],
)
@pytest.mark.xfail(
    strict=True, reason="C-035/C-036 historical unmatched diagnostic; not validation"
)
def test_historical_formula_error_remains_visible(
    hardware_id, model_id, precision, context, measured
):
    repo = get_default_repository()
    hw = next(h for h in repo.catalog().hardware if h.id == hardware_id)
    model = next(m for m in repo.catalog().models if m.id == model_id)
    inp = _inp(
        repo,
        hardware=hw,
        model=model,
        precision=PrecisionFormat(precision),
        target_context_length=context,
    )
    formula, _ = _formula_decode(inp, PARAMS)
    assert abs(formula.value - measured) / measured <= 0.30
