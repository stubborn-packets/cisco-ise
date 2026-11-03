# terraform/modules/identity-source-sequence/main.tf
# One identity source sequence.
# Resource address: module.<label>.ise_identity_source_sequence.this
# Do not manage built-in sequences. Certificate profile is optional.

resource "ise_identity_source_sequence" "this" {
  name                = var.name
  description         = var.description != "" ? var.description : null
  break_on_store_fail = var.break_on_store_fail

  certificate_authentication_profile = (
    var.certificate_authentication_profile != ""
    ? var.certificate_authentication_profile
    : null
  )

  identity_sources = var.identity_sources
}