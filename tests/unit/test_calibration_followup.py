"""Prevent contradictory run hints and unsupported calibration predictions."""

import pytest
from tests.unit.test_benchmark_eligibility import complete_record
from tests.unit.test_performance import _inp, _perf, _rec
from tests.unit.test_tco import PARAMS, _aggregate_record, _base

from ai_tco_dss.catalog import get_default_repository
from ai_tco_dss.domain import BenchmarkSet
from ai_tco_dss.engines.tco import compute_tco
from ai_tco_dss.services import calibration_report as cr


@pytest.mark.parametrize("matches_workload", [False, True])
def test_decode_matches_generated_output_volume_instead_of_hint(matches_workload):
    repo = get_default_repository()
    inp = _inp(repo)
    inp = inp.model_copy(
        update={
            "options": inp.options.model_copy(
                update={
                    "benchmark_conditions": inp.options.benchmark_conditions.model_copy(
                        update={"output_tokens": 512}
                    )
                }
            )
        }
    )
    output = round(inp.workload.out_think)
    assert output != 512
    record = _rec(value=123)
    record = record.model_copy(
        update={
            "conditions": record.conditions.model_copy(
                update={"output_tokens": output if matches_workload else 512}
            )
        }
    )
    inp = inp.model_copy(update={"benchmarks": BenchmarkSet(records=(record,))})
    result = _perf(inp)
    assert result.decode_tps.origin.origin == ("measured" if matches_workload else "formula")


@pytest.mark.parametrize("matches_workload", [False, True])
def test_aggregate_matches_generated_output_volume_instead_of_hint(matches_workload):
    inp = _base()
    inp = inp.model_copy(
        update={
            "options": inp.options.model_copy(
                update={
                    "benchmark_conditions": inp.options.benchmark_conditions.model_copy(
                        update={"output_tokens": 512}
                    )
                }
            )
        }
    )
    record = _aggregate_record(123)
    record = record.model_copy(
        update={
            "conditions": record.conditions.model_copy(
                update={"output_tokens": round(inp.workload.out_think) if matches_workload else 512}
            )
        }
    )
    result = compute_tco(
        inp.model_copy(update={"benchmarks": BenchmarkSet(records=(record,))}), PARAMS
    )
    assert result.aggregate_tps.origin.origin == ("measured" if matches_workload else "formula")


def test_calibration_excludes_api_models_instead_of_crashing():
    catalog = get_default_repository().catalog()
    model = next(m for m in catalog.models if m.type == "commercial-api")
    record = complete_record(model_id=model.id)
    assert "open-weights" in cr.calibration_reason(record, catalog)
    assert cr.formula_value(record, catalog, PARAMS) is None


def test_calibration_excludes_context_beyond_the_catalog_model_limit():
    catalog = get_default_repository().catalog()
    record = complete_record()
    model = next(m for m in catalog.models if m.id == record.model_id)
    record = record.model_copy(update={"prompt_tokens": model.max_context_length.value + 1})
    assert "model context" in cr.calibration_reason(record, catalog)
    assert cr.formula_value(record, catalog, PARAMS) is None


def test_calibration_does_not_predict_resident_performance_for_model_oom():
    catalog = get_default_repository().catalog()
    record = complete_record(model_id="qwen-3-8-flash-next")
    assert "sizing" in cr.calibration_reason(record, catalog)
    assert cr.formula_value(record, catalog, PARAMS) is None
    catalog = catalog.model_copy(update={"benchmarks": (record,)})
    report = cr.calibrate(catalog, PARAMS)
    assert report.metrics[0].count == 0
    assert "sizing" in report.metrics[0].excluded[0].reason
