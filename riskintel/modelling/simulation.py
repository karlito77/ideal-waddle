"""Monte Carlo aggregate loss. Standard library only so the outline runs
anywhere; swap for numpy when volume matters."""
from __future__ import annotations

import random
from dataclasses import dataclass

from .frequency_severity import FittedModel


@dataclass
class SimulationResult:
    trials: int
    mean: float
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float
    max: float
    samples: list[list[float]]     # per-trial list of individual losses (kept for layering)


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 50:  # normal approximation for large lambda
        return max(0, int(round(rng.gauss(lam, lam ** 0.5))))
    limit, k, p = pow(2.718281828459045, -lam), 0, 1.0
    while True:
        p *= rng.random()
        if p < limit:
            return k
        k += 1


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * pct
    lo, hi = int(k), min(int(k) + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def simulate_aggregate(model: FittedModel, trials: int = 10_000, seed: int = 42) -> SimulationResult:
    rng = random.Random(seed)
    lam = model.annual_frequency * model.frequency_modifier
    samples: list[list[float]] = []
    totals: list[float] = []
    for _ in range(trials):
        n = _poisson(rng, lam)
        losses = [rng.lognormvariate(model.severity_mu, model.severity_sigma) for _ in range(n)]
        samples.append(losses)
        totals.append(sum(losses))
    ordered = sorted(totals)
    return SimulationResult(
        trials=trials,
        mean=sum(totals) / trials,
        p50=_percentile(ordered, 0.50),
        p75=_percentile(ordered, 0.75),
        p90=_percentile(ordered, 0.90),
        p95=_percentile(ordered, 0.95),
        p99=_percentile(ordered, 0.99),
        max=ordered[-1],
        samples=samples,
    )
