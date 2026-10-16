# terraform/modules/authorization-exception-rule/variables.tf
# Inputs for one ise_network_access_authorization_exception_rule.
# CiscoDevNet/ise 0.4.1: required name and policy_set_id.
# profiles is a set of profile names, not UUIDs.
# condition_type ConditionReference is fixed in main.tf.
# Do not set default. That flag owns the built-in Default rule.
# security_group is omitted. The first exception has no SGT.

variable "name" {
  type        = string
  description = "ISE exception rule name. EX- + kebab-case. Not Default."

  validation {
    condition     = can(regex("^EX-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be EX- + kebab-case (e.g. EX-vendor-wired-temp)."
  }
}

variable "policy_set_id" {
  type        = string
  description = "ISE UUID of the parent policy set. Pass module.ps_*.id. Do not copy it into policy/."

  validation {
    condition     = length(var.policy_set_id) > 0
    error_message = "policy_set_id is the policy set UUID from the policy-set module output."
  }
}

variable "description" {
  type        = string
  default     = ""
  description = "Review text. This resource has no description argument."
}

variable "rank" {
  type        = number
  default     = 0
  description = "Exception order inside the set. Lower is first. 0 is the first exception."

  validation {
    condition     = var.rank >= 0 && var.rank <= 98 && var.rank == floor(var.rank)
    error_message = "Rank must be an integer from 0 to 98."
  }
}

variable "state" {
  type        = string
  default     = "enabled"
  description = "enabled, disabled, or monitor. A disabled exception is not matched."

  validation {
    condition     = contains(["enabled", "disabled", "monitor"], var.state)
    error_message = "state must be enabled, disabled, or monitor."
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
  description = "Negate the library-condition reference. Lab exceptions stay false."
}

variable "profiles" {
  type        = set(string)
  description = "Authorization profile names. Not UUIDs. Lab exceptions pass PR-wired-lab-access."

  validation {
    condition     = length(var.profiles) > 0 && alltrue([for profile in var.profiles : length(profile) > 0])
    error_message = "profiles must contain at least one profile name."
  }

  validation {
    condition     = !contains(var.profiles, "PermitAccess") && !contains(var.profiles, "DenyAccess")
    error_message = "Do not return a built-in PermitAccess or DenyAccess profile from a managed exception."
  }
}