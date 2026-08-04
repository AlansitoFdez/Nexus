"""Terminal failure node: persists status="failed" when entry_node or
router_node errors out before the specialist fan-out even starts.

Ticket domain's escalation_node handed off to a human support team —
there's no equivalent here (Fase 2.11 conclusion). What IS still
needed is a single place that leaves the AnalysisRequest honestly
terminal instead of stuck at "running" forever, which is what would
happen if the early-failure edges went straight to END without
persisting anything.

Specialist-level failures never reach this node: those are captured
per-specialist in failed_specialists (Fase 2.5) and still let the
graph continue to synthesizer_node, which reports them honestly
without treating the whole run as a failure.

This node is already the graph's own terminal error handler — nothing
routes on its output (its only edge goes straight to END) — so if its
own write fails for a reason other than "not found", there's no
further node to hand off to. Logged rather than raised: runner.py's
own last-resort handler is the outer safety net for exactly this kind
of unexpected failure.
"""

import logging

from app.agents.state import CodeReviewState
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestRepository,
    AnalysisRequestNotFoundError,
)
from app.schemas.analysis_request import AnalysisRequestUpdate

logger = logging.getLogger(__name__)


async def failure_node(state: CodeReviewState) -> dict:
    db = SessionLocal()
    try:
        repo = AnalysisRequestRepository(db)
        repo.update(state["analysis_request_id"], AnalysisRequestUpdate(status="failed"))
    except AnalysisRequestNotFoundError:
        pass
    except Exception:
        logger.exception(
            "Failed to persist status=\"failed\" for AnalysisRequest %s in failure_node",
            state["analysis_request_id"],
        )
    finally:
        db.close()

    return {"node_history": ["failure"]}