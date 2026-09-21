# terraform/modules/sgt/variables.tf
# Inputs that map to ise_trustsec_security_group.
# owner / bu / state live in policy YAML later. ISE has no fields for them.

variable "name" {
  type        = string
  description = "ISE SGT name. ERS allows [A-Za-z0-9_], max 32. Hyphens are rejected."

  validation {
    condition = (
      can(regex("^SGT_[a-z0-9]+(_[a-z0-9]+)*$", var.name)) &&
      length(var.name) <= 32
    )
    error_message = "SGT name must be SGT_ + snake_case, max 32 characters. ISE rejects hyphens."
  }
}

variable "value" {
  type        = number
  description = "Numeric tag. -1 lets ISE assign one. Do not use -1 if you want a stable tag."

  validation {
    condition     = var.value == -1 || (var.value >= 0 && var.value <= 65519)
    error_message = "value must be -1 (auto) or 0 through 65519."
  }
}

variable "description" {
  type        = string
  default     = ""
  description = "Optional ISE description. Ownership notes belong in policy YAML, not here."
}

variable "propagate_to_apic" {
  type        = bool
  default     = false
  description = "Send this SGT to ACI/APIC. Lab default is false."
}