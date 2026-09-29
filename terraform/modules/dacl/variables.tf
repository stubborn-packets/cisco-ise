# terraform/modules/dacl/variables.tf
# Inputs that map to ise_downloadable_acl.
# owner / state live in policy YAML. This resource has no state field.

variable "name" {
  type        = string
  description = "ISE downloadable ACL name. ACL- + kebab-case."

  validation {
    condition     = can(regex("^ACL-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be ACL- + kebab-case (e.g. ACL-permit-all)."
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

variable "dacl" {
  type        = string
  description = "ACL body as ISE stores it (one ACE per line)."
}

variable "dacl_type" {
  type        = string
  default     = "IPV4"
  description = "ISE DACL type."

  validation {
    condition     = contains(["IPV4", "IPV6", "IP_AGNOSTIC"], var.dacl_type)
    error_message = "dacl_type must be IPV4, IPV6, or IP_AGNOSTIC."
  }
}