# terraform/modules/condition/variables.tf
# Inputs that map to ise_network_access_condition.
# One resource. condition_type is the class: attribute, AND, or OR.
# owner / state live in policy YAML. This resource has no state field.
# Children are optional. An attribute call passes no children.
# Nested children are one level deep. A deeper nest widens this type.
# Cross-field rules (attribute vs block) are preconditions in main.tf.
# A variable validation can only read that variable.
# Do not use the Device Admin condition resource.

variable "name" {
  type        = string
  description = "ISE library condition name. CND- + kebab-case."

  validation {
    condition     = can(regex("^CND-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be CND- + kebab-case (e.g. CND-wired-dot1x)."
  }
}

variable "description" {
  type        = string
  default     = ""
  description = "Optional ISE description. ISE rejects < and > (XSS validation)."

  validation {
    condition     = !can(regex("[<>]", var.description))
    error_message = "ISE rejects < and > in description (XSS validation)."
  }
}

variable "condition_type" {
  type        = string
  default     = "LibraryConditionAttributes"
  description = "LibraryConditionAttributes, LibraryConditionAndBlock, or LibraryConditionOrBlock. The parent type is the operator."

  validation {
    condition = contains(
      ["LibraryConditionAttributes", "LibraryConditionAndBlock", "LibraryConditionOrBlock"],
      var.condition_type
    )
    error_message = "condition_type must be LibraryConditionAttributes, LibraryConditionAndBlock, or LibraryConditionOrBlock."
  }
}

variable "is_negate" {
  type        = bool
  default     = false
  description = "Negate the whole condition. Lab objects stay false."
}

variable "dictionary_name" {
  type        = string
  default     = ""
  description = "ISE dictionary for an attribute condition. Empty on an AND/OR block."
}

variable "attribute_name" {
  type        = string
  default     = ""
  description = "Dictionary attribute for an attribute condition. Empty on an AND/OR block."
}

variable "operator" {
  type        = string
  default     = ""
  description = "Comparison operator for an attribute condition. Empty on an AND/OR block."

  validation {
    condition = var.operator == "" || contains(
      [
        "contains", "endsWith", "equals", "greaterOrEquals", "greaterThan",
        "in", "ipEquals", "ipGreaterThan", "ipLessThan", "ipNotEquals",
        "lessOrEquals", "lessThan", "matches", "notContains", "notEndsWith",
        "notEquals", "notIn", "notStartsWith", "startsWith",
        "macContains", "macEndsWith", "macEquals", "macIn",
        "macNotContains", "macNotEndsWith", "macNotEquals", "macNotIn",
        "macNotStartsWith", "macStartsWith",
      ],
      var.operator
    )
    error_message = "operator must be empty or an ise_network_access_condition operator."
  }
}

variable "attribute_value" {
  type        = string
  default     = ""
  description = "Value compared by operator. Empty on an AND/OR block."
}

variable "children" {
  type = list(object({
    condition_type  = string
    dictionary_name = optional(string, "")
    attribute_name  = optional(string, "")
    operator        = optional(string, "")
    attribute_value = optional(string, "")
    is_negate       = optional(bool, false)
    children = optional(list(object({
      condition_type  = string
      dictionary_name = optional(string, "")
      attribute_name  = optional(string, "")
      operator        = optional(string, "")
      attribute_value = optional(string, "")
      is_negate       = optional(bool, false)
    })), [])
  }))
  default     = []
  description = "Operands of an AND/OR block. Empty for an attribute condition. Inner children are leaves."

  validation {
    condition = alltrue([
      for child in var.children : contains(
        ["ConditionAttributes", "ConditionAndBlock", "ConditionOrBlock", "ConditionReference"],
        child.condition_type
      )
    ])
    error_message = "Child condition_type must be ConditionAttributes, ConditionAndBlock, ConditionOrBlock, or ConditionReference."
  }

  validation {
    condition = alltrue([
      for child in var.children : (
        child.condition_type != "ConditionAttributes" ||
        (
          length(child.dictionary_name) > 0 &&
          length(child.attribute_name) > 0 &&
          length(child.attribute_value) > 0 &&
          length(child.children) == 0
        )
      )
    ])
    error_message = "A ConditionAttributes child needs dictionary, attribute, and value, and no children of its own."
  }

  validation {
    condition = alltrue([
      for child in var.children : (
        !contains(["ConditionAndBlock", "ConditionOrBlock"], child.condition_type) ||
        (
          length(child.children) >= 2 &&
          length(child.dictionary_name) == 0 &&
          length(child.attribute_name) == 0
        )
      )
    ])
    error_message = "An AND/OR child needs at least two inner leaves and no leaf attributes of its own."
  }

  validation {
    condition = alltrue(flatten([
      for child in var.children : [
        for leaf in child.children : (
          leaf.condition_type == "ConditionAttributes" &&
          length(leaf.dictionary_name) > 0 &&
          length(leaf.attribute_name) > 0 &&
          length(leaf.attribute_value) > 0
        )
      ]
    ]))
    error_message = "Inner children are leaves. Each needs ConditionAttributes, dictionary, attribute, and value."
  }
}