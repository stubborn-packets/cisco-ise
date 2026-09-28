# terraform/modules/allowed-protocols/main.tf
# One Network Access allowed-protocols object.
# Do not manage Default Network Access. Do not use the TACACS resource.
# Resource address: module.<label>.ise_allowed_protocols.this
#
# ISE 3.3 requires allow_5g on every POST. When allow_peap / allow_teap /
# allow_eap_tls is true, the matching inner attributes must be present.

resource "ise_allowed_protocols" "this" {
  name                         = var.name
  description                  = var.description != "" ? var.description : null
  process_host_lookup          = var.process_host_lookup
  allow_pap_ascii              = var.allow_pap_ascii
  allow_chap                   = var.allow_chap
  allow_ms_chap_v1             = var.allow_ms_chap_v1
  allow_ms_chap_v2             = var.allow_ms_chap_v2
  allow_eap_md5                = var.allow_eap_md5
  allow_leap                   = var.allow_leap
  allow_eap_tls                = var.allow_eap_tls
  allow_eap_ttls               = var.allow_eap_ttls
  allow_eap_fast               = var.allow_eap_fast
  allow_peap                   = var.allow_peap
  allow_teap                   = var.allow_teap
  allow_preferred_eap_protocol = var.allow_preferred_eap_protocol
  allow_weak_ciphers_for_eap   = var.allow_weak_ciphers_for_eap
  eap_tls_l_bit                = var.eap_tls_l_bit
  require_message_auth         = var.require_message_auth
  allow_5g                     = var.allow_5g

  eap_tls_allow_auth_of_expired_certs     = var.allow_eap_tls ? var.eap_tls_allow_auth_of_expired_certs : null
  eap_tls_enable_stateless_session_resume = var.allow_eap_tls ? var.eap_tls_enable_stateless_session_resume : null

  peap_allow_peap_eap_ms_chap_v2                    = var.allow_peap ? var.peap_allow_peap_eap_ms_chap_v2 : null
  peap_allow_peap_eap_ms_chap_v2_pwd_change         = var.allow_peap && var.peap_allow_peap_eap_ms_chap_v2 ? var.peap_allow_peap_eap_ms_chap_v2_pwd_change : null
  peap_allow_peap_eap_ms_chap_v2_pwd_change_retries = var.allow_peap && var.peap_allow_peap_eap_ms_chap_v2 ? var.peap_allow_peap_eap_ms_chap_v2_pwd_change_retries : null
  peap_allow_peap_eap_gtc                           = var.allow_peap ? var.peap_allow_peap_eap_gtc : null
  peap_allow_peap_eap_tls                           = var.allow_peap ? var.peap_allow_peap_eap_tls : null
  peap_allow_peap_eap_tls_auth_of_expired_certs     = var.allow_peap && var.peap_allow_peap_eap_tls ? var.peap_allow_peap_eap_tls_auth_of_expired_certs : null
  peap_peap_v0                                      = var.allow_peap ? var.peap_peap_v0 : null
  require_cryptobinding                             = var.allow_peap ? var.require_cryptobinding : null

  teap_eap_tls                               = var.allow_teap ? var.teap_eap_tls : null
  teap_eap_tls_auth_of_expired_certs         = var.allow_teap && var.teap_eap_tls ? var.teap_eap_tls_auth_of_expired_certs : null
  teap_eap_ms_chap_v2                        = var.allow_teap ? var.teap_eap_ms_chap_v2 : null
  teap_eap_accept_client_cert_during_tunnel_est = var.allow_teap ? var.teap_eap_accept_client_cert_during_tunnel_est : null
  teap_eap_chaining                          = var.allow_teap ? var.teap_eap_chaining : null
  teap_downgrade_msk                         = var.allow_teap ? var.teap_downgrade_msk : null
  teap_request_basic_pwd_auth                = var.allow_teap ? var.teap_request_basic_pwd_auth : null
}