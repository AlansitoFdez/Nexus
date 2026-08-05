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

import { useEffect, useRef, useState } from "react";
import { decideApproval, listApprovals, getAnalysisRequest, ApiError } from "@/lib/api/client";
import type { ApprovalDecisionValue, WSEvent } from "@/lib/api/types";

interface ApprovalPanelProps {
  analysisRequestId: number;
  // Passed down from page.tsx's single useAnalysisRequestSocket call
  // (Fase 4.6 review) instead of opened here directly — this component
  // used to open its own socket connection to the same
  // analysis_request_id AgentTrace was already watching.
  events: WSEvent[];
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
  // A decision is already in flight for this analysis_request_id (someone
  // already POSTed to /decision — claimed_at is set, but status is still
  // "pending" until human_approval_node actually resumes) — distinct from
  // "none" so this reload doesn't show the approve/reject buttons again
  // for a decision that's already on its way.
  | { status: "claimed" }
  | { status: "found"; context: ApprovalContext };

function isApprovalRequired(
  event: WSEvent,
): event is Extract<WSEvent, { type: "approval_required" }> {
  return event.type === "approval_required";
}

export function ApprovalPanel({ analysisRequestId, events, onResolved }: ApprovalPanelProps) {
  const [fallback, setFallback] = useState<FallbackState>({ status: "loading" });
  const [decisionSubmitted, setDecisionSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Resets fallback to "loading" during render, not inside the effect
  // below — same react-hooks/set-state-in-effect fix as useWebSocket.ts,
  // and the same React-recommended pattern for "clear state when a
  // prop changes." In practice page.tsx always keys this component by
  // analysisRequestId, so React already remounts it (and this branch
  // never actually fires) — kept anyway so this component stays
  // correct for a future caller that passes a new analysisRequestId
  // without remounting.
  const [watchedAnalysisRequestId, setWatchedAnalysisRequestId] = useState(analysisRequestId);
  if (analysisRequestId !== watchedAnalysisRequestId) {
    setWatchedAnalysisRequestId(analysisRequestId);
    setFallback({ status: "loading" });
  }

  useEffect(() => {
    let cancelled = false;

    async function loadFallback() {
      try {
        // In practice at most one row: human_approval_node creates
        // exactly one Approval per graph run, and each AnalysisRequest
        // maps to exactly one run.
        const approvals = await listApprovals({ analysisRequestId });
        const pending = approvals.find(
          (approval) => approval.status === "pending" && approval.claimed_at === null,
        );
        if (!pending) {
          const alreadyClaimed = approvals.some(
            (approval) => approval.status === "pending" && approval.claimed_at !== null,
          );
          if (!cancelled) setFallback(alreadyClaimed ? { status: "claimed" } : { status: "none" });
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

  // onResolved is a fresh function identity on every render of page.tsx
  // (an inline arrow there) — listing it as a dependency below would
  // re-run this effect on every render, not just when resumed actually
  // flips. Stashing the latest callback in a ref sidesteps that: the
  // effect only needs to depend on resumed itself, and reading
  // onResolvedRef.current always sees the latest onResolved without
  // needing to be a dependency (Fase 6 review — replaces a silenced
  // react-hooks/exhaustive-deps warning with the actual fix for it).
  const onResolvedRef = useRef(onResolved);
  useEffect(() => {
    onResolvedRef.current = onResolved;
  });

  // Fires once, right when the graph actually resumes past the gate — the
  // metrics snapshot (pr_comments_posted in particular) only changes once
  // post_comment_node runs, so this is the signal MetricsPanel needs to
  // know it's worth a refetch.
  useEffect(() => {
    if (resumed) onResolvedRef.current?.();
  }, [resumed]);

  if (!liveEvent && fallback.status === "loading") {
    return <p className="text-sm text-gray-500">Comprobando si hay una aprobación pendiente…</p>;
  }

  if (!context) {
    if (fallback.status === "claimed") {
      return <p className="text-sm text-gray-500">Tu decisión se está procesando…</p>;
    }
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
