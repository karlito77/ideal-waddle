from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from riskintel.api.deps import get_repo
from riskintel.domain import IoTAlert, IoTSignal
from riskintel.ingestion import ingest_signals, signals_to_issues
from riskintel.storage import Repository

router = APIRouter(prefix="/iot", tags=["iot"])


class SignalIngestResponse(BaseModel):
    signals: int
    alerts: int
    issues_raised: int


@router.post("/signals", response_model=SignalIngestResponse, status_code=201)
def post_signals(signals: list[IoTSignal], repo: Repository = Depends(get_repo)) -> SignalIngestResponse:
    repo.add_signals(signals)
    alerts = ingest_signals(signals)
    repo.add_alerts(alerts)
    issues = 0
    for client_id in {a.client_id for a in alerts}:
        for issue in signals_to_issues(repo.alerts_for(client_id)):
            existing = {i.title for i in repo.issues_for(client_id)}
            if issue.title not in existing:
                repo.add_issue(issue)
                issues += 1
    return SignalIngestResponse(signals=len(signals), alerts=len(alerts), issues_raised=issues)


@router.get("/{client_id}/alerts", response_model=list[IoTAlert])
def alerts(client_id: str, repo: Repository = Depends(get_repo)) -> list[IoTAlert]:
    return repo.alerts_for(client_id)
