# terraform/modules/authorization-profile/main.tf
# One authorization profile. No SGT on the first lab object.
# Resource address: module.<label>.ise_authorization_profile.this

resource "ise_authorization_profile" "this" {
  name         = var.name
  description  = var.description != "" ? var.description : null
  access_type  = var.access_type
  profile_name = var.profile_name
  dacl_name    = var.dacl_name != "" ? var.dacl_name : null
  vlan_name_id = var.vlan_name_id != "" ? var.vlan_name_id : null
  vlan_tag_id  = var.vlan_name_id != "" ? var.vlan_tag_id : null
}