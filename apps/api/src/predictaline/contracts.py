from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Priority(StrEnum):
    ROUTINE = "routine"
    WATCH = "watch"
    PLAN = "plan"
    URGENT_REVIEW = "urgent_review"


class TelemetryEvent(BaseModel):
    event_id: str = Field(min_length=3, max_length=80)
    occurred_at: datetime
    asset_id: str = Field(pattern=r"^[a-z0-9-]{3,40}$")
    line: str = Field(pattern=r"^[a-z0-9-]{3,40}$")
    scenario: str = Field(pattern=r"^[a-z_]{3,40}$")
    vibration_mm_s: float = Field(ge=0, le=50)
    temperature_c: float = Field(ge=-40, le=250)
    pressure_bar: float = Field(ge=0, le=30)
    current_a: float = Field(ge=0, le=200)
    runtime_hours: float = Field(ge=0, le=200000)


class EvidenceFactor(BaseModel):
    metric: str
    observed: float
    baseline: float
    contribution: int = Field(ge=0, le=100)
    rationale: str


class MaintenanceAdvisory(BaseModel):
    asset_id: str
    scenario: str
    generated_at: datetime
    risk_score: int = Field(ge=0, le=100)
    priority: Priority
    model_anomaly_score: float = Field(ge=0, le=1)
    trend_score: int = Field(ge=0, le=100)
    inspection_window: str
    summary: str
    validation_step: str
    limitations: str
    factors: list[EvidenceFactor]


class AssetSnapshot(BaseModel):
    event: TelemetryEvent
    advisory: MaintenanceAdvisory


class FleetSummary(BaseModel):
    generated_at: datetime
    total_assets: int
    priority_counts: dict[str, int]
    assets: list[AssetSnapshot]


class MetricsSnapshot(BaseModel):
    telemetry_events: int
    maintenance_advisories: int
    replay_runs: int
    rejected_topics: int


class ReplayResult(BaseModel):
    scenario: str
    generated_events: int
    fleet: FleetSummary
