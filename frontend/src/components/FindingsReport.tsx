"use client";

import { useState } from "react";
import { extractSummary, groupBySeverity, SEVERITY_LABELS } from "@/lib/findings";
import { SPECIALIST_LABELS } from "@/lib/specialists";
import type { Finding, Severity } from "@/lib/api/types";

const SEVERITY_DOT: Record<Severity, string> = {
  critical: "bg-critical",
  high: "bg-high",
  medium: "bg-medium",
  low: "bg-low",
};

const SEVERITY_TEXT: Record<Severity, string> = {
  critical: "text-critical",
  high: "text-high",
  medium: "text-medium",
  low: "text-low",
};

const SEVERITY_BORDER_L: Record<Severity, string> = {
  critical: "border-l-critical",
  high: "border-l-high",
  medium: "border-l-medium",
  low: "border-l-low",
};

const SEVERITY_CHIP_ACTIVE: Record<Severity, string> = {
  critical: "border-critical/30 bg-critical/10 text-critical",
  high: "border-high/30 bg-high/10 text-high",
  medium: "border-medium/30 bg-medium/10 text-medium",
  low: "border-low/30 bg-low/10 text-low",
};

const CHIP_INACTIVE = "border-line text-ink-muted";

interface FindingsReportProps {
  finalReport: string;
  findings: Finding[];
}

/**
 * Replaces the raw final_report <pre> dump with the LLM's narrative
 * (extracted via extractSummary, see lib/findings.ts for why the split
 * is safe) plus the findings themselves as severity-grouped cards, read
 * straight from AnalysisRequest.findings — not re-parsed out of the
 * markdown deterministic section, which says the same thing in prose.
 */
export function FindingsReport({ finalReport, findings }: FindingsReportProps) {
  const [filter, setFilter] = useState<Severity | "all">("all");
  const groups = groupBySeverity(findings);
  const visibleGroups = filter === "all" ? groups : groups.filter((group) => group.severity === filter);
  const summary = extractSummary(finalReport);

  return (
    <div className="flex flex-col gap-[18px]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-ink-dim text-[12.5px]">
          {findings.length} hallazgo{findings.length === 1 ? "" : "s"}
        </span>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setFilter("all")}
            className={`rounded-[7px] border px-2.5 py-[5px] text-[11.5px] font-medium ${
              filter === "all" ? "border-line-strong bg-active text-ink" : CHIP_INACTIVE
            }`}
          >
            Todas <span className="font-mono">{findings.length}</span>
          </button>
          {groups.map((group) => (
            <button
              key={group.severity}
              type="button"
              onClick={() => setFilter(group.severity)}
              className={`flex items-center gap-1.5 rounded-[7px] border px-2.5 py-[5px] text-[11.5px] font-medium ${
                filter === group.severity ? SEVERITY_CHIP_ACTIVE[group.severity] : CHIP_INACTIVE
              }`}
            >
              <span className={`size-1.5 rounded-[2px] ${SEVERITY_DOT[group.severity]}`} />
              {SEVERITY_LABELS[group.severity]} <span className="font-mono">{group.findings.length}</span>
            </button>
          ))}
        </div>
      </div>

      {summary && (
        <div className="bg-sunken border-line-soft flex flex-col gap-2 rounded-[11px] border px-4 py-[15px]">
          <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
            Resumen del sintetizador
          </span>
          <p className="text-ink-body max-w-[78ch] text-[13.5px] leading-[1.65] whitespace-pre-wrap">
            {summary}
          </p>
        </div>
      )}

      {findings.length === 0 ? (
        <p className="text-ink-muted text-sm">No se encontraron hallazgos.</p>
      ) : (
        <div className="flex flex-col gap-[18px]">
          {visibleGroups.map((group) => (
            <div key={group.severity} className="flex flex-col gap-2.5">
              <div className="flex items-center gap-2.5">
                <span className={`size-[7px] rounded-[2px] ${SEVERITY_DOT[group.severity]}`} />
                <span
                  className={`font-mono text-[10.5px] tracking-[0.09em] uppercase ${SEVERITY_TEXT[group.severity]}`}
                >
                  {SEVERITY_LABELS[group.severity]}
                </span>
                <span className="text-ink-dim font-mono text-[10.5px]">{group.findings.length}</span>
                <span className="bg-line-soft h-px flex-1" />
              </div>

              {group.findings.map((finding) => (
                <article
                  key={finding.id}
                  className={`bg-sunken border-line-soft flex flex-col gap-2.5 rounded-[10px] border border-l-2 px-[15px] py-3.5 ${SEVERITY_BORDER_L[group.severity]}`}
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded-[5px] border px-[7px] py-[3px] font-mono text-[10px] font-medium tracking-[0.08em] uppercase ${SEVERITY_CHIP_ACTIVE[group.severity]}`}
                    >
                      {SEVERITY_LABELS[group.severity]}
                    </span>
                    <span className="text-ink-muted font-mono text-[10.5px]">
                      {SPECIALIST_LABELS[finding.specialist]}
                    </span>
                    {finding.file_path && (
                      <span className="text-ink-faint font-mono text-[10.5px]">{finding.file_path}</span>
                    )}
                  </div>

                  <p className="text-ink max-w-[84ch] text-[13.5px] leading-[1.6]">{finding.description}</p>

                  {finding.suggestion && (
                    <div className="bg-canvas border-line-soft flex flex-col gap-1 rounded-[8px] border px-3 py-2.5">
                      <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
                        Sugerencia
                      </span>
                      <p className="text-ink-body max-w-[84ch] text-[12.5px] leading-[1.6]">
                        {finding.suggestion}
                      </p>
                    </div>
                  )}
                </article>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
