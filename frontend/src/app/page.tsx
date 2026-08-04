"use client";

import { useState } from "react";
import { NewAnalysisForm } from "@/components/NewAnalysisForm";
import { AgentTrace } from "@/components/AgentTrace";
import { ApprovalPanel } from "@/components/ApprovalPanel";
import { MetricsPanel } from "@/components/MetricsPanel";
import { useAnalysisRequestSocket } from "@/lib/hooks/useWebSocket";
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

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-8 p-8">
      <header>
        <h1 className="text-4xl font-bold">Nexus</h1>
        <p className="mt-2 text-gray-500">Orquestador multi-agente</p>
      </header>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Nuevo análisis</h2>
        <NewAnalysisForm onCreated={setActiveRequest} />
      </section>

      {activeRequest && (
        <>
          <section className="space-y-3">
            <h2 className="text-lg font-semibold">
              Especialistas — solicitud #{activeRequest.id}
            </h2>
            {/* Keyed by id: a fresh AnalysisRequest must remount these,
                not just receive a new prop — ApprovalPanel's own
                decisionSubmitted state would otherwise leak across runs. */}
            <AgentTrace key={activeRequest.id} events={events} isConnected={isConnected} />
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold">Aprobación</h2>
            <ApprovalPanel
              key={activeRequest.id}
              analysisRequestId={activeRequest.id}
              events={events}
              onResolved={() => setMetricsRefreshToken((token) => token + 1)}
            />
          </section>
        </>
      )}

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Métricas</h2>
        <MetricsPanel refreshKey={metricsRefreshToken} />
      </section>
    </main>
  );
}
