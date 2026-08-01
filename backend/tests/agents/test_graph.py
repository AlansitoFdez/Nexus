"""Integration test for the compiled graph — the human_approval_node +
real checkpointer test inherited unresolved from the ticket domain.

Requires a real Redis instance (redis-stack-server) running. Connects
to the same Redis db (0) as dev — RediSearch's FT.CREATE only works on
db 0, so logical-database isolation (the approach tried first) isn't
viable here. Isolation instead comes from a fresh UUID thread_id per
run: request.id is always 1 in nexus_test (it resets every test), so
reusing it as thread_id collided with a stale checkpoint left over
from manual testing of the old ticket-domain graph — a UUID guarantees
no prior checkpoint could exist under this key, without needing to
touch or flush any existing Redis data.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.types import Command

from app.agents.graph import build_graph
from app.agents.schemas import RouterDecision, SpecialistOutput
from app.repositories.analysis_request_repository import AnalysisRequestRepository
from app.schemas.analysis_request import AnalysisRequestCreate

REDIS_URL = "redis://localhost:6379"
TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.mark.asyncio
async def test_graph_pauses_at_human_approval_and_resumes_on_approval(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code",
        pasted_code="def foo(): pass",
        review_request="revisa seguridad",
        post_to_pr=True,
    ))

    mock_router_llm = MagicMock()
    mock_router_llm.with_structured_output.return_value.ainvoke = AsyncMock(
        return_value=RouterDecision(agents_to_run=["security"], reasoning="solo seguridad")
    )

    mock_specialist_llm = MagicMock()
    mock_specialist_llm.with_structured_output.return_value.ainvoke = AsyncMock(
        return_value=SpecialistOutput(findings=[])
    )

    mock_synth_llm = MagicMock()
    mock_synth_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Sin hallazgos relevantes."))

    thread_id = str(uuid.uuid4())

    async with AsyncRedisSaver.from_conn_string(REDIS_URL) as checkpointer:
        await checkpointer.asetup()
        graph = await build_graph(checkpointer)

        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "analysis_request_id": request.id,
            "source_type": "pasted_code",
            "repo_url": None,
            "pasted_code": "def foo(): pass",
            "review_request": "revisa seguridad",
            "post_to_pr": True,
        }

        with patch("app.agents.nodes.router_node.ChatGroq", return_value=mock_router_llm), \
             patch("app.agents.nodes.specialists.security_agent.ChatGroq", return_value=mock_specialist_llm), \
             patch("app.agents.nodes.synthesizer_node.ChatGroq", return_value=mock_synth_llm), \
             patch("app.agents.nodes.entry_node.SessionLocal", TestSessionLocal), \
             patch("app.agents.nodes.specialists.security_agent.SessionLocal", TestSessionLocal), \
             patch("app.agents.nodes.synthesizer_node.SessionLocal", TestSessionLocal), \
             patch("app.agents.nodes.human_approval_node.SessionLocal", TestSessionLocal):

            result = await graph.ainvoke(initial_state, config=config)
            assert "__interrupt__" in result, f"Grafo no se pausó; estado final: {result}"

            resumed = await graph.ainvoke(Command(resume="approved"), config=config)

    assert resumed["node_history"][-1] == "human_approval"