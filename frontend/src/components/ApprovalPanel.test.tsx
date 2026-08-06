import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ApprovalPanel } from "./ApprovalPanel";
import { decideApproval, listApprovals, getAnalysisRequest, ApiError } from "@/lib/api/client";
import type { AnalysisRequest, Approval, WSEvent } from "@/lib/api/types";

vi.mock("@/lib/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api/client")>();
  return {
    ...actual,
    decideApproval: vi.fn(),
    listApprovals: vi.fn(),
    getAnalysisRequest: vi.fn(),
  };
});

const decideApprovalMock = vi.mocked(decideApproval);
const listApprovalsMock = vi.mocked(listApprovals);
const getAnalysisRequestMock = vi.mocked(getAnalysisRequest);

const FAKE_APPROVAL: Approval = {
  id: 9,
  analysis_request_id: 1,
  proposed_action: "Comentar hallazgos en el PR",
  status: "pending",
  claimed_at: null,
  decided_at: null,
  created_at: "2026-08-06T00:00:00Z",
};

const FAKE_ANALYSIS_REQUEST: AnalysisRequest = {
  id: 1,
  source_type: "github_repo",
  repo_url: "https://github.com/owner/repo",
  pasted_code: null,
  review_request: "seguridad",
  post_to_pr: true,
  pr_number: 3,
  status: "pending",
  final_report: "Informe final",
  pr_comment_url: null,
  findings: [],
  created_at: "2026-08-06T00:00:00Z",
  updated_at: null,
};

function liveEvent(overrides: Partial<Extract<WSEvent, { type: "approval_required" }>> = {}): WSEvent {
  return {
    type: "approval_required",
    analysis_request_id: 1,
    approval_id: 9,
    proposed_action: "aprobar esto",
    final_report: null,
    ...overrides,
  };
}

describe("ApprovalPanel", () => {
  beforeEach(() => {
    decideApprovalMock.mockReset();
    listApprovalsMock.mockReset();
    getAnalysisRequestMock.mockReset();
    listApprovalsMock.mockResolvedValue([]);
  });

  // --- Fallback (REST) states, no live event ---------------------------

  it("shows a loading message while checking for a pending approval", () => {
    listApprovalsMock.mockReturnValue(new Promise(() => {}));

    render(<ApprovalPanel analysisRequestId={1} events={[]} />);

    expect(screen.getByText("Comprobando si hay una aprobación pendiente…")).toBeInTheDocument();
  });

  it("shows 'nothing pending' when the fallback finds no approval at all", async () => {
    listApprovalsMock.mockResolvedValue([]);

    render(<ApprovalPanel analysisRequestId={1} events={[]} />);

    expect(await screen.findByText("Ninguna aprobación pendiente por ahora.")).toBeInTheDocument();
  });

  it("shows 'nothing pending' when the fallback fetch itself fails", async () => {
    listApprovalsMock.mockRejectedValue(new Error("network down"));

    render(<ApprovalPanel analysisRequestId={1} events={[]} />);

    expect(await screen.findByText("Ninguna aprobación pendiente por ahora.")).toBeInTheDocument();
  });

  it("shows a 'decision in flight' message when the pending approval is already claimed", async () => {
    listApprovalsMock.mockResolvedValue([{ ...FAKE_APPROVAL, claimed_at: "2026-08-06T00:05:00Z" }]);

    render(<ApprovalPanel analysisRequestId={1} events={[]} />);

    expect(await screen.findByText("Tu decisión se está procesando…")).toBeInTheDocument();
  });

  it("shows the approval UI from the fallback when an unclaimed pending approval exists", async () => {
    listApprovalsMock.mockResolvedValue([FAKE_APPROVAL]);
    getAnalysisRequestMock.mockResolvedValue(FAKE_ANALYSIS_REQUEST);

    render(<ApprovalPanel analysisRequestId={1} events={[]} />);

    expect(await screen.findByText("Comentar hallazgos en el PR")).toBeInTheDocument();
    expect(screen.getByText("Informe final")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Aprobar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Rechazar" })).toBeInTheDocument();
  });

  // --- Live WebSocket event -----------------------------------------------

  it("prefers a live approval_required event over the REST fallback, without waiting on it", () => {
    listApprovalsMock.mockReturnValue(new Promise(() => {}));

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);

    expect(screen.getByText("aprobar esto")).toBeInTheDocument();
  });

  it("uses the most recent approval_required event when there are several", () => {
    const events = [
      liveEvent({ approval_id: 1, proposed_action: "primero" }),
      liveEvent({ approval_id: 2, proposed_action: "segundo" }),
    ];

    render(<ApprovalPanel analysisRequestId={1} events={events} />);

    expect(screen.getByText("segundo")).toBeInTheDocument();
    expect(screen.queryByText("primero")).not.toBeInTheDocument();
  });

  // --- Submitting a decision -----------------------------------------------

  it("submits an 'approved' decision and shows a confirmation", async () => {
    const user = userEvent.setup();
    decideApprovalMock.mockResolvedValue(FAKE_APPROVAL);

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);
    await user.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(decideApprovalMock).toHaveBeenCalledWith(9, { decision: "approved" });
    expect(await screen.findByText("Decisión enviada — el análisis continuó.")).toBeInTheDocument();
  });

  it("submits a 'rejected' decision and shows a confirmation", async () => {
    const user = userEvent.setup();
    decideApprovalMock.mockResolvedValue(FAKE_APPROVAL);

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);
    await user.click(screen.getByRole("button", { name: "Rechazar" }));

    expect(decideApprovalMock).toHaveBeenCalledWith(9, { decision: "rejected" });
    expect(await screen.findByText("Decisión enviada — el análisis continuó.")).toBeInTheDocument();
  });

  it("shows the ApiError message when submitting a decision fails", async () => {
    const user = userEvent.setup();
    decideApprovalMock.mockRejectedValue(new ApiError(409, "La aprobación ya fue decidida"));

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);
    await user.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(await screen.findByText("La aprobación ya fue decidida")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Aprobar" })).toBeInTheDocument();
  });

  it("shows a generic error message for a non-ApiError failure", async () => {
    const user = userEvent.setup();
    decideApprovalMock.mockRejectedValue(new Error("network down"));

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);
    await user.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(
      await screen.findByText("No se pudo enviar la decisión, inténtalo de nuevo."),
    ).toBeInTheDocument();
  });

  it("disables both buttons while a decision is being submitted", async () => {
    const user = userEvent.setup();
    let resolveDecide: (value: Approval) => void = () => {};
    decideApprovalMock.mockReturnValue(
      new Promise((resolve) => {
        resolveDecide = resolve;
      }),
    );

    render(<ApprovalPanel analysisRequestId={1} events={[liveEvent()]} />);
    await user.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(screen.getByRole("button", { name: "Aprobar" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Rechazar" })).toBeDisabled();

    resolveDecide(FAKE_APPROVAL);
  });

  // --- "resumed" detection (human_approval_node's own node_finished) ------

  it("shows the confirmation and calls onResolved once human_approval finishes", async () => {
    const onResolved = vi.fn();
    const events = [liveEvent(), { type: "node_finished", node: "human_approval" } as WSEvent];

    render(<ApprovalPanel analysisRequestId={1} events={events} onResolved={onResolved} />);

    expect(await screen.findByText("Decisión enviada — el análisis continuó.")).toBeInTheDocument();
    expect(onResolved).toHaveBeenCalledTimes(1);
  });

  it("also treats a finished post_comment node as the graph having resumed", async () => {
    const events = [liveEvent(), { type: "node_finished", node: "post_comment" } as WSEvent];

    render(<ApprovalPanel analysisRequestId={1} events={events} />);

    expect(await screen.findByText("Decisión enviada — el análisis continuó.")).toBeInTheDocument();
  });

  it("does not treat an unrelated node finishing as the graph having resumed", () => {
    const events = [liveEvent(), { type: "node_finished", node: "entry" } as WSEvent];

    render(<ApprovalPanel analysisRequestId={1} events={events} />);

    expect(screen.getByRole("button", { name: "Aprobar" })).toBeInTheDocument();
  });
});
