"""Retention layering. Given simulated ground-up losses, split each trial
into retained (below the per-occurrence SIR, capped by an aggregate) and
ceded, and cost the ceded layer with a simple premium indication."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .simulation import SimulationResult, _percentile


@dataclass
class RetentionOption:
    sir: float
    aggregate_cap: Optional[float]
    expected_retained: float
    retained_p90: float
    retained_p95: float
    retained_p99: float
    expected_ceded: float
    premium_indication: float
    total_cost_of_risk: float
    volatility_charge: float


def evaluate_retention(
    sim: SimulationResult,
    sir: float,
    aggregate_cap: Optional[float] = None,
    insurer_loading: float = 1.35,
    fixed_expense: float = 0.0,
    volatility_weight: float = 0.5,
) -> RetentionOption:
    """Price a retention. Premium = loaded expected ceded + expense.
    TCOR = expected retained + premium + volatility charge, where the
    volatility charge penalises how far the P95 retained sits above the mean."""
    retained_totals: list[float] = []
    ceded_totals: list[float] = []
    for losses in sim.samples:
        retained = sum(min(x, sir) for x in losses)
        ceded = sum(max(x - sir, 0.0) for x in losses)
        if aggregate_cap is not None and retained > aggregate_cap:
            ceded += retained - aggregate_cap
            retained = aggregate_cap
        retained_totals.append(retained)
        ceded_totals.append(ceded)
    n = len(retained_totals) or 1
    exp_ret = sum(retained_totals) / n
    exp_ced = sum(ceded_totals) / n
    ordered = sorted(retained_totals)
    p95 = _percentile(ordered, 0.95)
    premium = exp_ced * insurer_loading + fixed_expense
    volatility = volatility_weight * max(p95 - exp_ret, 0.0)
    return RetentionOption(
        sir=sir,
        aggregate_cap=aggregate_cap,
        expected_retained=exp_ret,
        retained_p90=_percentile(ordered, 0.90),
        retained_p95=p95,
        retained_p99=_percentile(ordered, 0.99),
        expected_ceded=exp_ced,
        premium_indication=premium,
        total_cost_of_risk=exp_ret + premium + volatility,
        volatility_charge=volatility,
    )
