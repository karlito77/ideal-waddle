"""Loss development. Open claims grow; a chain-ladder on an incurred
triangle gives the factors to bring immature years to ultimate."""
from __future__ import annotations

from datetime import date
from typing import Sequence

from riskintel.domain import LossEvent


def incurred_triangle(losses: Sequence[LossEvent], as_at: date) -> dict[int, list[float]]:
    """Cumulative incurred by origin year and development year (0 = same year).

    The outline lacks transaction history, so each loss is placed at its
    report lag and carried forward. With real payment/reserve transactions
    this becomes a true cumulative triangle.
    """
    years = sorted({l.exposure_year for l in losses})
    if not years:
        return {}
    triangle: dict[int, list[float]] = {}
    for origin in years:
        max_dev = as_at.year - origin
        row = [0.0] * (max_dev + 1)
        for loss in losses:
            if loss.exposure_year != origin:
                continue
            lag = ((loss.report_date or loss.occurrence_date).year - origin)
            lag = max(0, min(lag, max_dev))
            for dev in range(lag, max_dev + 1):
                row[dev] += loss.incurred
        triangle[origin] = row
    return triangle


def chain_ladder(triangle: dict[int, list[float]]) -> tuple[list[float], dict[int, float]]:
    """Return (age-to-age factors, ultimate by origin year)."""
    if not triangle:
        return [], {}
    max_dev = max(len(row) for row in triangle.values())
    factors: list[float] = []
    for dev in range(max_dev - 1):
        num = sum(row[dev + 1] for row in triangle.values() if len(row) > dev + 1)
        den = sum(row[dev] for row in triangle.values() if len(row) > dev + 1)
        factors.append(num / den if den else 1.0)
    ultimates: dict[int, float] = {}
    for origin, row in triangle.items():
        latest = row[-1]
        for f in factors[len(row) - 1:]:
            latest *= f
        ultimates[origin] = latest
    return factors, ultimates
