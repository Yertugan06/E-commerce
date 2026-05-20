#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== Checking minikube ==="
if ! minikube status &>/dev/null; then
  echo "Error: minikube is not running. Start it with: minikube start"
  exit 1
fi

echo "=== Enabling metrics-server ==="
minikube addons enable metrics-server 2>/dev/null || true

echo "=== Building images inside minikube ==="
minikube image build -t ecommerce-backend:latest -f backend/Dockerfile backend
MINIKUBE_IP=$(minikube ip)
minikube image build -t ecommerce-frontend:latest -f frontend/Dockerfile \
  --build-arg VITE_API_URL=http://${MINIKUBE_IP}:30080 \
  frontend

echo "=== Creating namespace ==="
kubectl apply -f k8s/namespace.yaml

echo "=== Deploying secrets ==="
kubectl apply -f k8s/secrets.yaml

echo "=== Deploying PostgreSQL ==="
kubectl apply -f k8s/postgres.yaml
echo "Waiting for postgres to be ready..."
kubectl wait --namespace=ecommerce --for=condition=ready pod -l app=postgres --timeout=120s

echo "=== Deploying backend ==="
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/backend-hpa.yaml

echo "=== Deploying nginx ==="
kubectl apply -f k8s/nginx.yaml

echo "=== Deploying frontend ==="
kubectl apply -f k8s/frontend.yaml

echo "=== Deploying monitoring stack ==="
kubectl apply -f k8s/prometheus-config.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/alertmanager.yaml
kubectl apply -f k8s/alert-receiver.yaml
kubectl apply -f k8s/grafana.yaml

echo "=== Deploying locust ==="
kubectl apply -f k8s/locust-config.yaml
kubectl apply -f k8s/locust.yaml

echo "=== Running alembic migrations and seed ==="
POD=$(kubectl get pod --namespace=ecommerce -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [ -n "$POD" ]; then
  echo "Waiting for backend pod to be ready..."
  kubectl wait --namespace=ecommerce --for=condition=ready pod "$POD" --timeout=120s
  echo "Running database migration and seed inside backend pod..."
  kubectl exec --namespace=ecommerce "$POD" -- uv run alembic upgrade head || true
  kubectl exec --namespace=ecommerce "$POD" -- uv run python -m scripts.seed || true
fi

echo ""
echo "=== Deploy complete ==="
MINIKUBE_IP=$(minikube ip)
echo ""
echo "  Application:   http://$MINIKUBE_IP:30080"
echo "  Grafana:       http://$MINIKUBE_IP:33000  (admin/admin)"
echo "  Prometheus:    http://$MINIKUBE_IP:39090"
echo ""
echo "  HPA status:    kubectl get hpa -n ecommerce backend"
echo "  Pods:          kubectl get pods -n ecommerce"
echo "  Logs:          kubectl logs -n ecommerce -l app=backend"
echo "  Scale test:    kubectl run -it --rm load-test --image=busybox -- sh -c \"while true; do wget -q -O- http://nginx:80/health; done\""
echo ""
