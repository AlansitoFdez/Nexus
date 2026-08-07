"""Factory for a code-review specialist's node function (Fase 4.1
review — SOLID/design pass).

Every specialist needs the exact same shape: LLM + structured output
using SPECIALIST_MODEL, persisting each finding immediately via
FindingRepository, and routing its own failure to failed_specialists
rather than halting the graph (Fase 2.5) — only the prompt and the
specialist's own name vary. make_specialist_node(name, prompt) builds
that shared shape once; graph.py calls it once per entry in
agents/specialists.SPECIALISTS instead of importing four
near-identical hand-written files.

Kept in its own module, separate from agents/specialists.py: this file
needs SpecialistOutput from agents/schemas.py, and agents/schemas.py
itself needs SPECIALISTS (for RouterDecision's dynamic Literal) — so
agents/specialists.py stays a zero-dependency registry precisely so it
can be imported from schemas.py without a cycle back through here.

Both except blocks now log the real exception (Fase 5.1 review) —
before, a specialist's failure vanished completely: only its name
showed up in failed_specialists, with no record anywhere of what
actually went wrong. Safe to log the raw exception here, unlike
state["error"] elsewhere in the graph: this never becomes a
client-facing WebSocket event (see ws_events.build_event), only
failed_specialists' bare name does.
"""

import logging

from langchain_groq import ChatGroq

from app.agents.schemas import SpecialistOutput
from app.config import settings
from app.database import SessionLocal
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.finding import FindingCreate

logger = logging.getLogger(__name__)


def make_specialist_node(name: str, prompt: str):
    """Builds the node function for one specialist.

    payload is the dict a Send() carried to this node (see
    route_after_router, Fase 2.4) — only code_content, review_request
    and analysis_request_id, never the full CodeReviewState.
    """

    async def specialist_node(payload: dict) -> dict:
        llm = ChatGroq(model=settings.SPECIALIST_MODEL, api_key=settings.GROQ_API_KEY, temperature=0)
        structured_llm = llm.with_structured_output(SpecialistOutput)

        try:
            output = await structured_llm.ainvoke(
                prompt.format(
                    review_request=payload["review_request"],
                    code=payload["code_content"],
                )
            )
        except Exception:
            logger.error("Specialist %s failed during the LLM call", name, exc_info=True)
            return {"failed_specialists": [name], "node_history": [f"{name}_agent"]}

        db = SessionLocal()
        try:
            repo = FindingRepository(db, AnalysisRequestRepository(db))
            persisted = []
            for finding in output.findings:
                saved = repo.create(FindingCreate(
                    analysis_request_id=payload["analysis_request_id"],
                    specialist=name,
                    severity=finding.severity,
                    description=finding.description,
                    file_path=finding.file_path,
                    suggestion=finding.suggestion,
                ))
                persisted.append({
                    "id": saved.id,
                    "specialist": name,
                    "severity": saved.severity,
                    "description": saved.description,
                    "file_path": saved.file_path,
                    "suggestion": saved.suggestion,
                })
        except Exception:
            logger.error("Specialist %s failed to persist its findings", name, exc_info=True)
            return {"failed_specialists": [name], "node_history": [f"{name}_agent"]}
        finally:
            db.close()

        return {"findings": persisted, "node_history": [f"{name}_agent"]}

    return specialist_node
