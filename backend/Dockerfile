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

CMD uv run alembic upgrade head && uv run python -m scripts.seed && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
