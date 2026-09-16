from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from riskintel.api.deps import get_repo
from riskintel.domain import LineOfBusiness
from riskintel.pipeline import build_risk_view
from riskintel.storage import Repository

router = APIRouter(prefix="/models", tags=["modelling"])


@router.post("/{client_id}/fit")
def fit(
    client_id: str,
    line_of_business: Optional[LineOfBusiness] = None,
    trials: int = 10_000,
    repo: Repository = Depends(get_repo),
) -> dict:
    try:
        view = build_risk_view(repo, client_id, line_of_business, trials=trials)
    except KeyError:
        raise HTTPException(404, "client not found")
    sim = view.simulation
    return {
        "model": {
            "annual_frequency": view.model.annual_frequency,
            "frequency_modifier": view.model.frequency_modifier,
            "modifiers_applied": view.model.modifiers_applied,
            "severity_mu": view.model.severity_mu,
            "severity_sigma": view.model.severity_sigma,
            "expected_severity": view.model.expected_severity,
            "expected_annual_loss": view.model.expected_annual_loss,
            "basis": view.model.basis,
        },
        "simulation": {
            "trials": sim.trials, "mean": sim.mean, "p50": sim.p50, "p75": sim.p75,
            "p90": sim.p90, "p95": sim.p95, "p99": sim.p99, "max": sim.max,
        },
    }
