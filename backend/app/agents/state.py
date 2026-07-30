"""Shared state that flows through every node of the code review graph.

Like TicketState before it, this only exists for the lifetime of a
single graph execution. Individual fields get written to the
AnalysisRequest/Finding tables via the corresponding repositories as
nodes produce them — this TypedDict itself is never persisted whole.

`findings` is the central case for the operator.add reducer in this
domain: unlike `node_history` (written by every node in sequence),
`findings` is written by multiple specialist nodes running in
parallel. Without the reducer, only the last specialist to finish
would "win," silently discarding the others' results.
"""

import operator
from typing import Annotated, Literal, TypedDict


class CodeReviewState(TypedDict):
    analysis_request_id: int
    source_type: Literal["github_repo", "pasted_code"]
    repo_url: str | None
    pasted_code: str | None
    review_request: str
    post_to_pr: bool
    code_content: str | None
    agents_to_run: list[str]
    findings: Annotated[list[dict], operator.add]
    final_report: str | None
    node_history: Annotated[list[str], operator.add]
    error: str | None