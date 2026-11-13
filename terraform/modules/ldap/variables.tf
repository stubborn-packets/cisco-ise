# terraform/modules/ldap/variables.tf
# Inputs that map to a future ise_ldap resource.
# FUTURE FEATURE — not wired to a live provider resource yet.
# owner / state live in policy YAML. Bind password is never a variable here.
# All values come from policy/ldap.yaml via the reader (when it is extended).

variable "name" {
  type        = string
  description = "ISE LDAP identity source name. LDAP- + kebab-case."

  validation {
    condition     = can(regex("^LDAP-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be LDAP- + kebab-case (e.g. LDAP-lab-stubbornpackets-uid)."
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

variable "host" {
  type        = string
  description = "LDAP server hostname or IP. Empty string is allowed while the object is hand-built."
}

variable "port" {
  type        = number
  default     = 389
  description = "LDAP port. 389 for plain LDAP."
}

variable "enable_secure_connection" {
  type        = bool
  default     = false
  description = "Use LDAPS / StartTLS. False for the current lab (plain 389)."
}

variable "base_dn" {
  type        = string
  description = "Base DN for the directory."
}

variable "bind_dn" {
  type        = string
  description = "Bind DN used by ISE to connect."
}

variable "user_search_base" {
  type        = string
  description = "Search base for subjects (users)."
}

variable "subject_object_class" {
  type        = string
  description = "Object class of user entries (e.g. inetOrgPerson)."
}

variable "subject_name_attribute" {
  type        = string
  description = "Attribute that holds the username (e.g. uid)."
}

variable "group_search_base" {
  type        = string
  description = "Search base for groups."
}

variable "group_object_class" {
  type        = string
  description = "Object class of group entries (e.g. posixGroup)."
}

variable "group_map_attribute" {
  type        = string
  description = "Attribute that holds group members (e.g. memberUid)."
}

variable "subjects_in_groups_stored_as" {
  type        = string
  default     = "username"
  description = "How the member attribute value is interpreted. username for posixGroup + memberUid."
}

variable "groups" {
  type        = list(string)
  default     = []
  description = "Groups selected into ISE. Documentation only until the provider supports LDAP."
}