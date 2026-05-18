# ── Network ───────────────────────────────────────────────────────────────────

variable "network_name" {
  description = "Name of the Docker bridge network for inter-container communication"
  type        = string
  default     = "ecommerce-network"
}

# ── PostgreSQL ────────────────────────────────────────────────────────────────

variable "postgres_image" {
  description = "PostgreSQL Docker image tag"
  type        = string
  default     = "postgres:15-alpine"
}

variable "postgres_container_name" {
  description = "Name of the PostgreSQL container"
  type        = string
  default     = "ecommerce-postgres"
}

variable "postgres_port_external" {
  description = "Host port mapped to PostgreSQL (5432)"
  type        = number
  default     = 5433
}

variable "postgres_user" {
  description = "PostgreSQL superuser name"
  type        = string
  default     = "postgres"
}

variable "postgres_password" {
  description = "PostgreSQL superuser password"
  type        = string
  sensitive   = true
  default     = "postgres"
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "ecommerce"
}

# ── Backend ───────────────────────────────────────────────────────────────────

variable "backend_image_name" {
  description = "Tag for the built backend Docker image"
  type        = string
  default     = "ecommerce-backend:latest"
}

variable "backend_container_name" {
  description = "Name prefix for backend containers (appended with -0, -1, ...)"
  type        = string
  default     = "ecommerce-backend"
}

variable "backend_replicas" {
  description = "Initial number of backend container replicas"
  type        = number
  default     = 1
}

variable "backend_secret_key" {
  description = "JWT signing secret key"
  type        = string
  sensitive   = true
  default     = "change-me-to-a-random-secret-key"
}

variable "backend_algorithm" {
  description = "JWT signing algorithm"
  type        = string
  default     = "HS256"
}

variable "backend_access_token_expire_minutes" {
  description = "JWT access token expiry in minutes"
  type        = number
  default     = 30
}

# ── Frontend ──────────────────────────────────────────────────────────────────

variable "frontend_image_name" {
  description = "Tag for the built frontend Docker image"
  type        = string
  default     = "ecommerce-frontend:latest"
}

variable "frontend_container_name" {
  description = "Name of the frontend container"
  type        = string
  default     = "ecommerce-frontend"
}

variable "frontend_port_external" {
  description = "Host port mapped to the frontend dev server (5173)"
  type        = number
  default     = 5173
}

variable "frontend_vite_api_url" {
  description = "Backend API base URL injected into the Vite dev server"
  type        = string
  default     = "http://localhost:8000"
}

# ── Nginx (load balancer) ─────────────────────────────────────────────────────

variable "nginx_image_name" {
  description = "Tag for the built nginx Docker image"
  type        = string
  default     = "ecommerce-nginx:latest"
}

variable "nginx_container_name" {
  description = "Name of the nginx container"
  type        = string
  default     = "ecommerce-nginx"
}

variable "nginx_port_external" {
  description = "Host port mapped to nginx (80)"
  type        = number
  default     = 8000
}

# ── Prometheus ────────────────────────────────────────────────────────────────

variable "prometheus_image" {
  description = "Prometheus Docker image tag"
  type        = string
  default     = "prom/prometheus:v2.53.0"
}

variable "prometheus_container_name" {
  description = "Name of the Prometheus container"
  type        = string
  default     = "ecommerce-prometheus"
}

variable "prometheus_port_external" {
  description = "Host port mapped to Prometheus (9090)"
  type        = number
  default     = 9090
}

# ── Grafana ───────────────────────────────────────────────────────────────────

variable "grafana_image" {
  description = "Grafana Docker image tag"
  type        = string
  default     = "grafana/grafana:11.1.0"
}

variable "grafana_container_name" {
  description = "Name of the Grafana container"
  type        = string
  default     = "ecommerce-grafana"
}

variable "grafana_port_external" {
  description = "Host port mapped to Grafana (3000)"
  type        = number
  default     = 3000
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  sensitive   = true
  default     = "admin"
}

# ── Auto-Scaler ───────────────────────────────────────────────────────────────

variable "autoscaler_image_name" {
  description = "Tag for the built autoscaler Docker image"
  type        = string
  default     = "ecommerce-autoscaler:latest"
}

variable "autoscaler_container_name" {
  description = "Name of the autoscaler container"
  type        = string
  default     = "ecommerce-autoscaler"
}

variable "autoscaler_compose_project" {
  description = "Docker Compose project name used by the autoscaler for scaling"
  type        = string
  default     = "ecommerce"
}

variable "autoscaler_service_name" {
  description = "Docker Compose service name to scale"
  type        = string
  default     = "backend"
}

variable "autoscaler_min_replicas" {
  description = "Minimum number of backend replicas"
  type        = number
  default     = 1
}

variable "autoscaler_max_replicas" {
  description = "Maximum number of backend replicas"
  type        = number
  default     = 5
}

variable "autoscaler_scale_up_threshold" {
  description = "CPU utilization ratio to trigger scale-up (0.0–1.0)"
  type        = number
  default     = 0.70
}

variable "autoscaler_scale_down_threshold" {
  description = "CPU utilization ratio to trigger scale-down (0.0–1.0)"
  type        = number
  default     = 0.30
}

variable "autoscaler_cooldown_seconds" {
  description = "Minimum seconds between scale actions"
  type        = number
  default     = 60
}

variable "autoscaler_p95_latency_threshold" {
  description = "P95 read latency in seconds to trigger scale-up"
  type        = number
  default     = 1.0
}

variable "autoscaler_request_rate_threshold" {
  description = "Requests per second per instance to trigger scale-up"
  type        = number
  default     = 50
}

variable "autoscaler_poll_interval" {
  description = "Seconds between autoscaler evaluation cycles"
  type        = number
  default     = 15
}

# ── Alertmanager ─────────────────────────────────────────────────────────────

variable "alertmanager_image" {
  description = "Alertmanager Docker image tag"
  type        = string
  default     = "prom/alertmanager:v0.27.0"
}

variable "alertmanager_container_name" {
  description = "Name of the Alertmanager container"
  type        = string
  default     = "ecommerce-alertmanager"
}

variable "alertmanager_port_external" {
  description = "Host port mapped to Alertmanager (9093)"
  type        = number
  default     = 9093
}

# ── Registry / CI-CD overrides ──────────────────────────────────────────────

variable "backend_image_registry_prefix" {
  description = "Registry prefix for the backend image (e.g. 'ghcr.io/myorg/myrepo/'). When non-empty, Terraform pulls instead of building locally."
  type        = string
  default     = ""
}

variable "frontend_image_registry_prefix" {
  description = "Registry prefix for the frontend image. When non-empty, Terraform pulls instead of building locally."
  type        = string
  default     = ""
}

variable "backend_image_tag" {
  description = "Image tag for the backend when pulling from a registry. Ignored when registry_prefix is empty."
  type        = string
  default     = "latest"
}

variable "frontend_image_tag" {
  description = "Image tag for the frontend when pulling from a registry. Ignored when registry_prefix is empty."
  type        = string
  default     = "latest"
}

variable "nginx_image_registry_prefix" {
  description = "Registry prefix for the nginx image. When non-empty, Terraform pulls instead of building locally."
  type        = string
  default     = ""
}

variable "nginx_image_tag" {
  description = "Image tag for nginx when pulling from a registry."
  type        = string
  default     = "latest"
}

variable "autoscaler_image_registry_prefix" {
  description = "Registry prefix for the autoscaler image. When non-empty, Terraform pulls instead of building locally."
  type        = string
  default     = ""
}

variable "autoscaler_image_tag" {
  description = "Image tag for the autoscaler when pulling from a registry."
  type        = string
  default     = "latest"
}
