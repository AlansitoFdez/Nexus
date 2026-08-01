"""Tests for conditional edges routing the code-review graph."""

from langgraph.graph import END
from langgraph.types import Send

from app.agents.edges import route_after_router


def test_route_after_router_fans_out_to_selected_agents():
    state = {
        "agents_to_run": ["security", "performance"],
        "code_content": "def foo(): pass",
        "review_request": "revisa seguridad y rendimiento",
        "analysis_request_id": 1,
        "error": None,
    }

    result = route_after_router(state)

    assert len(result) == 2
    assert all(isinstance(s, Send) for s in result)
    assert {s.node for s in result} == {"security_agent", "performance_agent"}
    assert result[0].arg == {
        "code_content": "def foo(): pass",
        "review_request": "revisa seguridad y rendimiento",
        "analysis_request_id": 1,
    }


def test_route_after_router_fans_out_to_all_four_agents():
    state = {
        "agents_to_run": ["security", "performance", "design_patterns", "best_practices"],
        "code_content": "def foo(): pass",
        "review_request": "revisa todo",
        "analysis_request_id": 1,
        "error": None,
    }

    result = route_after_router(state)

    assert len(result) == 4
    assert {s.node for s in result} == {
        "security_agent", "performance_agent", "design_patterns_agent", "best_practices_agent",
    }


def test_route_after_router_returns_empty_list_when_no_agents_selected():
    state = {
        "agents_to_run": [],
        "code_content": "def foo(): pass",
        "review_request": "petición vacía",
        "analysis_request_id": 1,
        "error": None,
    }

    result = route_after_router(state)

    assert result == []


def test_route_after_router_ends_graph_when_router_failed():
    state = {
        "agents_to_run": [],
        "code_content": None,
        "review_request": "revisa seguridad",
        "analysis_request_id": 1,
        "error": "Router failed to decide agents: groq unavailable",
    }

    result = route_after_router(state)

    assert result == END