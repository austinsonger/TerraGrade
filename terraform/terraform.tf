terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.36.0"
    }

    acme = {
      source  = "vancluever/acme"
      version = "~> 2.20.0"
    }
  }

  required_version = ">= 1.5.0"
}
