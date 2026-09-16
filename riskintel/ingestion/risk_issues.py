"""Risk issue ingestion.

Issues arrive from the client's own risk register, from assessor visits,
from peers (via the community exchange) and from IoT / model outputs. All
land in the same RiskIssue shape so they can be scored and compared.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from riskintel.domain import IssueSource, RiskIssue, Severity

# Category taxonomy is hierarchical with dot separators so analytics can roll up.
ISSUE_TAXONOMY: dict[str, str] = {
    "hot work": "fire.hot_work",
    "electrical": "fire.electrical",
    "sprinkler": "fire.protection",
    "freeze": "water.pipe_freeze",
    "leak": "water.leak",
    "roof": "property.roof",
    "housekeeping": "property.housekeeping",
    "forklift": "injury.vehicle",
    "ladder": "injury.working_at_height",
    "lifting": "injury.manual_handling",
    "backup": "cyber.backup",
    "mfa": "cyber.access_control",
    "contractor": "liability.contractor_management",
}


class RiskIssueIn(BaseModel):
    client_id: str
    location_id: Optional[str] = None
    source: IssueSource = IssueSource.OWN
    category: Optional[str] = None       # explicit taxonomy node if known
    title: str
    description: str = ""
    severity: Severity = Severity.MEDIUM
    likelihood: float = Field(0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)


def map_category(text: str) -> str:
    lowered = text.lower()
    for key, node in ISSUE_TAXONOMY.items():
        if key in lowered:
            return node
    return "unclassified"


def ingest_risk_issue(issue_in: RiskIssueIn) -> RiskIssue:
    category = issue_in.category or map_category(f"{issue_in.title} {issue_in.description}")
    return RiskIssue(
        client_id=issue_in.client_id,
        location_id=issue_in.location_id,
        source=issue_in.source,
        category=category,
        title=issue_in.title,
        description=issue_in.description,
        severity=issue_in.severity,
        likelihood=issue_in.likelihood,
        tags=issue_in.tags,
    )
