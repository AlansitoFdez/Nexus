"""FastAPI application entry point.

Assembles all routers and middleware (CORS) into a single app instance,
served via `uvicorn app.main:app`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  
from app.api import tickets, knowledge_base, approvals
from app.config import settings

app = FastAPI(title="Nexus")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(tickets.router)
app.include_router(knowledge_base.router)
app.include_router(approvals.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}