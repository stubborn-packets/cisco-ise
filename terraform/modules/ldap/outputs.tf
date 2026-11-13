# terraform/modules/ldap/outputs.tf
# Outputs for a future ise_ldap resource.
# FUTURE FEATURE — id is not available until the provider supports the resource.
# name is always available so other families can reference it by string.

output "name" {
  description = "ISE LDAP identity source name."
  value       = var.name
}

output "id" {
  description = "ISE UUID. Empty until the provider supports LDAP and the resource is live."
  value       = ""
}