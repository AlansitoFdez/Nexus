import { describe, expect, it } from "vitest";
import { deriveAgentTrace } from "./agent-trace";
import type { WSEvent } from "./api/types";

describe("deriveAgentTrace", () => {
  it("returns an empty trace for no events", () => {
    expect(deriveAgentTrace([])).toEqual([]);
  });

  it("marks every named specialist as running when the fan-out starts", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance"] },
    ];

    expect(deriveAgentTrace(events)).toEqual([
      { specialist: "security", status: "running" },
      { specialist: "performance", status: "running" },
    ]);
  });

  it("transitions a specialist from running to done with its findings count", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 2, failed: false },
    ];

    expect(deriveAgentTrace(events)).toEqual([
      { specialist: "security", status: "done", findingsCount: 2 },
    ]);
  });

  it("marks a specialist as failed instead of done when its own chunk failed", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["performance"] },
      { type: "specialist_finished", specialist: "performance", findings_count: 0, failed: true },
    ];

    expect(deriveAgentTrace(events)).toEqual([
      { specialist: "performance", status: "failed", findingsCount: 0 },
    ]);
  });

  it("still shows a specialist that finished without ever seeing its own start event", () => {
    // Not expected from the real backend (specialists_started always
    // fires first, from router_node's own chunk) but the function
    // shouldn't silently drop a specialist just because of stream
    // ordering it didn't control.
    const events: WSEvent[] = [
      { type: "specialist_finished", specialist: "design_patterns", findings_count: 1, failed: false },
    ];

    expect(deriveAgentTrace(events)).toEqual([
      { specialist: "design_patterns", status: "done", findingsCount: 1 },
    ]);
  });

  it("preserves first-seen order across multiple specialists finishing out of order", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance", "best_practices"] },
      { type: "specialist_finished", specialist: "best_practices", findings_count: 0, failed: false },
      { type: "specialist_finished", specialist: "security", findings_count: 3, failed: false },
    ];

    expect(deriveAgentTrace(events).map((entry) => entry.specialist)).toEqual([
      "security",
      "performance",
      "best_practices",
    ]);
  });

  it("ignores event types that aren't about specialist progress", () => {
    const events: WSEvent[] = [
      { type: "node_finished", node: "entry" },
      { type: "run_failed", node: "router_node", message: "boom" },
      {
        type: "approval_required",
        analysis_request_id: 1,
        approval_id: 1,
        proposed_action: "publicar en el PR",
        final_report: null,
      },
    ];

    expect(deriveAgentTrace(events)).toEqual([]);
  });
});
