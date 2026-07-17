from app.api import tickets
from fastapi import FastAPI

app = FastAPI(title="Nexus")

app.include_router(tickets.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}