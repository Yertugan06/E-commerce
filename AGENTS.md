# Repository Agent Guide (E-Commerce MVP)

## 1. Context & Core Intent (The WHY)
This repository is a lightweight, high-performance E-Commerce MVP designed for rapid scaling. 
- **Backend:** FastAPI + SQLModel + PostgreSQL (Asynchronous).
- **Frontend:** React + Vite + TailwindCSS.
- **Architectural Style:** Feature-Sliced Design (FSD) coupled with Clean Architecture principles.

## 2. Architectural Boundaries (The WHAT)
We enforce a strict separation of concerns. Do not bypass these boundaries:
- **Monorepo Split:** `/backend` and `/frontend` are completely isolated workspaces.
- **Backend Layers:** Inside `/backend/app/features/{feature_name}/`, dependencies must strictly flow inward: `Presentation -> Application -> Domain`. The `Domain` layer must remain pure Python and free of direct framework dependencies.
- **Frontend Layers:** Follow Feature-Sliced Design. Code is stratified into `app`, `pages`, `widgets`, `features`, `entities`, and `shared`. Cross-importing between features or slices on the same level is strictly prohibited.

## 3. Tooling & Local Execution (The HOW)
We use specific tools and environment isolation. Always default to these commands:

### Backend
- **Environment Management:** Python 3.11+ isolated via a standard virtual environment (`.venv`). 
- **Package Management:** We use `uv` to manage dependencies within the venv (do not use raw pip). Always ensure the `.venv` is active or let `uv` target it automatically.
- **Database Migrations:** Managed exclusively via Alembic. Run `uv run alembic upgrade head` after schema changes.
- **Run Command:** `uv run uvicorn app.main:app --reload`
- **Tests:** `uv run pytest -v` (requires a running PostgreSQL instance)

### Frontend
- **Package Manager:** `bun` (do not use npm or yarn).
- **Run Command:** `bun run dev`
- **Tests:** `bun run test`
- **Lint:** `bun run lint`

### Monorepo Orchestration
- **Docker Compose:** Use `docker-compose up --build` to spin up local PostgreSQL, backend, and frontend concurrently for integration testing.
  - *Note:* The local `.venv` is excluded from containers via `.dockerignore`. Do not attempt to run `uv` commands inside docker services manually.
- **Terraform (IaC):** Use `terraform -chdir=terraform apply` to provision the full stack via the Docker provider.

- **Terraform Drift Recovery:** If `terraform apply` reports "No changes" in ~1s despite containers being down:
  1. Sync state with reality: `terraform -chdir=terraform apply -refresh-only`
  2. Re-create drifted resources: `terraform -chdir=terraform taint <resource>` then `terraform -chdir=terraform apply`
  3. Import orphaned containers: `terraform -chdir=terraform import docker_container.<name> <container_id>` 
- **Kubernetes (auto-scaling):** Deploy the full stack to minikube with auto-scaling via HPA:
  - Prerequisites: `minikube start`
  - Deploy: `scripts/deploy-k8s.sh`
  - View HPA: `kubectl get hpa -n ecommerce backend`
  - Access app: `minikube ip:30080`
  - Scale test: `kubectl run -it --rm load-test --image=busybox -- sh -c "while true; do wget -q -O- http://nginx:80/health; done"`

## 4. Deep-Dive Documentation Pointers (Progressive Disclosure)
Do not guess schema layouts or complex validation rules. Read these specific files *only* if your current task explicitly requires modifying these subsystems:

- Database Schema & ERD details: See `docs/agent/database_schema.md`
- Authentication & JWT implementation details: See `docs/agent/auth_flow.md`
- Checkout Transaction & Stock Locking state rules: See `docs/agent/checkout_state.md`
- Frontend State Management (Zustand) patterns: See `docs/agent/frontend_state.md`
- Repository Layout & Structural Synchronization: See `docs/agent/repo_map_guidelines.md` before making file structure modifications or completing large tasks.

