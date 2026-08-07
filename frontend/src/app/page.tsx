"use client";

import { useEffect, useState } from "react";
import { NewAnalysisForm } from "@/components/NewAnalysisForm";
import { AgentTrace } from "@/components/AgentTrace";
import { ApprovalPanel } from "@/components/ApprovalPanel";
import { FindingsReport } from "@/components/FindingsReport";
import { MetricsPanel } from "@/components/MetricsPanel";
import { Panel } from "@/components/Panel";
import { useAnalysisRequestSocket } from "@/lib/hooks/useWebSocket";
import { getAnalysisRequest } from "@/lib/api/client";
import type { AnalysisRequest } from "@/lib/api/types";

export default function Home() {
  const [activeRequest, setActiveRequest] = useState<AnalysisRequest | null>(null);
  const [metricsRefreshToken, setMetricsRefreshToken] = useState(0);

  // Opened once here instead of once each inside AgentTrace and
  // ApprovalPanel (Fase 4.6 review) — both watch the same
  // analysis_request_id, so two independent sockets doubled the
  // traffic and meant each side only ever saw events that arrived
  // after it individually mounted.
  const { events, isConnected } = useAnalysisRequestSocket(activeRequest?.id ?? null);

  const activeRequestId = activeRequest?.id ?? null;
  const synthesizerFinished = events.some(
    (event) => event.type === "node_finished" && event.node === "synthesizer",
  );
  const runFailedEvent = events.find((event) => event.type === "run_failed");

  // synthesizer_node is what writes final_report, and it always runs —
  // human_approval_node/post_comment_node self-nullify when post_to_pr
  // is false, but the report already exists by the time synthesizer
  // itself finishes. Without this, final_report was only ever visible
  // through ApprovalPanel, which only renders anything at all when
  // post_to_pr is true — a plain pasted-code review with no PR involved
  // showed the specialists' finding counts and then nothing else.
  // Depends on the id (a stable primitive), not activeRequest itself:
  // the fetch below calls setActiveRequest, which would otherwise
  // retrigger this same effect on every completion.
  useEffect(() => {
    if (!synthesizerFinished || activeRequestId === null) return;
    let cancelled = false;
    getAnalysisRequest(activeRequestId).then((request) => {
      if (!cancelled) setActiveRequest(request);
    });
    return () => {
      cancelled = true;
    };
  }, [synthesizerFinished, activeRequestId]);

  return (
    <main className="flex flex-1 flex-col items-center px-7 pt-6 pb-10">
      <div className="flex w-full max-w-[1360px] flex-col gap-[22px]">
        <header className="border-line flex flex-wrap items-end justify-between gap-6 border-b pb-[18px]">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center gap-2.5">
              <span className="bg-accent size-[9px] rounded-full shadow-[0_0_12px_var(--color-accent)]" />
              <h1 className="text-[21px] font-semibold tracking-[-0.02em]">Nexus</h1>
              <span className="text-ink-dim border-line rounded border px-1.5 py-[3px] font-mono text-[10px] tracking-[0.09em] uppercase">
                self-hosted
              </span>
            </div>
            <p className="text-ink-muted text-[13px]">
              Revisión de código multi-agente · orquestador
            </p>
          </div>

          {/* Only rendered once a run exists: with no activeRequest the hook
              never opens a socket at all, so a permanent "desconectado" would
              be reporting a problem that isn't one. */}
          {activeRequest && (
            <div className="text-ink-muted flex items-center gap-[7px] font-mono text-[11px]">
              <span className={`size-1.5 rounded-full ${isConnected ? "bg-ok" : "bg-ink-faint"}`} />
              {isConnected ? "websocket conectado" : "websocket desconectado"}
            </div>
          )}
        </header>

        <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-[372px_minmax(0,1fr)]">
          {/* Sticky only from lg up: below that the grid is a single column,
              and a sticky form would pin itself over the results underneath it. */}
          <div className="lg:sticky lg:top-6">
            <Panel title="Nuevo análisis">
              <NewAnalysisForm onCreated={setActiveRequest} />
            </Panel>
          </div>

          <div className="flex min-w-0 flex-col gap-5">
            {activeRequest ? (
              <>
                <Panel
                  title="Especialistas"
                  meta={
                    <span className="text-ink-dim border-line rounded-[5px] border px-[7px] py-0.5 font-mono text-[11px]">
                      solicitud #{activeRequest.id}
                    </span>
                  }
                >
                  {/* Keyed by id: a fresh AnalysisRequest must remount these,
                      not just receive a new prop — ApprovalPanel's own
                      decisionSubmitted state would otherwise leak across runs. */}
                  <AgentTrace key={activeRequest.id} events={events} isConnected={isConnected} />
                </Panel>

                {runFailedEvent ? (
                  <Panel title="El análisis falló" tone="danger">
                    <div className="flex flex-col gap-2.5">
                      <p className="text-warn-ink/80 text-[13.5px]">
                        El grafo se detuvo antes de terminar, así que no hay informe para esta
                        solicitud. Los hallazgos de los especialistas que sí acabaron se conservan.
                      </p>
                      <p className="text-ink-muted bg-canvas border-line rounded-[9px] border px-3 py-[11px] font-mono text-xs whitespace-pre-wrap">
                        run_failed · nodo &quot;{runFailedEvent.node}&quot;: {runFailedEvent.message}
                      </p>
                    </div>
                  </Panel>
                ) : (
                  activeRequest.final_report && (
                    <Panel title="Informe final">
                      <FindingsReport
                        key={activeRequest.id}
                        finalReport={activeRequest.final_report}
                        findings={activeRequest.findings}
                      />
                    </Panel>
                  )
                )}

                <Panel title="Aprobación">
                  <ApprovalPanel
                    key={activeRequest.id}
                    analysisRequestId={activeRequest.id}
                    events={events}
                    onResolved={() => setMetricsRefreshToken((token) => token + 1)}
                  />
                </Panel>
              </>
            ) : (
              <section className="border-line-strong bg-sunken flex flex-col items-center gap-3 rounded-[14px] border border-dashed px-8 py-[46px] text-center">
                <div className="flex gap-1.5">
                  <span className="bg-line-strong size-2 rounded-full" />
                  <span className="bg-line-strong size-2 rounded-full" />
                  <span className="bg-line-strong size-2 rounded-full" />
                  <span className="bg-line-strong size-2 rounded-full" />
                </div>
                <h2 className="text-[15px] font-semibold">Ningún análisis en curso</h2>
                <p className="text-ink-dim max-w-[46ch] text-[13px]">
                  Describe qué quieres revisar y el router elegirá qué especialistas activar. Los
                  resultados aparecerán aquí en vivo.
                </p>
              </section>
            )}

            <Panel title="Métricas">
              <MetricsPanel refreshKey={metricsRefreshToken} />
            </Panel>
          </div>
        </div>

        <p className="text-ink-faint font-mono text-[10.5px]">
          nexus · instancia local · un solo desarrollador
        </p>
      </div>
    </main>
  );
}
