from __future__ import annotations

from datetime import UTC, datetime, timedelta

from predictaline.contracts import TelemetryEvent

BASE_TIME = datetime(2026, 8, 19, 9, 0, tzinfo=UTC)


def _event(
    *,
    event_id: str,
    minutes: int,
    asset_id: str,
    scenario: str,
    vibration: float,
    temperature: float,
    pressure: float,
    current: float,
    runtime: float,
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=event_id,
        occurred_at=BASE_TIME + timedelta(minutes=minutes),
        asset_id=asset_id,
        line="demo-line-a",
        scenario=scenario,
        vibration_mm_s=vibration,
        temperature_c=temperature,
        pressure_bar=pressure,
        current_a=current,
        runtime_hours=runtime,
    )


SCENARIOS: dict[str, list[TelemetryEvent]] = {
    "steady_state": [
        _event(
            event_id="steady-conveyor-01",
            minutes=0,
            asset_id="conveyor-03",
            scenario="steady_state",
            vibration=1.8,
            temperature=61.2,
            pressure=5.1,
            current=7.4,
            runtime=894.0,
        ),
        _event(
            event_id="steady-conveyor-02",
            minutes=15,
            asset_id="conveyor-03",
            scenario="steady_state",
            vibration=1.9,
            temperature=61.8,
            pressure=5.0,
            current=7.5,
            runtime=894.25,
        ),
    ],
    "thermal_drift": [
        _event(
            event_id="thermal-pump-01",
            minutes=0,
            asset_id="pump-12",
            scenario="thermal_drift",
            vibration=2.3,
            temperature=70.0,
            pressure=5.1,
            current=8.2,
            runtime=1210.0,
        ),
        _event(
            event_id="thermal-pump-02",
            minutes=15,
            asset_id="pump-12",
            scenario="thermal_drift",
            vibration=2.5,
            temperature=78.8,
            pressure=5.0,
            current=8.6,
            runtime=1210.25,
        ),
        _event(
            event_id="thermal-pump-03",
            minutes=30,
            asset_id="pump-12",
            scenario="thermal_drift",
            vibration=2.6,
            temperature=84.5,
            pressure=5.0,
            current=8.9,
            runtime=1210.5,
        ),
    ],
    "bearing_wear": [
        _event(
            event_id="bearing-press-01",
            minutes=0,
            asset_id="press-07",
            scenario="bearing_wear",
            vibration=4.2,
            temperature=72.0,
            pressure=5.0,
            current=9.8,
            runtime=1842.0,
        ),
        _event(
            event_id="bearing-press-02",
            minutes=15,
            asset_id="press-07",
            scenario="bearing_wear",
            vibration=6.1,
            temperature=80.1,
            pressure=5.0,
            current=11.5,
            runtime=1842.25,
        ),
        _event(
            event_id="bearing-press-03",
            minutes=30,
            asset_id="press-07",
            scenario="bearing_wear",
            vibration=7.3,
            temperature=87.1,
            pressure=5.0,
            current=13.2,
            runtime=1842.5,
        ),
    ],
    "pressure_instability": [
        _event(
            event_id="pressure-mixer-01",
            minutes=0,
            asset_id="mixer-04",
            scenario="pressure_instability",
            vibration=2.4,
            temperature=65.0,
            pressure=4.8,
            current=8.1,
            runtime=502.0,
        ),
        _event(
            event_id="pressure-mixer-02",
            minutes=15,
            asset_id="mixer-04",
            scenario="pressure_instability",
            vibration=3.5,
            temperature=66.1,
            pressure=3.6,
            current=8.3,
            runtime=502.25,
        ),
        _event(
            event_id="pressure-mixer-03",
            minutes=30,
            asset_id="mixer-04",
            scenario="pressure_instability",
            vibration=4.1,
            temperature=67.3,
            pressure=6.8,
            current=8.7,
            runtime=502.5,
        ),
    ],
}


def scenario_events(scenario: str) -> list[TelemetryEvent]:
    try:
        return [event.model_copy(deep=True) for event in SCENARIOS[scenario]]
    except KeyError as error:
        available = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"Unknown local scenario '{scenario}'. Available: {available}") from error
