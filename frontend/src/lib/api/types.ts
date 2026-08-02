/**
 * TypeScript types mirroring the backend's Pydantic schemas
 * (backend/app/schemas/*.py, backend/app/agents/schemas.py).
 *
 * Kept as plain interfaces/unions, hand-written against the real schemas
 * rather than generated — with only 8 endpoints total, a codegen step
 * (e.g. openapi-typescript) would be more ceremony than the problem
 * needs right now. Revisit if the API surface grows enough that this
 * file drifting out of sync becomes a real risk.
 */

export type SourceType = "github_repo" | "pasted_code";

export type AnalysisStatus =
  | "pending"
  | "running"
  | "completed"
  | "completed_with_errors"
  | "failed";

export type ApprovalStatus = "pending" | "approved" | "rejected";

// Mirrors RouterDecision.agents_to_run's Literal in agents/schemas.py —
// also the name of every specialist node in graph.py.
export type Specialist =
  | "security"
  | "performance"
  | "design_patterns"
  | "best_practices";

// Mirrors SpecialistFinding.severity's Literal in agents/schemas.py.
export type Severity = "critical" | "high" | "medium" | "low";

export type ApprovalDecisionValue = "approved" | "rejected";

export interface Finding {
  id: number;
  analysis_request_id: number;
  specialist: Specialist;
  severity: Severity;
  file_path: string | null;
  description: string;
  suggestion: string | null;
  created_at: string; // ISO 8601, as returned by FastAPI's datetime serialization
}

export interface AnalysisRequest {
  id: number;
  source_type: SourceType;
  repo_url: string | null;
  pasted_code: string | null;
  review_request: string;
  post_to_pr: boolean;
  pr_number: number | null;
  status: AnalysisStatus;
  final_report: string | null;
  findings: Finding[];
  created_at: string;
  updated_at: string | null;
}

/**
 * Payload for POST /analysis-requests/.
 *
 * A discriminated union instead of one loose interface with optional
 * fields, on purpose: it encodes the same two rules the backend enforces
 * with @model_validator in schemas/analysis_request.py —
 * "exactly one of repo_url/pasted_code, matching source_type" and
 * "post_to_pr=true requires source_type='github_repo' and pr_number" —
 * at compile time, so a form that tries to build an invalid combination
 * fails to type-check here instead of round-tripping to the API to
 * discover a 422.
 */
export type AnalysisRequestCreate =
  | {
      source_type: "pasted_code";
      pasted_code: string;
      review_request: string;
      post_to_pr?: false;
    }
  | ({
      source_type: "github_repo";
      repo_url: string;
      review_request: string;
    } & (
      | { post_to_pr?: false; pr_number?: number | null }
      | { post_to_pr: true; pr_number: number }
    ));

export interface AnalysisRequestUpdatePayload {
  status?: AnalysisStatus;
  final_report?: string | null;
}

export interface Approval {
  id: number;
  analysis_request_id: number;
  proposed_action: string;
  status: ApprovalStatus;
  decided_at: string | null;
  created_at: string;
}

export interface ApprovalCreatePayload {
  analysis_request_id: number;
  proposed_action: string;
}

export interface ApprovalDecisionPayload {
  decision: ApprovalDecisionValue;
}

// --- WebSocket events ---------------------------------------------------
//
// Mirrors backend/app/agents/ws_events.py's build_event() output exactly —
// that's the one place on the backend that decides what shape these take,
// so this union should only change in lockstep with that file. Plain-text
// messages (a few human-readable notices entry_node/post_comment_node send
// directly, e.g. "Procesando análisis...") also arrive on the same socket
// but aren't part of this union — see useWebSocket's JSON.parse fallback.

export type NodeName = "entry" | "synthesizer" | "human_approval" | "post_comment" | "failure";

export type WSEvent =
  | { type: "specialists_started"; specialists: Specialist[] }
  | {
      type: "specialist_finished";
      specialist: Specialist;
      findings_count: number;
      failed: boolean;
    }
  | { type: "node_finished"; node: NodeName }
  | { type: "run_failed"; node: string; message: string }
  | {
      type: "approval_required";
      analysis_request_id: number;
      approval_id: number;
      proposed_action: string;
      final_report: string | null;
    };
