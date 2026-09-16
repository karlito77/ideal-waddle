from datetime import date, datetime

import pytest
from pydantic import ValidationError

from riskintel.domain import IoTSignal, LineOfBusiness, LossEvent, LossStatus, Severity
from riskintel.ingestion import LossRecordIn, RiskIssueIn, ingest_loss_records, ingest_risk_issue, ingest_signals, signals_to_issues
from riskintel.ingestion.loss_history import map_cause


def test_cause_mapping():
    assert map_cause("Escape of water from roof tank") == "water"
    assert map_cause("Forklift collision with racking") == "auto.collision"
    assert map_cause("something odd") == "unclassified"


def test_duplicate_claim_reference_skipped():
    rec = LossRecordIn(client_id="c", claim_reference="X1", line_of_business=LineOfBusiness.PROPERTY,
                       cause_of_loss="fire", occurrence_date=date(2024, 1, 1), paid=100)
    events, warnings = ingest_loss_records([rec, rec])
    assert len(events) == 1
    assert "duplicate" in warnings[0]
    again, warnings2 = ingest_loss_records([rec], existing=events)
    assert again == [] and warnings2


def test_closed_claim_reserve_zeroed():
    rec = LossRecordIn(client_id="c", line_of_business=LineOfBusiness.PROPERTY, cause_of_loss="fire",
                       occurrence_date=date(2024, 1, 1), paid=100, reserved=50, status=LossStatus.CLOSED)
    events, warnings = ingest_loss_records([rec])
    assert events[0].reserved == 0 and events[0].incurred == 100
    assert warnings


def test_loss_event_rejects_report_before_occurrence():
    with pytest.raises(ValidationError):
        LossEvent(client_id="c", line_of_business=LineOfBusiness.AUTO, cause_of_loss="x",
                  occurrence_date=date(2024, 5, 1), report_date=date(2024, 4, 1))


def test_risk_issue_category_inferred():
    issue = ingest_risk_issue(RiskIssueIn(client_id="c", title="Hot work permits missing"))
    assert issue.category == "fire.hot_work"
    assert issue.score == 2 * 0.5


def test_iot_alerts_and_promotion():
    base = datetime(2025, 1, 1)
    signals = [IoTSignal(client_id="c", location_id="l", device_id="d", metric="water_flow_lpm", value=v, observed_at=base)
               for v in (5, 25, 70, 65)]
    alerts = ingest_signals(signals)
    assert [a.severity for a in alerts] == [Severity.HIGH, Severity.CRITICAL, Severity.CRITICAL]
    issues = signals_to_issues(alerts)
    assert len(issues) == 1 and issues[0].category == "water.leak" and issues[0].severity == Severity.CRITICAL
    assert signals_to_issues(alerts[:1]) == []
