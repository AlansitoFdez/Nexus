"""Tests for app/logging_config.py — the JSON formatter, the
analysis_request_id context injection, and the context-propagation
claim runner.py's design relies on (Fase 5.1)."""

import asyncio
import json
import logging

from app.logging_config import JSONFormatter, analysis_request_id_var, setup_logging


def test_json_formatter_includes_core_fields():
    record = logging.LogRecord(
        name="app.agents.nodes.entry_node",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="Failed to read repository %s",
        args=("https://github.com/alan/nexus",),
        exc_info=None,
    )

    payload = json.loads(JSONFormatter().format(record))

    assert payload["level"] == "ERROR"
    assert payload["logger"] == "app.agents.nodes.entry_node"
    assert payload["message"] == "Failed to read repository https://github.com/alan/nexus"
    assert "timestamp" in payload


def test_json_formatter_includes_analysis_request_id_when_context_is_set():
    """JSONFormatter reads analysis_request_id_var directly (Fase 5.1
    correction — see the class docstring for the Filter-based approach
    that didn't actually work and why)."""
    record = logging.LogRecord(
        name="x", level=logging.ERROR, pathname=__file__, lineno=1,
        msg="boom", args=(), exc_info=None,
    )
    token = analysis_request_id_var.set(47)
    try:
        payload = json.loads(JSONFormatter().format(record))
    finally:
        analysis_request_id_var.reset(token)

    assert payload["analysis_request_id"] == 47


def test_json_formatter_omits_analysis_request_id_when_context_is_unset():
    assert analysis_request_id_var.get() is None  # sanity check: no leakage from another test

    record = logging.LogRecord(
        name="x", level=logging.ERROR, pathname=__file__, lineno=1,
        msg="boom", args=(), exc_info=None,
    )

    payload = json.loads(JSONFormatter().format(record))

    assert "analysis_request_id" not in payload


def test_json_formatter_includes_exception_traceback():
    try:
        raise ValueError("something broke")
    except ValueError:
        import sys
        record = logging.LogRecord(
            name="x", level=logging.ERROR, pathname=__file__, lineno=1,
            msg="failed", args=(), exc_info=sys.exc_info(),
        )

    payload = json.loads(JSONFormatter().format(record))

    assert "ValueError: something broke" in payload["exception"]


async def _read_analysis_request_id_var() -> int | None:
    return analysis_request_id_var.get()


def test_analysis_request_id_var_propagates_into_concurrently_spawned_tasks():
    """Proves the core claim runner.py's design relies on: a new
    asyncio Task copies the current context at creation time, so
    setting the var once before the Send() fan-out starts is enough for
    every concurrently spawned specialist task to see it — no need to
    pass analysis_request_id through every individual call by hand."""

    async def scenario() -> list[int | None]:
        token = analysis_request_id_var.set(99)
        try:
            return await asyncio.gather(
                _read_analysis_request_id_var(),
                _read_analysis_request_id_var(),
            )
        finally:
            analysis_request_id_var.reset(token)

    assert asyncio.run(scenario()) == [99, 99]


def test_setup_logging_configures_json_formatter_on_root():
    """setup_logging() mutates the root logger globally — save and
    restore its handlers/level around the call so this test doesn't
    leak configuration into whichever test runs next."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    original_filters = root.filters[:]

    try:
        setup_logging(logging.DEBUG)

        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JSONFormatter)
    finally:
        root.handlers[:] = original_handlers
        root.filters[:] = original_filters
        root.setLevel(original_level)
