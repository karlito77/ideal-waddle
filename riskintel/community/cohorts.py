"""Peer cohorts.

A client's peers are other community members that look like it on the
dimensions that drive loss experience: where they operate, what they do,
and how big they are. Similarity is a weighted score; callers choose a
threshold. Cohorts are recomputed on demand (cheap at community scale).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from riskintel.domain import Client


@dataclass(frozen=True)
class PeerMatch:
    peer_id: str
    score: float
    shares_community: bool
    location_overlap: bool
    activity_match_depth: int   # number of leading activity-code characters in common
    size_ratio: float           # peer revenue / client revenue, clipped to [0.1, 10]


def _activity_depth(a: str, b: str) -> int:
    depth = 0
    for x, y in zip(a, b):
        if x != y:
            break
        depth += 1
    return depth


def similarity(client: Client, peer: Client) -> PeerMatch:
    shares_community = bool(set(client.community_ids) & set(peer.community_ids))
    location_overlap = bool(client.regions & peer.regions)
    depth = _activity_depth(client.activity_code, peer.activity_code)
    max_depth = max(len(client.activity_code), 1)
    size_ratio = max(0.1, min(10.0, (peer.annual_revenue or 1.0) / (client.annual_revenue or 1.0)))
    size_score = 1.0 - min(1.0, abs(math.log10(size_ratio)))   # 1.0 at equal size, 0 at 10x

    score = 0.45 * (depth / max_depth) + 0.35 * (1.0 if location_overlap else 0.0) + 0.20 * size_score
    return PeerMatch(
        peer_id=peer.id,
        score=round(score, 3),
        shares_community=shares_community,
        location_overlap=location_overlap,
        activity_match_depth=depth,
        size_ratio=size_ratio,
    )


def find_peers(client: Client, candidates: list[Client], min_score: float = 0.4) -> list[PeerMatch]:
    matches = [
        similarity(client, other)
        for other in candidates
        if other.id != client.id
    ]
    matches = [m for m in matches if m.shares_community and m.score >= min_score]
    return sorted(matches, key=lambda m: m.score, reverse=True)
