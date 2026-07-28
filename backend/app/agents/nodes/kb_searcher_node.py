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


async def kb_searcher_node(state: TicketState) -> dict:
    """Searches the knowledge base for documents relevant to the ticket.

    Relevance filtering happens in the DB layer (search_vector @@ tsquery),
    not here — the tool only ever returns real linguistic matches, already
    ranked by ts_rank. On failure to reach the MCP server or call the tool,
    returns an error delta instead of raising.
    """
    try:
        async with Client(settings.MCP_SERVER_URL) as client:
            result = await client.call_tool(
                "search_knowledge_base", {"query": state["cleaned_text"]}
            )
            documents = result.data

    except Exception as e:
        return {
            "error": f"KB Searcher node failed: {e}",
            "node_history": ["kb_searcher"],
        }

    return {
        "kb_documents": documents,
        "node_history": ["kb_searcher"],
    }