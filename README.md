# E-Commerce MVP

A lightweight, high-performance e-commerce platform built with FastAPI + PostgreSQL (backend) and React + Vite + TailwindCSS (frontend).

## Architecture

This repository follows a monorepo structure with strict separation of concerns:

- `/backend` — FastAPI application with Clean Architecture (Presentation → Application → Domain)
- `/frontend` — React application with Feature-Sliced Design

## Quick Start

### One-Command Startup (Docker)

```bash
docker compose up --build
```

This starts all 3 services:

| Service    | Port | URL                  |
|------------|------|----------------------|
| PostgreSQL | 5433 | `localhost:5433`     |
| Backend    | 8000 | `http://localhost:8000` |
| Frontend   | 5173 | `http://localhost:5173` |

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose).

---

### Local Development (without Docker)

#### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (running on port 5433, or update `backend/.env`)
- `uv` (Python package manager)
- `bun` (JavaScript package manager)

#### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
bun install
bun run dev
```

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/           # Config, security, DB, dependencies
│   │   ├── features/       # auth, cart, checkout, orders, users
│   │   └── main.py         # FastAPI app entry point
│   ├── alembic/            # DB migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── entities/       # Business entities (auth, cart, orders)
│   │   ├── features/       # Feature components
│   │   ├── pages/          # Page components
│   │   ├── shared/         # Shared UI, API client
│   │   └── widgets/        # Reusable widgets
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── docs/agent/             # Deep-dive documentation
│   ├── auth_flow.md
│   ├── database_schema.md
│   ├── checkout_state.md
│   └── frontend_state.md
└── AGENTS.md               # Repository conventions
```

## Documentation

- `AGENTS.md` — Repository conventions, tooling, and architectural boundaries
- `docs/agent/auth_flow.md` — JWT authentication flow (register, login, token verification)
- `docs/agent/database_schema.md` — All 5 SQLModel tables, relationships, and indexes
- `docs/agent/checkout_state.md` — Checkout flow, order status lifecycle, stock locking
- `docs/agent/frontend_state.md` — Zustand stores, API client, data flow patterns

## Environment Variables

| Variable | Default | Service | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Backend | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | Backend | JWT signing key |
| `ALGORITHM` | `HS256` | Backend | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Backend | JWT expiry |
| `VITE_API_URL` | `http://localhost:8000` | Frontend | Backend API base URL |
