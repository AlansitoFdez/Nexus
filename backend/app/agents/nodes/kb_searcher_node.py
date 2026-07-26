"""Knowledge base searcher node: the first real MCP client in the pipeline.

Calls the search_knowledge_base tool on the Nexus MCP server (a separate
process, started with `python -m app.mcp_server.server`) rather than
importing KnowledgeBaseRepository directly — this node is the first
real consumer of the MCP server built in Fase 1.4, exercising the
exact reason it was built that way: any client speaking MCP can reuse
this tool without coupling to the backend's internal code.
"""

from app.agents.state import TicketState
from app.config import settings
from fastmcp import Client

MIN_RELEVANCE_SCORE = 0.7


async def kb_searcher_node(state: TicketState) -> dict:
    """Searches the knowledge base for documents relevant to the ticket.

    Filters out results below MIN_RELEVANCE_SCORE before storing them
    in the state. On failure to reach the MCP server or call the tool,
    returns an error delta instead of raising.
    """
    try:
        async with Client(settings.MCP_SERVER_URL) as client:
            result = await client.call_tool(
                "search_knowledge_base", {"query": state["cleaned_text"]}
            )

            relevant_docs = [
                doc for doc in result.data if doc["relevance_score"] >= MIN_RELEVANCE_SCORE
            ]

    except Exception as e:
        return {
            "error": f"KB Searcher node failed: {e}",
            "node_history": ["kb_searcher"],
        }

    return {
        "kb_documents": relevant_docs,
        "node_history": ["kb_searcher"],
    }