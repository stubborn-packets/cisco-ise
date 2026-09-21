# environments/lab/versions.tf
# Plane: environment wiring. Pins the writer for this ISE only.
# No resources. No URL. No credentials.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    ise = {
      source  = "CiscoDevNet/ise"
      version = "0.4.1"
    }
  }
}