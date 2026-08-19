from fastapi.testclient import TestClient
from predictaline.main import app

client = TestClient(app)


def test_health_declares_local_demo_mode() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["external_connectivity"] == "disabled"


def test_bearing_replay_returns_explainable_advisory() -> None:
    response = client.post("/api/replay/bearing_wear")
    assert response.status_code == 200
    body = response.json()
    assert body["generated_events"] == 3
    advisory = body["fleet"]["assets"][0]["advisory"]
    assert advisory["priority"] == "urgent_review"
    assert advisory["factors"]
    assert "not a calibrated" in advisory["limitations"]


def test_unknown_replay_is_not_available() -> None:
    response = client.post("/api/replay/not-a-scenario")
    assert response.status_code == 404
