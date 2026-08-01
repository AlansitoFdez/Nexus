"""Security specialist node: analyzes code for security vulnerabilities.

First of four specialist nodes (2.5-2.8), all sharing the same shape:
LLM + with_structured_output() using SPECIALIST_MODEL (denser reasoning
than ROUTER_MODEL), invoked in parallel via the Send() fan-out from
route_after_router — this node only ever sees the payload it was given,
never the full CodeReviewState.

Persists each finding immediately via FindingRepository as soon as it's
produced, same pattern as entry_node/router_node writing to their
repositories mid-graph rather than waiting for the whole run to finish.

A specialist's own failure (LLM error, persistence error) does NOT set
state["error"] — that field is reserved for entry_node/router_node,
which run sequentially before the fan-out and whose failure should halt
the whole graph. Losing one specialist out of four shouldn't cancel the
other three's real findings, so failures here go to failed_specialists
instead — its own operator.add reducer, for the same reason findings
needs one: multiple specialists can fail concurrently.
"""

from langchain_groq import ChatGroq

from app.agents.schemas import SpecialistOutput
from app.config import settings
from app.database import SessionLocal
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.repositories.finding_repository import FindingRepository
from app.schemas.finding import FindingCreate

SECURITY_PROMPT = """Eres un especialista en seguridad revisando código. \
Busca vulnerabilidades reales: inyección SQL, secretos hardcodeados, \
validación de entrada ausente, control de acceso débil, dependencias \
inseguras, y similares.

Petición del usuario sobre qué revisar: {review_request}

Código a analizar:
{code}

Si no encuentras ningún problema de seguridad real, devuelve una lista \
de findings vacía — no inventes hallazgos para rellenar."""


async def security_agent(payload: dict) -> dict:
    """Analyzes code_content for security issues and persists findings.

    payload is the dict a Send() carried to this node — only
    code_content, review_request and analysis_request_id, never the
    full CodeReviewState (see route_after_router, Fase 2.4).
    """
    llm = ChatGroq(model=settings.SPECIALIST_MODEL, temperature=0)
    structured_llm = llm.with_structured_output(SpecialistOutput)

    try:
        output = await structured_llm.ainvoke(
            SECURITY_PROMPT.format(
                review_request=payload["review_request"],
                code=payload["code_content"],
            )
        )
    except Exception:
        return {
            "failed_specialists": ["security"],
            "node_history": ["security_agent"],
        }

    db = SessionLocal()
    try:
        repo = FindingRepository(db, AnalysisRequestRepository(db))
        persisted = []
        for finding in output.findings:
            saved = repo.create(FindingCreate(
                analysis_request_id=payload["analysis_request_id"],
                specialist="security",
                severity=finding.severity,
                description=finding.description,
                file_path=finding.file_path,
                suggestion=finding.suggestion,
            ))
            persisted.append({
                "id": saved.id,
                "specialist": "security",
                "severity": saved.severity,
                "description": saved.description,
                "file_path": saved.file_path,
                "suggestion": saved.suggestion,
            })
    except Exception:
        return {
            "failed_specialists": ["security"],
            "node_history": ["security_agent"],
        }
    finally:
        db.close()

    return {
        "findings": persisted,
        "node_history": ["security_agent"],
    }