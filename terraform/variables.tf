variable "network_name" {
  description = "Name of the Docker bridge network for inter-container communication"
  type        = string
  default     = "ecommerce-network"
}

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

variable "backend_image_name" {
  description = "Tag for the built backend Docker image"
  type        = string
  default     = "ecommerce-backend:latest"
}

variable "backend_container_name" {
  description = "Name of the backend container"
  type        = string
  default     = "ecommerce-backend"
}

variable "backend_port_external" {
  description = "Host port mapped to the backend (8000)"
  type        = number
  default     = 8000
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
