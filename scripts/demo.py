"""Run the whole pipeline on the sample community and print the SIR options table.

    python scripts/demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from riskintel.community import find_peers, share_issues
from riskintel.decisions import RiskAppetite
from riskintel.demo import NORTHWIND, seed_repository
from riskintel.pipeline import build_risk_view, sir_decision


def main() -> None:
    repo = seed_repository()
    client = repo.get_client(NORTHWIND)
    assert client
    view = build_risk_view(repo, NORTHWIND, trials=20_000)

    ex = view.experience
    print(f"== {client.name} ==")
    print(f"claims {ex.claim_count} over {ex.years[0]}-{ex.years[-1]}, trended incurred {ex.total_incurred:,.0f}")
    print(f"frequency {ex.frequency_per_unit:.3f} per $1m revenue, mean severity {ex.mean_severity:,.0f}, p90 {ex.p90_severity:,.0f}")

    print("\n== peers ==")
    for m in view.peers:
        print(f"  {m.peer_id:10s} score {m.score:.2f} location={m.location_overlap} activity_depth={m.activity_match_depth}")
    if view.benchmark:
        b = view.benchmark
        print(f"\n== benchmark == pool {b.pool_claim_count} claims from {b.pool_members} member(s); credibility on own {b.credibility}")
        print(f"  frequency own {b.own_frequency:.3f} vs pool {b.pool_frequency:.3f} -> blended {b.blended_frequency:.3f}")
        print(f"  severity  own {b.own_mean_severity:,.0f} vs pool {b.pool_mean_severity:,.0f} -> blended {b.blended_mean_severity:,.0f}")

    print("\n== shared peer issues ==")
    for s in share_issues(repo, NORTHWIND, find_peers(client, repo.list_clients())):
        print(f"  [{s.severity}] {s.title} (from {s.owner_token})")

    m = view.model
    print(f"\n== model == {m.basis}")
    print(f"  annual frequency {m.annual_frequency:.2f} x modifier {m.frequency_modifier} ({', '.join(m.modifiers_applied) or 'none'})")
    print(f"  expected severity {m.expected_severity:,.0f}, expected annual loss {m.expected_annual_loss:,.0f}")
    s = view.simulation
    print(f"  aggregate: mean {s.mean:,.0f} p50 {s.p50:,.0f} p90 {s.p90:,.0f} p95 {s.p95:,.0f} p99 {s.p99:,.0f}")

    appetite = RiskAppetite(max_retained_p99=250_000, volatility_weight=0.5)
    decision = sir_decision(view, [25_000, 50_000, 100_000, 250_000, 500_000], appetite)
    print(f"\n== SIR options (appetite: 1-in-100 retained <= {appetite.max_retained_p99:,.0f}) ==")
    print(f"  {'SIR':>9} {'E[ret]':>10} {'P95 ret':>10} {'P99 ret':>10} {'premium':>10} {'TCOR':>10}  status")
    for o in decision.options:
        status = decision.rejected.get(o.sir, "recommended" if decision.recommended and o.sir == decision.recommended.sir else "feasible")
        print(f"  {o.sir:>9,.0f} {o.expected_retained:>10,.0f} {o.retained_p95:>10,.0f} {o.retained_p99:>10,.0f} "
              f"{o.premium_indication:>10,.0f} {o.total_cost_of_risk:>10,.0f}  {status}")
    print("\nreasons:")
    for r in decision.reasons:
        print(f"  - {r}")


if __name__ == "__main__":
    main()
