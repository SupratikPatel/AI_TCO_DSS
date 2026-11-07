"""Validate_CLI (Req 8.1, 8.4, 8.5, 8.7 to 8.10, 9.1, 9.2, 9.8, 11.3 to 11.6, 11.8, 11.9,
12.2, 13.8)."""

import json
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ai_tco_dss.catalog import validate

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "catalog_min"
HW = "catalog/hardware/mac-studio-m5-max-128gb.json"
GPU = "catalog/hardware/rtx-pro-6000-96gb.json"
MODEL = "catalog/models/qwen-3-8-27b.json"
QUALITY = "benchmarks/quality.json"
SOURCES = "sources.json"
ERROR_LINE = re.compile(r"^(?P<path>\S+\.json): (?P<field>\S*): (?P<message>.+)$")


@pytest.fixture
def root(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(FIXTURE, target)
    return target


def _load(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _save(root: Path, rel: str, data: Any) -> None:
    (root / rel).write_text(json.dumps(data, indent=2), encoding="utf-8")


def _edit(root: Path, rel: str, change: Callable[[Any], None]) -> None:
    data = _load(root, rel)
    change(data)
    _save(root, rel, data)


def _run(root: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, list[str]]:
    code = validate.main(["--root", str(root)])
    out = capsys.readouterr()
    return code, (out.out + out.err).strip().splitlines()


def _errors(lines: list[str]) -> list[re.Match[str]]:
    return [m for m in (ERROR_LINE.match(line.replace("\\", "/")) for line in lines) if m]


def _assert_error(lines: list[str], path_part: str, field_part: str, *message_parts: str) -> None:
    for match in _errors(lines):
        located = path_part in match["path"] and field_part in match["field"]
        if located and all(p.lower() in match["message"].lower() for p in message_parts):
            return
    raise AssertionError(
        f"no error for {path_part} {field_part} {message_parts}:\n" + "\n".join(lines)
    )


# --------------------------------------------------------------------------- success


def test_req_11_9_valid_fixture_reports_summary_and_exits_0(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, lines = _run(root, capsys)
    assert code == 0, lines
    assert lines[-1] == "Validated 2 hardware, 2 model, 1 benchmark, 9 reference files: 0 errors"


def test_req_11_2_non_json_files_are_ignored(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / "catalog" / "hardware" / "notes.txt").write_text("not json", encoding="utf-8")
    code, lines = _run(root, capsys)
    assert code == 0, lines


# --------------------------------------------------------------------------- format


def test_req_11_4_error_lines_total_and_exit_1(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(source_id="NOPE-1"))
    _edit(root, GPU, lambda d: d["load_watts"].update(source_id="NOPE-2"))
    code, lines = _run(root, capsys)
    assert code == 1
    errors = _errors(lines)
    assert len(errors) == 2, lines
    assert lines[-1] == "2 errors"


def test_req_11_4_unparseable_json_reports_line_and_column(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / MODEL).write_text('{\n  "id": "qwen-3-8-27b",\n  "name": \n}\n', encoding="utf-8")
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, MODEL, "4:1", "json")


def test_req_8_10_11_3_all_errors_reported_in_one_run(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(source_id="NOPE-1"))
    _edit(root, QUALITY, lambda d: d["records"][0].update(model_id="ghost-model"))
    (root / GPU).write_text("{", encoding="utf-8")
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts", "NOPE-1")
    _assert_error(lines, QUALITY, "records[0].model_id", "ghost-model")
    _assert_error(lines, GPU, "1:2", "json")


# --------------------------------------------------------------------------- source registry


@pytest.mark.parametrize("field", ["title", "publisher", "tier"])
def test_req_8_1_8_8_source_entry_missing_field(
    root: Path, capsys: pytest.CaptureFixture[str], field: str
) -> None:
    _edit(root, SOURCES, lambda d: d["sources"][0].pop(field))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, SOURCES, f"sources[0].{field}", "YT-01")


def test_req_8_1_source_needs_url_or_reference(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, SOURCES, lambda d: d["sources"][0].update(url=None, reference=None))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, SOURCES, "sources[0]", "YT-01", "url or reference")


def test_req_8_8_source_invalid_tier(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, SOURCES, lambda d: d["sources"][1].update(tier="blog"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, SOURCES, "sources[1].tier", "YT-02")


def test_req_8_8_duplicate_source_id(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, SOURCES, lambda d: d["sources"].append(dict(d["sources"][0])))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, SOURCES, "source_id", "duplicate", "YT-01")


# --------------------------------------------------------------------------- provenance


def test_req_8_4_11_6_unknown_source_id(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, HW, lambda d: d["memory_bandwidth_gbs"].update(source_id="HW-UNKNOWN"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "memory_bandwidth_gbs.source_id", "HW-UNKNOWN")


def test_req_8_5_missing_provenance(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, HW, lambda d: d.update(idle_watts=10))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts", "lacks Provenance_Record")


def test_req_8_5_missing_provenance_in_reference_file(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, "reference/fx.json", lambda d: d.pop("source_id"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "reference/fx.json", "eur_to_usd", "lacks Provenance_Record")


def test_req_8_9_youtube_source_must_be_community(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d["os_reserved_memory_ratio"].update(tier="official"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "os_reserved_memory_ratio.tier", "YT-02", "community")


def test_req_8_7_youtube_value_needs_single_source_note(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d["os_reserved_memory_ratio"].pop("note"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "os_reserved_memory_ratio.note", "single-source")


def test_provenance_tier_must_match_registry(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(tier="official"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts.tier", "SPEC-03", "assumption")


def test_req_8_9_invalid_tier(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(tier="rumour"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts.tier", "rumour")


@pytest.mark.parametrize("accessed", ["07.11.2026", "2026-11-07T10:00:00", "2026/11/07"])
def test_req_8_9_bad_date_format(
    root: Path, capsys: pytest.CaptureFixture[str], accessed: str
) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(accessed=accessed))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts.accessed", "YYYY-MM-DD")


def test_req_8_9_future_access_date(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, HW, lambda d: d["idle_watts"].update(accessed="2999-01-01"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "idle_watts.accessed", "future")


# --------------------------------------------------------------------------- benchmarks


def _decode_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "metric": "decode_tps",
        "value": 14.7,
        "model_id": "qwen-3-8-27b",
        "hardware_id": "mac-studio-m5-max-128gb",
        "precision": "INT4",
        "context_tokens": 8192,
        "engine": "mlx",
        "source_id": "YT-21",
        "tier": "community",
        "accessed": "2026-11-07",
        "note": "single-source",
    }
    return {**record, **overrides}


def test_req_9_1_valid_decode_record_passes(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _save(root, "benchmarks/decode.json", {"records": [_decode_record()]})
    code, lines = _run(root, capsys)
    assert code == 0, lines
    assert "2 benchmark" in lines[-1]


@pytest.mark.parametrize("context_tokens", [None, 0])
def test_req_9_2_9_8_context_tokens_required(
    root: Path, capsys: pytest.CaptureFixture[str], context_tokens: int | None
) -> None:
    record = _decode_record()
    if context_tokens is None:
        record.pop("context_tokens")
    else:
        record["context_tokens"] = context_tokens
    _save(root, "benchmarks/decode.json", {"records": [record]})
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "benchmarks/decode.json", "records[0].context_tokens", "")


@pytest.mark.parametrize(
    ("field", "value"), [("model_id", "ghost-model"), ("hardware_id", "ghost-hardware")]
)
def test_req_11_6_dangling_benchmark_reference(
    root: Path, capsys: pytest.CaptureFixture[str], field: str, value: str
) -> None:
    _save(root, "benchmarks/decode.json", {"records": [_decode_record(**{field: value})]})
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "benchmarks/decode.json", f"records[0].{field}", value)


# --------------------------------------------------------------------------- catalog items


def test_req_11_5_duplicate_id_across_folders(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    data = _load(root, MODEL)
    data["id"] = "rtx-pro-6000-96gb"
    _save(root, "catalog/models/rtx-pro-6000-96gb.json", data)
    code, lines = _run(root, capsys)
    assert code == 1
    duplicate = [m for m in _errors(lines) if "duplicate id" in m["message"]]
    assert len(duplicate) == 1, lines
    assert "rtx-pro-6000-96gb" in duplicate[0]["message"]
    assert "catalog/hardware/rtx-pro-6000-96gb.json" in duplicate[0]["message"]
    assert "catalog/models/rtx-pro-6000-96gb.json" in duplicate[0]["message"]


def test_req_11_8_filename_id_mismatch(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (root / MODEL).rename(root / "catalog/models/qwen-27b.json")
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "catalog/models/qwen-27b.json", "id", "qwen-3-8-27b")


def test_req_11_3_contract_violation_names_field(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _edit(root, HW, lambda d: d.update(memory_architecture="quantum"))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, HW, "memory_architecture", "")


# --------------------------------------------------------------------------- reference data


@pytest.mark.parametrize(
    ("rel", "change", "field", "entry"),
    [
        (
            "reference/electricity.json",
            lambda d: d["tariffs"][1]["price_per_kwh"].update(value=1.5),
            "tariffs[1].price_per_kwh.value",
            "de-office",
        ),
        (
            "reference/electricity.json",
            lambda d: d["tariffs"].pop(2),
            "tariffs",
            "eu-nordic",
        ),
        (
            "reference/staffing_hubs.json",
            lambda d: d["hubs"][2]["employer_social_tax_pct"].update(value=101),
            "hubs[2].employer_social_tax_pct.value",
            "ro-cluj-bucharest",
        ),
        (
            "reference/staffing_hubs.json",
            lambda d: d["hubs"][0]["recruiting_delay_months"].update(value=25),
            "hubs[0].recruiting_delay_months.value",
            "de-munich-hq",
        ),
        (
            "reference/staffing_hubs.json",
            lambda d: d["hubs"][3]["base_salary"].update(value=0),
            "hubs[3].base_salary.value",
            "pl-warsaw-krakow",
        ),
        (
            "reference/harnesses.json",
            lambda d: d["harnesses"][4]["scaffolding_tokens_per_turn"].update(
                tier="community", source_id="YT-16", note="single-source"
            ),
            "harnesses[4].scaffolding_tokens_per_turn.tier",
            "custom-lean",
        ),
        (
            "reference/use_cases.json",
            lambda d: d["use_cases"][0]["quality_floor"].update(value=120),
            "use_cases[0].quality_floor.value",
            "writing-email",
        ),
        (
            "reference/rentals.json",
            lambda d: d["rentals"][0]["monthly_price"].update(value=0),
            "rentals[0].monthly_price.value",
            "hetzner-gex63",
        ),
        (
            "reference/rentals.json",
            lambda d: d["rentals"].pop(1),
            "rentals",
            "hetzner-gex430",
        ),
        (
            "reference/rentals.json",
            lambda d: d["rentals"][0].update(gpu_hardware_id="ghost-gpu"),
            "rentals[0].gpu_hardware_id",
            "ghost-gpu",
        ),
    ],
)
def test_req_13_8_reference_rules(
    root: Path,
    capsys: pytest.CaptureFixture[str],
    rel: str,
    change: Callable[[Any], None],
    field: str,
    entry: str,
) -> None:
    _edit(root, rel, change)
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, rel, field, entry)


def test_req_12_2_fx_rate_must_be_positive(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _edit(root, "reference/fx.json", lambda d: d.update(eur_to_usd=0))
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "reference/fx.json", "eur_to_usd", "")


def test_missing_reference_file(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (root / "reference" / "harnesses.json").unlink()
    code, lines = _run(root, capsys)
    assert code == 1
    _assert_error(lines, "reference/harnesses.json", "", "missing")
