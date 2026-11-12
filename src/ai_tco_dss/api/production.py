"""Same-origin deployment of the built Vite client and the Python API.

Run from the checkout root with uvicorn --factory; fail early on missing build.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from ai_tco_dss.api.app import app as api


def create_app(dist: Path | None = None) -> FastAPI:
    root = (dist or Path(os.environ.get("AI_TCO_WEB_DIST", "frontend/dist"))).resolve()
    if not (root / "index.html").is_file():
        raise RuntimeError("Frontend build missing. Run npm run build before serving.")
    app = FastAPI(title=api.title, version=api.version)
    app.include_router(api.router)
    app.exception_handlers.update(api.exception_handlers)

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        target = (root / path).resolve()
        if not target.is_relative_to(root) or path.split("/")[0] == "api":
            raise HTTPException(404)
        if target.is_file():
            cache = (
                "public, max-age=31536000, immutable" if path.startswith("assets/") else "no-cache"
            )
            return FileResponse(target, headers={"Cache-Control": cache})
        if Path(path).suffix or path.startswith("assets/"):
            raise HTTPException(404)
        return FileResponse(root / "index.html", headers={"Cache-Control": "no-cache"})

    return app
