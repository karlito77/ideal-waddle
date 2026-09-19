"""Repository interface. The outline ships an in-memory implementation; the
interface is the seam where Postgres / a warehouse would plug in."""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional, Protocol

from riskintel.domain import (
    Client,
    Community,
    ExposureProfile,
    IoTAlert,
    IoTSignal,
    LossEvent,
    RiskIssue,
    SharingConsent,
)


class Repository(Protocol):
    def add_client(self, client: Client) -> Client: ...
    def get_client(self, client_id: str) -> Optional[Client]: ...
    def list_clients(self) -> list[Client]: ...
    def add_community(self, community: Community) -> Community: ...
    def get_community(self, community_id: str) -> Optional[Community]: ...
    def add_consent(self, consent: SharingConsent) -> SharingConsent: ...
    def consents_for(self, client_id: str) -> list[SharingConsent]: ...
    def add_losses(self, losses: Iterable[LossEvent]) -> list[LossEvent]: ...
    def losses_for(self, client_id: str) -> list[LossEvent]: ...
    def add_exposure(self, exposure: ExposureProfile) -> ExposureProfile: ...
    def exposures_for(self, client_id: str) -> list[ExposureProfile]: ...
    def add_issue(self, issue: RiskIssue) -> RiskIssue: ...
    def issues_for(self, client_id: str) -> list[RiskIssue]: ...
    def add_signals(self, signals: Iterable[IoTSignal]) -> list[IoTSignal]: ...
    def signals_for(self, client_id: str) -> list[IoTSignal]: ...
    def add_alerts(self, alerts: Iterable[IoTAlert]) -> list[IoTAlert]: ...
    def alerts_for(self, client_id: str) -> list[IoTAlert]: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}
        self._communities: dict[str, Community] = {}
        self._consents: dict[str, list[SharingConsent]] = defaultdict(list)
        self._losses: dict[str, list[LossEvent]] = defaultdict(list)
        self._exposures: dict[str, list[ExposureProfile]] = defaultdict(list)
        self._issues: dict[str, list[RiskIssue]] = defaultdict(list)
        self._signals: dict[str, list[IoTSignal]] = defaultdict(list)
        self._alerts: dict[str, list[IoTAlert]] = defaultdict(list)

    # clients / communities
    def add_client(self, client: Client) -> Client:
        self._clients[client.id] = client
        for cid in client.community_ids:
            community = self._communities.get(cid)
            if community and client.id not in community.member_ids:
                community.member_ids.append(client.id)
        return client

    def get_client(self, client_id: str) -> Optional[Client]:
        return self._clients.get(client_id)

    def list_clients(self) -> list[Client]:
        return list(self._clients.values())

    def add_community(self, community: Community) -> Community:
        self._communities[community.id] = community
        return community

    def get_community(self, community_id: str) -> Optional[Community]:
        return self._communities.get(community_id)

    # consent
    def add_consent(self, consent: SharingConsent) -> SharingConsent:
        self._consents[consent.client_id].append(consent)
        return consent

    def consents_for(self, client_id: str) -> list[SharingConsent]:
        return list(self._consents.get(client_id, []))

    # losses / exposure
    def add_losses(self, losses: Iterable[LossEvent]) -> list[LossEvent]:
        added = list(losses)
        for loss in added:
            self._losses[loss.client_id].append(loss)
        return added

    def losses_for(self, client_id: str) -> list[LossEvent]:
        return list(self._losses.get(client_id, []))

    def add_exposure(self, exposure: ExposureProfile) -> ExposureProfile:
        self._exposures[exposure.client_id].append(exposure)
        return exposure

    def exposures_for(self, client_id: str) -> list[ExposureProfile]:
        return list(self._exposures.get(client_id, []))

    # risk issues
    def add_issue(self, issue: RiskIssue) -> RiskIssue:
        self._issues[issue.client_id].append(issue)
        return issue

    def issues_for(self, client_id: str) -> list[RiskIssue]:
        return list(self._issues.get(client_id, []))

    # iot
    def add_signals(self, signals: Iterable[IoTSignal]) -> list[IoTSignal]:
        added = list(signals)
        for s in added:
            self._signals[s.client_id].append(s)
        return added

    def signals_for(self, client_id: str) -> list[IoTSignal]:
        return list(self._signals.get(client_id, []))

    def add_alerts(self, alerts: Iterable[IoTAlert]) -> list[IoTAlert]:
        added = list(alerts)
        for a in added:
            self._alerts[a.client_id].append(a)
        return added

    def alerts_for(self, client_id: str) -> list[IoTAlert]:
        return list(self._alerts.get(client_id, []))
