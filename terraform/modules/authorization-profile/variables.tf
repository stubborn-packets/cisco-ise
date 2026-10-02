# terraform/modules/authorization-profile/variables.tf
# Inputs that map to ise_authorization_profile.
# owner / bu / state live in policy YAML. This resource has no state field.
# SGT is not an input on the first lab object.

variable "name" {
  type        = string
  description = "ISE authorization profile name. PR- + kebab-case."

  validation {
    condition     = can(regex("^PR-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be PR- + kebab-case (e.g. PR-wired-lab-access)."
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

variable "access_type" {
  type        = string
  default     = "ACCESS_ACCEPT"
  description = "ACCESS_ACCEPT or ACCESS_REJECT."

  validation {
    condition     = contains(["ACCESS_ACCEPT", "ACCESS_REJECT"], var.access_type)
    error_message = "access_type must be ACCESS_ACCEPT or ACCESS_REJECT."
  }
}

variable "dacl_name" {
  type        = string
  default     = ""
  description = "ISE downloadable ACL name (ACL-...). Empty means no DACL."
}

variable "vlan_name_id" {
  type        = string
  default     = ""
  description = "VLAN name or ID string ISE returns to the NAD. Empty means no VLAN."
}

variable "vlan_tag_id" {
  type        = number
  default     = 1
  description = "RADIUS tunnel tag (0-31). 1 is the usual enterprise value."

  validation {
    condition     = var.vlan_tag_id >= 0 && var.vlan_tag_id <= 31
    error_message = "vlan_tag_id must be 0-31."
  }
}

variable "profile_name" {
  type        = string
  default     = "Cisco"
  description = "ISE network device profile. Built-in Cisco is the lab default."
}

variable "asa_vpn" {
  type        = string
  default     = ""
  description = "ASA VPN Class value. Lab VPN uses ou=gp-global-vpn. Empty means unset."
}

variable "reauthentication_timer" {
  type        = number
  default     = 0
  description = "Reauthentication timer in seconds. 0 means unset. ISE range is 1-65535."

  validation {
    condition     = var.reauthentication_timer == 0 || (var.reauthentication_timer >= 1 && var.reauthentication_timer <= 65535)
    error_message = "reauthentication_timer must be 0 or 1-65535."
  }
}

variable "reauthentication_connectivity" {
  type        = string
  default     = "DEFAULT"
  description = "Required by ISE when the timer is set. DEFAULT or RADIUS_REQUEST."

  validation {
    condition     = contains(["DEFAULT", "RADIUS_REQUEST"], var.reauthentication_connectivity)
    error_message = "reauthentication_connectivity must be DEFAULT or RADIUS_REQUEST."
  }
}