#!/usr/bin/env bash
set -euo pipefail

REGISTRY="ghcr.io"
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-}"
REPO_NAME="${GITHUB_REPOSITORY##*/}"

if [ -z "$REPO_OWNER" ]; then
  echo "Error: GITHUB_REPOSITORY_OWNER is not set."
  echo "Usage: GITHUB_REPOSITORY_OWNER=myuser ./scripts/deploy.sh"
  exit 1
fi

echo "=== Pulling latest images from $REGISTRY ==="
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-backend:latest"
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-frontend:latest"
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-nginx:latest"

echo "=== Writing deploy.auto.tfvars ==="
cat > terraform/deploy.auto.tfvars << EOF
backend_image_registry_prefix    = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
frontend_image_registry_prefix   = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
nginx_image_registry_prefix      = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
EOF

if ! command -v terraform &>/dev/null; then
  echo "Error: terraform is not installed or not in PATH."
  echo ""
  echo "Install it from: https://developer.hashicorp.com/terraform/install"
  echo "Or use 'docker compose up --build' for local development instead."
  exit 1
fi

echo "=== Applying Terraform ==="
terraform -chdir=terraform init -reconfigure
terraform -chdir=terraform apply -auto-approve

echo "=== Running database seed (reset stock, clear stale data) ==="
sleep 3
docker exec "${BACKEND_CONTAINER_NAME:-ecommerce-backend}-0" python -m scripts.seed 2>/dev/null \
  && echo "Seed OK" || echo "Seed skipped (first deploy may need manual run)"

echo "=== Deploy complete ==="
