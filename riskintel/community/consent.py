"""Consent rules.

Sharing is opt-in per client, per data scope. A consent names an audience
(location cohort, activity cohort, whole community) and an anonymisation
level. The exchange layer never reads a client's data for another client
without an active consent that covers the relationship.
"""
from __future__ import annotations

from typing import Optional

from riskintel.domain import Audience, SharingConsent, SharingScope

from .cohorts import PeerMatch


def effective_consent(consents: list[SharingConsent], scope: SharingScope) -> Optional[SharingConsent]:
    """Latest active consent for a scope, or None."""
    active = [c for c in consents if c.scope == scope and c.active]
    if not active:
        return None
    return max(active, key=lambda c: c.granted_at)


def can_share(consent: Optional[SharingConsent], match: PeerMatch) -> bool:
    """Does `consent` (owned by the data owner) permit sharing with `match`?"""
    if consent is None or not consent.active:
        return False
    if consent.audience == Audience.COMMUNITY:
        return match.shares_community
    if consent.audience == Audience.COHORT_LOCATION:
        return match.shares_community and match.location_overlap
    if consent.audience == Audience.COHORT_ACTIVITY:
        return match.shares_community and match.activity_match_depth >= 2
    return False
