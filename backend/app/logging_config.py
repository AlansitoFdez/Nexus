"""Centralized logging configuration (Fase 5.1 — calidad/observabilidad).

Structured (JSON) logging, not the "logger.error(...) sprinkled ad hoc"
approach that grew organically during the Fase 3 code-review pass — a
LogRecord that arrives as one JSON object per line, with fixed fields
(timestamp, level, logger, message, analysis_request_id), is what a
real log aggregator (the natural next step once Fase 6 actually
deploys somewhere) can index and filter on, instead of grepping free
text. It also closes a real gap: nothing configured the root logger's
level/handler before this, so several of the logger.error(...) calls
added during that pass may not have been emitted anywhere at all —
Python's logging defaults to WARNING on the root logger with no handler
attached.

analysis_request_id is injected into every record via a
contextvars.ContextVar instead of threading it through every individual
logger call by hand (extra={...} everywhere, easy to forget in a new
node). It's set once, in runner.py, right before a graph run starts;
every node's existing logging calls pick it up automatically for the
rest of that run — including inside the Send() fan-out, because a new
asyncio Task copies the current context at the moment it's created, so
the value set before astream() begins is already visible inside every
specialist task LangGraph spawns from it (see
tests/test_logging_config.py for the test that proves this specific
claim in isolation).

No new dependency: JSON formatting and context propagation are both
handled with stdlib logging/contextvars — this project's own precedent
(Fase 3.1: httpx over PyGithub) is to reach for a library only when the
stdlib genuinely can't do the job, not by default.
"""

import contextvars
import json
import logging
from datetime import datetime, timezone
from typing import Any

analysis_request_id_var: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "analysis_request_id", default=None
)


class JSONFormatter(logging.Formatter):
    """Renders each LogRecord as a single JSON line.

    Reads analysis_request_id_var directly here, rather than relying on
    a logging.Filter to stash it onto the record first — a real
    corrected mistake (Fase 5.1): a Filter attached to the root logger
    only runs for records logged directly on the root logger itself,
    never for ones logged through a named child logger like
    logging.getLogger(__name__) (which is every real call site in this
    app) — only Handlers propagate up the logger hierarchy, Filters
    don't. Caught by manually running a log call end-to-end and
    noticing the field was missing from the JSON output, not by
    inspection. Reading the contextvar directly in the formatter
    sidesteps the whole Filter/Handler/Logger hierarchy question:
    formatting happens synchronously, inside the same call that
    produced the record, so it's still the same context that whatever
    set analysis_request_id_var runs in.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        analysis_request_id = analysis_request_id_var.get()
        if analysis_request_id is not None:
            payload["analysis_request_id"] = analysis_request_id

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


def setup_logging(level: int) -> None:
    """Configures the root logger once, at app startup.

    Every module's own logging.getLogger(__name__) call inherits this
    handler/formatter through normal logger hierarchy propagation — no
    per-module setup needed, that's the point of configuring this once
    at the root instead of once per module.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
