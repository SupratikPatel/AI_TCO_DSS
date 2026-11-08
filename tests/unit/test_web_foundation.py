"""Reference assets, boundary and dev entry point: 43.1, 43.3, 43.9."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_req_43_1_43_9_stack_and_launcher():
    package = json.loads((ROOT / "package.json").read_text())
    frontend = json.loads((ROOT / "frontend/package.json").read_text())
    assert package["scripts"]["dev"] == "node scripts/dev.mjs"
    for dependency in ("react", "react-dom", "radix-ui", "plotly.js-basic-dist-min"):
        assert dependency in frontend["dependencies"]
    for dependency in ("vite", "typescript", "tailwindcss"):
        assert dependency in frontend["devDependencies"]
    assert (ROOT / "frontend/src/components/ui/button.tsx").exists()


def test_req_43_3_stitch_exports():
    folder = ROOT / "design/stitch"
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["project"] == "12247395809959632226"
    for screen in manifest["screens"]:
        assert (folder / (screen["id"] + ".html")).stat().st_size > 100
        assert any((folder / (screen["id"] + ext)).exists() for ext in (".jpg", ".png"))
    assert (folder / "design-system.json").exists()
