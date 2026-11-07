"""Schema export CLI: ``uv run ai-tco-schemas [--out DIR]`` (Req 7.8 to 7.10, 40.2).

Writes ``<ContractName>.json`` for every input and output contract of the four
Service_Layer functions. Output is ``json.dumps(sort_keys=True, indent=2)`` plus a
trailing newline, so repeated runs give byte-identical files.
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel

from ai_tco_dss.domain.requests import (
    RecommendRequest,
    ScenarioRequest,
    SizeRequest,
    SizeResult,
    TcoProjection,
    TcoRequest,
)
from ai_tco_dss.domain.results import Recommendation, ScenarioResult

# Inputs and outputs of evaluate_scenario, recommend, size and project_tco.
SERVICE_CONTRACTS: tuple[type[BaseModel], ...] = (
    ScenarioRequest,
    ScenarioResult,
    RecommendRequest,
    Recommendation,
    SizeRequest,
    SizeResult,
    TcoRequest,
    TcoProjection,
)


def export(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for contract in SERVICE_CONTRACTS:
        try:
            schema = contract.model_json_schema()
            text = json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
            (out_dir / f"{contract.__name__}.json").write_bytes(text.encode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"cannot export schema of {contract.__name__}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export Service_Layer JSON Schemas.")
    parser.add_argument("--out", type=Path, default=Path("schemas"), help="output directory")
    args = parser.parse_args(argv)
    try:
        export(args.out)
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(SERVICE_CONTRACTS)} schemas to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
