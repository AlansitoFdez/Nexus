import { describe, expect, it } from "vitest";
import { deriveAgentTrace, derivePhases } from "./agent-trace";
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

describe("derivePhases", () => {
  it("shows router as active and the rest pending before anything happens", () => {
    expect(derivePhases([])).toEqual([
      { phase: "router", status: "active" },
      { phase: "specialists", status: "pending" },
      { phase: "synthesis", status: "pending" },
    ]);
  });

  it("moves to specialists active once the router names them", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance"] },
    ];

    expect(derivePhases(events)).toEqual([
      { phase: "router", status: "done" },
      { phase: "specialists", status: "active" },
      { phase: "synthesis", status: "pending" },
    ]);
  });

  it("keeps specialists active while any of them is still running", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance"] },
      { type: "specialist_finished", specialist: "security", findings_count: 1, failed: false },
    ];

    expect(derivePhases(events)[1]).toEqual({ phase: "specialists", status: "active" });
  });

  it("moves to synthesis active once every specialist has settled", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 1, failed: false },
    ];

    expect(derivePhases(events)).toEqual([
      { phase: "router", status: "done" },
      { phase: "specialists", status: "done" },
      { phase: "synthesis", status: "active" },
    ]);
  });

  // A specialist marked "failed" still counts as settled — the pipeline
  // moves on to synthesis regardless, same as failed_specialists never
  // blocking the graph on the backend side.
  it("treats a failed specialist as settled, same as a done one", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 0, failed: true },
    ];

    expect(derivePhases(events)[1]).toEqual({ phase: "specialists", status: "done" });
  });

  it("marks synthesis as done once its node_finished event arrives", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 1, failed: false },
      { type: "node_finished", node: "synthesizer" },
    ];

    expect(derivePhases(events)).toEqual([
      { phase: "router", status: "done" },
      { phase: "specialists", status: "done" },
      { phase: "synthesis", status: "done" },
    ]);
  });

  it("marks the phase that was in flight as failed, not the one named in run_failed", () => {
    // node here is the raw graph node ("entry_node"), which isn't one of
    // the three phase keys at all — router is what was actually pending.
    const events: WSEvent[] = [{ type: "run_failed", node: "entry_node", message: "boom" }];

    expect(derivePhases(events)).toEqual([
      { phase: "router", status: "failed" },
      { phase: "specialists", status: "pending" },
      { phase: "synthesis", status: "pending" },
    ]);
  });

  it("marks specialists as failed when the run dies mid fan-out, leaving synthesis pending", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance"] },
      { type: "specialist_finished", specialist: "security", findings_count: 1, failed: false },
      { type: "run_failed", node: "runner", message: "boom" },
    ];

    expect(derivePhases(events)).toEqual([
      { phase: "router", status: "done" },
      { phase: "specialists", status: "failed" },
      { phase: "synthesis", status: "pending" },
    ]);
  });
});
