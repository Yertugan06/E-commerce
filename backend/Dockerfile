FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY scripts/ ./scripts/

EXPOSE 8000

# Periodic stock restock for load testing — resets every 5 minutes in background
RUN printf '#!/bin/sh\nwhile true; do uv run python -m scripts.seed; sleep 300; done\n' > /app/restock.sh && chmod +x /app/restock.sh

CMD /app/restock.sh & uv run alembic upgrade head && uv run python -m scripts.seed && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
