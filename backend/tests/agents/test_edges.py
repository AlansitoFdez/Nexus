"""Tests for conditional routing edges — pure functions, no mocking needed."""

from app.agents.edges import (
    route_after_entry,
    route_after_classifier,
    route_after_kb_searcher,
    route_after_diagnosis,
    route_after_human_approval,
)


def test_route_after_entry_goes_to_classifier_without_error():
    assert route_after_entry({"error": None}) == "classifier"


def test_route_after_entry_goes_to_error_when_present():
    assert route_after_entry({"error": "ticket not found"}) == "error"


def test_route_after_classifier_urgent_goes_to_escalation():
    assert route_after_classifier({"error": None, "classification": "urgent"}) == "escalation"


def test_route_after_classifier_bug_goes_to_kb_searcher():
    assert route_after_classifier({"error": None, "classification": "bug"}) == "kb_searcher"


def test_route_after_kb_searcher_bug_goes_to_diagnosis():
    assert route_after_kb_searcher({"error": None, "classification": "bug"}) == "diagnosis"


def test_route_after_kb_searcher_usage_question_goes_to_response():
    assert route_after_kb_searcher({"error": None, "classification": "usage_question"}) == "response"


def test_route_after_diagnosis_with_actions_goes_to_human_approval():
    assert route_after_diagnosis({"error": None, "pending_actions": ["refund"]}) == "human_approval"


def test_route_after_diagnosis_without_actions_goes_to_response():
    assert route_after_diagnosis({"error": None, "pending_actions": []}) == "response"


def test_route_after_human_approval_rejected_goes_to_escalation():
    assert route_after_human_approval({"escalated": True}) == "escalation"


def test_route_after_human_approval_approved_goes_to_response():
    assert route_after_human_approval({"escalated": False}) == "response"