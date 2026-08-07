/**
 * Pure helpers for rendering findings as grouped, filterable cards —
 * kept separate from the component for the same reason agent-trace.ts
 * is: testable without mounting anything.
 */

import type { Finding, Severity } from "@/lib/api/types";

// Mirrors backend/app/agents/nodes/synthesizer_node.py's own SEVERITY_ORDER —
// keep both in sync if the domain ever grows a fifth severity.
const SEVERITIES: Severity[] = ["critical", "high", "medium", "low"];

export const SEVERITY_LABELS: Record<Severity, string> = {
  critical: "Crítico",
  high: "Alto",
  medium: "Medio",
  low: "Bajo",
};

const REPORT_SEPARATOR = "\n\n---\n\n";

/**
 * synthesizer_node.py always builds final_report as
 * `f"{narrative}\n\n---\n\n{deterministic_section}"` — splitting on that
 * exact separator recovers just the LLM's prose summary, discarding the
 * deterministic findings listing that would otherwise duplicate what the
 * finding cards already show. Falls back to the whole string if the
 * separator is ever missing, rather than showing nothing.
 */
export function extractSummary(finalReport: string): string {
  const index = finalReport.indexOf(REPORT_SEPARATOR);
  return index === -1 ? finalReport.trim() : finalReport.slice(0, index).trim();
}

export interface SeverityGroup {
  severity: Severity;
  findings: Finding[];
}

/** Only severities that actually have findings, in critical → low order. */
export function groupBySeverity(findings: Finding[]): SeverityGroup[] {
  return SEVERITIES.map((severity) => ({
    severity,
    findings: findings.filter((finding) => finding.severity === severity),
  })).filter((group) => group.findings.length > 0);
}
