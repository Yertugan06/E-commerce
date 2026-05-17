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

## CI/CD

### Overview

| Pipeline | Trigger | Runner | Action |
|---|---|---|---|
| **CI** | Push/PR → main | GitHub-hosted | Test, lint, build & push Docker images to GHCR |
| **Deploy** | CI success on main | Self-hosted (`laptop`) | Pull latest images, `terraform apply` |
| **Terraform Plan** | PR touching `terraform/` | GitHub-hosted | `terraform plan` as PR comment |

### Workflows

- **`.github/workflows/ci.yml`** — Backend tests (PostgreSQL service container), frontend tests + lint, Docker build & push to GHCR.
- **`.github/workflows/deploy.yml`** — Pulls `:latest` images from GHCR and runs `terraform apply` via the self-hosted runner.
- **`.github/workflows/terraform-plan.yml`** — Validates and plans Terraform changes on PRs.

### Self-hosted Runner Setup (Laptop)

1. Go to repo **Settings → Actions → Runners → New self-hosted runner**
2. Follow the OS-specific download and configure steps
3. When prompted for labels, enter: `laptop`
4. Start the runner service

### Required Secrets

| Secret | Purpose |
|---|---|
| `TFE_TOKEN` | HCP Terraform API token — used by both the GitHub-hosted runner (`terraform-plan.yml`) and the self-hosted runner (`deploy.yml`) to authenticate with the remote state backend |

### Self-hosted Runner Security

Deploy is only triggered on `push` to `main` (via `workflow_run` on CI). It will **not** trigger on PRs from forks, preventing untrusted code from reaching the self-hosted runner.

### Terraform Remote State

Terraform state is stored remotely in [HCP Terraform](https://app.terraform.io) under the organization **my-ecommerce-org** in the **ecommerce-production** workspace. This provides:

- **State locking** — prevents concurrent modifications
- **Run history** — full audit trail of all infrastructure changes
- **Remote execution** — plans and applies can run in HCP's infrastructure

To set up local access:

```bash
# Interactive (recommended)
cd terraform
terraform login

# Headless
export TFE_TOKEN="<your-hcp-api-token>"
terraform -chdir=terraform init   # migrates local state to HCP
```

### Manual Deploy (Fallback)

```bash
# Requires Docker, Terraform, and HCP Terraform token locally
GITHUB_REPOSITORY_OWNER=myuser TFE_TOKEN=$(cat ~/.terraform.d/credentials.tfrc.json | jq -r '.credentials."app.terraform.io".token') ./scripts/deploy.sh
```

## Environment Variables

| Variable | Default | Service | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Backend | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | Backend | JWT signing key |
| `ALGORITHM` | `HS256` | Backend | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Backend | JWT expiry |
| `VITE_API_URL` | `http://localhost:8000` | Frontend | Backend API base URL |
