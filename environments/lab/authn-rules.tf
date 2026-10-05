# environments/lab/authn-rules.tf
# First authentication rules. One per wired policy set.
# Names copied from policy/policy-sets.yaml. Terraform does not read that file.
# policy_set_id and condition_id are module UUIDs. They stay in state.
# 802.1X searches Internal Users. MAB searches Internal Endpoints.
# Do not set default. The parent sets stay disabled.
# No for_each. No authorization rules in this file.

module "an_wired_dot1x" {
  source = "../../terraform/modules/authentication-rule"

  name                 = "AN-wired-dot1x"
  policy_set_id        = module.ps_global_wired_8021x.id
  rank                 = 0
  state                = "enabled"
  condition_id         = module.cnd_wired_dot1x_framed.id
  condition_is_negate  = false
  identity_source_name = "Internal Users"
  if_auth_fail         = "REJECT"
  if_process_fail      = "DROP"
  if_user_not_found    = "REJECT"

  depends_on = [module.ps_global_wired_8021x, module.cnd_wired_dot1x_framed]
}

module "an_wired_mab" {
  source = "../../terraform/modules/authentication-rule"

  name                 = "AN-wired-mab"
  policy_set_id        = module.ps_global_wired_mab.id
  rank                 = 0
  state                = "enabled"
  condition_id         = module.cnd_wired_mab.id
  condition_is_negate  = false
  identity_source_name = "Internal Endpoints"
  if_auth_fail         = "REJECT"
  if_process_fail      = "DROP"
  if_user_not_found    = "CONTINUE"

  depends_on = [module.ps_global_wired_mab, module.cnd_wired_mab]
}

module "an_vpn" {
  source = "../../terraform/modules/authentication-rule"

  name                 = "AN-vpn"
  policy_set_id        = module.ps_global_vpn.id
  rank                 = 0
  state                = "enabled"
  condition_id         = module.cnd_vpn.id
  condition_is_negate  = false
  identity_source_name = "Internal Users"
  if_auth_fail         = "REJECT"
  if_process_fail      = "DROP"
  if_user_not_found    = "REJECT"

  depends_on = [module.ps_global_vpn, module.cnd_vpn]
}

module "an_wireless_dot1x" {
  source = "../../terraform/modules/authentication-rule"

  name                 = "AN-wireless-dot1x"
  policy_set_id        = module.ps_global_wireless_8021x.id
  rank                 = 0
  state                = "enabled"
  condition_id         = module.cnd_wireless_dot1x_framed.id
  condition_is_negate  = false
  identity_source_name = "Internal Users"
  if_auth_fail         = "REJECT"
  if_process_fail      = "DROP"
  if_user_not_found    = "REJECT"

  depends_on = [module.ps_global_wireless_8021x, module.cnd_wireless_dot1x_framed]
}

module "an_wireless_mab" {
  source = "../../terraform/modules/authentication-rule"

  name                 = "AN-wireless-mab"
  policy_set_id        = module.ps_global_wireless_mab.id
  rank                 = 0
  state                = "enabled"
  condition_id         = module.cnd_wireless_mab_call_check.id
  condition_is_negate  = false
  identity_source_name = "Internal Endpoints"
  if_auth_fail         = "REJECT"
  if_process_fail      = "DROP"
  if_user_not_found    = "CONTINUE"

  depends_on = [module.ps_global_wireless_mab, module.cnd_wireless_mab_call_check]
}