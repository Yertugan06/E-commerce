locals {
  backend_image_ref  = var.backend_image_registry_prefix  == "" ? var.backend_image_name  : "${trimspace(var.backend_image_registry_prefix)}ecommerce-backend:${var.backend_image_tag}"
  frontend_image_ref = var.frontend_image_registry_prefix == "" ? var.frontend_image_name : "${trimspace(var.frontend_image_registry_prefix)}ecommerce-frontend:${var.frontend_image_tag}"
}

resource "docker_network" "this" {
  name = var.network_name
}

resource "docker_volume" "postgres_data" {
  name = "ecommerce_postgres_data"
}

resource "docker_container" "postgres" {
  name  = var.postgres_container_name
  image = var.postgres_image
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 5432
    external = var.postgres_port_external
  }

  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}",
  ]

  healthcheck {
    test         = ["CMD-SHELL", "pg_isready -U ${var.postgres_user}"]
    interval     = "5s"
    timeout      = "5s"
    retries      = 5
    start_period = "10s"
  }
}

resource "docker_image" "backend" {
  count = var.backend_image_registry_prefix == "" ? 1 : 0
  name  = var.backend_image_name
  build {
    context    = abspath("${path.module}/../backend")
    dockerfile = "Dockerfile"
    tag        = [var.backend_image_name]
  }

  triggers = {
    dir_sha256 = filesha256(abspath("${path.module}/../backend/Dockerfile"))
  }
}

resource "docker_container" "backend" {
  name  = var.backend_container_name
  image = local.backend_image_ref
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 8000
    external = var.backend_port_external
  }

  env = [
    "DATABASE_URL=postgresql+asyncpg://${var.postgres_user}:${var.postgres_password}@${var.postgres_container_name}:5432/${var.postgres_db}",
    "SECRET_KEY=${var.backend_secret_key}",
    "ALGORITHM=${var.backend_algorithm}",
    "ACCESS_TOKEN_EXPIRE_MINUTES=${var.backend_access_token_expire_minutes}",
  ]

  depends_on = [docker_container.postgres]
}

resource "docker_image" "frontend" {
  count = var.frontend_image_registry_prefix == "" ? 1 : 0
  name  = var.frontend_image_name
  build {
    context    = abspath("${path.module}/../frontend")
    dockerfile = "Dockerfile"
    tag        = [var.frontend_image_name]
  }

  triggers = {
    dir_sha256 = filesha256(abspath("${path.module}/../frontend/Dockerfile"))
  }
}

resource "docker_container" "frontend" {
  name  = var.frontend_container_name
  image = local.frontend_image_ref
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 5173
    external = var.frontend_port_external
  }

  env = [
    "VITE_API_URL=${var.frontend_vite_api_url}",
  ]

  depends_on = [docker_container.backend]
}
