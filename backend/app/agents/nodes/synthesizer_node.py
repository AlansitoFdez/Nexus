"""Synthesizer node: combines every specialist's findings into the final report.

Two-part design, deliberately split by responsibility:

1. A deterministic section (pure Python) listing every finding sorted
   by severity — this is guaranteed complete by construction, so no
   finding a specialist actually persisted can ever be silently dropped,
   regardless of what the LLM does or doesn't do next.
2. An LLM-written executive summary sitting above that guaranteed list —
   its job is only to connect patterns and prioritize, never to decide
   what's included. If the LLM call fails, the guaranteed section still
   ships; only the narrative degrades to a fallback line.

This mirrors the same principle behind post_to_pr never being LLM-decided
(Fase 2.3): the LLM adds value where the risk of being wrong is low, but
never becomes the sole guardian of something that must be guaranteed.

Runs once, after LangGraph waits for every Send()-invoked specialist
from the Fase 2.4 fan-out to finish — no manual synchronization needed
here, that join is implicit in how the edges get wired in Fase 2.12.
"""

from langchain_groq import ChatGroq

from app.agents.state import CodeReviewState
from app.config import settings
from app.database import SessionLocal
from app.repositories.analysis_request_repository import (
    AnalysisRequestRepository,
    AnalysisRequestNotFoundError,
)
from app.schemas.analysis_request import AnalysisRequestUpdate

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

SYNTHESIZER_PROMPT = """Eres un redactor técnico que escribe el resumen \
ejecutivo de un análisis de código, a partir de una lista ya cerrada y \
verificada de hallazgos producidos por especialistas (seguridad, \
rendimiento, diseño, buenas prácticas).

No inventes ningún hallazgo nuevo ni omitas ninguno de los que aparecen \
abajo — tu trabajo es solo escribir una introducción breve que conecte \
patrones entre hallazgos y priorice qué atacar primero. La lista completa \
se mostrará aparte, debajo de tu resumen, así que no hace falta que la \
repitas entera.

Hallazgos:
{findings_summary}

Escribe un resumen ejecutivo de 3-5 frases."""


def _build_deterministic_section(findings: list[dict], failed_specialists: list[str]) -> str:
    """Builds the guaranteed, LLM-independent findings listing."""
    lines = ["## Hallazgos completos"]

    if not findings:
        lines.append("No se encontraron hallazgos.")
    else:
        sorted_findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))
        for finding in sorted_findings:
            location = f" ({finding['file_path']})" if finding.get("file_path") else ""
            lines.append(f"- [{finding['severity'].upper()}] {finding['specialist']}{location}: {finding['description']}")
            if finding.get("suggestion"):
                lines.append(f"  Sugerencia: {finding['suggestion']}")

    if failed_specialists:
        lines.append("")
        lines.append(f"Nota: no se pudo completar el análisis de: {', '.join(failed_specialists)}.")

    return "\n".join(lines)


async def synthesizer_node(state: CodeReviewState) -> dict:
    findings = state.get("findings", [])
    failed_specialists = state.get("failed_specialists", [])

    deterministic_section = _build_deterministic_section(findings, failed_specialists)

    llm = ChatGroq(model=settings.SPECIALIST_MODEL, temperature=0)
    try:
        response = await llm.ainvoke(SYNTHESIZER_PROMPT.format(findings_summary=deterministic_section))
        narrative = response.content
    except Exception:
        narrative = "No se pudo generar el resumen narrativo; se muestra el listado completo de hallazgos a continuación."

    final_report = f"{narrative}\n\n---\n\n{deterministic_section}"

    db = SessionLocal()
    try:
        repo = AnalysisRequestRepository(db)
        new_status = "completed_with_errors" if failed_specialists else "completed"
        repo.update(
            state["analysis_request_id"],
            AnalysisRequestUpdate(status=new_status, final_report=final_report),
        )
    except AnalysisRequestNotFoundError:
        return {
            "final_report": final_report,
            "error": f"AnalysisRequest {state['analysis_request_id']} not found during synthesizer_node",
            "node_history": ["synthesizer"],
        }
    except Exception as exc:
        # Same reasoning as entry_node's widened except: the "not found"
        # case isn't the only way this write can fail, and an uncaught
        # exception here would leave the AnalysisRequest at "running"
        # forever with no route to failure_node.
        return {
            "final_report": final_report,
            "error": f"Failed to persist AnalysisRequest {state['analysis_request_id']} during synthesizer_node: {exc}",
            "node_history": ["synthesizer"],
        }
    finally:
        db.close()

    return {
        "final_report": final_report,
        "node_history": ["synthesizer"],
    }