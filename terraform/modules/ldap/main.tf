# terraform/modules/ldap/main.tf
# One LDAP identity source.
# Resource address (future): module.<label>.ise_ldap.this
#
# FUTURE FEATURE — NOT MANAGED BY TERRAFORM YET
# The pinned CiscoDevNet/ise 0.4.1 provider has no LDAP identity-source
# resource. This file is a placeholder. The live object is created by hand
# in the ISE GUI under the exact name from policy/ldap.yaml.
# When the provider adds the resource, replace the comment below with the
# real resource block and remove the null_resource (or count = 0) guard.
# Phase 15 operational docs will cover the hand-build steps.

# Placeholder so the module can be referenced without creating anything.
# Remove this and uncomment the resource block when the provider supports it.
resource "null_resource" "placeholder" {
  triggers = {
    name = var.name
  }
}

# Future resource (do not enable until the provider has ise_ldap or equivalent):
#
# resource "ise_ldap" "this" {
#   name                         = var.name
#   description                  = var.description != "" ? var.description : null
#   host                         = var.host
#   port                         = var.port
#   enable_secure_connection     = var.enable_secure_connection
#   base_dn                      = var.base_dn
#   bind_dn                      = var.bind_dn
#   user_search_base             = var.user_search_base
#   subject_object_class         = var.subject_object_class
#   subject_name_attribute       = var.subject_name_attribute
#   group_search_base            = var.group_search_base
#   group_object_class           = var.group_object_class
#   group_map_attribute          = var.group_map_attribute
#   subjects_in_groups_stored_as = var.subjects_in_groups_stored_as
#   groups                       = var.groups
#   # bind_password = var.bind_password  # sensitive, from env when supported
# }