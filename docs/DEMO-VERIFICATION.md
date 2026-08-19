# PredictaLine Demonstration Verification

## Live local dashboard review

The React operations dashboard was opened against the local FastAPI service through the temporary preview host. The `bearing-wear` synthetic scenario completed successfully and presented the bounded workflow as designed.

| Check | Verified result |
|---|---|
| Operating mode | The dashboard visibly labels **Simulation mode**, **MQTT-shaped stream**, **Local-only**, and **No device connection**. |
| Fleet summary | The rendered view showed 12% fleet readiness, one reviewed asset, one maintenance cue, and six accepted telemetry events. |
| Maintenance outcome | Synthetic asset `press-07` received an **Urgent review** advisory of 88/100. |
| Evidence presentation | Vibration, temperature, current-draw, and pressure-variability contributions were shown alongside the latest synthetic readings. |
| Safety framing | The dashboard states that the recommendation needs human validation and is not a diagnosis, repair instruction, calibrated remaining-useful-life estimate, or substitute for engineering judgment. |

No external device, broker, remote target, or cloud service was contacted during this verification.

## Reviewed baseline workflow

The dashboard was then switched to the approved `reviewed-baseline` fixture. Synthetic asset `conveyor-03` rendered a **Routine** advisory of 0/100, with 100% fleet readiness, zero maintenance cues, two accepted telemetry events, and zero-percent contributions from every displayed evidence factor. This confirms that the local scoring workflow can present both human-review and no-escalation states without changing its safety framing.
