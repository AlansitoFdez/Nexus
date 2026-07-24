"""Response node: drafts the final message to the user.

Unlike classifier_node or diagnosis_node, this node has no downstream
code depending on the exact shape of its output — a human reads
proposed_response directly — so no with_structured_output() is used
here; the LLM's free-text answer is stored as-is.
"""

from app.agents.state import TicketState
from app.config import settings
from langchain_groq import ChatGroq


async def response_node(state: TicketState) -> dict:
    """Drafts the final response combining diagnosis, KB docs and actions taken."""
    llm = ChatGroq(model=settings.CLASSIFIER_MODEL, api_key=settings.GROQ_API_KEY)

    prompt = f"""Write a clear, helpful response to the user based on the following.

Ticket: {state["cleaned_text"]}

Diagnosis: {state["diagnosis"]}

Knowledge base documents: {state["kb_documents"]}

Actions taken: {state["pending_actions"]}
"""

    try:
        result = await llm.ainvoke(prompt)

    except Exception as e:
        return {
            "error": f"Response node failed: {e}",
            "node_history": ["response"],
        }

    return {
        "proposed_response": result.content,
        "node_history": ["response"],
    }