# terraform/modules/identity-source-sequence/variables.tf
# Inputs that map to ise_identity_source_sequence.
# owner / state live in policy YAML. This resource has no state field.
# break_on_store_fail defaults to false (continue on store failure).
# The reader always emits the YAML value.

variable "name" {
  type        = string
  description = "ISE identity source sequence name. ISS_ + snake_case. ISE rejects hyphens."

  validation {
    condition     = can(regex("^ISS_[a-z0-9]+(_[a-z0-9]+)*$", var.name))
    error_message = "Name must be ISS_ + snake_case (e.g. ISS_lab_internal). ISE rejects hyphens."
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

variable "break_on_store_fail" {
  type        = bool
  default     = false
  description = "Do not access other stores if a selected store cannot be reached. false continues and treats the user as not found."
}

variable "certificate_authentication_profile" {
  type        = string
  default     = ""
  description = "Optional certificate authentication profile name. Empty string means none."
}

variable "identity_sources" {
  type = list(object({
    name  = string
    order = number
  }))
  description = "Ordered list of identity source names. Order starts at 1."

  validation {
    condition     = length(var.identity_sources) > 0
    error_message = "identity_sources must contain at least one entry."
  }

  validation {
    condition = alltrue([
      for s in var.identity_sources : s.order >= 1
    ])
    error_message = "Each identity source order must be >= 1."
  }
}