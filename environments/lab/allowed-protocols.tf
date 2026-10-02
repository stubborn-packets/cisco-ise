# environments/lab/allowed-protocols.tf
# First allowed-protocols writes. Two services. No Default Network Access.
# No for_each over policy/. No TACACS resource.
# allow_5g is required on ISE 3.2+ even when false.
# Inner PEAP/TEAP/EAP-TLS settings are required when those parents are true.

module "ap_wired_dot1x" {
  source = "../../terraform/modules/allowed-protocols"

  name          = "AP-wired-dot1x"
  description   = "Wired 802.1X. No MAB on this service."
  allow_eap_tls = true
  allow_teap    = true
  allow_peap    = true
  allow_5g      = false

  eap_tls_allow_auth_of_expired_certs     = false
  eap_tls_enable_stateless_session_resume = false

  peap_allow_peap_eap_ms_chap_v2                    = true
  peap_allow_peap_eap_ms_chap_v2_pwd_change         = false
  peap_allow_peap_eap_ms_chap_v2_pwd_change_retries = 0
  peap_allow_peap_eap_gtc                           = false
  require_cryptobinding                             = false
  peap_allow_peap_eap_tls                       = true
  peap_allow_peap_eap_tls_auth_of_expired_certs = false
  peap_peap_v0                                  = false

  teap_eap_tls                                  = true
  teap_eap_tls_auth_of_expired_certs            = false
  teap_eap_ms_chap_v2                           = false
  teap_eap_accept_client_cert_during_tunnel_est = true
  teap_eap_chaining                             = false
  teap_downgrade_msk                            = false
  teap_request_basic_pwd_auth                   = false
}

module "ap_wired_mab" {
  source = "../../terraform/modules/allowed-protocols"

  name                = "AP-wired-mab"
  description         = "Wired MAB host lookup. No EAP on this service."
  process_host_lookup = true
  allow_5g            = false
}

module "ap_vpn" {
  source = "../../terraform/modules/allowed-protocols"

  name             = "AP-vpn"
  description      = "VPN 802.1X. EAP-TLS, PEAP, TEAP, and PAP. No MAB."
  allow_pap_ascii  = true
  allow_eap_tls    = true
  allow_teap       = true
  allow_peap       = true
  allow_5g         = false

  eap_tls_allow_auth_of_expired_certs     = false
  eap_tls_enable_stateless_session_resume = false

  peap_allow_peap_eap_ms_chap_v2                    = true
  peap_allow_peap_eap_ms_chap_v2_pwd_change         = false
  peap_allow_peap_eap_ms_chap_v2_pwd_change_retries = 0
  peap_allow_peap_eap_gtc                           = false
  require_cryptobinding                             = false
  peap_allow_peap_eap_tls                           = true
  peap_allow_peap_eap_tls_auth_of_expired_certs     = false
  peap_peap_v0                                      = false

  teap_eap_tls                                  = true
  teap_eap_tls_auth_of_expired_certs            = false
  teap_eap_ms_chap_v2                           = false
  teap_eap_accept_client_cert_during_tunnel_est = true
  teap_eap_chaining                             = false
  teap_downgrade_msk                            = false
  teap_request_basic_pwd_auth                   = false
}