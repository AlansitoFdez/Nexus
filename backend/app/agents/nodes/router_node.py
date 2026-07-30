"""Router node: interprets the user's free-text review request and
decides which specialist agents should analyze the code.

First LLM-backed node in this domain's pipeline (mirrors classifier_node
before the pivot). Uses ROUTER_MODEL — the cheaper model, appropriate
for this classification-style task — not SPECIALIST_MODEL, which the
specialist nodes (2.5-2.8) will use for denser reasoning.

post_to_pr is NOT decided here — see agents/schemas.py docstring.
"""

from langchain_groq import ChatGroq

from app.agents.state import CodeReviewState
from app.agents.schemas import RouterDecision
from app.config import settings

ROUTER_PROMPT = """Eres un router que decide qué especialistas deben \
analizar un fragmento de código, según lo que el usuario pidió revisar.

Especialistas disponibles: security, performance, design_patterns, best_practices.

Petición del usuario: {review_request}

Elige solo los especialistas relevantes para lo que se pidió. Si la \
petición es genérica ("revisa el código"), incluye los cuatro."""


async def router_node(state: CodeReviewState) -> dict:
    llm = ChatGroq(model=settings.ROUTER_MODEL, temperature=0)
    structured_llm = llm.with_structured_output(RouterDecision)

    try:
        decision = await structured_llm.ainvoke(
            ROUTER_PROMPT.format(review_request=state["review_request"])
        )
    except Exception as exc:
        return {
            "error": f"Router failed to decide agents: {exc}",
            "node_history": ["router"],
        }

    return {
        "agents_to_run": decision.agents_to_run,
        "node_history": ["router"],
    }