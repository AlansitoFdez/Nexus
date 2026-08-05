"""Assembles the code-review graph: entry -> router -> parallel
specialist fan-out -> synthesizer -> human approval -> post comment,
with a single failure_node terminal path for pre-fanout errors
(Fase 2.11).

build_graph() takes an already-created checkpointer rather than
opening its own Redis connection — the connection's lifecycle (when
to open/close it) is the caller's responsibility. FastAPI's lifespan
(app/main.py) owns that connection for the app's whole lifetime and
calls this function once at startup.

Specialist nodes are registered from SPECIALISTS (Fase 4.1 review)
instead of one add_node() call per hand-imported specialist — adding a
fifth specialist to the ensemble now means adding one entry to that
dict, not editing this loop.
"""

from langgraph.graph import END, START, StateGraph

from app.agents.edges import route_after_entry, route_after_router, route_after_synthesizer
from app.agents.nodes.entry_node import entry_node
from app.agents.nodes.failure_node import failure_node
from app.agents.nodes.human_approval_node import human_approval_node
from app.agents.nodes.post_comment_node import post_comment_node
from app.agents.nodes.router_node import router_node
from app.agents.nodes.specialist_node import make_specialist_node
from app.agents.nodes.synthesizer_node import synthesizer_node
from app.agents.specialists import SPECIALISTS
from app.agents.state import CodeReviewState


async def build_graph(checkpointer):
    """Builds and compiles the code-review graph using the given checkpointer.

    Args:
        checkpointer: An already-instantiated LangGraph checkpointer
            (e.g. AsyncRedisSaver), so this function stays a pure
            graph-assembly step, decoupled from connection lifecycle.

    Returns:
        The compiled graph, ready to be `.ainvoke()`d with a config
        carrying a unique thread_id (the analysis_request_id).
    """
    graph = StateGraph(CodeReviewState)

    graph.add_node("entry_node", entry_node)
    graph.add_node("router_node", router_node)

    for name, prompt in SPECIALISTS.items():
        graph.add_node(f"{name}_agent", make_specialist_node(name, prompt))

    graph.add_node("synthesizer_node", synthesizer_node)
    graph.add_node("human_approval_node", human_approval_node)
    graph.add_node("post_comment_node", post_comment_node)
    graph.add_node("failure_node", failure_node)

    graph.add_edge(START, "entry_node")
    graph.add_conditional_edges("entry_node", route_after_entry)
    graph.add_conditional_edges("router_node", route_after_router)

    for name in SPECIALISTS:
        graph.add_edge(f"{name}_agent", "synthesizer_node")

    graph.add_conditional_edges("synthesizer_node", route_after_synthesizer)
    graph.add_edge("human_approval_node", "post_comment_node")
    graph.add_edge("post_comment_node", END)
    graph.add_edge("failure_node", END)

    return graph.compile(checkpointer=checkpointer)
