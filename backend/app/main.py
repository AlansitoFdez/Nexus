"""FastAPI application entry point.

Assembles all routers and middleware (CORS) into a single app instance,
served via `uvicorn app.main:app`.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from app.agents.graph import build_graph
from app.api import analysis_requests, approvals, metrics, websocket
from app.config import settings
from app.logging_config import setup_logging

# Configured once, at module load — before the lifespan even starts, so
# every node/repository/tool that logs during startup (or the very
# first request, which can race the lifespan's own setup) already goes
# through the structured JSON formatter (Fase 5.1), not Python's
# unconfigured default (WARNING, no handler).
setup_logging(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    """Owns the checkpointer connection's lifecycle for the app's whole
    lifetime, instead of opening/closing it per request.

    AsyncRedisSaver has no pooling of its own the way SQLAlchemy's
    `engine`/`SessionLocal` in database.py already do — so this makes
    that same "connect once, reuse everywhere" behavior explicit for
    the checkpointer. The compiled graph is built once here (it's a
    pure function of the checkpointer, per build_graph()'s docstring)
    and stored on app.state so every request reuses the same compiled
    graph instead of recompiling it, or reconnecting to Redis, per call.

    Deliberately excluded from coverage (Fase 5.4 review): the `client`
    fixture (tests/api/conftest.py) stands in a mocked app.state.graph
    instead of letting this real lifespan run, precisely so tests don't
    need a real Redis connection.
    """
    async with AsyncRedisSaver.from_conn_string(settings.REDIS_URL) as checkpointer:
        await checkpointer.asetup()
        app.state.graph = await build_graph(checkpointer)
        yield


app = FastAPI(title="Nexus", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(approvals.router)
app.include_router(websocket.router)
app.include_router(analysis_requests.router)
app.include_router(metrics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
