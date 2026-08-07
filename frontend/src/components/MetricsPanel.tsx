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
import { SPECIALIST_LABELS } from "@/lib/specialists";
import { SEVERITY_LABELS } from "@/lib/findings";
import type { AnalysisStatus, Metrics, Severity, Specialist } from "@/lib/api/types";

const STATUS_LABELS: Record<AnalysisStatus, string> = {
  pending: "Pendientes",
  running: "En curso",
  completed: "Completados",
  completed_with_errors: "Completados con errores",
  failed: "Fallidos",
};

// Pipeline order, not insertion order — a run's own status only ever
// moves forward through this sequence, so this is the order a person
// scanning the breakdown expects to read it in.
const STATUS_ORDER: AnalysisStatus[] = [
  "pending",
  "running",
  "completed",
  "completed_with_errors",
  "failed",
];

const STATUS_COLORS: Record<AnalysisStatus, string> = {
  pending: "bg-ink-faint",
  running: "bg-accent",
  completed: "bg-ok",
  completed_with_errors: "bg-high",
  failed: "bg-critical",
};

const SPECIALIST_ORDER: Specialist[] = [
  "security",
  "performance",
  "design_patterns",
  "best_practices",
];

// critical → low, same order FindingsReport groups findings in.
const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low"];

const SEVERITY_COLORS: Record<Severity, string> = {
  critical: "bg-critical",
  high: "bg-high",
  medium: "bg-medium",
  low: "bg-low",
};

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "Sin datos todavía";
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  return `${(seconds / 60).toFixed(1)} min`;
}

interface BarEntry {
  key: string;
  label: string;
  count: number;
  color: string;
}

function buildStatusEntries(counts: Metrics["by_status"]): BarEntry[] {
  return STATUS_ORDER.filter((status) => (counts[status] ?? 0) > 0).map((status) => ({
    key: status,
    label: STATUS_LABELS[status],
    count: counts[status]!,
    color: STATUS_COLORS[status],
  }));
}

function buildSpecialistEntries(counts: Metrics["findings_by_specialist"]): BarEntry[] {
  return SPECIALIST_ORDER.filter((specialist) => (counts[specialist] ?? 0) > 0).map((specialist) => ({
    key: specialist,
    label: SPECIALIST_LABELS[specialist],
    count: counts[specialist]!,
    color: "bg-accent/70",
  }));
}

function buildSeverityEntries(counts: Metrics["findings_by_severity"]): BarEntry[] {
  return SEVERITY_ORDER.filter((severity) => (counts[severity] ?? 0) > 0).map((severity) => ({
    key: severity,
    label: SEVERITY_LABELS[severity],
    count: counts[severity]!,
    color: SEVERITY_COLORS[severity],
  }));
}

/**
 * Each bar's width is relative to the largest count in its own group
 * (not to the group's total), so the biggest contributor always reads
 * as a full bar and the rest scale against it — more useful for
 * spotting "what dominates" at a glance than a stacked-to-100% layout.
 */
function BarList({ entries }: { entries: BarEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-ink-muted text-sm">Sin datos todavía.</p>;
  }
  const max = Math.max(...entries.map((entry) => entry.count));
  return (
    <ul className="flex flex-col gap-2.5">
      {entries.map((entry) => (
        <li key={entry.key} className="flex flex-col gap-1">
          <div className="flex items-center justify-between text-[12.5px]">
            <span className="text-ink-body">{entry.label}</span>
            <span className="text-ink font-mono font-medium">{entry.count}</span>
          </div>
          <div className="bg-line-soft h-1.5 overflow-hidden rounded-full">
            <div
              className={`h-full rounded-full ${entry.color}`}
              style={{ width: `${(entry.count / max) * 100}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

interface MetricsPanelProps {
  // Bump this (e.g. after an approval decision resumes the graph) to force
  // a refetch — a plain snapshot otherwise never updates itself.
  refreshKey?: number;
}

export function MetricsPanel({ refreshKey }: MetricsPanelProps = {}) {
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
  }, [refreshKey]);

  if (error) {
    return <p className="text-danger-ink text-sm">{error}</p>;
  }

  if (!metrics) {
    return <p className="text-ink-muted text-sm">Cargando métricas…</p>;
  }

  const statusEntries = buildStatusEntries(metrics.by_status);
  const specialistEntries = buildSpecialistEntries(metrics.findings_by_specialist);
  const severityEntries = buildSeverityEntries(metrics.findings_by_severity);

  return (
    <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
      <div className="bg-sunken border-line-soft flex flex-col gap-3 rounded-[11px] border px-4 py-[15px]">
        <div>
          <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
            Análisis totales
          </span>
          <p className="text-ink text-2xl font-semibold">{metrics.total_analysis_requests}</p>
        </div>
        <BarList entries={statusEntries} />
      </div>

      <div className="bg-sunken border-line-soft flex flex-col gap-3 rounded-[11px] border px-4 py-[15px]">
        <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
          Hallazgos por especialidad
        </span>
        <BarList entries={specialistEntries} />
      </div>

      <div className="bg-sunken border-line-soft flex flex-col gap-3 rounded-[11px] border px-4 py-[15px]">
        <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
          Hallazgos por severidad
        </span>
        <BarList entries={severityEntries} />
      </div>

      <div className="bg-sunken border-line-soft flex flex-col gap-3 rounded-[11px] border px-4 py-[15px]">
        <div>
          <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
            Tiempo medio de análisis
          </span>
          <p className="text-ink text-2xl font-semibold">
            {formatDuration(metrics.average_analysis_seconds)}
          </p>
        </div>
        <div>
          <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
            PRs comentados
          </span>
          <p className="text-ink text-2xl font-semibold">{metrics.pr_comments_posted}</p>
        </div>
      </div>
    </div>
  );
}
