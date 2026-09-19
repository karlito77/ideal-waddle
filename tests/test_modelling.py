import math
from datetime import date

from riskintel.analytics import chain_ladder, incurred_triangle, summarise_experience, trend_losses
from riskintel.decisions import RiskAppetite, recommend_sir
from riskintel.demo import NORTHWIND
from riskintel.modelling import FittedModel, evaluate_retention, simulate_aggregate
from riskintel.pipeline import build_risk_view, sir_decision


def test_experience_summary(repo):
    losses = repo.losses_for(NORTHWIND)
    summary = summarise_experience(losses, repo.exposures_for(NORTHWIND), to_year=2025)
    assert summary.claim_count == len(losses) > 0
    assert summary.total_incurred > sum(l.incurred for l in losses)      # trend inflates older years
    assert math.isclose(summary.total_incurred, sum(trend_losses(losses, 2025)))
    assert summary.frequency_per_unit > 0


def test_chain_ladder_basic():
    tri = {2022: [100.0, 150.0, 165.0], 2023: [120.0, 180.0], 2024: [90.0]}
    factors, ult = chain_ladder(tri)
    assert math.isclose(factors[0], (150 + 180) / (100 + 120))
    assert math.isclose(factors[1], 165 / 150)
    assert math.isclose(ult[2024], 90 * factors[0] * factors[1])
    assert ult[2022] == 165.0


def test_triangle_from_losses(repo):
    tri = incurred_triangle(repo.losses_for(NORTHWIND), date(2025, 12, 31))
    assert set(tri) == {2021, 2022, 2023, 2024, 2025}
    assert len(tri[2021]) == 5 and len(tri[2025]) == 1
    assert all(a <= b for row in tri.values() for a, b in zip(row, row[1:]))   # cumulative


def test_simulation_moments():
    model = FittedModel(annual_frequency=5.0, severity_mu=9.0, severity_sigma=1.0, basis="test")
    sim = simulate_aggregate(model, trials=20_000, seed=1)
    assert abs(sim.mean - model.expected_annual_loss) / model.expected_annual_loss < 0.05
    assert sim.p50 <= sim.p90 <= sim.p95 <= sim.p99 <= sim.max
    assert simulate_aggregate(model, trials=500, seed=3).mean == simulate_aggregate(model, trials=500, seed=3).mean


def test_retention_layering_conserves_loss():
    model = FittedModel(annual_frequency=4.0, severity_mu=10.0, severity_sigma=1.2, basis="test")
    sim = simulate_aggregate(model, trials=5_000, seed=5)
    low, high = evaluate_retention(sim, 10_000), evaluate_retention(sim, 500_000)
    assert math.isclose(low.expected_retained + low.expected_ceded, sim.mean, rel_tol=1e-9)
    assert high.expected_retained > low.expected_retained
    assert high.expected_ceded < low.expected_ceded
    capped = evaluate_retention(sim, 500_000, aggregate_cap=200_000)
    assert capped.retained_p99 <= 200_000


def test_recommendation_respects_appetite():
    model = FittedModel(annual_frequency=6.0, severity_mu=10.5, severity_sigma=1.3, basis="test")
    sim = simulate_aggregate(model, trials=5_000, seed=11)
    decision = recommend_sir(sim, [10_000, 100_000, 1_000_000], RiskAppetite(max_retained_p99=800_000))
    assert decision.recommended is not None
    assert decision.recommended.retained_p99 <= 800_000
    assert 1_000_000 in decision.rejected
    impossible = recommend_sir(sim, [1_000_000], RiskAppetite(max_retained_p99=1.0))
    assert impossible.recommended is None and impossible.rejected


def test_pipeline_end_to_end(repo):
    view = build_risk_view(repo, NORTHWIND, trials=2_000)
    assert view.benchmark is not None and view.benchmark.pool_claim_count > 0
    assert "credibility" in view.model.basis
    assert view.model.frequency_modifier != 1.0         # open issues + water monitoring both apply
    assert any("fire" in n for n in view.model.modifiers_applied)
    assert any("IoT" in n for n in view.model.modifiers_applied)
    decision = sir_decision(view, [50_000, 250_000], RiskAppetite(max_retained_p99=5_000_000))
    assert decision.recommended is not None
