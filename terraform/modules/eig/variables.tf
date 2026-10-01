# terraform/modules/eig/variables.tf
# Inputs that map to ise_endpoint_identity_group.
# owner / bu / state / parent name live in policy YAML.
# parent UUID is not an input. First objects omit the parent id.

variable "name" {
  type        = string
  description = "ISE endpoint identity group name. EIG- + kebab-case."

  validation {
    condition     = can(regex("^EIG-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be EIG- + kebab-case (e.g. EIG-printers)."
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

variable "system_defined" {
  type        = bool
  default     = false
  description = "ISE built-in flag. Lab objects stay false."

  validation {
    condition     = var.system_defined == false
    error_message = "Do not manage system-defined endpoint identity groups."
  }
}