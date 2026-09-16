"""IoT / intelligence ingestion.

Device telemetry is high volume and low value per reading; the platform
keeps signals for a window, derives alerts against thresholds, and turns
persistent alerts into risk issues so they enter the same workflow as
everything else. Device vendor adapters (MQTT, webhook, batch) sit in
front of `ingest_signals` and only need to emit IoTSignal rows.

Longer term, presence and quality of monitoring feeds the models as a
frequency modifier (see modelling.frequency_severity.MODIFIERS).
"""
from __future__ import annotations

from dataclasses import dataclass

from riskintel.domain import IoTAlert, IoTSignal, IssueSource, RiskIssue, Severity


@dataclass(frozen=True)
class Threshold:
    metric: str
    warn: float
    critical: float
    issue_category: str
    message: str


DEFAULT_THRESHOLDS: dict[str, Threshold] = {
    "water_flow_lpm": Threshold("water_flow_lpm", 20.0, 60.0, "water.leak", "Abnormal water flow"),
    "temperature_c": Threshold("temperature_c", 45.0, 60.0, "fire.electrical", "High temperature"),
    "freeze_temperature_c": Threshold("freeze_temperature_c", -1.0, -5.0, "water.pipe_freeze", "Freeze risk"),
    "vibration_g": Threshold("vibration_g", 2.0, 5.0, "property.machinery", "Excess vibration"),
    "smoke_ppm": Threshold("smoke_ppm", 50.0, 150.0, "fire.detection", "Smoke detected"),
}


def _breaches(value: float, threshold: Threshold) -> Severity | None:
    # freeze thresholds are "lower is worse"; everything else "higher is worse"
    if threshold.metric.startswith("freeze"):
        if value <= threshold.critical:
            return Severity.CRITICAL
        if value <= threshold.warn:
            return Severity.HIGH
        return None
    if value >= threshold.critical:
        return Severity.CRITICAL
    if value >= threshold.warn:
        return Severity.HIGH
    return None


def ingest_signals(
    signals: list[IoTSignal],
    thresholds: dict[str, Threshold] | None = None,
) -> list[IoTAlert]:
    thresholds = thresholds or DEFAULT_THRESHOLDS
    alerts: list[IoTAlert] = []
    for signal in signals:
        threshold = thresholds.get(signal.metric)
        if not threshold:
            continue
        severity = _breaches(signal.value, threshold)
        if severity is None:
            continue
        alerts.append(
            IoTAlert(
                client_id=signal.client_id,
                location_id=signal.location_id,
                device_id=signal.device_id,
                metric=signal.metric,
                value=signal.value,
                threshold=threshold.critical if severity == Severity.CRITICAL else threshold.warn,
                severity=severity,
                observed_at=signal.observed_at,
                message=f"{threshold.message}: {signal.value} ({severity.value})",
            )
        )
    return alerts


def signals_to_issues(alerts: list[IoTAlert], min_repeats: int = 2) -> list[RiskIssue]:
    """Promote a repeated alert on the same device+metric into a risk issue."""
    counts: dict[tuple[str, str, str, str], list[IoTAlert]] = {}
    for alert in alerts:
        counts.setdefault((alert.client_id, alert.location_id, alert.device_id, alert.metric), []).append(alert)
    issues: list[RiskIssue] = []
    for (client_id, location_id, device_id, metric), group in counts.items():
        if len(group) < min_repeats:
            continue
        worst = max(group, key=lambda a: a.value)
        threshold = DEFAULT_THRESHOLDS.get(metric)
        issues.append(
            RiskIssue(
                client_id=client_id,
                location_id=location_id,
                source=IssueSource.IOT,
                category=threshold.issue_category if threshold else "unclassified",
                title=f"{metric} repeatedly above threshold on {device_id}",
                description=f"{len(group)} alerts, worst reading {worst.value}",
                severity=worst.severity,
                likelihood=min(1.0, 0.3 + 0.1 * len(group)),
                tags=["iot", metric],
            )
        )
    return issues
