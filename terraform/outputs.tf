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
    container_names = [for c in docker_container.backend : c.name]
    url             = "http://localhost:${var.nginx_port_external}"
    docs_url        = "http://localhost:${var.nginx_port_external}/docs"
    replicas        = var.backend_replicas
  }
}

output "frontend" {
  description = "Frontend app details"
  value = {
    container_name = docker_container.frontend.name
    url            = "http://localhost:${var.frontend_port_external}"
  }
}

output "nginx" {
  description = "Nginx load balancer details"
  value = {
    container_name = docker_container.nginx.name
    url            = "http://localhost:${var.nginx_port_external}"
  }
}

output "prometheus" {
  description = "Prometheus monitoring details"
  value = {
    container_name = docker_container.prometheus.name
    url            = "http://localhost:${var.prometheus_port_external}"
  }
}

output "grafana" {
  description = "Grafana dashboard details"
  value = {
    container_name = docker_container.grafana.name
    url            = "http://localhost:${var.grafana_port_external}"
    admin_password = var.grafana_admin_password
  }
  sensitive = true
}

output "alertmanager" {
  description = "Alertmanager details"
  value = {
    container_name = docker_container.alertmanager.name
    url            = "http://localhost:${var.alertmanager_port_external}"
  }
}

output "autoscaler" {
  description = "Auto-scaler configuration"
  value = {
    container_name  = docker_container.autoscaler.name
    min_replicas    = var.autoscaler_min_replicas
    max_replicas    = var.autoscaler_max_replicas
    scale_up_cpu    = var.autoscaler_scale_up_threshold
    scale_down_cpu  = var.autoscaler_scale_down_threshold
    cooldown        = var.autoscaler_cooldown_seconds
  }
}
