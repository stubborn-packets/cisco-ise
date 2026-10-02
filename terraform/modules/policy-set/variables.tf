# terraform/modules/policy-set/variables.tf
# Inputs for one ise_network_access_policy_set.
# CiscoDevNet/ise 0.4.1: required name + service_name. Rank, state, and
# the condition reference are optional on the resource and required here
# so a call cannot omit them.
# Authentication and authorization rules are not attributes of this
# resource. They are ise_network_access_authentication_rule and
# ise_network_access_authorization_rule, keyed by policy_set_id.
# Do not set default = true. The provider refuses to change rank or
# description when name is Default.

variable "name" {
  type        = string
  description = "ISE policy set name. PS- + kebab-case. Not Default."

  validation {
    condition     = can(regex("^PS-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be PS- + kebab-case (e.g. PS-global-wired-8021x)."
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

variable "rank" {
  type        = number
  description = "Evaluation order. Lower rank is evaluated first. Rank 99 is Default."

  validation {
    condition     = var.rank >= 0 && var.rank <= 98 && var.rank == floor(var.rank)
    error_message = "Rank must be an integer from 0 to 98. Rank 99 is the built-in Default."
  }
}

variable "state" {
  type        = string
  description = "enabled, disabled, or monitor. A disabled set is not matched."

  validation {
    condition     = contains(["enabled", "disabled", "monitor"], var.state)
    error_message = "state must be enabled, disabled, or monitor."
  }
}

variable "service_name" {
  type        = string
  description = "Allowed Protocols name. Not a proxy sequence. Not Default Network Access."

  validation {
    condition     = var.service_name != "Default Network Access" && length(var.service_name) > 0
    error_message = "Do not manage Default Network Access. Pass an AP- name."
  }
}

variable "is_proxy" {
  type        = bool
  default     = false
  description = "True only when service_name is a proxy sequence. Wired sets are allowed protocols."

  validation {
    condition     = var.is_proxy == false
    error_message = "This module writes allowed-protocols services only. is_proxy must be false."
  }
}

variable "condition_id" {
  type        = string
  description = "ISE UUID of a library condition. Pass module.cnd_*.id. Do not copy it into policy/."

  validation {
    condition     = length(var.condition_id) > 0
    error_message = "condition_id is the library condition UUID from the condition module output."
  }
}

variable "condition_is_negate" {
  type        = bool
  default     = false
  description = "Negate the library-condition reference. Wired sets stay false."
}