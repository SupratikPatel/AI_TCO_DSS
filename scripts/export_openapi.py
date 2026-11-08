"""Emit deterministic OpenAPI without starting a server."""

import json
import sys
from pathlib import Path

from ai_tco_dss.api.app import app

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(app.openapi(), sort_keys=True, indent=2) + "\n")
