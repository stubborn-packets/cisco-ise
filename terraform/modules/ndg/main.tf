# terraform/modules/ndg/main.tf
# One network device group: a custom type container (is_root) or a leaf.
# Custom type container name is type#type, not the bare type token.
# Do not use is_root for Location or Device Type.
# Resource address: module.<label>.ise_network_device_group.this

resource "ise_network_device_group" "this" {
  name        = var.name
  root_group  = var.root_group
  description = var.description != "" ? var.description : null
}