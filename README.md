# E-Commerce MVP

A lightweight, high-performance e-commerce platform built with FastAPI + PostgreSQL (backend) and React + Vite + TailwindCSS (frontend), with full observability (Prometheus/Grafana/Alertmanager), auto-scaling, and Kubernetes deployment support.

## Architecture

This repository follows a monorepo structure with strict separation of concerns:

- `/backend` — FastAPI application with Clean Architecture (Presentation → Application → Domain)
- `/frontend` — React application with Feature-Sliced Design

## Quick Start

### One-Command Startup (Docker)

```bash
docker compose up --build
```

This starts all services:

| Service      | Port | URL                                |
|--------------|------|------------------------------------|
| PostgreSQL   | 5433 | `localhost:5433`                   |
| Backend      | 8000 | `http://localhost:8000` (via nginx) |
| Frontend     | 5173 | `http://localhost:5173`            |
| Prometheus   | 9090 | `http://localhost:9090`            |
| Grafana      | 3000 | `http://localhost:3000` (admin/admin) |
| Alertmanager | 9093 | `http://localhost:9093`            |
| Locust       | 8089 | `http://localhost:8089`            |

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

## Usage Guide

### Run everything locally (Docker)

```bash
docker compose up --build
```

Access:
- **App:** http://localhost:8000
- **Frontend:** http://localhost:5173
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)
- **Alertmanager:** http://localhost:9093
- **Locust (load test):** http://localhost:8089

Stop with `Ctrl+C` or `docker compose down`.

### Run in Kubernetes (minikube)

```bash
# Start minikube
minikube start

# Deploy everything
bash scripts/deploy-k8s.sh

# Check status
kubectl get pods -n ecommerce
kubectl get hpa -n ecommerce

# Access
minikube service list -n ecommerce
```

### Run CI/CD (requires self-hosted runner)

The CI pipeline runs automatically on push/PR to `main`. To set up the self-hosted runner for deploy:
1. Add a self-hosted runner in repo **Settings → Actions → Runners** (label: `laptop`)
2. Push to `main` — CI builds images, then Deploy starts containers via Terraform

Manual deploy from your machine:

```bash
export GITHUB_REPOSITORY_OWNER=''; export GITHUB_REPOSITORY=''; bash scripts/deploy.sh
```

### Run load tests

```bash
# With Docker (headless, 10 users for 10 minutes)
docker compose up locust

# Or with web UI: edit docker-compose.yml, remove --headless, then:
docker compose up locust
# Open http://localhost:8089
```

### Run tests

```bash
# Backend
cd backend && uv run pytest -v

# Frontend
cd frontend && bun run test
```

---

## Monitoring Stack

### Prometheus

Prometheus scrapes the backend `/metrics` endpoint every 5 seconds. Configuration is in `prometheus/prometheus.yml`.

**Rule files** (in `prometheus/rules/`):

| File | Purpose |
|------|---------|
| `sli_recording.yml` | Pre-computed SLI metrics (availability, latency p95, success rates, consistency) |
| `sli_alerts.yml` | SLO burn-rate alerts (availability < 99.9%, latency thresholds, etc.) |
| `autoscaling_alerts.yml` | Capacity alerts (CPU > 0.8, memory > 500MB, error rate > 5%, request rate > 100/s) |

### Grafana

Pre-provisioned dashboards are loaded automatically from `grafana/dashboards/`:

- **SLI Overview** (`sli_overview.json`) — All SLI metrics with SLO targets, burn rate visualizations, and status panels

Credentials: `admin` / `admin`

### Alertmanager

Alertmanager receives alerts from Prometheus and routes them via `prometheus/alertmanager.yml`. An alert receiver webhook (`prometheus/webhook-receiver.py`) logs alerts for development/demo purposes.

### SLI / SLO System

| SLI | SLO Target | Measurement Source |
|-----|-----------|-------------------|
| API Availability | >= 99.9% | FastAPI Middleware (`http_requests_total`) |
| Checkout Success Rate | >= 99.5% | FastAPI Middleware (`http_requests_total`) |
| Cart Read Latency p95 | <= 300ms | Prometheus Histogram |
| Order Read Latency p95 | <= 500ms | Prometheus Histogram |
| Cart Update Latency p95 | <= 500ms | Prometheus Histogram |
| Checkout Latency p95 | <= 2000ms | Prometheus Histogram |
| Cart Consistency Rate | >= 99.9% | Application Validation |

Full SLO definitions: [docs/SLOs.md](docs/SLOs.md)

---

## Auto-Scaling

### HorizontalPodAutoscaler (K8s)

The backend HPA (`k8s/backend-hpa.yaml`) scales based on:

- **CPU**: 60% average utilization target
- **Memory**: 70% average utilization target

Range: 1-10 replicas.

### Prometheus Capacity Alerts

Defined in `prometheus/rules/autoscaling_alerts.yml`:

- **CPUUtilizationHigh** — CPU > 0.8 cores for 5m (warning)
- **MemoryUtilizationHigh** — RSS > 500 MB for 5m (warning)
- **ErrorRateHigh** — 5xx rate > 5% for 5m (critical)
- **RequestRateHigh** — > 100 req/s for 2m (warning)

---

## Load Testing (Locust)

### Docker (headless)

```bash
docker compose up locust
```

Runs 10 users, spawn rate 2/s, for 10 minutes against the backend through nginx.

### Docker (web UI)

Override the command in `docker-compose.yml` to remove `--headless`, then access `http://localhost:8089` to configure test parameters interactively.

### Locustfile

`backend/scripts/locustfile.py` defines two user classes:

- **AnonymousBrowser** — browses products (weight 3)
- **AuthenticatedUser** — registers/logs in, adds items to cart, browses, checks out, views orders (weighted tasks)

---

## Kubernetes Deployment

The `k8s/` directory contains all manifests for deploying to a local minikube cluster.

### Prerequisites

- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### Deploy

```bash
./scripts/deploy-k8s.sh
```

This script:
1. Enables minikube's metrics-server (required for HPA)
2. Builds backend and frontend images inside minikube
3. Creates the `ecommerce` namespace and secrets
4. Deploys PostgreSQL, waits for readiness
5. Deploys backend with HPA
6. Deploys nginx, frontend, monitoring stack (Prometheus, Alertmanager, Grafana), and Locust
7. Runs Alembic migrations and seed data

### Access

| Service     | URL                              |
|-------------|----------------------------------|
| Application | `http://$(minikube ip):30080`    |
| Grafana     | `http://$(minikube ip):33000`    |
| Prometheus  | `http://$(minikube ip):39090`    |
| Locust      | `http://$(minikube ip):38089`    |

### K8s Manifests

| File | Description |
|------|-------------|
| `namespace.yaml` | `ecommerce` namespace |
| `secrets.yaml` | DB credentials, JWT secret key |
| `postgres.yaml` | PostgreSQL stateful workload |
| `backend.yaml` | Backend deployment + service (init container waits for Postgres) |
| `backend-hpa.yaml` | CPU/memory-based autoscaler (1-10 replicas) |
| `nginx.yaml` | Reverse proxy (NodePort 30080) |
| `frontend.yaml` | Nginx-served React SPA |
| `prometheus-config.yaml` | Prometheus config + all rule files |
| `prometheus.yaml` | Prometheus deployment + PVC + NodePort |
| `alertmanager.yaml` | Alertmanager deployment + NodePort |
| `alert-receiver.yaml` | Webhook receiver for alert notifications |
| `grafana.yaml` | Grafana with pre-provisioned dashboards |
| `locust.yaml` | Locust deployment + NodePort |
| `locust-config.yaml` | Embedded locustfile.py as ConfigMap |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # App settings, env vars
│   │   │   ├── database.py         # SQLAlchemy async engine
│   │   │   ├── dependencies.py     # FastAPI dependency injection
│   │   │   ├── error_handlers.py   # Global exception handlers
│   │   │   ├── exceptions.py       # Custom exception classes
│   │   │   ├── health.py           # Health check endpoint
│   │   │   ├── metrics.py          # Prometheus counters/histograms
│   │   │   ├── metrics_aggregator.py
│   │   │   ├── middleware.py       # Request metrics middleware
│   │   │   ├── security.py         # JWT helpers
│   │   │   └── sli_checks.py       # Business logic SLI validations
│   │   ├── features/
│   │   │   ├── auth/               # JWT register/login
│   │   │   ├── cart/               # Cart CRUD with product validation
│   │   │   ├── checkout/           # Order checkout flow + payment stubs
│   │   │   ├── orders/             # Order history + detail
│   │   │   ├── products/           # Product catalog CRUD
│   │   │   └── users/              # User management
│   │   └── main.py                 # FastAPI app entry point
│   ├── alembic/                    # DB migrations
│   ├── scripts/
│   │   ├── generate_sli_traffic.py # SLI traffic generator
│   │   ├── locustfile.py           # Load testing scenarios
│   │   └── seed.py                 # Database seed data
│   ├── tests/
│   │   ├── conftest.py             # Test fixtures (async DB, client)
│   │   ├── test_auth.py
│   │   ├── test_cart.py
│   │   ├── test_checkout.py
│   │   └── test_sli.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── entities/
│   │   │   ├── auth/
│   │   │   │   ├── store.ts        # Zustand auth store
│   │   │   │   └── store.test.ts
│   │   │   ├── cart/
│   │   │   │   └── store.ts        # Zustand cart store
│   │   │   └── orders/
│   │   │       └── store.ts        # Zustand orders store
│   │   ├── features/
│   │   │   └── auth/
│   │   │       ├── LoginForm.tsx
│   │   │       ├── LoginForm.test.tsx
│   │   │       ├── RegisterForm.tsx
│   │   │       ├── ProtectedRoute.tsx
│   │   │       └── ProtectedRoute.test.tsx
│   │   ├── pages/
│   │   │   ├── CartPage.tsx
│   │   │   ├── CheckoutPage.tsx
│   │   │   ├── CheckoutSuccess.tsx
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── OrderDetail.tsx
│   │   │   ├── OrderHistory.tsx
│   │   │   ├── Products.tsx
│   │   │   └── Register.tsx
│   │   ├── shared/
│   │   │   ├── api/
│   │   │   │   └── client.ts       # Axios instance + auth interceptor
│   │   │   └── ui/
│   │   │       └── Layout.tsx      # App shell with nav
│   │   ├── widgets/
│   │   │   └── cart/
│   │   │       └── QuantitySelector.tsx
│   │   ├── test/
│   │   │   └── setup.ts            # Vitest test setup
│   │   ├── App.tsx                 # Route definitions
│   │   ├── main.tsx                # Entry point
│   │   └── index.css               # Tailwind imports
│   ├── nginx.conf                  # SPA nginx config
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── k8s/                        # Kubernetes manifests
│   ├── backend.yaml
│   ├── backend-hpa.yaml
│   ├── frontend.yaml
│   ├── nginx.yaml
│   ├── postgres.yaml
│   ├── prometheus.yaml
│   ├── prometheus-config.yaml
│   ├── alertmanager.yaml
│   ├── alert-receiver.yaml
│   ├── grafana.yaml
│   ├── locust.yaml
│   ├── locust-config.yaml
│   ├── namespace.yaml
│   └── secrets.yaml
├── prometheus/
│   ├── prometheus.yml           # Scrape config
│   ├── alertmanager.yml         # Alert routing
│   ├── webhook-receiver.py      # Alert notification webhook
│   └── rules/
│       ├── sli_recording.yml    # SLI recording rules
│       ├── sli_alerts.yml       # SLO alert rules
│       └── autoscaling_alerts.yml  # Capacity alert rules
├── grafana/
│   ├── dashboards/
│   │   └── sli_overview.json    # SLI dashboard
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── prometheus.yml
├── nginx/
│   ├── nginx.conf               # Reverse proxy config
│   └── Dockerfile
├── scripts/
│   ├── deploy.sh                # Terraform-based deploy
│   └── deploy-k8s.sh            # Minikube deploy
├── terraform/                   # Infrastructure as Code (Docker provider)
├── docs/
│   ├── SLOs.md                  # Full SLO definitions
│   └── agent/                   # Deep-dive documentation
│       ├── auth_flow.md
│       ├── checkout_state.md
│       ├── database_schema.md
│       ├── frontend_state.md
│       └── repo_map_guidelines.md
├── .env.example                 # Root environment variables
├── AGENTS.md                    # Repository conventions
├── docker-compose.yml           # Full stack with monitoring + load testing
└── REPO_MAP.md                  # Repository map
```

## Documentation

- `AGENTS.md` — Repository conventions, tooling, and architectural boundaries
- `REPO_MAP.md` — Repository map and codebase navigation
- `docs/SLOs.md` — SLO definitions, targets, and measurement methodology
- `docs/agent/auth_flow.md` — JWT authentication flow (register, login, token verification)
- `docs/agent/database_schema.md` — All SQLModel tables, relationships, and indexes
- `docs/agent/checkout_state.md` — Checkout flow, order status lifecycle, stock locking
- `docs/agent/frontend_state.md` — Zustand stores, API client, data flow patterns
- `docs/agent/repo_map_guidelines.md` — Guidelines for maintaining the repo map

## CI/CD

### Overview

| Pipeline | Trigger | Runner | Action |
|---|---|---|---|
| **CI** | Push/PR → main | GitHub-hosted | Backend tests, frontend tests + lint, build & push images to GHCR |
| **Deploy** | CI success on main (or manual dispatch) | Self-hosted (`laptop`) | Pull latest images from GHCR, `terraform apply` |
| **Terraform Plan** | PR touching `terraform/` | Self-hosted | `terraform validate`, `terraform plan` |

### Workflows

- **`.github/workflows/ci.yml`** — Backend tests (PostgreSQL service container), frontend tests + lint, Docker build & push to GHCR (backend, frontend, nginx images).
- **`.github/workflows/deploy.yml`** — Triggered by CI completion on main or `workflow_dispatch`. Pulls `:latest` images from GHCR and runs `terraform apply -auto-approve` on the self-hosted runner.
- **`.github/workflows/terraform-plan.yml`** — Triggered on PRs touching `terraform/`. Runs `terraform validate` and `terraform plan` on the self-hosted runner.

### Self-hosted Runner Setup (Laptop)

1. Go to repo **Settings → Actions → Runners → New self-hosted runner**
2. Follow the OS-specific download and configure steps
3. When prompted for labels, enter: `laptop`
4. Start the runner service

### Required Secrets

| Secret | Purpose |
|---|---|
| `GITHUB_TOKEN` | Built-in token — used for GHCR authentication in CI and Deploy workflows |

### Self-hosted Runner Security

Deploy is triggered via `workflow_run` on CI completion (push to `main`) or manually via `workflow_dispatch`. It will **not** trigger on PRs from forks, preventing untrusted code from reaching the self-hosted runner.

### Terraform

Terraform uses the **kreuzwerker/docker** provider to manage Docker containers directly (no cloud infrastructure). State is stored **locally** in `terraform/terraform.tfstate`.

To run Terraform locally:

```bash
cd terraform
terraform init
terraform apply
```

### Manual Deploy (Fallback)

```bash
# Pulls images from GHCR and deploys via Terraform
GITHUB_REPOSITORY_OWNER=myuser ./scripts/deploy.sh
```

## Environment Variables

| Variable | Default | Service | Description |
|----------|---------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5433/ecommerce` | Backend | PostgreSQL connection string |
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | Backend | JWT signing key |
| `ALGORITHM` | `HS256` | Backend | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Backend | JWT expiry |
| `SLI_ENABLED` | `true` | Backend | Enable SLI validation metrics |
| `VITE_API_URL` | `http://localhost:8000` | Frontend | Backend API base URL |
