# terraform/modules/eig/main.tf
# One static endpoint identity group.
# Do not set parent_endpoint_identity_group_id. ISE hangs new groups
# off the root. Do not create endpoints here.
# Resource address: module.<label>.ise_endpoint_identity_group.this

resource "ise_endpoint_identity_group" "this" {
  name           = var.name
  description    = var.description != "" ? var.description : null
  system_defined = var.system_defined
}