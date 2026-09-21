# terraform/modules/sgt/variables.tf
# Inputs that map to ise_trustsec_security_group.
# owner / bu / state live in policy YAML later. ISE has no fields for them.

variable "name" {
  type        = string
  description = "SGT name. PREFIX- + kebab-case, e.g. SGT-lab-bootstrap."

  validation {
    condition     = can(regex("^SGT-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "name must match SGT- + kebab-case (docs/naming.md)."
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