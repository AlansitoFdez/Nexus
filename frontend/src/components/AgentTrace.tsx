"use client";

import { deriveAgentTrace, type SpecialistStatus } from "@/lib/agent-trace";
import { SPECIALIST_LABELS } from "@/lib/specialists";
import type { WSEvent } from "@/lib/api/types";

const STATUS_STYLES: Record<SpecialistStatus, string> = {
  running: "border-blue-400 bg-blue-50 text-blue-700 animate-pulse",
  done: "border-green-500 bg-green-50 text-green-700",
  failed: "border-red-500 bg-red-50 text-red-700",
};

interface AgentTraceProps {
  events: WSEvent[];
  isConnected: boolean;
}

/**
 * Shows every specialist the router selected, transitioning live from
 * "running" (as soon as router_node's chunk names them, all at once —
 * they really do start together, via the Fase 2.4 fan-out) to "done" or
 * "failed" as each one's own chunk arrives.
 *
 * events/isConnected are passed down from page.tsx's single
 * useAnalysisRequestSocket call (Fase 4.6 review) rather than opened
 * here directly — this component used to open its own socket
 * connection to the same analysis_request_id ApprovalPanel was already
 * watching, doubling the traffic and each side only ever seeing events
 * that arrived after it individually mounted.
 */
export function AgentTrace({ events, isConnected }: AgentTraceProps) {
  const trace = deriveAgentTrace(events);

  if (trace.length === 0) {
    return (
      <p className="text-sm text-gray-500">
        {isConnected ? "Esperando a que el router elija especialistas…" : "Conectando…"}
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-3">
      {trace.map((entry) => (
        <div
          key={entry.specialist}
          className={`rounded-lg border px-3 py-2 text-sm font-medium ${STATUS_STYLES[entry.status]}`}
        >
          {SPECIALIST_LABELS[entry.specialist]}
          {entry.status === "done" && entry.findingsCount !== undefined && (
            <span>
              {" · "}
              {entry.findingsCount} hallazgo{entry.findingsCount === 1 ? "" : "s"}
            </span>
          )}
          {entry.status === "failed" && <span> · error</span>}
        </div>
      ))}
    </div>
  );
}
