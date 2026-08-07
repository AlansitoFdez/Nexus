"use client";

import {
  deriveAgentTrace,
  derivePhases,
  type PhaseStatus,
  type SpecialistStatus,
} from "@/lib/agent-trace";
import { SPECIALIST_LABELS } from "@/lib/specialists";
import type { WSEvent } from "@/lib/api/types";

const PHASE_LABELS = {
  router: "router",
  specialists: "especialistas",
  synthesis: "síntesis",
} as const;

const PHASE_DOT: Record<PhaseStatus, string> = {
  pending: "bg-line-strong",
  active: "bg-accent animate-status-pulse",
  done: "bg-ok",
  failed: "bg-critical",
};

const PHASE_PILL: Record<PhaseStatus, string> = {
  pending: "border-line bg-sunken text-ink-dim",
  active: "border-accent/30 bg-accent/[0.07] text-ink-body",
  done: "border-line-soft bg-sunken text-ink-body",
  failed: "border-critical/30 bg-critical/5 text-danger-ink",
};

const CARD_STYLES: Record<
  SpecialistStatus,
  { border: string; bg: string; dot: string; statusColor: string }
> = {
  running: {
    border: "border-accent/30",
    bg: "bg-accent/5",
    dot: "bg-accent animate-status-pulse",
    statusColor: "text-accent",
  },
  done: {
    border: "border-line-soft",
    bg: "bg-sunken",
    dot: "bg-ok",
    statusColor: "text-ink-muted",
  },
  failed: {
    border: "border-critical/28",
    bg: "bg-critical/5",
    dot: "bg-critical",
    statusColor: "text-danger-ink",
  },
};

interface AgentTraceProps {
  events: WSEvent[];
  isConnected: boolean;
}

/**
 * Shows every specialist the router selected, transitioning live from
 * "running" (as soon as router_node's chunk names them, all at once —
 * they really do start together, via the Fase 2.4 fan-out) to "done" or
 * "failed" as each one's own chunk arrives, plus a router → especialistas
 * → síntesis phase stepper above the cards.
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
  const phases = derivePhases(events);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        {phases.map((phase, index) => (
          <div key={phase.phase} className="flex items-center gap-2">
            <div
              className={`flex items-center gap-[7px] rounded-full border py-[5px] pr-[11px] pl-[9px] ${PHASE_PILL[phase.status]}`}
            >
              <span className={`size-[7px] rounded-full ${PHASE_DOT[phase.status]}`} />
              <span className="font-mono text-[11px]">{PHASE_LABELS[phase.phase]}</span>
            </div>
            {index < phases.length - 1 && <span className="bg-line-soft h-px w-[22px]" />}
          </div>
        ))}
      </div>

      {trace.length === 0 ? (
        <p className="text-ink-muted text-sm">
          {isConnected ? "Esperando a que el router elija especialistas…" : "Conectando…"}
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
          {trace.map((entry) => {
            const style = CARD_STYLES[entry.status];
            return (
              <div
                key={entry.specialist}
                className={`relative flex flex-col gap-[9px] overflow-hidden rounded-[11px] border px-3.5 py-[13px] ${style.border} ${style.bg}`}
              >
                <div className="flex items-center justify-between gap-2.5">
                  <span className="text-ink text-[13px] font-medium">
                    {SPECIALIST_LABELS[entry.specialist]}
                  </span>
                  <span className={`size-[7px] rounded-full ${style.dot}`} />
                </div>
                <span className={`font-mono text-[11.5px] ${style.statusColor}`}>
                  {entry.status === "running" && "en curso…"}
                  {entry.status === "done" &&
                    entry.findingsCount !== undefined &&
                    `hecho · ${entry.findingsCount} hallazgo${entry.findingsCount === 1 ? "" : "s"}`}
                  {entry.status === "failed" && "error · el especialista no respondió"}
                </span>
                {entry.status === "running" && (
                  <div className="bg-line-soft absolute right-0 bottom-0 left-0 h-0.5 overflow-hidden">
                    <div className="bg-accent animate-sweep h-full w-[30%]" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
