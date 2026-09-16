from __future__ import annotations

from fastapi import FastAPI

from riskintel import __version__
from riskintel.storage import InMemoryRepository, Repository

from .routers import clients, community, decisions, iot, losses, models, risk_issues


def create_app(repo: Repository | None = None) -> FastAPI:
    app = FastAPI(
        title="Risk Intelligence Platform (outline)",
        version=__version__,
        description=(
            "Community risk intelligence: loss history, risk issues, IoT signals, "
            "analytics and loss modelling driving self-insured retention decisions."
        ),
    )
    app.state.repo = repo or InMemoryRepository()

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    app.include_router(clients.community_router)
    for router in (clients, losses, risk_issues, iot, community, models, decisions):
        app.include_router(router.router)
    return app


app = create_app()
