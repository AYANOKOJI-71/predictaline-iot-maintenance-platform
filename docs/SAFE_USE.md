# Safe Use

## What PredictaLine is

PredictaLine is a learning and portfolio application that demonstrates telemetry ingestion, time-series thinking, anomaly scoring, and maintenance-dashboard design. All included assets, values, equipment names, and scenarios are fictional.

## What it must not do

The default application must not connect to real industrial networks, discover devices, control equipment, alter PLC or SCADA settings, transmit data to external services, retain credentials, or create autonomous maintenance decisions. It must not be used to determine whether equipment is safe to operate.

## Interpretation limits

The risk score is an explainable demo heuristic that uses simulated baselines and a deterministic anomaly signal. It is not a calibrated remaining-useful-life model, an engineering diagnosis, a fault certification, or a substitute for site-specific inspection procedures. A qualified engineer must validate any real-world maintenance concern.

## Data rules

Only fictional, synthetic, public, or explicitly authorised and sanitised data may be imported. Do not include names, serial numbers, access credentials, network addresses, production schedules, customer information, or unredacted industrial telemetry in a repository.

## Review checklist

| Check | Required behaviour |
|---|---|
| Target boundary | The demo uses bundled fixtures and local loopback services only. |
| Data boundary | Inputs must be synthetic or explicitly authorised and sanitised. |
| Decision boundary | Results remain advisory and require human validation. |
| Deployment boundary | Compose services are local by default; do not expose broker or database ports publicly. |
