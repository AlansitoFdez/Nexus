"""Pydantic schemas for structured LLM output in the code-review graph.

post_to_pr is deliberately absent from RouterDecision: whether to post
a PR comment is an explicit field on AnalysisRequest, set by the user
at creation time — never inferred by an LLM from free text. See the
Fase 2.3 architecture discussion for the reasoning.
"""

from typing import Literal
from pydantic import BaseModel, Field

from app.agents.specialists import SPECIALISTS


class RouterDecision(BaseModel):
    """The router's decision on which specialists should run.

    reasoning is kept as a short audit trail — it costs nothing extra
    from the LLM call and makes a wrong decision debuggable later
    ("why did it skip performance here?") without re-running anything.

    agents_to_run requires at least one entry: the prompt already tells
    the LLM to include all four for a generic request, but that's a
    text instruction, not a guarantee — the same reasoning that put
    ck_analysis_requests_exactly_one_source at the database level
    applies here too. An empty list would otherwise fan out to zero
    Send()s in route_after_router, ending the graph with the
    AnalysisRequest stuck at status="running" forever.

    The Literal itself is built from SPECIALISTS' keys (Fase 4.1
    review) instead of listed by hand — adding a fifth specialist to
    the ensemble means adding one entry there, not remembering to also
    update this Literal to match.
    """

    agents_to_run: list[Literal[*SPECIALISTS.keys()]] = Field(min_length=1)
    reasoning: str


class SpecialistFinding(BaseModel):
    """A single issue detected by a specialist agent's structured output.

    Mirrors FindingCreate's shape but lives here, not in app/schemas/,
    because this is the LLM-facing validation boundary — the specialist
    node translates each SpecialistFinding into a FindingCreate itself,
    attaching specialist name and analysis_request_id, neither of which
    the LLM should be deciding.
    """

    severity: Literal["critical", "high", "medium", "low"]
    description: str
    file_path: str | None = None
    suggestion: str | None = None


class SpecialistOutput(BaseModel):
    """A specialist's full structured output: zero or more findings."""

    findings: list[SpecialistFinding]
