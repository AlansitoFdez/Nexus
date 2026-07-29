"""Diagnosis node: combines KB documents and similar historical
tickets to produce a structured root-cause diagnosis via LLM.

Uses DIAGNOSIS_MODEL (the larger model), not CLASSIFIER_MODEL, since
this node reasons over multiple sources of context at once rather
than performing a simple categorization.
"""

from app.agents.schemas import DiagnosisOutput
from app.agents.state import TicketState
from app.config import settings
from fastmcp import Client
from langchain_groq import ChatGroq


async def diagnosis_node(state: TicketState) -> dict:
    """Diagnoses a ticket's root cause using KB docs and similar tickets.

    Fetches similar resolved tickets via MCP, then feeds them alongside
    the KB documents already gathered by kb_searcher_node into the LLM
    for structured diagnosis. Any failure — MCP call or LLM call —
    aborts the whole node with an error delta, per Alan's decision to
    never diagnose with incomplete context.
    """
    try:
        async with Client(settings.MCP_SERVER_URL, auth=settings.MCP_API_KEY) as client:
            tickets_result = await client.call_tool(
                "query_tickets_db", {"category": state["classification"]}
            )
            similar_tickets = tickets_result.data

        prompt = f"""Diagnose the root cause of this support ticket and propose a solution.

Ticket: {state["cleaned_text"]}

Relevant knowledge base documents:
{state["kb_documents"]}

Similar previously resolved tickets:
{similar_tickets}
"""

        llm = ChatGroq(model=settings.DIAGNOSIS_MODEL, api_key=settings.GROQ_API_KEY)
        structured_llm = llm.with_structured_output(DiagnosisOutput)
        result = await structured_llm.ainvoke(prompt)

    except Exception as e:
        return {
            "error": f"Diagnosis node failed: {e}",
            "node_history": ["diagnosis"],
        }

    return {
        "diagnosis": f"{result.probable_cause} {result.proposed_solution}",
        "diagnosis_confidence": result.confidence,
        "pending_actions": result.actions_required or [],
        "similar_tickets": similar_tickets,
        "node_history": ["diagnosis"],
    }