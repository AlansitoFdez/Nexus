"""Human-in-the-loop node: pauses the graph for approval before posting
findings to a real PR.

Uses LangGraph's interrupt() to freeze execution here, with the full
graph state checkpointed to Redis (via the AsyncRedisSaver configured
when the graph is compiled in Fase 2.12). The graph resumes later via
Command(resume=...), invoked with the same thread_id, from whichever
endpoint handles the human's decision.

Trigger condition changed from the ticket domain (there: any
pending_actions existed) to this domain: post_to_pr was explicitly
True on the AnalysisRequest — never inferred by an LLM (Fase 2.3).

Unlike the ticket domain's version, this node also persists a real
Approval row (analysis_request_id-linked) so the pending decision is
queryable via GET /approvals/{id} while the graph sits paused —
not just visible inside the ephemeral interrupt() payload.

Approval lookup, not blind creation, before interrupt(): interrupt()
doesn't pause mid-function the way it reads — when the graph resumes,
LangGraph re-runs this node's whole function from the top, and only
the interrupt() call itself "remembers" the resume value instead of
pausing again. Anything before that call genuinely runs twice. Blindly
calling repo.create() there created a second Approval row on every
resume, leaving the first stuck at "pending" forever with nothing left
to update it. Reusing an existing pending row instead makes this node
safe to re-execute — exactly once gets created, no matter how many
times LangGraph replays the function around the interrupt.
"""

from langgraph.types import interrupt

from app.agents.state import CodeReviewState
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestNotFoundError,
    AnalysisRequestRepository,
)
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.approval import ApprovalCreate, ApprovalUpdate

PROPOSED_ACTION = "Publicar el informe de hallazgos como comentario en el PR"


async def human_approval_node(state: CodeReviewState) -> dict:
    """Pauses the graph and waits for a human decision, only if post_to_pr is set.

    If post_to_pr is False, the user never asked for this action in the
    first place — the node is a no-op, no Approval is created and no
    interrupt happens.
    """
    if not state.get("post_to_pr"):
        return {"node_history": ["human_approval"]}

    db = SessionLocal()
    try:
        repo = ApprovalRepository(db, AnalysisRequestRepository(db))
        pending = next(
            (a for a in repo.get_by_analysis_request_id(state["analysis_request_id"]) if a.status == "pending"),
            None,
        )
        approval = pending or repo.create(ApprovalCreate(
            analysis_request_id=state["analysis_request_id"],
            proposed_action=PROPOSED_ACTION,
        ))
    except AnalysisRequestNotFoundError:
        return {
            "error": f"AnalysisRequest {state['analysis_request_id']} not found during human_approval_node",
            "node_history": ["human_approval"],
        }
    finally:
        db.close()

    decision = interrupt({
        "analysis_request_id": state["analysis_request_id"],
        "approval_id": approval.id,
        "proposed_action": approval.proposed_action,
        "final_report": state.get("final_report"),
    })

    db = SessionLocal()
    try:
        repo = ApprovalRepository(db, AnalysisRequestRepository(db))
        repo.update(approval.id, ApprovalUpdate(status="approved" if decision == "approved" else "rejected"))
    finally:
        db.close()

    if decision == "approved":
        return {"node_history": ["human_approval"]}
    else:
        return {
            "post_to_pr": False,
            "node_history": ["human_approval"],
        }
