"""Frequency / severity model.

Frequency ~ Poisson(lambda) per year, severity ~ LogNormal(mu, sigma).
Parameters come from the client's own trended experience blended with the
community pool via credibility. Risk issues and IoT monitoring act as
multiplicative modifiers on frequency, which is how the community's
qualitative intelligence feeds the quantitative model.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Optional, Sequence

from riskintel.analytics.experience import Benchmark, ExperienceSummary
from riskintel.domain import IssueStatus, RiskIssue, Severity


@dataclass
class FittedModel:
    annual_frequency: float        # expected claims per year
    severity_mu: float
    severity_sigma: float
    basis: str                     # human-readable note on what drove the parameters
    frequency_modifier: float = 1.0
    modifiers_applied: list[str] = field(default_factory=list)

    @property
    def expected_severity(self) -> float:
        return math.exp(self.severity_mu + 0.5 * self.severity_sigma ** 2)

    @property
    def expected_annual_loss(self) -> float:
        return self.annual_frequency * self.frequency_modifier * self.expected_severity


def _lognormal_params(amounts: Sequence[float]) -> tuple[float, float]:
    positive = [a for a in amounts if a > 0]
    if len(positive) < 2:
        # nothing to fit: fall back to a wide, moderate prior
        return math.log(positive[0]) if positive else math.log(10_000.0), 1.0
    logs = [math.log(a) for a in positive]
    return statistics.fmean(logs), max(statistics.pstdev(logs), 0.3)


def fit_frequency_severity(
    own: ExperienceSummary,
    trended_amounts: Sequence[float],
    benchmark: Optional[Benchmark] = None,
    next_year_exposure_units: Optional[float] = None,
) -> FittedModel:
    n_years = max(len(own.years), 1)
    exposure_next = next_year_exposure_units or (own.exposure_units / n_years)
    mu, sigma = _lognormal_params(trended_amounts)

    if benchmark and benchmark.pool_claim_count:
        freq_per_unit = benchmark.blended_frequency
        # Blend severity by shifting mu so the lognormal mean hits the blended mean
        target_mean = benchmark.blended_mean_severity
        if target_mean > 0:
            mu = math.log(target_mean) - 0.5 * sigma ** 2
        basis = f"credibility {benchmark.credibility:.2f} own / {1 - benchmark.credibility:.2f} pool"
    else:
        freq_per_unit = own.frequency_per_unit
        basis = "own experience only"

    return FittedModel(
        annual_frequency=freq_per_unit * exposure_next,
        severity_mu=mu,
        severity_sigma=sigma,
        basis=basis,
    )


# Frequency modifiers. Positive = worse. Keys are taxonomy prefixes so an
# open "water.leak" issue matches "water". Values are illustrative.
MODIFIERS: dict[str, float] = {
    "fire": 0.10,
    "water": 0.08,
    "injury": 0.06,
    "cyber": 0.12,
    "liability": 0.05,
    "property": 0.04,
}
IOT_MONITORING_CREDIT = -0.07   # per monitored category with active devices, capped below


def apply_modifiers(
    model: FittedModel,
    issues: Sequence[RiskIssue],
    monitored_categories: Sequence[str] = (),
) -> FittedModel:
    modifier = 1.0
    notes: list[str] = []
    seen: set[str] = set()
    for issue in issues:
        if issue.status in (IssueStatus.CLOSED,):
            continue
        prefix = issue.category.split(".")[0]
        if prefix in seen or prefix not in MODIFIERS:
            continue
        seen.add(prefix)
        weight = MODIFIERS[prefix] * (1.5 if issue.severity in (Severity.HIGH, Severity.CRITICAL) else 1.0)
        modifier *= 1 + weight
        notes.append(f"+{weight:.0%} open {prefix} issue")
    for category in set(monitored_categories):
        prefix = category.split(".")[0]
        if prefix in MODIFIERS:
            modifier *= 1 + IOT_MONITORING_CREDIT
            notes.append(f"{IOT_MONITORING_CREDIT:.0%} IoT monitoring on {prefix}")
    modifier = max(0.6, min(modifier, 1.8))
    return FittedModel(
        annual_frequency=model.annual_frequency,
        severity_mu=model.severity_mu,
        severity_sigma=model.severity_sigma,
        basis=model.basis,
        frequency_modifier=round(modifier, 4),
        modifiers_applied=notes,
    )
