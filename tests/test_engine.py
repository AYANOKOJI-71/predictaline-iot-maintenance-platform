from predictaline.contracts import Priority
from predictaline.engine import LocalTopicBridge, PredictiveEngine, TelemetryJournal
from predictaline.fixtures import scenario_events


def run_scenario(scenario: str):
    journal = TelemetryJournal()
    bridge = LocalTopicBridge(journal, PredictiveEngine())
    for event in scenario_events(scenario):
        bridge.publish(f"factory/demo/telemetry/{event.asset_id}", event)
    return journal.fleet().assets[0].advisory


def test_bearing_wear_is_higher_priority_than_steady_state() -> None:
    baseline = run_scenario("steady_state")
    bearing = run_scenario("bearing_wear")
    assert baseline.priority == Priority.ROUTINE
    assert bearing.priority == Priority.URGENT_REVIEW
    assert bearing.risk_score > baseline.risk_score
    assert bearing.model_anomaly_score > baseline.model_anomaly_score


def test_thermal_drift_includes_temperature_evidence() -> None:
    advisory = run_scenario("thermal_drift")
    temperature = next(factor for factor in advisory.factors if factor.metric == "Temperature")
    assert advisory.priority in {Priority.WATCH, Priority.PLAN}
    assert temperature.contribution > 0
    assert advisory.trend_score > 0


def test_topic_bridge_rejects_non_local_topic() -> None:
    journal = TelemetryJournal()
    bridge = LocalTopicBridge(journal, PredictiveEngine())
    event = scenario_events("steady_state")[0]
    try:
        bridge.publish("factory/production/telemetry/conveyor-03", event)
    except ValueError as error:
        assert "local synthetic telemetry" in str(error)
    else:
        raise AssertionError("Expected the local topic bridge to reject a non-demo topic")
    assert journal.metrics.rejected_topics == 1
