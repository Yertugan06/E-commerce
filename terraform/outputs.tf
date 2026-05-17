output "network_name" {
  description = "Docker bridge network name"
  value       = docker_network.this.name
}

output "postgres" {
  description = "PostgreSQL connection details"
  value = {
    container_name = docker_container.postgres.name
    host_port      = var.postgres_port_external
    internal_url   = "postgresql://${var.postgres_user}:${var.postgres_password}@${var.postgres_container_name}:5432/${var.postgres_db}"
    external_url   = "postgresql://${var.postgres_user}:${var.postgres_password}@localhost:${var.postgres_port_external}/${var.postgres_db}"
  }
  sensitive = true
}

output "backend" {
  description = "Backend API details"
  value = {
    container_name = docker_container.backend.name
    url            = "http://localhost:${var.backend_port_external}"
    docs_url       = "http://localhost:${var.backend_port_external}/docs"
  }
}

output "frontend" {
  description = "Frontend app details"
  value = {
    container_name = docker_container.frontend.name
    url            = "http://localhost:${var.frontend_port_external}"
  }
}
