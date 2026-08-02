"use client";

/**
 * The dashboard's summary view: findings by specialty, average analysis
 * time, and PR comments actually posted (backend/app/repositories/
 * metrics_repository.py). A plain fetch-on-mount, not a live view — an
 * aggregated snapshot doesn't need a WebSocket the way a single
 * in-progress run does.
 */

import { useEffect, useState } from "react";
import { getMetrics } from "@/lib/api/client";
import type { Metrics } from "@/lib/api/types";

const SPECIALIST_LABELS: Record<string, string> = {
  security: "Seguridad",
  performance: "Rendimiento",
  design_patterns: "Patrones de diseño",
  best_practices: "Buenas prácticas",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "Pendientes",
  running: "En curso",
  completed: "Completados",
  completed_with_errors: "Completados con errores",
  failed: "Fallidos",
};

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "Sin datos todavía";
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  return `${(seconds / 60).toFixed(1)} min`;
}

function CountList({ counts, labels }: { counts: Partial<Record<string, number>>; labels: Record<string, string> }) {
  const entries = Object.entries(counts);
  if (entries.length === 0) {
    return <p className="text-sm text-gray-500">Sin datos todavía.</p>;
  }
  return (
    <ul className="space-y-1">
      {entries.map(([key, count]) => (
        <li key={key} className="flex justify-between text-sm">
          <span className="text-gray-700">{labels[key] ?? key}</span>
          <span className="font-medium text-gray-900">{count}</span>
        </li>
      ))}
    </ul>
  );
}

export function MetricsPanel() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getMetrics()
      .then((result) => {
        if (!cancelled) setMetrics(result);
      })
      .catch(() => {
        if (!cancelled) setError("No se pudieron cargar las métricas.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  if (!metrics) {
    return <p className="text-sm text-gray-500">Cargando métricas…</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border p-4">
        <p className="text-sm text-gray-500">Análisis totales</p>
        <p className="text-2xl font-semibold">{metrics.total_analysis_requests}</p>
        <div className="mt-3">
          <CountList counts={metrics.by_status} labels={STATUS_LABELS} />
        </div>
      </div>

      <div className="rounded-lg border p-4">
        <p className="mb-2 text-sm text-gray-500">Hallazgos por especialidad</p>
        <CountList counts={metrics.findings_by_specialist} labels={SPECIALIST_LABELS} />
      </div>

      <div className="rounded-lg border p-4">
        <p className="mb-2 text-sm text-gray-500">Hallazgos por severidad</p>
        <CountList counts={metrics.findings_by_severity} labels={{}} />
      </div>

      <div className="rounded-lg border p-4">
        <p className="text-sm text-gray-500">Tiempo medio de análisis</p>
        <p className="text-2xl font-semibold">{formatDuration(metrics.average_analysis_seconds)}</p>
        <p className="mt-3 text-sm text-gray-500">PRs comentados</p>
        <p className="text-2xl font-semibold">{metrics.pr_comments_posted}</p>
      </div>
    </div>
  );
}
