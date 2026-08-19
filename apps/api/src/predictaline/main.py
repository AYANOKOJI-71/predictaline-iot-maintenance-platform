from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from predictaline.contracts import AssetSnapshot, FleetSummary, MetricsSnapshot, ReplayResult
from predictaline.engine import LocalTopicBridge, PredictiveEngine, TelemetryJournal
from predictaline.fixtures import SCENARIOS, scenario_events

journal = TelemetryJournal()
bridge = LocalTopicBridge(journal, PredictiveEngine())

app = FastAPI(title="PredictaLine Local Demo API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5203", "http://127.0.0.1:5203"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _replay(scenario: str) -> ReplayResult:
    journal.reset()
    try:
        events = scenario_events(scenario)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    for event in events:
        bridge.publish(f"factory/demo/telemetry/{event.asset_id}", event)
    journal.increment_replay()
    return ReplayResult(scenario=scenario, generated_events=len(events), fleet=journal.fleet())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-deterministic-demo", "external_connectivity": "disabled"}


@app.get("/api/scenarios")
def scenarios() -> dict[str, list[str]]:
    return {"scenarios": sorted(SCENARIOS)}


@app.post("/api/replay/{scenario}", response_model=ReplayResult)
def replay(scenario: str) -> ReplayResult:
    return _replay(scenario)


@app.get("/api/fleet", response_model=FleetSummary)
def fleet() -> FleetSummary:
    return journal.fleet()


@app.get("/api/assets/{asset_id}", response_model=AssetSnapshot)
def asset(asset_id: str) -> AssetSnapshot:
    fleet_state = journal.fleet()
    for snapshot in fleet_state.assets:
        if snapshot.event.asset_id == asset_id:
            return snapshot
    raise HTTPException(status_code=404, detail="No local demo telemetry has been replayed for this asset.")


@app.get("/api/metrics", response_model=MetricsSnapshot)
def metrics() -> MetricsSnapshot:
    return journal.metrics


@app.get("/metrics")
def prometheus_metrics() -> str:
    metrics_state = journal.metrics
    return "\n".join(
        [
            "# TYPE predictaline_telemetry_events_total counter",
            f"predictaline_telemetry_events_total {metrics_state.telemetry_events}",
            "# TYPE predictaline_maintenance_advisories_total counter",
            f"predictaline_maintenance_advisories_total {metrics_state.maintenance_advisories}",
            "# TYPE predictaline_replay_runs_total counter",
            f"predictaline_replay_runs_total {metrics_state.replay_runs}",
            "# TYPE predictaline_rejected_topics_total counter",
            f"predictaline_rejected_topics_total {metrics_state.rejected_topics}",
            "",
        ]
    )
