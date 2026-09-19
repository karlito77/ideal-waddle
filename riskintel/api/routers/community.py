from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from riskintel.api.deps import get_repo
from riskintel.community import find_peers, pool_experience
from riskintel.domain import LineOfBusiness
from riskintel.pipeline import build_risk_view
from riskintel.storage import Repository

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/{client_id}/peers")
def peers(client_id: str, min_score: float = 0.4, repo: Repository = Depends(get_repo)) -> list[dict]:
    client = repo.get_client(client_id)
    if client is None:
        raise HTTPException(404, "client not found")
    return [m.__dict__ for m in find_peers(client, repo.list_clients(), min_score)]


@router.get("/{client_id}/pool")
def pool(client_id: str, line_of_business: Optional[LineOfBusiness] = None, repo: Repository = Depends(get_repo)) -> list[dict]:
    client = repo.get_client(client_id)
    if client is None:
        raise HTTPException(404, "client not found")
    matches = find_peers(client, repo.list_clients())
    return [s.__dict__ for s in pool_experience(repo, client_id, matches, line_of_business)]


@router.get("/{client_id}/benchmark")
def benchmark(client_id: str, repo: Repository = Depends(get_repo)) -> dict:
    try:
        view = build_risk_view(repo, client_id, trials=1_000)
    except KeyError:
        raise HTTPException(404, "client not found")
    if view.benchmark is None:
        return {"message": "no peer data shared with this client yet", "own": view.experience.__dict__}
    return view.benchmark.__dict__
