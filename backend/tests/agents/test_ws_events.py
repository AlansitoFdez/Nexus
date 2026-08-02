"""Tests for translating LangGraph astream() chunks into dashboard events."""

from types import SimpleNamespace

from app.agents.ws_events import build_event


def test_router_node_chunk_becomes_specialists_started():
    chunk = {"router_node": {"agents_to_run": ["security", "performance"], "node_history": ["router"]}}

    event = build_event(chunk)

    assert event == {"type": "specialists_started", "specialists": ["security", "performance"]}


def test_specialist_chunk_becomes_specialist_finished():
    chunk = {"security_agent": {"findings": [{"severity": "high"}, {"severity": "low"}], "node_history": ["security"]}}

    event = build_event(chunk)

    assert event == {
        "type": "specialist_finished",
        "specialist": "security",
        "findings_count": 2,
        "failed": False,
    }


def test_specialist_chunk_marks_failed_specialist():
    chunk = {"performance_agent": {"findings": [], "failed_specialists": ["performance"], "node_history": ["performance"]}}

    event = build_event(chunk)

    assert event == {
        "type": "specialist_finished",
        "specialist": "performance",
        "findings_count": 0,
        "failed": True,
    }


def test_entry_node_chunk_becomes_node_finished():
    chunk = {"entry_node": {"code_content": "def foo(): pass", "node_history": ["entry"]}}

    event = build_event(chunk)

    assert event == {"type": "node_finished", "node": "entry"}


def test_synthesizer_node_chunk_becomes_node_finished():
    chunk = {"synthesizer_node": {"final_report": "Sin hallazgos.", "node_history": ["synthesizer"]}}

    assert build_event(chunk) == {"type": "node_finished", "node": "synthesizer"}


def test_node_chunk_with_error_becomes_run_failed_regardless_of_which_node():
    chunk = {"router_node": {"error": "Router failed to decide agents: groq unavailable", "node_history": ["router"]}}

    event = build_event(chunk)

    assert event == {
        "type": "run_failed",
        "node": "router_node",
        "message": "Router failed to decide agents: groq unavailable",
    }


def test_interrupt_chunk_becomes_approval_required():
    interrupt = SimpleNamespace(value={
        "analysis_request_id": 5,
        "approval_id": 9,
        "proposed_action": "Publicar el informe de hallazgos como comentario en el PR",
        "final_report": "2 hallazgos de seguridad.",
    })
    chunk = {"__interrupt__": (interrupt,)}

    event = build_event(chunk)

    assert event == {
        "type": "approval_required",
        "analysis_request_id": 5,
        "approval_id": 9,
        "proposed_action": "Publicar el informe de hallazgos como comentario en el PR",
        "final_report": "2 hallazgos de seguridad.",
    }


def test_empty_interrupt_tuple_returns_none():
    assert build_event({"__interrupt__": ()}) is None


def test_unrecognized_node_returns_none():
    assert build_event({"some_future_node": {"node_history": ["some_future_node"]}}) is None
