"""Deterministic sample community used by the demo script and the tests.

Three warehousing / logistics clients in two regions. Northwind shares
record-level pseudonymised losses with its activity cohort, Contoso shares
banded aggregates with the whole community, Fabrikam shares nothing.
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from riskintel.domain import (
    AnonymisationLevel,
    Audience,
    Client,
    Community,
    ExposureProfile,
    IoTSignal,
    IssueSource,
    LineOfBusiness,
    Location,
    LossStatus,
    Severity,
    SharingConsent,
    SharingScope,
)
from riskintel.ingestion import LossRecordIn, RiskIssueIn, ingest_loss_records, ingest_risk_issue, ingest_signals
from riskintel.storage import InMemoryRepository

COMMUNITY_ID = "logistics-community"
NORTHWIND, CONTOSO, FABRIKAM = "northwind", "contoso", "fabrikam"
YEARS = [2021, 2022, 2023, 2024, 2025]
CAUSES = ["burst pipe", "forklift collision", "slip and fall", "theft", "storm damage", "fire"]


def _losses(rng: random.Random, client_id: str, per_year: float, sev_scale: float) -> list[LossRecordIn]:
    records: list[LossRecordIn] = []
    counter = 0
    for year in YEARS:
        n = max(0, int(round(rng.gauss(per_year, per_year ** 0.5))))
        for _ in range(n):
            counter += 1
            occurred = date(year, rng.randint(1, 12), rng.randint(1, 28))
            reported = occurred + timedelta(days=rng.randint(0, 120))
            amount = rng.lognormvariate(sev_scale, 1.1)
            closed = year < 2024 or rng.random() < 0.5
            records.append(
                LossRecordIn(
                    client_id=client_id,
                    claim_reference=f"{client_id.upper()}-{year}-{counter:03d}",
                    line_of_business=LineOfBusiness.PROPERTY if rng.random() < 0.6 else LineOfBusiness.GENERAL_LIABILITY,
                    cause_of_loss=rng.choice(CAUSES),
                    occurrence_date=occurred,
                    report_date=reported,
                    paid=amount if closed else amount * 0.4,
                    reserved=0.0 if closed else amount * 0.6,
                    status=LossStatus.CLOSED if closed else LossStatus.OPEN,
                )
            )
    return records


def seed_repository(seed: int = 7) -> InMemoryRepository:
    rng = random.Random(seed)
    repo = InMemoryRepository()
    repo.add_community(Community(id=COMMUNITY_ID, name="Logistics & Warehousing Community"))

    clients = [
        Client(id=NORTHWIND, name="Northwind Logistics", activity_code="4931", annual_revenue=120e6,
               employee_count=800, community_ids=[COMMUNITY_ID],
               locations=[Location(id="nw-1", name="Leeds DC", country="GB", region="Yorkshire"),
                          Location(id="nw-2", name="Sheffield Hub", country="GB", region="Yorkshire")]),
        Client(id=CONTOSO, name="Contoso Distribution", activity_code="4931", annual_revenue=90e6,
               employee_count=600, community_ids=[COMMUNITY_ID],
               locations=[Location(id="ct-1", name="Wakefield DC", country="GB", region="Yorkshire")]),
        Client(id=FABRIKAM, name="Fabrikam Freight", activity_code="4841", annual_revenue=200e6,
               employee_count=1500, community_ids=[COMMUNITY_ID],
               locations=[Location(id="fb-1", name="Bristol Depot", country="GB", region="South West")]),
    ]
    for c in clients:
        repo.add_client(c)
        for year in YEARS:
            repo.add_exposure(ExposureProfile(client_id=c.id, year=year, revenue=c.annual_revenue * (1 + 0.03 * (year - 2021))))

    for client_id, per_year, scale in ((NORTHWIND, 6, 9.2), (CONTOSO, 5, 9.0), (FABRIKAM, 9, 9.6)):
        events, _ = ingest_loss_records(_losses(rng, client_id, per_year, scale))
        repo.add_losses(events)

    repo.add_consent(SharingConsent(client_id=NORTHWIND, scope=SharingScope.LOSS_HISTORY,
                                    audience=Audience.COHORT_ACTIVITY, anonymisation=AnonymisationLevel.PSEUDONYMISED))
    repo.add_consent(SharingConsent(client_id=NORTHWIND, scope=SharingScope.RISK_ISSUES,
                                    audience=Audience.COMMUNITY, anonymisation=AnonymisationLevel.PSEUDONYMISED))
    repo.add_consent(SharingConsent(client_id=CONTOSO, scope=SharingScope.LOSS_HISTORY,
                                    audience=Audience.COMMUNITY, anonymisation=AnonymisationLevel.AGGREGATED))
    repo.add_consent(SharingConsent(client_id=CONTOSO, scope=SharingScope.RISK_ISSUES,
                                    audience=Audience.COHORT_LOCATION, anonymisation=AnonymisationLevel.PSEUDONYMISED))

    repo.add_issue(ingest_risk_issue(RiskIssueIn(client_id=NORTHWIND, location_id="nw-1", title="Hot work permits not enforced",
                                                 severity=Severity.HIGH, likelihood=0.4)))
    repo.add_issue(ingest_risk_issue(RiskIssueIn(client_id=NORTHWIND, location_id="nw-2", title="Forklift pedestrian segregation missing",
                                                 severity=Severity.MEDIUM, likelihood=0.5)))
    repo.add_issue(ingest_risk_issue(RiskIssueIn(client_id=CONTOSO, location_id="ct-1", source=IssueSource.ASSESSOR,
                                                 title="Sprinkler impairment during roof works", severity=Severity.CRITICAL, likelihood=0.3)))

    base = datetime(2025, 12, 1, 8, 0)
    signals = [
        IoTSignal(client_id=NORTHWIND, location_id="nw-1", device_id="flow-01", metric="water_flow_lpm",
                  value=v, observed_at=base + timedelta(hours=i))
        for i, v in enumerate([5, 8, 25, 30, 70, 12])
    ] + [
        IoTSignal(client_id=CONTOSO, location_id="ct-1", device_id="temp-04", metric="temperature_c",
                  value=v, observed_at=base + timedelta(hours=i))
        for i, v in enumerate([21, 22, 23])
    ]
    repo.add_signals(signals)
    repo.add_alerts(ingest_signals(signals))
    return repo
