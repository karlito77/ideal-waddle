"""End-to-end pipeline for one client: experience -> peers -> pooled data
-> benchmark -> fitted model -> simulation -> SIR options.

This is the spine of the platform. Everything else (API, batch jobs,
reports) calls into here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

from riskintel.analytics import Benchmark, ExperienceSummary, benchmark_against_pool, summarise_experience, trend_losses
from riskintel.community import PeerMatch, find_peers, pool_experience
from riskintel.decisions import RiskAppetite, SIRDecision, recommend_sir
from riskintel.domain import LineOfBusiness
from riskintel.modelling import FittedModel, SimulationResult, apply_modifiers, fit_frequency_severity, simulate_aggregate
from riskintel.storage import Repository


@dataclass
class ClientRiskView:
    client_id: str
    experience: ExperienceSummary
    peers: list[PeerMatch]
    benchmark: Optional[Benchmark]
    model: FittedModel
    simulation: SimulationResult


def build_risk_view(
    repo: Repository,
    client_id: str,
    line_of_business: Optional[LineOfBusiness] = None,
    as_at: Optional[date] = None,
    trials: int = 10_000,
    seed: int = 42,
) -> ClientRiskView:
    client = repo.get_client(client_id)
    if client is None:
        raise KeyError(f"unknown client {client_id}")
    as_at = as_at or date.today()

    losses = repo.losses_for(client_id)
    if line_of_business:
        losses = [l for l in losses if l.line_of_business == line_of_business]
    exposures = repo.exposures_for(client_id)
    experience = summarise_experience(losses, exposures, to_year=as_at.year)
    trended = trend_losses(losses, as_at.year)

    peers = find_peers(client, repo.list_clients())
    pool = pool_experience(repo, client_id, peers, line_of_business)
    benchmark = None
    if pool:
        pool_units = sum(
            sum(e.revenue for e in repo.exposures_for(p.peer_id)) for p in peers
        ) / 1_000_000 or 1.0
        benchmark = benchmark_against_pool(experience, pool, pool_units)

    model = fit_frequency_severity(experience, trended, benchmark)
    monitored = sorted({a.metric for a in repo.alerts_for(client_id)})
    monitored_categories = [_metric_category(m) for m in monitored]
    model = apply_modifiers(model, repo.issues_for(client_id), monitored_categories)

    simulation = simulate_aggregate(model, trials=trials, seed=seed)
    return ClientRiskView(client_id, experience, peers, benchmark, model, simulation)


def _metric_category(metric: str) -> str:
    from riskintel.ingestion.iot import DEFAULT_THRESHOLDS
    threshold = DEFAULT_THRESHOLDS.get(metric)
    return threshold.issue_category if threshold else "unclassified"


def sir_decision(
    view: ClientRiskView,
    candidate_sirs: Sequence[float],
    appetite: RiskAppetite,
    aggregate_cap: Optional[float] = None,
) -> SIRDecision:
    return recommend_sir(view.simulation, candidate_sirs, appetite, aggregate_cap)
