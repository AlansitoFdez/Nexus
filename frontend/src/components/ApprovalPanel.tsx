"use client";

/**
 * The dashboard's human-in-the-loop gate: shows the proposed PR comment
 * (backend/app/agents/nodes/human_approval_node.py's PROPOSED_ACTION +
 * the synthesizer's final_report) and lets the user approve or reject
 * it, mirroring the real gate — nothing posts to a real PR without this.
 *
 * Two ways this panel learns about a pending approval:
 * - Live: the "approval_required" WebSocket event, taken straight from
 *   human_approval_node's interrupt() payload — has everything
 *   (approval_id, proposed_action, final_report) in one shot.
 * - Fallback: if the user loads this page after the interrupt already
 *   fired (so there's no live event to catch), GET /approvals/ filtered
 *   by analysis_request_id recovers the approval_id and proposed_action,
 *   and GET /analysis-requests/{id} supplies final_report (not part of
 *   ApprovalResponse). Only ever needed once per mount, and only if no
 *   live event beat it to the punch.
 */

import { useEffect, useState } from "react";
import { useAnalysisRequestSocket } from "@/lib/hooks/useWebSocket";
import { decideApproval, listApprovals, getAnalysisRequest, ApiError } from "@/lib/api/client";
import type { ApprovalDecisionValue, WSEvent } from "@/lib/api/types";

interface ApprovalPanelProps {
  analysisRequestId: number;
  onResolved?: () => void;
}

interface ApprovalContext {
  approvalId: number;
  proposedAction: string;
  finalReport: string | null;
}

type FallbackState =
  | { status: "loading" }
  | { status: "none" }
  | { status: "found"; context: ApprovalContext };

function isApprovalRequired(
  event: WSEvent,
): event is Extract<WSEvent, { type: "approval_required" }> {
  return event.type === "approval_required";
}

export function ApprovalPanel({ analysisRequestId, onResolved }: ApprovalPanelProps) {
  const { events } = useAnalysisRequestSocket(analysisRequestId);
  const [fallback, setFallback] = useState<FallbackState>({ status: "loading" });
  const [decisionSubmitted, setDecisionSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setFallback({ status: "loading" });

    async function loadFallback() {
      try {
        // In practice at most one row: human_approval_node creates
        // exactly one Approval per graph run, and each AnalysisRequest
        // maps to exactly one run.
        const approvals = await listApprovals({ analysisRequestId });
        const pending = approvals.find((approval) => approval.status === "pending");
        if (!pending) {
          if (!cancelled) setFallback({ status: "none" });
          return;
        }

        const analysisRequest = await getAnalysisRequest(analysisRequestId);
        if (!cancelled) {
          setFallback({
            status: "found",
            context: {
              approvalId: pending.id,
              proposedAction: pending.proposed_action,
              finalReport: analysisRequest.final_report,
            },
          });
        }
      } catch {
        if (!cancelled) setFallback({ status: "none" });
      }
    }

    loadFallback();
    return () => {
      cancelled = true;
    };
  }, [analysisRequestId]);

  const liveEvent = [...events].reverse().find(isApprovalRequired);

  const context: ApprovalContext | null = liveEvent
    ? {
        approvalId: liveEvent.approval_id,
        proposedAction: liveEvent.proposed_action,
        finalReport: liveEvent.final_report,
      }
    : fallback.status === "found"
      ? fallback.context
      : null;

  // human_approval_node's own "node_finished" fires once the graph has
  // actually resumed past the gate — the definitive signal the decision
  // took effect, independent of whether decideApproval()'s response came
  // back cleanly.
  const resumed = events.some(
    (event) =>
      event.type === "node_finished" &&
      (event.node === "human_approval" || event.node === "post_comment"),
  );

  // Fires once, right when the graph actually resumes past the gate — the
  // metrics snapshot (pr_comments_posted in particular) only changes once
  // post_comment_node runs, so this is the signal MetricsPanel needs to
  // know it's worth a refetch.
  useEffect(() => {
    if (resumed) onResolved?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumed]);

  if (!liveEvent && fallback.status === "loading") {
    return <p className="text-sm text-gray-500">Comprobando si hay una aprobación pendiente…</p>;
  }

  if (!context) {
    return <p className="text-sm text-gray-500">Ninguna aprobación pendiente por ahora.</p>;
  }

  if (resumed || decisionSubmitted) {
    return (
      <p className="text-sm text-green-700">Decisión enviada — el análisis continuó.</p>
    );
  }

  async function handleDecision(decision: ApprovalDecisionValue) {
    if (!context) return;
    setSubmitting(true);
    setError(null);
    try {
      await decideApproval(context.approvalId, { decision });
      setDecisionSubmitted(true);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "No se pudo enviar la decisión, inténtalo de nuevo.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-3 rounded-lg border border-amber-400 bg-amber-50 p-4">
      <p className="font-medium text-amber-900">{context.proposedAction}</p>

      {context.finalReport && (
        <pre className="whitespace-pre-wrap rounded border bg-white p-3 text-sm text-gray-700">
          {context.finalReport}
        </pre>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => handleDecision("approved")}
          disabled={submitting}
          className="rounded bg-green-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          Aprobar
        </button>
        <button
          type="button"
          onClick={() => handleDecision("rejected")}
          disabled={submitting}
          className="rounded bg-red-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          Rechazar
        </button>
      </div>
    </div>
  );
}
