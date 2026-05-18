locals {
  backend_image_ref  = var.backend_image_registry_prefix  == "" ? var.backend_image_name  : "${trimspace(var.backend_image_registry_prefix)}ecommerce-backend:${var.backend_image_tag}"
  frontend_image_ref = var.frontend_image_registry_prefix == "" ? var.frontend_image_name : "${trimspace(var.frontend_image_registry_prefix)}ecommerce-frontend:${var.frontend_image_tag}"
  nginx_image_ref    = var.nginx_image_registry_prefix    == "" ? var.nginx_image_name    : "${trimspace(var.nginx_image_registry_prefix)}ecommerce-nginx:${var.nginx_image_tag}"
  autoscaler_image_ref = var.autoscaler_image_registry_prefix == "" ? var.autoscaler_image_name : "${trimspace(var.autoscaler_image_registry_prefix)}ecommerce-autoscaler:${var.autoscaler_image_tag}"
}

resource "docker_network" "this" {
  name = var.network_name
}

# ── Volumes ────────────────────────────────────────────────────────────────────

resource "docker_volume" "postgres_data" {
  name = "ecommerce_postgres_data"
}

resource "docker_volume" "prometheus_data" {
  name = "ecommerce_prometheus_data"
}

resource "docker_volume" "grafana_data" {
  name = "ecommerce_grafana_data"
}

# ── PostgreSQL ────────────────────────────────────────────────────────────────

resource "docker_container" "postgres" {
  name    = var.postgres_container_name
  image   = var.postgres_image
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

# ── Backend (multi-replica) ───────────────────────────────────────────────────

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
  count  = var.backend_replicas
  name   = "${var.backend_container_name}-${count.index}"
  image  = local.backend_image_ref
  restart = "unless-stopped"

  labels {
    label = "com.ecommerce.autoscaler"
    value = "backend"
  }

  networks_advanced {
    name    = docker_network.this.name
    aliases = ["backend"]
  }

  ports {
    internal = 8000
  }

  env = [
    "DATABASE_URL=postgresql+asyncpg://${var.postgres_user}:${var.postgres_password}@${var.postgres_container_name}:5432/${var.postgres_db}",
    "SECRET_KEY=${var.backend_secret_key}",
    "ALGORITHM=${var.backend_algorithm}",
    "ACCESS_TOKEN_EXPIRE_MINUTES=${var.backend_access_token_expire_minutes}",
  ]

  depends_on = [docker_container.postgres]
}

# ── Nginx (load balancer) ─────────────────────────────────────────────────────

resource "docker_image" "nginx" {
  count = var.nginx_image_registry_prefix == "" ? 1 : 0
  name  = var.nginx_image_name
  build {
    context    = abspath("${path.module}/../nginx")
    dockerfile = "Dockerfile"
    tag        = [var.nginx_image_name]
  }

  triggers = {
    dir_sha256 = filesha256(abspath("${path.module}/../nginx/Dockerfile"))
  }
}

resource "docker_container" "nginx" {
  name    = var.nginx_container_name
  image   = local.nginx_image_ref
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 80
    external = var.nginx_port_external
  }

  depends_on = [docker_container.backend]
}

# ── Frontend ──────────────────────────────────────────────────────────────────

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
  name    = var.frontend_container_name
  image   = local.frontend_image_ref
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

  depends_on = [docker_container.nginx]
}

# ── Prometheus ────────────────────────────────────────────────────────────────

resource "docker_container" "prometheus" {
  name    = var.prometheus_container_name
  image   = var.prometheus_image
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 9090
    external = var.prometheus_port_external
  }

  volumes {
    container_path = "/etc/prometheus/prometheus.yml"
    host_path      = abspath("${path.module}/../prometheus/prometheus.yml")
    read_only      = true
  }

  volumes {
    container_path = "/etc/prometheus/rules"
    host_path      = abspath("${path.module}/../prometheus/rules")
    read_only      = true
  }

  volumes {
    volume_name    = docker_volume.prometheus_data.name
    container_path = "/prometheus"
  }

  command = [
    "--config.file=/etc/prometheus/prometheus.yml",
    "--storage.tsdb.path=/prometheus",
  ]

  depends_on = [docker_container.backend]
}

# ── Grafana ───────────────────────────────────────────────────────────────────

resource "docker_container" "grafana" {
  name    = var.grafana_container_name
  image   = var.grafana_image
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 3000
    external = var.grafana_port_external
  }

  env = [
    "GF_SECURITY_ADMIN_PASSWORD=${var.grafana_admin_password}",
  ]

  volumes {
    container_path = "/var/lib/grafana"
    volume_name    = docker_volume.grafana_data.name
  }

  volumes {
    container_path = "/etc/grafana/provisioning"
    host_path      = abspath("${path.module}/../grafana/provisioning")
    read_only      = true
  }

  volumes {
    container_path = "/var/lib/grafana/dashboards"
    host_path      = abspath("${path.module}/../grafana/dashboards")
    read_only      = true
  }

  depends_on = [docker_container.prometheus]
}

# ── Alertmanager ──────────────────────────────────────────────────────────────

resource "docker_container" "alertmanager" {
  name    = var.alertmanager_container_name
  image   = var.alertmanager_image
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  ports {
    internal = 9093
    external = var.alertmanager_port_external
  }

  volumes {
    container_path = "/etc/alertmanager/alertmanager.yml"
    host_path      = abspath("${path.module}/../prometheus/alertmanager.yml")
    read_only      = true
  }

  command = [
    "--config.file=/etc/alertmanager/alertmanager.yml",
    "--storage.path=/alertmanager",
  ]

  depends_on = [docker_container.prometheus]
}

# ── Auto-Scaler ───────────────────────────────────────────────────────────────

resource "docker_image" "autoscaler" {
  count = var.autoscaler_image_registry_prefix == "" ? 1 : 0
  name  = var.autoscaler_image_name
  build {
    context    = abspath("${path.module}/../autoscaler")
    dockerfile = "Dockerfile"
    tag        = [var.autoscaler_image_name]
  }

  triggers = {
    dir_sha256 = filesha256(abspath("${path.module}/../autoscaler/Dockerfile"))
  }
}

resource "docker_container" "autoscaler" {
  name    = var.autoscaler_container_name
  image   = local.autoscaler_image_ref
  restart = "unless-stopped"

  networks_advanced {
    name = docker_network.this.name
  }

  env = [
    "AUTOSCALER_PROMETHEUS_URL=http://${var.prometheus_container_name}:9090",
    "AUTOSCALER_COMPOSE_PROJECT=${var.autoscaler_compose_project}",
    "AUTOSCALER_SERVICE_NAME=${var.autoscaler_service_name}",
    "AUTOSCALER_MIN_REPLICAS=${var.autoscaler_min_replicas}",
    "AUTOSCALER_MAX_REPLICAS=${var.autoscaler_max_replicas}",
    "AUTOSCALER_SCALE_UP_THRESHOLD=${var.autoscaler_scale_up_threshold}",
    "AUTOSCALER_SCALE_DOWN_THRESHOLD=${var.autoscaler_scale_down_threshold}",
    "AUTOSCALER_COOLDOWN_SECONDS=${var.autoscaler_cooldown_seconds}",
    "AUTOSCALER_P95_LATENCY_THRESHOLD=${var.autoscaler_p95_latency_threshold}",
    "AUTOSCALER_REQUEST_RATE_THRESHOLD=${var.autoscaler_request_rate_threshold}",
    "AUTOSCALER_POLL_INTERVAL=${var.autoscaler_poll_interval}",
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
    read_only      = true
  }

  depends_on = [docker_container.prometheus, docker_container.backend]
}
