# terraform/modules/ldap/versions.tf
# Thin module for one LDAP identity source.
# FUTURE FEATURE — the pinned CiscoDevNet/ise 0.4.1 provider has no
# LDAP identity-source resource. This module is a skeleton only.
# The live object is created by hand in the ISE GUI under the YAML name
# until the provider adds support. Phase 15 will document the hand-build.

terraform {
  required_providers {
    ise = {
      source  = "CiscoDevNet/ise"
      version = "0.4.1"
    }
  }
}