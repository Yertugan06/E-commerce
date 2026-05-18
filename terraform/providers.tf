terraform {
  required_version = ">= 1.6"
  # No `cloud {}` block — state is stored in terraform.tfstate locally
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}