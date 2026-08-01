"""Pydantic schemas for structured LLM output in the code-review graph.

post_to_pr is deliberately absent from RouterDecision: whether to post
a PR comment is an explicit field on AnalysisRequest, set by the user
at creation time — never inferred by an LLM from free text. See the
Fase 2.3 architecture discussion for the reasoning.
"""

from typing import Literal
from pydantic import BaseModel


class RouterDecision(BaseModel):
    """The router's decision on which specialists should run.

    reasoning is kept as a short audit trail — it costs nothing extra
    from the LLM call and makes a wrong decision debuggable later
    ("why did it skip performance here?") without re-running anything.
    """

    agents_to_run: list[Literal["security", "performance", "design_patterns", "best_practices"]]
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