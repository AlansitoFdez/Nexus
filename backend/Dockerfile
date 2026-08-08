# Runs both the FastAPI backend and the MCP server — they share the same
# source tree and requirements.txt, only the startup command differs
# (set per service in docker-compose.yml, not baked in here).
FROM python:3.13-slim

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Requirements copied and installed before the rest of the source, so a
# rebuild that only touches application code reuses this layer instead
# of reinstalling every dependency from scratch.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
