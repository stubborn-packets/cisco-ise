# terraform/modules/dacl/main.tf
# One downloadable ACL.
# Resource address: module.<label>.ise_downloadable_acl.this

resource "ise_downloadable_acl" "this" {
  name        = var.name
  description = var.description != "" ? var.description : null
  dacl        = var.dacl
  dacl_type   = var.dacl_type
}