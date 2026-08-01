"""Tests for conditional edges routing the code-review graph."""

from langgraph.graph import END
from langgraph.types import Send

from app.agents.edges import route_after_router, route_after_entry, route_after_synthesizer


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


def test_route_after_router_routes_to_failure_node_when_router_failed():
    state = {
        "agents_to_run": [],
        "code_content": None,
        "review_request": "revisa seguridad",
        "analysis_request_id": 1,
        "error": "Router failed to decide agents: groq unavailable",
    }

    result = route_after_router(state)

    assert result == "failure_node"


def test_route_after_entry_proceeds_to_router_when_no_error():
    state = {"error": None}
    assert route_after_entry(state) == "router_node"


def test_route_after_entry_routes_to_failure_node_on_error():
    state = {"error": "AnalysisRequest 1 not found during entry_node"}
    assert route_after_entry(state) == "failure_node"


def test_route_after_synthesizer_proceeds_to_human_approval_when_no_error():
    state = {"error": None}
    assert route_after_synthesizer(state) == "human_approval_node"


def test_route_after_synthesizer_ends_on_error():
    state = {"error": "AnalysisRequest 1 not found during synthesizer_node"}
    assert route_after_synthesizer(state) == END