/**
 * Thin fetch wrapper for the Nexus backend (backend/app/api/*.py).
 *
 * NEXT_PUBLIC_API_URL defaults to http://localhost:8000 — uvicorn's own
 * default port, since app/main.py doesn't pin one explicitly (it's
 * launched as `uvicorn app.main:app`). Override it via .env.local if
 * your backend runs elsewhere.
 */

import type {
  AnalysisRequest,
  AnalysisRequestCreate,
  AnalysisRequestUpdatePayload,
  Approval,
  ApprovalCreatePayload,
  ApprovalDecisionPayload,
  Metrics,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Thrown for any non-2xx response. Carries the parsed `detail` field
 * FastAPI puts on both HTTPException responses (404, 409) and Pydantic
 * validation errors (422) — callers need to tell "Approval not found"
 * apart from "Approval already decided" apart from a raw status code.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? null);
  }

  return response.json() as Promise<T>;
}

// --- Analysis requests -----------------------------------------------

export function createAnalysisRequest(
  data: AnalysisRequestCreate,
): Promise<AnalysisRequest> {
  return request<AnalysisRequest>("/analysis-requests/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getAnalysisRequest(id: number): Promise<AnalysisRequest> {
  return request<AnalysisRequest>(`/analysis-requests/${id}`);
}

export function listAnalysisRequests(): Promise<AnalysisRequest[]> {
  return request<AnalysisRequest[]>("/analysis-requests/");
}

export function updateAnalysisRequest(
  id: number,
  data: AnalysisRequestUpdatePayload,
): Promise<AnalysisRequest> {
  return request<AnalysisRequest>(`/analysis-requests/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// --- Approvals ---------------------------------------------------------

export function createApproval(data: ApprovalCreatePayload): Promise<Approval> {
  return request<Approval>("/approvals/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getApproval(id: number): Promise<Approval> {
  return request<Approval>(`/approvals/${id}`);
}

export function listApprovals(filter?: { analysisRequestId?: number }): Promise<Approval[]> {
  const query =
    filter?.analysisRequestId !== undefined
      ? `?analysis_request_id=${filter.analysisRequestId}`
      : "";
  return request<Approval[]>(`/approvals/${query}`);
}

/**
 * Submits a human decision for a pending approval. The response still
 * carries status "pending" — human_approval_node is what flips it once
 * the graph actually resumes (see backend/app/api/approvals.py) — so
 * callers shouldn't treat this response as confirmation the resume
 * finished, only that it was accepted and scheduled.
 */
export function decideApproval(
  id: number,
  data: ApprovalDecisionPayload,
): Promise<Approval> {
  return request<Approval>(`/approvals/${id}/decision`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// --- Metrics -------------------------------------------------------------

/**
 * A point-in-time snapshot, not a live view — unlike AgentTrace/
 * ApprovalPanel there's no WebSocket involved here, just a plain fetch
 * the caller can re-run (e.g. on an interval, or a manual refresh
 * button) if they want it to stay current.
 */
export function getMetrics(): Promise<Metrics> {
  return request<Metrics>("/metrics/");
}
