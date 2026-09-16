"""Experience exchange.

Builds the pooled dataset a client is allowed to see. For every peer the
exchange checks the *peer's* consent (the data owner decides), then applies
the anonymisation the peer chose before the record leaves their boundary.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from riskintel.domain import (
    AnonymisationLevel,
    LineOfBusiness,
    LossEvent,
    RiskIssue,
    SharingScope,
)
from riskintel.storage import Repository

from .cohorts import PeerMatch
from .consent import can_share, effective_consent

AMOUNT_BANDS = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]


@dataclass(frozen=True)
class SharedLoss:
    owner_token: str                 # pseudonym or "aggregated"
    line_of_business: LineOfBusiness
    cause_of_loss: str
    exposure_year: int
    incurred: float                  # exact or banded midpoint depending on anonymisation
    banded: bool


@dataclass(frozen=True)
class SharedIssue:
    owner_token: str
    origin_issue_id: str
    category: str
    title: str
    severity: str
    likelihood: float


def pseudonym(client_id: str, salt: str = "riskintel") -> str:
    return hashlib.sha256(f"{salt}:{client_id}".encode()).hexdigest()[:12]


def band_amount(amount: float) -> float:
    """Return the midpoint of the band containing `amount`."""
    lower = 0.0
    for upper in AMOUNT_BANDS:
        if amount < upper:
            return (lower + upper) / 2
        lower = float(upper)
    return lower * 1.5


def _anonymise_loss(loss: LossEvent, level: AnonymisationLevel) -> SharedLoss:
    if level == AnonymisationLevel.IDENTIFIED:
        return SharedLoss(loss.client_id, loss.line_of_business, loss.cause_of_loss, loss.exposure_year, loss.incurred, False)
    if level == AnonymisationLevel.PSEUDONYMISED:
        return SharedLoss(pseudonym(loss.client_id), loss.line_of_business, loss.cause_of_loss, loss.exposure_year, loss.incurred, False)
    return SharedLoss("aggregated", loss.line_of_business, loss.cause_of_loss, loss.exposure_year, band_amount(loss.incurred), True)


def pool_experience(
    repo: Repository,
    requester_id: str,
    peers: list[PeerMatch],
    line_of_business: Optional[LineOfBusiness] = None,
) -> list[SharedLoss]:
    pooled: list[SharedLoss] = []
    for match in peers:
        consent = effective_consent(repo.consents_for(match.peer_id), SharingScope.LOSS_HISTORY)
        if not can_share(consent, match):
            continue
        assert consent is not None
        for loss in repo.losses_for(match.peer_id):
            if line_of_business and loss.line_of_business != line_of_business:
                continue
            pooled.append(_anonymise_loss(loss, consent.anonymisation))
    return pooled


def share_issues(repo: Repository, requester_id: str, peers: list[PeerMatch]) -> list[SharedIssue]:
    """Open risk issues peers have agreed to share, so a client can learn from them."""
    shared: list[SharedIssue] = []
    for match in peers:
        consent = effective_consent(repo.consents_for(match.peer_id), SharingScope.RISK_ISSUES)
        if not can_share(consent, match):
            continue
        assert consent is not None
        token = match.peer_id if consent.anonymisation == AnonymisationLevel.IDENTIFIED else pseudonym(match.peer_id)
        for issue in repo.issues_for(match.peer_id):
            if issue.origin_issue_id:      # don't re-share something that was itself shared in
                continue
            shared.append(SharedIssue(token, issue.id, issue.category, issue.title, issue.severity.value, issue.likelihood))
    return shared


def adopt_issue(shared: SharedIssue, client_id: str) -> RiskIssue:
    """Copy a peer's issue into the client's own register as a PEER-sourced issue."""
    from riskintel.domain import IssueSource, Severity
    return RiskIssue(
        client_id=client_id,
        source=IssueSource.PEER,
        category=shared.category,
        title=shared.title,
        description=f"Adopted from peer {shared.owner_token}",
        severity=Severity(shared.severity),
        likelihood=shared.likelihood,
        origin_issue_id=shared.origin_issue_id,
        tags=["peer"],
    )
