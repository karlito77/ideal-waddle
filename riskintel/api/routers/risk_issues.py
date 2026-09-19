from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from riskintel.api.deps import get_repo
from riskintel.community import find_peers, share_issues
from riskintel.community.exchange import adopt_issue
from riskintel.domain import RiskIssue
from riskintel.ingestion import RiskIssueIn, ingest_risk_issue
from riskintel.storage import Repository

router = APIRouter(prefix="/risk-issues", tags=["risk issues"])


@router.post("", response_model=RiskIssue, status_code=201)
def create_issue(issue_in: RiskIssueIn, repo: Repository = Depends(get_repo)) -> RiskIssue:
    return repo.add_issue(ingest_risk_issue(issue_in))


@router.get("/{client_id}", response_model=list[RiskIssue])
def list_issues(client_id: str, repo: Repository = Depends(get_repo)) -> list[RiskIssue]:
    return sorted(repo.issues_for(client_id), key=lambda i: i.score, reverse=True)


@router.get("/{client_id}/peer")
def peer_issues(client_id: str, repo: Repository = Depends(get_repo)) -> list[dict]:
    client = repo.get_client(client_id)
    if client is None:
        raise HTTPException(404, "client not found")
    peers = find_peers(client, repo.list_clients())
    return [s.__dict__ for s in share_issues(repo, client_id, peers)]


@router.post("/{client_id}/adopt/{origin_issue_id}", response_model=RiskIssue, status_code=201)
def adopt(client_id: str, origin_issue_id: str, repo: Repository = Depends(get_repo)) -> RiskIssue:
    client = repo.get_client(client_id)
    if client is None:
        raise HTTPException(404, "client not found")
    peers = find_peers(client, repo.list_clients())
    for shared in share_issues(repo, client_id, peers):
        if shared.origin_issue_id == origin_issue_id:
            return repo.add_issue(adopt_issue(shared, client_id))
    raise HTTPException(404, "issue not shared with this client")
