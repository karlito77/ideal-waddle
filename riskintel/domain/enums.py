from enum import Enum


class LineOfBusiness(str, Enum):
    PROPERTY = "property"
    GENERAL_LIABILITY = "general_liability"
    AUTO = "auto"
    WORKERS_COMP = "workers_comp"
    CYBER = "cyber"
    OTHER = "other"


class LossStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class IssueSource(str, Enum):
    OWN = "own"            # raised by the client's own business
    PEER = "peer"          # shared by another community member
    ASSESSOR = "assessor"  # risk survey / engineering visit
    IOT = "iot"            # derived from device telemetry
    MODEL = "model"        # derived from analytics / modelling


class IssueStatus(str, Enum):
    OPEN = "open"
    MITIGATING = "mitigating"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SharingScope(str, Enum):
    """What kind of data a consent covers."""
    LOSS_HISTORY = "loss_history"
    RISK_ISSUES = "risk_issues"
    IOT_SIGNALS = "iot_signals"


class Audience(str, Enum):
    """Who may see shared data."""
    NONE = "none"
    COHORT_LOCATION = "cohort_location"   # peers in the same region
    COHORT_ACTIVITY = "cohort_activity"   # peers in the same business activity
    COMMUNITY = "community"               # every member of the community


class AnonymisationLevel(str, Enum):
    AGGREGATED = "aggregated"        # only counts / totals / bands leave the client
    PSEUDONYMISED = "pseudonymised"  # record level, client identity replaced by a stable token
    IDENTIFIED = "identified"        # record level with client identity (rare, explicit)
