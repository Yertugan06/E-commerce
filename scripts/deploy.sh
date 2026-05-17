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

if [ -z "${TFE_TOKEN:-}" ]; then
  echo "Error: TFE_TOKEN is not set."
  echo "Usage: GITHUB_REPOSITORY_OWNER=myuser TFE_TOKEN=<token> ./scripts/deploy.sh"
  echo ""
  echo "Tip: export TFE_TOKEN=\$(cat ~/.terraform.d/credentials.tfrc.json | jq -r '.credentials.\"app.terraform.io\".token')"
  exit 1
fi

echo "=== Pulling latest images from $REGISTRY ==="
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-backend:latest"
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-frontend:latest"
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-nginx:latest"
docker pull "$REGISTRY/$REPO_OWNER/$REPO_NAME/ecommerce-autoscaler:latest"

echo "=== Writing deploy.auto.tfvars ==="
cat > terraform/deploy.auto.tfvars << EOF
backend_image_registry_prefix    = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
frontend_image_registry_prefix   = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
nginx_image_registry_prefix      = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
autoscaler_image_registry_prefix = "$REGISTRY/$REPO_OWNER/$REPO_NAME/"
backend_image_tag     = "latest"
frontend_image_tag    = "latest"
nginx_image_tag       = "latest"
autoscaler_image_tag  = "latest"
EOF

echo "=== Applying Terraform ==="
terraform -chdir=terraform init -reconfigure
terraform -chdir=terraform apply -auto-approve

echo "=== Deploy complete ==="
