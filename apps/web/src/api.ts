export type Priority = "routine" | "watch" | "plan" | "urgent_review";

export interface EvidenceFactor {
  metric: string;
  observed: number;
  baseline: number;
  contribution: number;
  rationale: string;
}

export interface AssetSnapshot {
  event: {
    asset_id: string;
    line: string;
    scenario: string;
    occurred_at: string;
    vibration_mm_s: number;
    temperature_c: number;
    pressure_bar: number;
    current_a: number;
    runtime_hours: number;
  };
  advisory: {
    risk_score: number;
    priority: Priority;
    model_anomaly_score: number;
    trend_score: number;
    inspection_window: string;
    summary: string;
    validation_step: string;
    limitations: string;
    factors: EvidenceFactor[];
  };
}

export interface FleetSummary {
  generated_at: string;
  total_assets: number;
  priority_counts: Record<string, number>;
  assets: AssetSnapshot[];
}

export interface MetricsSnapshot {
  telemetry_events: number;
  maintenance_advisories: number;
  replay_runs: number;
  rejected_topics: number;
}

export interface ReplayResult {
  scenario: string;
  generated_events: number;
  fleet: FleetSummary;
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, init);
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

export const api = {
  fleet: () => request<FleetSummary>("/api/fleet"),
  metrics: () => request<MetricsSnapshot>("/api/metrics"),
  scenarios: () => request<{ scenarios: string[] }>("/api/scenarios"),
  replay: (scenario: string) => request<ReplayResult>(`/api/replay/${scenario}`, { method: "POST" })
};
