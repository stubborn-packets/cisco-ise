# terraform/modules/certificate-authentication-profile/variables.tf
# Inputs that map to ise_certificate_authentication_profile.
# owner / state live in policy YAML. This resource has no state field.
# description is written to ISE.
# Name is CAP_ + snake_case. ISE rejects hyphens. YAML name equals the ISE name.
# Schema reference (pinned provider): see environments/lab/versions.tf
# for the CiscoDevNet/ise version, then the matching
# ise_certificate_authentication_profile resource docs.

variable "name" {
  type        = string
  description = "ISE certificate authentication profile name. CAP_ + snake_case. ISE rejects hyphens."

  validation {
    condition     = can(regex("^CAP_[a-z0-9]+(_[a-z0-9]+)*$", var.name))
    error_message = "Name must be CAP_ + snake_case (e.g. CAP_lab_subject_cn). ISE rejects hyphens."
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

variable "allowed_as_user_name" {
  type        = bool
  default     = false
  description = "Allow the certificate attribute value to be used as the username."
}

variable "external_identity_store_name" {
  type        = string
  default     = "[not applicable]"
  description = "Referred identity store name, or [not applicable] when none is chosen."
}

variable "certificate_attribute_name" {
  type        = string
  default     = "SUBJECT_COMMON_NAME"
  description = "Attribute used when username_from is CERTIFICATE. Ignored when username_from is UPN."

  validation {
    condition = contains(
      [
        "SUBJECT_COMMON_NAME",
        "SUBJECT_ALTERNATIVE_NAME",
        "SUBJECT_SERIAL_NUMBER",
        "SUBJECT",
        "SUBJECT_ALTERNATIVE_NAME_OTHER_NAME",
        "SUBJECT_ALTERNATIVE_NAME_EMAIL",
        "SUBJECT_ALTERNATIVE_NAME_DNS",
        "ALL_SUBJECT_AND_ALTERNATIVE_NAMES",
      ],
      var.certificate_attribute_name
    )
    error_message = "certificate_attribute_name must be one of the provider choices."
  }
}

variable "match_mode" {
  type        = string
  default     = "NEVER"
  description = "Match mode of the certificate authentication profile."

  validation {
    condition = contains(
      ["NEVER", "RESOLVE_IDENTITY_AMBIGUITY", "BINARY_COMPARISON"],
      var.match_mode
    )
    error_message = "match_mode must be NEVER, RESOLVE_IDENTITY_AMBIGUITY, or BINARY_COMPARISON."
  }
}

variable "username_from" {
  type        = string
  default     = "CERTIFICATE"
  description = "Where the username is taken from. CERTIFICATE uses certificate_attribute_name. UPN is AD-only."

  validation {
    condition     = contains(["CERTIFICATE", "UPN"], var.username_from)
    error_message = "username_from must be CERTIFICATE or UPN."
  }
}