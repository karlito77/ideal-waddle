"""Experience analytics: turn a loss run into the numbers underwriters and
risk managers actually use (frequency, severity, trended totals) and
compare them with the community pool."""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Optional, Sequence

from riskintel.community.exchange import SharedLoss
from riskintel.domain import ExposureProfile, LossEvent


@dataclass
class ExperienceSummary:
    years: list[int]
    claim_count: int
    total_incurred: float
    exposure_units: float                  # revenue in millions summed over years
    frequency_per_unit: float              # claims per exposure unit per year
    mean_severity: float
    median_severity: float
    p90_severity: float
    max_severity: float
    by_cause: dict[str, float] = field(default_factory=dict)
    by_year: dict[int, float] = field(default_factory=dict)


def trend_losses(losses: Sequence[LossEvent], to_year: int, annual_trend: float = 0.04) -> list[float]:
    """Bring historic incurred amounts to `to_year` money with a flat severity trend."""
    return [loss.incurred * (1 + annual_trend) ** (to_year - loss.exposure_year) for loss in losses]


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def summarise_experience(
    losses: Sequence[LossEvent],
    exposures: Sequence[ExposureProfile],
    to_year: Optional[int] = None,
    annual_trend: float = 0.04,
) -> ExperienceSummary:
    years = sorted({e.year for e in exposures} | {l.exposure_year for l in losses})
    to_year = to_year or (max(years) if years else 0)
    trended = trend_losses(losses, to_year, annual_trend)
    exposure_units = sum(e.revenue for e in exposures) / 1_000_000 or 1.0

    by_cause: dict[str, float] = {}
    by_year: dict[int, float] = {}
    for loss, amount in zip(losses, trended):
        by_cause[loss.cause_of_loss] = by_cause.get(loss.cause_of_loss, 0.0) + amount
        by_year[loss.exposure_year] = by_year.get(loss.exposure_year, 0.0) + amount

    return ExperienceSummary(
        years=years,
        claim_count=len(losses),
        total_incurred=sum(trended),
        exposure_units=exposure_units,
        frequency_per_unit=len(losses) / exposure_units,
        mean_severity=statistics.fmean(trended) if trended else 0.0,
        median_severity=statistics.median(trended) if trended else 0.0,
        p90_severity=_percentile(trended, 0.9),
        max_severity=max(trended) if trended else 0.0,
        by_cause=by_cause,
        by_year=by_year,
    )


@dataclass
class Benchmark:
    own_frequency: float
    pool_frequency: float
    own_mean_severity: float
    pool_mean_severity: float
    pool_claim_count: int
    pool_members: int
    credibility: float            # weight on own experience, 0..1
    blended_frequency: float
    blended_mean_severity: float
    top_pool_causes: list[tuple[str, float]]


def benchmark_against_pool(
    own: ExperienceSummary,
    pool: Sequence[SharedLoss],
    pool_exposure_units: float,
    credibility_k: float = 25.0,
) -> Benchmark:
    """Compare own experience with the pooled cohort and blend with limited
    fluctuation credibility Z = n / (n + k)."""
    pool_amounts = [s.incurred for s in pool]
    pool_freq = len(pool) / pool_exposure_units if pool_exposure_units else 0.0
    pool_sev = statistics.fmean(pool_amounts) if pool_amounts else own.mean_severity
    z = own.claim_count / (own.claim_count + credibility_k) if pool else 1.0

    by_cause: dict[str, float] = {}
    for s in pool:
        by_cause[s.cause_of_loss] = by_cause.get(s.cause_of_loss, 0.0) + s.incurred
    top = sorted(by_cause.items(), key=lambda kv: kv[1], reverse=True)[:5]

    return Benchmark(
        own_frequency=own.frequency_per_unit,
        pool_frequency=pool_freq,
        own_mean_severity=own.mean_severity,
        pool_mean_severity=pool_sev,
        pool_claim_count=len(pool),
        pool_members=len({s.owner_token for s in pool}),
        credibility=round(z, 3),
        blended_frequency=z * own.frequency_per_unit + (1 - z) * pool_freq,
        blended_mean_severity=z * own.mean_severity + (1 - z) * pool_sev,
        top_pool_causes=top,
    )
