# terraform/modules/authentication-rule/variables.tf
# Inputs for one ise_network_access_authentication_rule.
# CiscoDevNet/ise 0.4.1: required name, policy_set_id, and the three
# if_* actions. The rule is created inside an existing policy set.
# condition_type ConditionReference is fixed in main.tf.
# Do not set default. That flag owns the built-in Default rule.

variable "name" {
  type        = string
  description = "ISE authentication rule name. AN- + kebab-case. Not Default."

  validation {
    condition     = can(regex("^AN-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be AN- + kebab-case (e.g. AN-wired-dot1x)."
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
  description = "Rule order inside the set. Lower is first. 0 is the first non-default rule."

  validation {
    condition     = var.rank >= 0 && var.rank <= 98 && var.rank == floor(var.rank)
    error_message = "Rank must be an integer from 0 to 98."
  }
}

variable "state" {
  type        = string
  default     = "enabled"
  description = "enabled, disabled, or monitor. A disabled rule is not matched."

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
  description = "Negate the library-condition reference. Lab rules stay false."
}

variable "identity_source_name" {
  type        = string
  description = "Identity store name. Lab 802.1X uses Internal Users. MAB uses Internal Endpoints."

  validation {
    condition     = length(var.identity_source_name) > 0
    error_message = "identity_source_name is required. Lab values are Internal Users or Internal Endpoints."
  }
}

variable "if_auth_fail" {
  type        = string
  description = "Action when credentials fail. REJECT, DROP, or CONTINUE."

  validation {
    condition     = contains(["REJECT", "DROP", "CONTINUE"], var.if_auth_fail)
    error_message = "if_auth_fail must be REJECT, DROP, or CONTINUE."
  }
}

variable "if_process_fail" {
  type        = string
  description = "Action when ISE cannot reach the identity store. REJECT, DROP, or CONTINUE."

  validation {
    condition     = contains(["REJECT", "DROP", "CONTINUE"], var.if_process_fail)
    error_message = "if_process_fail must be REJECT, DROP, or CONTINUE."
  }
}

variable "if_user_not_found" {
  type        = string
  description = "Action when the identity is not in the store. MAB uses CONTINUE."

  validation {
    condition     = contains(["REJECT", "DROP", "CONTINUE"], var.if_user_not_found)
    error_message = "if_user_not_found must be REJECT, DROP, or CONTINUE."
  }
}