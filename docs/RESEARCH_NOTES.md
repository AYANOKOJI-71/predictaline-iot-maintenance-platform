# Research Notes

## Purpose

This project is a **local, deterministic portfolio demonstration**. It uses clearly labelled synthetic equipment telemetry and does not represent live plant data, equipment certification, maintenance advice, or a production control system.

## MQTT transport model

MQTT Version 5.0 is an OASIS client-server publish/subscribe messaging transport protocol designed to be lightweight and suitable for machine-to-machine and IoT contexts.[1]

Threat-free local topic shapes will be used for the demonstration:

```text
factory/demo/telemetry/{asset_id}
factory/demo/maintenance/{asset_id}
```

The simulator will publish only bundled synthetic payloads. The local demonstration will not connect to external brokers or accept device credentials.

## Time-series modelling

The time-series model follows the familiar separation of a timestamped measurement, queryable metadata tags, and numeric field values. InfluxDB documentation describes a point as a measurement, tag set, field set, and timestamp; it also notes that tags are indexed while fields should hold measured values.[2]

For the local demo, the conceptual `equipment_telemetry` measurement uses these values:

| Element | Demonstration value |
|---|---|
| Timestamp | UTC simulation timestamp |
| Tags | `asset_id`, `line`, `scenario` |
| Fields | vibration, temperature, pressure, current draw, health score |

The initial implementation persists the deterministic event history through a lightweight local store while Compose documents an optional production-shaped InfluxDB service. This keeps the demo no-cost and reviewable while demonstrating a production-compatible schema.

## Predictive-maintenance reference

NASA’s C-MAPSS description illustrates that predictive-maintenance data can comprise multivariate engine time series with operational settings, sensor noise, degradation, and a remaining-useful-life objective.[3] Threat-free synthetic telemetry in this project borrows only the **shape of the problem**: multiple sensor dimensions, equipment-specific trends, and early warning before a fault. It does not reproduce NASA records and does not claim a trained remaining-useful-life model.

## References

[1] [OASIS, *MQTT Version 5.0*](https://www.oasis-open.org/standard/mqtt-v5-0-os/)

[2] [InfluxData, *InfluxDB key concepts*](https://docs.influxdata.com/influxdb/v1/concepts/key_concepts/)

[3] [NASA, *C-MAPSS Jet Engine Simulated Data*](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data)
