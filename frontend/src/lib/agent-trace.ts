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
