# PredictaLine Architecture

## Scope

PredictaLine is a **portfolio-ready local predictive-maintenance demonstration**, not an industrial control system. It processes only bundled deterministic telemetry simulations and explicitly supplied sanitised fixture data. It does not connect to plant equipment, issue maintenance work orders, control machinery, retain credentials, or make safety-critical decisions.

## Operating modes

| Mode | Purpose | Transport and storage | External connectivity |
|---|---|---|---|
| Demo replay | Default review experience | In-process MQTT-shaped event bridge and local SQLite event journal | None |
| Compose lab | Production-shaped local topology | Mosquitto, InfluxDB, FastAPI, simulator, and dashboard containers | Local Docker network only |

The default uses an in-process bridge so a reviewer can reproduce the same result without hardware, Docker, a cloud account, or a background service. The Compose topology preserves realistic deployment vocabulary while remaining local-only.

## Component model

```text
Synthetic equipment profiles
        |
        v
Deterministic simulator --- MQTT-shaped topic --> Event bridge
                                                |
                                                v
                                       FastAPI analysis service
                                                |
                            +-------------------+------------------+
                            |                                      |
                            v                                      v
                Local event journal / optional InfluxDB      Explainable anomaly model
                                                                    |
                                                                    v
                                                            Maintenance advisory API
                                                                    |
                                                                    v
                                                          React operations dashboard
```

## Telemetry contract

The implementation uses a compact message whose values are fictional measurements expressed in engineering-like units for demonstration only.

```json
{
  "event_id": "demo-bearing-017",
  "occurred_at": "2026-08-19T09:15:00Z",
  "asset_id": "press-07",
  "line": "demo-line-a",
  "scenario": "bearing_wear",
  "vibration_mm_s": 7.3,
  "temperature_c": 87.1,
  "pressure_bar": 5.0,
  "current_a": 13.2,
  "runtime_hours": 1842.5
}
```

| Topic | Publisher | Consumer | Constraint |
|---|---|---|---|
| `factory/demo/telemetry/{asset_id}` | Bundled simulator | Event bridge | Local fixture records only |
| `factory/demo/maintenance/{asset_id}` | Analysis service | Dashboard | Advisory-only results |

## Explainable scoring

The scoring layer combines a deterministic, seeded isolation-forest anomaly signal with transparent domain guards. It produces an **advisory priority**, not a failure prediction or maintenance instruction.

| Priority | Score range | Meaning |
|---|---:|---|
| Routine | 0–29 | Stable or low-confidence deviation; continue ordinary review. |
| Watch | 30–54 | A developing deviation merits trend review at the next planned inspection. |
| Plan | 55–74 | Multiple evidence factors justify a maintenance-planning review. |
| Urgent review | 75–100 | Strong simulated evidence; validate with a qualified engineer before taking action. |

Every score exposes its contributing sensor factors, baseline comparison, model signal, limitations, and a conservative validation step.

## Local scenarios

| Scenario | Intent | Expected dashboard posture |
|---|---|---|
| `steady_state` | Controlled baseline | Routine |
| `thermal_drift` | Gradually increasing temperature | Watch or Plan |
| `bearing_wear` | Increasing vibration and current draw | Urgent review |
| `pressure_instability` | Oscillating pressure with vibration changes | Plan |
