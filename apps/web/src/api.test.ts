import { afterEach, describe, expect, it, vi } from "vitest";

import { api, type FleetSummary, type MetricsSnapshot, type ReplayResult } from "./api";

const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

function jsonResponse<T>(body: T, ok = true): Response {
  return {
    ok,
    json: vi.fn().mockResolvedValue(body),
    text: vi.fn().mockResolvedValue("Local demo request failed")
  } as unknown as Response;
}

afterEach(() => {
  fetchMock.mockReset();
});

describe("PredictaLine API client", () => {
  it("retrieves fleet and metrics snapshots from the local API", async () => {
    const fleet: FleetSummary = {
      generated_at: "2026-08-18T00:00:00Z",
      total_assets: 1,
      priority_counts: { routine: 1 },
      assets: []
    };
    const metrics: MetricsSnapshot = {
      telemetry_events: 12,
      maintenance_advisories: 0,
      replay_runs: 1,
      rejected_topics: 0
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(fleet)).mockResolvedValueOnce(jsonResponse(metrics));

    await expect(api.fleet()).resolves.toEqual(fleet);
    await expect(api.metrics()).resolves.toEqual(metrics);
    expect(fetchMock).toHaveBeenNthCalledWith(1, "/api/fleet", undefined);
    expect(fetchMock).toHaveBeenNthCalledWith(2, "/api/metrics", undefined);
  });

  it("replays a selected deterministic scenario using the POST contract", async () => {
    const replay: ReplayResult = {
      scenario: "bearing_wear",
      generated_events: 18,
      fleet: {
        generated_at: "2026-08-18T00:00:00Z",
        total_assets: 1,
        priority_counts: { urgent_review: 1 },
        assets: []
      }
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(replay));

    await expect(api.replay("bearing_wear")).resolves.toEqual(replay);
    expect(fetchMock).toHaveBeenCalledWith("/api/replay/bearing_wear", { method: "POST" });
  });

  it("surfaces a local API error when a scenario cannot be replayed", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ detail: "Unknown scenario" }, false));

    await expect(api.replay("unknown")).rejects.toThrow("Local demo request failed");
  });
});
