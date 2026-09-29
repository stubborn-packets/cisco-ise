# terraform/modules/condition/main.tf
# One Network Access library condition (attribute only).
# AND/OR children are a later module change. Do not use the Device Admin resource.
# Resource address: module.<label>.ise_network_access_condition.this

resource "ise_network_access_condition" "this" {
  name            = var.name
  description     = var.description != "" ? var.description : null
  condition_type  = var.condition_type
  is_negate       = var.is_negate
  dictionary_name = var.dictionary_name
  attribute_name  = var.attribute_name
  operator        = var.operator
  attribute_value = var.attribute_value
}