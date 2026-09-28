# terraform/modules/allowed-protocols/variables.tf
# Inputs that map to ise_allowed_protocols.
# owner / state live in policy YAML. This resource has no state field.
# Do not manage Default Network Access with this module.

variable "name" {
  type        = string
  description = "ISE allowed-protocols name. AP- + kebab-case."

  validation {
    condition     = can(regex("^AP-[a-z0-9]+(-[a-z0-9]+)*$", var.name))
    error_message = "Name must be AP- + kebab-case (e.g. AP-wired-dot1x)."
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

variable "process_host_lookup" {
  type        = bool
  default     = false
  description = "MAB / host lookup. True on AP-wired-mab. False on AP-wired-dot1x."
}

variable "allow_pap_ascii" {
  type        = bool
  default     = false
  description = "Allow PAP ASCII."
}

variable "allow_chap" {
  type        = bool
  default     = false
  description = "Allow CHAP."
}

variable "allow_ms_chap_v1" {
  type        = bool
  default     = false
  description = "Allow MS-CHAPv1."
}

variable "allow_ms_chap_v2" {
  type        = bool
  default     = false
  description = "Allow MS-CHAPv2."
}

variable "allow_eap_md5" {
  type        = bool
  default     = false
  description = "Allow EAP-MD5."
}

variable "allow_leap" {
  type        = bool
  default     = false
  description = "Allow LEAP."
}

variable "allow_eap_tls" {
  type        = bool
  default     = false
  description = "Allow EAP-TLS."
}

variable "allow_eap_ttls" {
  type        = bool
  default     = false
  description = "Allow EAP-TTLS."
}

variable "allow_eap_fast" {
  type        = bool
  default     = false
  description = "Allow EAP-FAST."
}

variable "allow_peap" {
  type        = bool
  default     = false
  description = "Allow PEAP."
}

variable "allow_teap" {
  type        = bool
  default     = false
  description = "Allow TEAP."
}

variable "allow_preferred_eap_protocol" {
  type        = bool
  default     = false
  description = "Prefer one EAP method. Lab first objects leave this off."
}

variable "allow_weak_ciphers_for_eap" {
  type        = bool
  default     = false
  description = "Allow weak EAP ciphers. Lab stays false."
}

variable "eap_tls_l_bit" {
  type        = bool
  default     = false
  description = "EAP-TLS L-bit. Lab stays false."
}

variable "require_message_auth" {
  type        = bool
  default     = false
  description = "Require RADIUS message authenticator."
}

variable "allow_5g" {
  type        = bool
  default     = false
  description = "Allow 5G. ISE 3.2+ requires this field on every object."
}

# Inner settings. Sent only when the parent method is true.
# ISE 3.3 400s if allow_peap / allow_teap / allow_eap_tls is true
# and the inner object is omitted.

variable "eap_tls_allow_auth_of_expired_certs" {
  type        = bool
  default     = false
  description = "Outer EAP-TLS: allow expired certs. Used when allow_eap_tls is true."
}

variable "eap_tls_enable_stateless_session_resume" {
  type        = bool
  default     = false
  description = "Outer EAP-TLS session resume. False avoids TTL fields."
}

variable "peap_allow_peap_eap_ms_chap_v2" {
  type        = bool
  default     = true
  description = "PEAP inner EAP-MSCHAPv2. Used when allow_peap is true."
}

variable "peap_allow_peap_eap_ms_chap_v2_pwd_change" {
  type        = bool
  default     = false
  description = "PEAP inner EAP-MSCHAPv2 password change."
}

variable "peap_allow_peap_eap_ms_chap_v2_pwd_change_retries" {
  type        = number
  default     = 0
  description = "PEAP inner EAP-MSCHAPv2 password-change retries (0-3). Required when inner MSCHAPv2 is on."

  validation {
    condition     = var.peap_allow_peap_eap_ms_chap_v2_pwd_change_retries >= 0 && var.peap_allow_peap_eap_ms_chap_v2_pwd_change_retries <= 3
    error_message = "PEAP MSCHAPv2 password-change retries must be 0-3."
  }
}

variable "peap_allow_peap_eap_gtc" {
  type        = bool
  default     = false
  description = "PEAP inner EAP-GTC."
}

variable "peap_allow_peap_eap_tls" {
  type        = bool
  default     = true
  description = "PEAP inner EAP-TLS."
}

variable "peap_allow_peap_eap_tls_auth_of_expired_certs" {
  type        = bool
  default     = false
  description = "PEAP inner EAP-TLS expired certs."
}

variable "peap_peap_v0" {
  type        = bool
  default     = false
  description = "PEAPv0."
}

variable "require_cryptobinding" {
  type        = bool
  default     = false
  description = "PEAP require cryptobinding. Required when allow_peap is true."
}

variable "teap_eap_tls" {
  type        = bool
  default     = true
  description = "TEAP inner EAP-TLS."
}

variable "teap_eap_tls_auth_of_expired_certs" {
  type        = bool
  default     = false
  description = "TEAP inner EAP-TLS expired certs."
}

variable "teap_eap_ms_chap_v2" {
  type        = bool
  default     = false
  description = "TEAP inner EAP-MSCHAPv2."
}

variable "teap_eap_accept_client_cert_during_tunnel_est" {
  type        = bool
  default     = true
  description = "TEAP accept client cert during tunnel setup."
}

variable "teap_eap_chaining" {
  type        = bool
  default     = false
  description = "TEAP EAP chaining. Off on the first lab object."
}

variable "teap_downgrade_msk" {
  type        = bool
  default     = false
  description = "TEAP downgrade to MSK."
}

variable "teap_request_basic_pwd_auth" {
  type        = bool
  default     = false
  description = "TEAP request basic password auth."
}