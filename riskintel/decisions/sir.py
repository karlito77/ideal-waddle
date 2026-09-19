"""Self-insured retention decision support.

The question a client asks: "how much of my own risk should I keep?"
The answer depends on what the loss model says and what the client can
stomach. This module turns a simulation plus a risk appetite into a ranked
options table and a recommendation with reasons. Other processes (captive
feasibility, budget setting, collateral, insurer negotiation) reuse the
same options table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from pydantic import BaseModel, Field

from riskintel.modelling import RetentionOption, SimulationResult, evaluate_retention


class RiskAppetite(BaseModel):
    """What the client can absorb in a bad year."""
    max_retained_p99: float = Field(..., gt=0, description="Worst tolerable retained loss in a 1-in-100 year")
    max_expected_retained: Optional[float] = Field(None, gt=0, description="Budget for expected retained losses")
    volatility_weight: float = Field(0.5, ge=0.0, le=2.0, description="How much volatility is penalised in TCOR")
    insurer_loading: float = Field(1.35, ge=1.0, description="Loading on expected ceded loss for premium indication")
    fixed_expense: float = Field(0.0, ge=0.0, description="Fixed cost of buying cover regardless of retention")


@dataclass
class SIRDecision:
    options: list[RetentionOption]
    recommended: Optional[RetentionOption]
    reasons: list[str] = field(default_factory=list)
    rejected: dict[float, str] = field(default_factory=dict)


def recommend_sir(
    sim: SimulationResult,
    candidate_sirs: Sequence[float],
    appetite: RiskAppetite,
    aggregate_cap: Optional[float] = None,
) -> SIRDecision:
    options: list[RetentionOption] = []
    rejected: dict[float, str] = {}
    for sir in sorted(set(candidate_sirs)):
        option = evaluate_retention(
            sim,
            sir=sir,
            aggregate_cap=aggregate_cap,
            insurer_loading=appetite.insurer_loading,
            fixed_expense=appetite.fixed_expense,
            volatility_weight=appetite.volatility_weight,
        )
        options.append(option)
        if option.retained_p99 > appetite.max_retained_p99:
            rejected[sir] = (
                f"1-in-100 retained {option.retained_p99:,.0f} exceeds appetite {appetite.max_retained_p99:,.0f}"
            )
        elif appetite.max_expected_retained and option.expected_retained > appetite.max_expected_retained:
            rejected[sir] = (
                f"expected retained {option.expected_retained:,.0f} exceeds budget {appetite.max_expected_retained:,.0f}"
            )

    feasible = [o for o in options if o.sir not in rejected]
    if not feasible:
        return SIRDecision(options, None, ["no candidate retention fits the stated risk appetite"], rejected)

    best = min(feasible, key=lambda o: o.total_cost_of_risk)
    reasons = [
        f"lowest total cost of risk among feasible options ({best.total_cost_of_risk:,.0f})",
        f"expected retained {best.expected_retained:,.0f}, premium indication {best.premium_indication:,.0f}",
        f"1-in-100 retained {best.retained_p99:,.0f} within appetite {appetite.max_retained_p99:,.0f}",
    ]
    cheaper_infeasible = [o for o in options if o.sir in rejected and o.total_cost_of_risk < best.total_cost_of_risk]
    if cheaper_infeasible:
        reasons.append(
            f"{len(cheaper_infeasible)} higher retention(s) look cheaper on TCOR but breach appetite; "
            "consider an aggregate stop-loss to unlock them"
        )
    return SIRDecision(options, best, reasons, rejected)
