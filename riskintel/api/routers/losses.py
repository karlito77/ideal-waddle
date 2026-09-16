from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from riskintel.analytics import chain_ladder, incurred_triangle, summarise_experience
from riskintel.api.deps import get_repo
from riskintel.domain import LossEvent
from riskintel.ingestion import LossRecordIn, ingest_loss_records
from riskintel.storage import Repository

router = APIRouter(prefix="/losses", tags=["loss history"])


class IngestResponse(BaseModel):
    accepted: int
    warnings: list[str]


@router.post("", response_model=IngestResponse, status_code=201)
def ingest(records: list[LossRecordIn], repo: Repository = Depends(get_repo)) -> IngestResponse:
    accepted = 0
    warnings: list[str] = []
    by_client: dict[str, list[LossRecordIn]] = {}
    for rec in records:
        by_client.setdefault(rec.client_id, []).append(rec)
    for client_id, recs in by_client.items():
        events, w = ingest_loss_records(recs, existing=repo.losses_for(client_id))
        repo.add_losses(events)
        accepted += len(events)
        warnings.extend(w)
    return IngestResponse(accepted=accepted, warnings=warnings)


@router.get("/{client_id}", response_model=list[LossEvent])
def list_losses(client_id: str, repo: Repository = Depends(get_repo)) -> list[LossEvent]:
    return repo.losses_for(client_id)


@router.get("/{client_id}/experience")
def experience(client_id: str, repo: Repository = Depends(get_repo)) -> dict:
    summary = summarise_experience(repo.losses_for(client_id), repo.exposures_for(client_id))
    return summary.__dict__


@router.get("/{client_id}/development")
def development(client_id: str, repo: Repository = Depends(get_repo)) -> dict:
    triangle = incurred_triangle(repo.losses_for(client_id), date.today())
    factors, ultimates = chain_ladder(triangle)
    return {"triangle": triangle, "factors": factors, "ultimates": ultimates}
