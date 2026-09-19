from datetime import datetime

from fastapi.testclient import TestClient

from riskintel.api import create_app
from riskintel.demo import CONTOSO, NORTHWIND, seed_repository


def client():
    return TestClient(create_app(seed_repository()))


def test_health():
    assert client().get("/health").json()["status"] == "ok"


def test_ingest_and_experience():
    c = client()
    payload = [{"client_id": NORTHWIND, "claim_reference": "API-1", "line_of_business": "property",
                "cause_of_loss": "storm", "occurrence_date": "2025-03-01", "paid": 12000}]
    r = c.post("/losses", json=payload)
    assert r.status_code == 201 and r.json()["accepted"] == 1
    assert c.post("/losses", json=payload).json()["accepted"] == 0      # duplicate reference
    assert c.get(f"/losses/{NORTHWIND}/experience").json()["claim_count"] > 0
    dev = c.get(f"/losses/{NORTHWIND}/development").json()
    assert "factors" in dev and "ultimates" in dev


def test_community_and_decision_flow():
    c = client()
    peers = c.get(f"/community/{NORTHWIND}/peers").json()
    assert peers and peers[0]["peer_id"] == CONTOSO
    assert c.get(f"/community/{NORTHWIND}/benchmark").json()["pool_claim_count"] > 0
    shared = c.get(f"/risk-issues/{NORTHWIND}/peer").json()
    assert shared
    adopted = c.post(f"/risk-issues/{NORTHWIND}/adopt/{shared[0]['origin_issue_id']}")
    assert adopted.status_code == 201 and adopted.json()["source"] == "peer"

    r = c.post(f"/decisions/{NORTHWIND}/sir", json={
        "candidate_sirs": [50000, 250000], "trials": 1000,
        "appetite": {"max_retained_p99": 5000000},
    })
    body = r.json()
    assert r.status_code == 200 and body["recommended_sir"] in (50000, 250000)
    assert len(body["options"]) == 2


def test_iot_signal_ingest_raises_issue():
    c = client()
    now = datetime(2025, 1, 1).isoformat()
    signals = [{"client_id": CONTOSO, "location_id": "ct-1", "device_id": "flow-9", "metric": "water_flow_lpm",
                "value": v, "observed_at": now} for v in (30, 80)]
    r = c.post("/iot/signals", json=signals)
    assert r.json() == {"signals": 2, "alerts": 2, "issues_raised": 1}
    assert any(i["source"] == "iot" for i in c.get(f"/risk-issues/{CONTOSO}").json())


def test_unknown_client_404():
    assert client().get("/clients/nope").status_code == 404
    assert client().post("/models/nope/fit").status_code == 404


def test_invalid_loss_record_is_422_not_500():
    r = client().post("/losses", json=[{"client_id": NORTHWIND, "line_of_business": "property", "cause_of_loss": "x",
                                        "occurrence_date": "2025-05-01", "report_date": "2025-04-01"}])
    assert r.status_code == 422
    assert "report_date" in r.json()["detail"][0]["msg"]
