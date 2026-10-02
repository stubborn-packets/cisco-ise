# terraform/modules/condition/main.tf
# One Network Access library condition.
# condition_type is the operator. Children are the operands.
# An attribute call leaves children empty. An AND/OR call leaves the
# leaf attributes empty. Do not use the Device Admin resource.
# Resource address: module.<label>.ise_network_access_condition.this

resource "ise_network_access_condition" "this" {
  name            = var.name
  description     = var.description != "" ? var.description : null
  condition_type  = var.condition_type
  is_negate       = var.is_negate
  dictionary_name = var.dictionary_name != "" ? var.dictionary_name : null
  attribute_name  = var.attribute_name != "" ? var.attribute_name : null
  operator        = var.operator != "" ? var.operator : null
  attribute_value = var.attribute_value != "" ? var.attribute_value : null

  children = length(var.children) == 0 ? null : [
    for child in var.children : {
      condition_type  = child.condition_type
      is_negate       = child.is_negate
      dictionary_name = child.dictionary_name != "" ? child.dictionary_name : null
      attribute_name  = child.attribute_name != "" ? child.attribute_name : null
      operator        = child.operator != "" ? child.operator : null
      attribute_value = child.attribute_value != "" ? child.attribute_value : null
      children = length(child.children) == 0 ? null : [
        for leaf in child.children : {
          condition_type  = leaf.condition_type
          is_negate       = leaf.is_negate
          dictionary_name = leaf.dictionary_name
          attribute_name  = leaf.attribute_name
          operator        = leaf.operator
          attribute_value = leaf.attribute_value
        }
      ]
    }
  ]

  lifecycle {
    precondition {
      condition = (
        var.condition_type != "LibraryConditionAttributes" ||
        (
          length(var.children) == 0 &&
          length(var.dictionary_name) > 0 &&
          length(var.attribute_name) > 0 &&
          length(var.operator) > 0 &&
          length(var.attribute_value) > 0
        )
      )
      error_message = "An attribute condition needs dictionary, attribute, operator, and value, and no children."
    }

    precondition {
      condition = (
        !contains(["LibraryConditionAndBlock", "LibraryConditionOrBlock"], var.condition_type) ||
        (
          length(var.children) >= 2 &&
          length(var.dictionary_name) == 0 &&
          length(var.attribute_name) == 0 &&
          length(var.operator) == 0 &&
          length(var.attribute_value) == 0
        )
      )
      error_message = "An AND/OR block needs at least two children and no leaf attributes."
    }
  }
}