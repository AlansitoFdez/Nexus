from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tickets
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


@app.get("/health")
def health_check():
    return {"status": "ok"}