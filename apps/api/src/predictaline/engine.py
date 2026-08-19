from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

import numpy as np
from sklearn.ensemble import IsolationForest

from predictaline.contracts import (
    AssetSnapshot,
    EvidenceFactor,
    FleetSummary,
    MaintenanceAdvisory,
    MetricsSnapshot,
    Priority,
    TelemetryEvent,
)


class TelemetryJournal:
    """In-memory journal for the deterministic no-service-required demo mode."""

    def __init__(self) -> None:
        self._events: dict[str, list[TelemetryEvent]] = defaultdict(list)
        self._advisories: dict[str, MaintenanceAdvisory] = {}
        self._metrics = MetricsSnapshot(telemetry_events=0, maintenance_advisories=0, replay_runs=0, rejected_topics=0)

    def reset(self) -> None:
        self._events.clear()
        self._advisories.clear()
        self._metrics = MetricsSnapshot(telemetry_events=0, maintenance_advisories=0, replay_runs=0, rejected_topics=0)

    def append(self, event: TelemetryEvent, advisory: MaintenanceAdvisory) -> None:
        self._events[event.asset_id].append(event)
        self._advisories[event.asset_id] = advisory
        self._metrics.telemetry_events += 1
        self._metrics.maintenance_advisories += 1

    def history(self, asset_id: str) -> list[TelemetryEvent]:
        return list(self._events[asset_id])

    def increment_replay(self) -> None:
        self._metrics.replay_runs += 1

    def increment_rejected_topic(self) -> None:
        self._metrics.rejected_topics += 1

    @property
    def metrics(self) -> MetricsSnapshot:
        return self._metrics.model_copy(deep=True)

    def fleet(self) -> FleetSummary:
        snapshots = [
            AssetSnapshot(event=events[-1], advisory=self._advisories[asset_id])
            for asset_id, events in sorted(self._events.items())
            if events and asset_id in self._advisories
        ]
        counts = {priority.value: 0 for priority in Priority}
        for snapshot in snapshots:
            counts[snapshot.advisory.priority.value] += 1
        return FleetSummary(
            generated_at=datetime.now(UTC),
            total_assets=len(snapshots),
            priority_counts=counts,
            assets=sorted(snapshots, key=lambda item: item.advisory.risk_score, reverse=True),
        )


class PredictiveEngine:
    """A deterministic synthetic-baseline anomaly model with transparent policy factors."""

    baseline = np.array([1.9, 62.0, 5.05, 7.5])
    spreads = np.array([0.35, 3.5, 0.22, 0.8])

    def __init__(self) -> None:
        rng = np.random.default_rng(71)
        training = rng.normal(loc=self.baseline, scale=self.spreads, size=(240, 4))
        self.model = IsolationForest(n_estimators=120, contamination=0.08, random_state=71)
        self.model.fit(training)

    @staticmethod
    def _bounded(value: float) -> float:
        return float(min(1.0, max(0.0, value)))

    def _model_signal(self, event: TelemetryEvent) -> float:
        vector = np.array([[event.vibration_mm_s, event.temperature_c, event.pressure_bar, event.current_a]])
        raw = float(-self.model.score_samples(vector)[0])
        return self._bounded((raw - 0.42) / 0.27)

    @staticmethod
    def _trend(history: list[TelemetryEvent], event: TelemetryEvent) -> int:
        if len(history) < 2:
            return 0
        prior = history[-2]
        vibration_change = max(0.0, event.vibration_mm_s - prior.vibration_mm_s) / 5.0
        temperature_change = max(0.0, event.temperature_c - prior.temperature_c) / 20.0
        current_change = max(0.0, event.current_a - prior.current_a) / 7.0
        return int(min(100, round(100 * (0.45 * vibration_change + 0.35 * temperature_change + 0.2 * current_change))))

    def evaluate(self, event: TelemetryEvent, history: list[TelemetryEvent]) -> MaintenanceAdvisory:
        model_signal = self._model_signal(event)
        trend_score = self._trend(history, event)
        vibration = self._bounded((event.vibration_mm_s - 2.6) / 5.0)
        temperature = self._bounded((event.temperature_c - 70.0) / 25.0)
        pressure = self._bounded(abs(event.pressure_bar - 5.05) / 1.5)
        current = self._bounded((event.current_a - 8.5) / 6.0)
        weighted_signal = 0.34 * model_signal + 0.26 * vibration + 0.18 * temperature + 0.12 * current + 0.1 * pressure
        risk_score = int(round(min(100, 100 * weighted_signal + 0.12 * trend_score)))

        if risk_score >= 75:
            priority = Priority.URGENT_REVIEW
            inspection_window = "Validate with a qualified engineer within the next simulated review window."
        elif risk_score >= 55:
            priority = Priority.PLAN
            inspection_window = "Include this asset in the next planned maintenance review."
        elif risk_score >= 30:
            priority = Priority.WATCH
            inspection_window = "Review the next scheduled synthetic telemetry trend."
        else:
            priority = Priority.ROUTINE
            inspection_window = "Continue ordinary review; no simulated escalation is indicated."

        factors = [
            EvidenceFactor(
                metric="Vibration",
                observed=event.vibration_mm_s,
                baseline=2.6,
                contribution=round(26 * vibration),
                rationale="Vibration is compared with the synthetic baseline envelope.",
            ),
            EvidenceFactor(
                metric="Temperature",
                observed=event.temperature_c,
                baseline=70.0,
                contribution=round(18 * temperature),
                rationale="Temperature is a simulated thermal-drift indicator, not a safety limit.",
            ),
            EvidenceFactor(
                metric="Current draw",
                observed=event.current_a,
                baseline=8.5,
                contribution=round(12 * current),
                rationale="Current draw supports correlated load or friction review in the demo.",
            ),
            EvidenceFactor(
                metric="Pressure variability",
                observed=event.pressure_bar,
                baseline=5.05,
                contribution=round(10 * pressure),
                rationale="Pressure deviation is contextual evidence only in this synthetic fixture.",
            ),
        ]
        return MaintenanceAdvisory(
            asset_id=event.asset_id,
            scenario=event.scenario,
            generated_at=datetime.now(UTC),
            risk_score=risk_score,
            priority=priority,
            model_anomaly_score=round(model_signal, 3),
            trend_score=trend_score,
            inspection_window=inspection_window,
            summary=(
                f"Synthetic {event.scenario.replace('_', ' ')} scenario for {event.asset_id} produced a "
                f"{priority.replace('_', ' ')} advisory from deterministic telemetry evidence."
            ),
            validation_step=(
                "Validate the underlying measurement and follow site-approved maintenance procedures; "
                "do not use this demo score as an operating or repair instruction."
            ),
            limitations=(
                "This is a deterministic demo model trained on synthetic baseline values. It is not a calibrated "
                "remaining-useful-life estimate or a substitute for engineering judgment."
            ),
            factors=factors,
        )


class LocalTopicBridge:
    """Restricts the default application to its local MQTT-shaped telemetry topic contract."""

    prefix = "factory/demo/telemetry/"

    def __init__(self, journal: TelemetryJournal, engine: PredictiveEngine) -> None:
        self.journal = journal
        self.engine = engine

    def publish(self, topic: str, event: TelemetryEvent) -> MaintenanceAdvisory:
        expected = f"{self.prefix}{event.asset_id}"
        if topic != expected:
            self.journal.increment_rejected_topic()
            raise ValueError("Only the local synthetic telemetry topic for the supplied asset is accepted.")
        advisory = self.engine.evaluate(event, self.journal.history(event.asset_id))
        self.journal.append(event, advisory)
        return advisory
