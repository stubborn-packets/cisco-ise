# terraform/modules/ndg/main.tf
# One network device group leaf. Roots (Location, Device Type, and any
# custom type node) are not this resource's first write.
# Resource address: module.<label>.ise_network_device_group.this

resource "ise_network_device_group" "this" {
  name        = var.name
  root_group  = var.root_group
  description = var.description != "" ? var.description : null
}