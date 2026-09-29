# terraform/modules/condition/variables.tf
# Inputs that map to ise_network_access_condition.
# owner / state live in policy YAML. This resource has no state field.
# First objects are attribute conditions only. No children / AND / OR.

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
  description = "Optional ISE description. ISE ERS rejects < and > (XSS validation)."

  validation {
    condition     = !can(regex("[<>]", var.description))
    error_message = "ISE ERS rejects < and > in description (XSS validation)."
  }
}

variable "condition_type" {
  type        = string
  default     = "LibraryConditionAttributes"
  description = "ISE condition class. First objects are attribute conditions only."

  validation {
    condition     = var.condition_type == "LibraryConditionAttributes"
    error_message = "This module only writes LibraryConditionAttributes. AND/OR blocks are later."
  }
}

variable "is_negate" {
  type        = bool
  default     = false
  description = "Negate the match. Lab first objects stay false."
}

variable "dictionary_name" {
  type        = string
  description = "ISE dictionary (Radius, Network Access, DEVICE, ...)."
}

variable "attribute_name" {
  type        = string
  description = "Dictionary attribute (NAS-Port-Type, AuthenticationMethod, ...)."
}

variable "operator" {
  type        = string
  description = "ISE comparison operator."

  validation {
    condition = contains(
      [
        "contains",
        "endsWith",
        "equals",
        "greaterOrEquals",
        "greaterThan",
        "in",
        "ipEquals",
        "ipGreaterThan",
        "ipLessThan",
        "ipNotEquals",
        "lessOrEquals",
        "lessThan",
        "matches",
        "notContains",
        "notEndsWith",
        "notEquals",
        "notIn",
        "notStartsWith",
        "startsWith",
        "macContains",
        "macEndsWith",
        "macEquals",
        "macIn",
        "macNotContains",
        "macNotEndsWith",
        "macNotEquals",
        "macNotIn",
        "macNotStartsWith",
        "macStartsWith",
      ],
      var.operator
    )
    error_message = "operator must be an ise_network_access_condition operator."
  }
}

variable "attribute_value" {
  type        = string
  description = "Value compared by operator (Ethernet, Lookup, ...)."
}