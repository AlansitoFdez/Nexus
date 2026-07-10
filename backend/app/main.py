from fastapi import FastAPI

app = FastAPI(title="Nexus")

@app.get("/health")
def health_check():
  return {"status": "ok"}
