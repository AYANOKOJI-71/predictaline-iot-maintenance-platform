import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type AssetSnapshot, type FleetSummary, type MetricsSnapshot, type Priority } from "./api";

const priorityCopy: Record<Priority, string> = {
  routine: "Routine",
  watch: "Watch",
  plan: "Plan inspection",
  urgent_review: "Urgent review"
};

const scenarios = [
  { key: "bearing_wear", label: "Bearing wear", description: "Increasing vibration and current" },
  { key: "thermal_drift", label: "Thermal drift", description: "Sustained temperature rise" },
  { key: "pressure_instability", label: "Pressure instability", description: "Pressure variance under load" },
  { key: "steady_state", label: "Reviewed baseline", description: "Stable normal-operation fixture" }
];

function priorityClass(priority: Priority) {
  return `priority priority--${priority}`;
}

function Gauge({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 44;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className="gauge" aria-label={`Maintenance risk score ${score} of 100`}>
      <svg viewBox="0 0 112 112" role="img">
        <circle className="gauge__track" cx="56" cy="56" r="44" />
        <circle className="gauge__value" cx="56" cy="56" r="44" strokeDasharray={circumference} strokeDashoffset={offset} />
      </svg>
      <strong>{score}</strong><span>/100</span>
    </div>
  );
}

function Metric({ label, value, unit, status = "normal" }: { label: string; value: number; unit: string; status?: string }) {
  return <div className={`sensor sensor--${status}`}><span>{label}</span><strong>{value.toFixed(1)}</strong><small>{unit}</small></div>;
}

export default function App() {
  const [fleet, setFleet] = useState<FleetSummary | null>(null);
  const [metrics, setMetrics] = useState<MetricsSnapshot | null>(null);
  const [selected, setSelected] = useState<AssetSnapshot | null>(null);
  const [activeScenario, setActiveScenario] = useState("bearing_wear");
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [nextFleet, nextMetrics] = await Promise.all([api.fleet(), api.metrics()]);
    setFleet(nextFleet);
    setMetrics(nextMetrics);
    setSelected((current) => nextFleet.assets.find((item) => item.event.asset_id === current?.event.asset_id) ?? nextFleet.assets[0] ?? null);
  }, []);

  const replay = useCallback(async (scenario: string) => {
    setError(null);
    setIsRunning(true);
    setActiveScenario(scenario);
    try {
      const result = await api.replay(scenario);
      setFleet(result.fleet);
      const nextMetrics = await api.metrics();
      setMetrics(nextMetrics);
      setSelected(result.fleet.assets[0] ?? null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The local replay could not be completed.");
    } finally {
      setIsRunning(false);
    }
  }, []);

  useEffect(() => { void replay("bearing_wear"); }, [replay]);

  const highestRisk = useMemo(() => fleet?.assets.reduce<AssetSnapshot | null>((highest, asset) => !highest || asset.advisory.risk_score > highest.advisory.risk_score ? asset : highest, null) ?? null, [fleet]);
  const selectedAsset = selected ?? highestRisk;
  const alertCount = Object.entries(fleet?.priority_counts ?? {}).filter(([key]) => key !== "routine").reduce((count, [, value]) => count + value, 0);

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand__mark">P</span><div><strong>PredictaLine</strong><small>Local maintenance intelligence</small></div></div>
        <div className="header-meta"><span className="status-dot" /> <span>SIMULATION MODE</span><span className="divider" /><span>MQTT-SHAPED STREAM</span></div>
      </header>

      <section className="hero">
        <div><p className="eyebrow">OPERATIONS / DEMO-LINE-A</p><h1>Turn sensor signals into an <em>explainable</em> maintenance decision.</h1><p className="lede">PredictaLine replays safe synthetic equipment telemetry locally, scores maintenance risk, and preserves the evidence a technician needs to validate the recommendation.</p></div>
        <div className="hero__seal"><span>LOCAL-ONLY</span><strong>NO DEVICE<br />CONNECTION</strong><small>deterministic replay</small></div>
      </section>

      <section className="scenario-strip" aria-label="Local demo scenarios">
        {scenarios.map((scenario) => <button key={scenario.key} className={activeScenario === scenario.key ? "scenario scenario--active" : "scenario"} onClick={() => void replay(scenario.key)} disabled={isRunning}>
          <span>{scenario.label}</span><small>{scenario.description}</small>
        </button>)}
      </section>

      {error && <div className="error">{error}</div>}
      <section className="score-row">
        <article className="score-card score-card--risk"><p>Fleet readiness</p><strong>{highestRisk ? `${100 - highestRisk.advisory.risk_score}%` : "—"}</strong><span>from local risk model</span></article>
        <article className="score-card"><p>Assets reviewed</p><strong>{fleet?.total_assets ?? "—"}</strong><span>in current local replay</span></article>
        <article className="score-card"><p>Maintenance cues</p><strong>{alertCount}</strong><span>requiring human review</span></article>
        <article className="score-card"><p>Telemetry events</p><strong>{metrics?.telemetry_events ?? "—"}</strong><span>accepted on approved topic</span></article>
      </section>

      <section className="content-grid">
        <article className="panel asset-panel"><div className="panel__head"><div><p className="eyebrow">FLEET REVIEW</p><h2>Equipment under review</h2></div><span className="quiet">{isRunning ? "Replaying…" : "Local evidence loaded"}</span></div>
          <div className="asset-list">{fleet?.assets.map((asset) => <button key={asset.event.asset_id} className={selectedAsset?.event.asset_id === asset.event.asset_id ? "asset asset--selected" : "asset"} onClick={() => setSelected(asset)}><span className="asset__icon">⚙</span><span className="asset__name"><strong>{asset.event.asset_id}</strong><small>{asset.event.line.replaceAll("-", " ")} · {asset.event.scenario.replaceAll("_", " ")}</small></span><span className={priorityClass(asset.advisory.priority)}>{priorityCopy[asset.advisory.priority]}</span><span className="asset__risk">{asset.advisory.risk_score}</span></button>)}</div>
        </article>

        <article className="panel review-panel">{selectedAsset ? <>
          <div className="panel__head"><div><p className="eyebrow">MAINTENANCE ADVISORY</p><h2>{selectedAsset.event.asset_id}</h2></div><span className={priorityClass(selectedAsset.advisory.priority)}>{priorityCopy[selectedAsset.advisory.priority]}</span></div>
          <div className="review-overview"><Gauge score={selectedAsset.advisory.risk_score} /><div><h3>{selectedAsset.advisory.summary}</h3><p>Suggested window: <strong>{selectedAsset.advisory.inspection_window}</strong></p><p className="muted">Model signal {Math.round(selectedAsset.advisory.model_anomaly_score * 100)}% · trend signal {selectedAsset.advisory.trend_score}%</p></div></div>
          <div className="sensor-grid"><Metric label="Vibration" value={selectedAsset.event.vibration_mm_s} unit="mm/s" status={selectedAsset.event.vibration_mm_s > 5 ? "alert" : "normal"} /><Metric label="Temperature" value={selectedAsset.event.temperature_c} unit="°C" status={selectedAsset.event.temperature_c > 80 ? "alert" : "normal"} /><Metric label="Pressure" value={selectedAsset.event.pressure_bar} unit="bar" /><Metric label="Current" value={selectedAsset.event.current_a} unit="A" status={selectedAsset.event.current_a > 10 ? "alert" : "normal"} /></div>
        </> : <div className="empty">Run an approved local scenario to view its maintenance evidence.</div>}</article>
      </section>

      {selectedAsset && <section className="evidence-grid">
        <article className="panel"><div className="panel__head"><div><p className="eyebrow">WHY THIS WAS FLAGGED</p><h2>Evidence factors</h2></div><span className="quiet">not a diagnosis</span></div><div className="factors">{selectedAsset.advisory.factors.map((factor) => <div className="factor" key={factor.metric}><div><strong>{factor.metric}</strong><span>{factor.rationale}</span></div><div className="factor__bar"><i style={{ width: `${factor.contribution}%` }} /></div><b>{factor.contribution}%</b></div>)}</div></article>
        <article className="panel action-card"><p className="eyebrow">HUMAN VALIDATION REQUIRED</p><h2>Recommended next step</h2><p>{selectedAsset.advisory.validation_step}</p><div className="action-card__note"><strong>Limitations</strong><span>{selectedAsset.advisory.limitations}</span></div><button className="export" onClick={() => navigator.clipboard?.writeText(`${selectedAsset.event.asset_id}: ${selectedAsset.advisory.summary}\nValidation: ${selectedAsset.advisory.validation_step}`)}>Copy maintenance note</button></article>
      </section>}

      <footer><span>PredictaLine local demo · Synthetic equipment telemetry only</span><span>Replay runs: {metrics?.replay_runs ?? 0} · Rejected topics: {metrics?.rejected_topics ?? 0}</span></footer>
    </main>
  );
}
