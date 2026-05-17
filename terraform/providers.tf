terraform {
  required_version = ">= 1.6"

  cloud {
    organization = "my-ecommerce-org"
    workspaces {
      name = "ecommerce-production"
    }
  }

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
}
