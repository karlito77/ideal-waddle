"""Core entities. Pydantic models so they validate at the API boundary and
serialise cleanly; a real build would map these to persistence separately."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from .enums import (
    AnonymisationLevel,
    Audience,
    IssueSource,
    IssueStatus,
    LineOfBusiness,
    LossStatus,
    Severity,
    SharingScope,
)


def new_id() -> str:
    return uuid4().hex


class Location(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    country: str
    region: str                      # e.g. state / county / postcode area used for cohorting
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_insured_value: Optional[float] = None


class Client(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    activity_code: str               # NAICS / SIC / ANZSIC style code, hierarchical by prefix
    annual_revenue: float
    employee_count: int = 0
    locations: list[Location] = Field(default_factory=list)
    community_ids: list[str] = Field(default_factory=list)

    @property
    def regions(self) -> set[str]:
        return {loc.region for loc in self.locations}


class Community(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    description: str = ""
    member_ids: list[str] = Field(default_factory=list)


class SharingConsent(BaseModel):
    """A client's decision about what it shares, with whom, and how anonymised."""
    id: str = Field(default_factory=new_id)
    client_id: str
    scope: SharingScope
    audience: Audience = Audience.NONE
    anonymisation: AnonymisationLevel = AnonymisationLevel.AGGREGATED
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None

    @property
    def active(self) -> bool:
        return self.revoked_at is None and self.audience != Audience.NONE


class ExposureProfile(BaseModel):
    """Exposure base for a policy / experience year, used to normalise frequency."""
    client_id: str
    year: int
    revenue: float
    payroll: Optional[float] = None
    vehicle_count: Optional[int] = None
    total_insured_value: Optional[float] = None


class LossEvent(BaseModel):
    id: str = Field(default_factory=new_id)
    client_id: str
    location_id: Optional[str] = None
    line_of_business: LineOfBusiness
    cause_of_loss: str               # free text mapped to a taxonomy during ingestion
    occurrence_date: date
    report_date: Optional[date] = None
    paid: float = 0.0
    reserved: float = 0.0
    status: LossStatus = LossStatus.OPEN
    currency: str = "USD"
    description: str = ""

    @property
    def incurred(self) -> float:
        return self.paid + self.reserved

    @property
    def exposure_year(self) -> int:
        return self.occurrence_date.year

    @model_validator(mode="after")
    def _validate(self) -> "LossEvent":
        if self.paid < 0 or self.reserved < 0:
            raise ValueError("paid and reserved must be non-negative")
        if self.report_date and self.report_date < self.occurrence_date:
            raise ValueError("report_date cannot precede occurrence_date")
        return self


class RiskIssue(BaseModel):
    id: str = Field(default_factory=new_id)
    client_id: str
    location_id: Optional[str] = None
    source: IssueSource
    category: str                    # taxonomy node, e.g. "fire.hot_work", "water.pipe_freeze"
    title: str
    description: str = ""
    severity: Severity = Severity.MEDIUM
    likelihood: float = Field(0.5, ge=0.0, le=1.0)
    status: IssueStatus = IssueStatus.OPEN
    raised_at: datetime = Field(default_factory=datetime.utcnow)
    origin_issue_id: Optional[str] = None   # set when the issue was copied in from a peer
    tags: list[str] = Field(default_factory=list)

    @property
    def score(self) -> float:
        weight = {Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3, Severity.CRITICAL: 4}
        return weight[self.severity] * self.likelihood


class IoTSignal(BaseModel):
    id: str = Field(default_factory=new_id)
    client_id: str
    location_id: str
    device_id: str
    metric: str                      # e.g. "water_flow_lpm", "temperature_c", "vibration_g"
    value: float
    observed_at: datetime


class IoTAlert(BaseModel):
    id: str = Field(default_factory=new_id)
    client_id: str
    location_id: str
    device_id: str
    metric: str
    value: float
    threshold: float
    severity: Severity
    observed_at: datetime
    message: str
