"""Assembles the full LangGraph pipeline: nodes, edges and conditional
routing for automated support ticket processing.

The graph is compiled inside build_graph() rather than at module level,
because the Redis checkpointer requires an async setup() call — and a
module's top-level code runs synchronously at import time, so it can't
await anything.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from app.agents.state import TicketState
from app.config import settings
from app.agents.edges import (
    route_after_entry,
    route_after_classifier,
    route_after_kb_searcher,
    route_after_diagnosis,
    route_after_human_approval,
)
from app.agents.nodes.entry_node import entry_node
from app.agents.nodes.classifier_node import classifier_node
from app.agents.nodes.kb_searcher_node import kb_searcher_node
from app.agents.nodes.diagnosis_node import diagnosis_node
from app.agents.nodes.human_approval_node import human_approval_node
from app.agents.nodes.response_node import response_node
from app.agents.nodes.escalation_node import escalation_node


async def build_graph():
    """Builds and compiles the ticket-processing graph with a Redis checkpointer.

    Must be awaited — the checkpointer's asetup() call requires it.
    """
    checkpointer = AsyncRedisSaver(redis_url=settings.REDIS_URL)
    await checkpointer.asetup()

    builder = StateGraph(TicketState)

    builder.add_node("entry", entry_node)
    builder.add_node("classifier", classifier_node)
    builder.add_node("kb_searcher", kb_searcher_node)
    builder.add_node("diagnosis", diagnosis_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("response", response_node)
    builder.add_node("escalation", escalation_node)

    builder.add_edge(START, "entry")

    builder.add_conditional_edges("entry", route_after_entry, {"classifier": "classifier", "error": END})
    builder.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {"kb_searcher": "kb_searcher", "escalation": "escalation", "error": END},
    )
    builder.add_conditional_edges(
        "kb_searcher", route_after_kb_searcher, {"diagnosis": "diagnosis", "response": "response", "error": END}
    )
    builder.add_conditional_edges(
        "diagnosis",
        route_after_diagnosis,
        {"human_approval": "human_approval", "response": "response", "error": END},
    )
    builder.add_conditional_edges(
        "human_approval", route_after_human_approval, {"escalation": "escalation", "response": "response"}
    )

    builder.add_edge("response", END)
    builder.add_edge("escalation", END)

    return builder.compile(checkpointer=checkpointer)