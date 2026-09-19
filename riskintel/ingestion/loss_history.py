"""Loss history ingestion.

Insurers, TPAs and brokers all send loss runs in different shapes. The
ingestion layer normalises them into LossEvent records:

1. validate the raw record (dates, amounts, currency)
2. map free-text cause of loss to the platform taxonomy
3. de-duplicate on (client, claim reference) when a reference is supplied
4. hand the clean records to the repository

The outline accepts an already-tabular record; CSV/XLSX/API adapters would
sit in front of `ingest_loss_records` and produce `LossRecordIn` rows.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from riskintel.domain import LineOfBusiness, LossEvent, LossStatus

# Very small cause-of-loss taxonomy. Real build: maintained reference table.
CAUSE_TAXONOMY: dict[str, str] = {
    "fire": "fire",
    "smoke": "fire",
    "water": "water",
    "escape of water": "water",
    "burst pipe": "water",
    "flood": "flood",
    "storm": "weather",
    "wind": "weather",
    "hail": "weather",
    "theft": "crime",
    "burglary": "crime",
    "slip": "liability.slip_trip",
    "trip": "liability.slip_trip",
    "fall": "liability.slip_trip",
    "collision": "auto.collision",
    "rear end": "auto.collision",
    "manual handling": "injury.manual_handling",
    "ransomware": "cyber.ransomware",
    "phishing": "cyber.social_engineering",
}


class LossRecordIn(BaseModel):
    client_id: str
    claim_reference: Optional[str] = None
    location_id: Optional[str] = None
    line_of_business: LineOfBusiness
    cause_of_loss: str
    occurrence_date: date
    report_date: Optional[date] = None
    paid: float = Field(0.0, ge=0.0)
    reserved: float = Field(0.0, ge=0.0)
    status: LossStatus = LossStatus.OPEN
    currency: str = "USD"
    description: str = ""

    @model_validator(mode="after")
    def _dates(self) -> "LossRecordIn":
        if self.report_date and self.report_date < self.occurrence_date:
            raise ValueError("report_date cannot precede occurrence_date")
        return self


def map_cause(raw: str) -> str:
    """Map free text to a taxonomy node; unknown text becomes 'unclassified'."""
    text = raw.strip().lower()
    for key, node in CAUSE_TAXONOMY.items():
        if key in text:
            return node
    return "unclassified"


def ingest_loss_records(
    records: list[LossRecordIn],
    existing: Optional[list[LossEvent]] = None,
) -> tuple[list[LossEvent], list[str]]:
    """Return (new LossEvents, warnings). Duplicates by claim reference are dropped."""
    warnings: list[str] = []
    seen: set[tuple[str, str]] = set()
    for loss in existing or []:
        if loss.description.startswith("ref:"):
            seen.add((loss.client_id, loss.description.split()[0][4:]))

    events: list[LossEvent] = []
    for rec in records:
        key = (rec.client_id, rec.claim_reference or "")
        if rec.claim_reference:
            if key in seen:
                warnings.append(f"duplicate claim reference {rec.claim_reference} skipped")
                continue
            seen.add(key)
        if rec.status == LossStatus.CLOSED and rec.reserved > 0:
            warnings.append(f"closed claim {rec.claim_reference or rec.occurrence_date} has reserve; zeroed")
            rec = rec.model_copy(update={"reserved": 0.0})
        description = rec.description
        if rec.claim_reference:
            description = f"ref:{rec.claim_reference} {description}".strip()
        events.append(
            LossEvent(
                client_id=rec.client_id,
                location_id=rec.location_id,
                line_of_business=rec.line_of_business,
                cause_of_loss=map_cause(rec.cause_of_loss),
                occurrence_date=rec.occurrence_date,
                report_date=rec.report_date,
                paid=rec.paid,
                reserved=rec.reserved,
                status=rec.status,
                currency=rec.currency,
                description=description,
            )
        )
    return events, warnings
