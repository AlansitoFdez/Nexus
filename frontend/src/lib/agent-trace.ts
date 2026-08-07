/**
 * Pure derivation of "which specialists are running/done/failed right
 * now" from the raw WSEvent stream — kept separate from the React
 * component so this logic is testable on its own, without mounting
 * anything or mocking a WebSocket.
 */

import type { Specialist, WSEvent } from "@/lib/api/types";

export type SpecialistStatus = "running" | "done" | "failed";

export interface AgentTraceEntry {
  specialist: Specialist;
  status: SpecialistStatus;
  findingsCount?: number;
}

export function deriveAgentTrace(events: WSEvent[]): AgentTraceEntry[] {
  const order: Specialist[] = [];
  const bySpecialist = new Map<Specialist, AgentTraceEntry>();

  for (const event of events) {
    if (event.type === "specialists_started") {
      for (const specialist of event.specialists) {
        if (!bySpecialist.has(specialist)) {
          order.push(specialist);
          bySpecialist.set(specialist, { specialist, status: "running" });
        }
      }
    } else if (event.type === "specialist_finished") {
      if (!bySpecialist.has(event.specialist)) {
        order.push(event.specialist);
      }
      bySpecialist.set(event.specialist, {
        specialist: event.specialist,
        status: event.failed ? "failed" : "done",
        findingsCount: event.findings_count,
      });
    }
  }

  return order.map((specialist) => bySpecialist.get(specialist)!);
}

/**
 * Derives the three-step "router → especialistas → síntesis" pipeline
 * progress the dashboard shows above the specialist cards.
 *
 * There's no direct "router finished" or "specialists phase finished"
 * event on the wire — router's own completion is only ever signaled by
 * specialists_started firing (ws_events.build_event has no separate
 * signal for it, see that module's docstring), and "all specialists
 * settled" has to be derived from deriveAgentTrace's own per-specialist
 * status. synthesis is the one phase with a direct signal: node_finished
 * for "synthesizer".
 *
 * run_failed's own `node` field carries the raw graph node name
 * (e.g. "router_node", "entry_node" — see ws_events.py's build_event),
 * not one of these three phase keys, so a failure can't be matched to a
 * phase by name. Instead, whichever phase hadn't completed yet when the
 * failure arrived is the one marked "failed" — that's the phase that was
 * actually in flight, regardless of which underlying node raised it.
 */
export type Phase = "router" | "specialists" | "synthesis";
export type PhaseStatus = "pending" | "active" | "done" | "failed";

export interface PhaseState {
  phase: Phase;
  status: PhaseStatus;
}

const PHASE_ORDER: Phase[] = ["router", "specialists", "synthesis"];

export function derivePhases(events: WSEvent[]): PhaseState[] {
  const trace = deriveAgentTrace(events);
  const done: Record<Phase, boolean> = {
    router: events.some((event) => event.type === "specialists_started"),
    specialists: trace.length > 0 && trace.every((entry) => entry.status !== "running"),
    synthesis: events.some(
      (event) => event.type === "node_finished" && event.node === "synthesizer",
    ),
  };
  const hasFailed = events.some((event) => event.type === "run_failed");
  const currentIndex = PHASE_ORDER.findIndex((phase) => !done[phase]);

  return PHASE_ORDER.map((phase, index) => {
    if (done[phase]) return { phase, status: "done" };
    if (index === currentIndex) return { phase, status: hasFailed ? "failed" : "active" };
    return { phase, status: "pending" };
  });
}
