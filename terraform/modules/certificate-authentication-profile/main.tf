# terraform/modules/certificate-authentication-profile/main.tf
# One certificate authentication profile.
# Resource address: module.<label>.ise_certificate_authentication_profile.this
# Do not manage built-in profiles. description is written to ISE when non-empty.

resource "ise_certificate_authentication_profile" "this" {
  name                         = var.name
  description                  = var.description != "" ? var.description : null
  allowed_as_user_name         = var.allowed_as_user_name
  external_identity_store_name = var.external_identity_store_name
  certificate_attribute_name   = var.certificate_attribute_name
  match_mode                   = var.match_mode
  username_from                = var.username_from
}