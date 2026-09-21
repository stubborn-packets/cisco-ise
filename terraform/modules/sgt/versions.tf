# terraform/modules/sgt/versions.tf
# Declares which provider this module speaks. Version pin stays in
# environments/lab/versions.tf so a later root can pin independently.

terraform {
  required_providers {
    ise = {
      source = "CiscoDevNet/ise"
    }
  }
}