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