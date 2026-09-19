from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from riskintel.api.deps import get_repo
from riskintel.decisions import RiskAppetite
from riskintel.domain import LineOfBusiness
from riskintel.pipeline import build_risk_view, sir_decision
from riskintel.storage import Repository

router = APIRouter(prefix="/decisions", tags=["decisions"])


class SIRRequest(BaseModel):
    candidate_sirs: list[float] = Field(..., min_length=1)
    appetite: RiskAppetite
    aggregate_cap: Optional[float] = None
    line_of_business: Optional[LineOfBusiness] = None
    trials: int = Field(10_000, ge=100, le=200_000)


@router.post("/{client_id}/sir")
def sir(client_id: str, request: SIRRequest, repo: Repository = Depends(get_repo)) -> dict:
    try:
        view = build_risk_view(repo, client_id, request.line_of_business, trials=request.trials)
    except KeyError:
        raise HTTPException(404, "client not found")
    decision = sir_decision(view, request.candidate_sirs, request.appetite, request.aggregate_cap)
    return {
        "recommended_sir": decision.recommended.sir if decision.recommended else None,
        "reasons": decision.reasons,
        "rejected": {str(k): v for k, v in decision.rejected.items()},
        "options": [o.__dict__ for o in decision.options],
        "model_basis": view.model.basis,
    }
