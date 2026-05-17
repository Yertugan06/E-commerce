# E-Commerce MVP

A lightweight, high-performance e-commerce platform built with FastAPI + PostgreSQL (backend) and React + Vite + TailwindCSS (frontend).

## Architecture

This repository follows a monorepo structure with strict separation of concerns:

- `/backend` — FastAPI application with Clean Architecture (Presentation → Application → Domain)
- `/frontend` — React application with Feature-Sliced Design

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- `uv` (Python package manager)
- `bun` (JavaScript package manager)

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
bun install
bun run dev
```

### Docker (full stack)

```bash
docker-compose up --build
```

## Documentation

See `AGENTS.md` for repository conventions and `docs/agent/` for subsystem deep-dives.
