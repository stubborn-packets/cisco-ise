# environments/lab/policy-sets.tf
# First policy-set writes. Wired subset only. State disabled.
# Names copied from policy/policy-sets.yaml. Terraform does not read that file.
# YAML rank 40 and 50 are the design band. ISE rank is a dense insert index.
# This lab rejects POST rank 40 (legal range was 0-9). Insert at 0, then 1,
# so the new sets sit above the old GUI sets and are not evaluated.
# The MAB module depends on the 802.1X module so the second insert sees the shift.
# condition_id is the AND condition UUID. It stays in state, not in policy/.
# No VPN, wireless, infra, or PS-<bu>-*. Rules are a later resource.

module "ps_global_vpn" {
  source = "../../terraform/modules/policy-set"

  name                = "PS-global-vpn"
  description         = "Global VPN. Evaluated before wired."
  rank                = 0
  state               = "disabled"
  service_name        = module.ap_vpn.name
  is_proxy            = false
  condition_id        = module.cnd_vpn.id
  condition_is_negate = false

  depends_on = [module.ap_vpn, module.cnd_vpn]
}

module "ps_global_wired_8021x" {
  source = "../../terraform/modules/policy-set"

  name                = "PS-global-wired-8021x"
  description         = "Global wired 802.1X. Evaluated before wired MAB."
  rank                = 1
  state               = "disabled"
  service_name        = module.ap_wired_dot1x.name
  is_proxy            = false
  condition_id        = module.cnd_wired_dot1x_framed.id
  condition_is_negate = false

  depends_on = [module.ap_wired_dot1x, module.cnd_wired_dot1x_framed]
}

module "ps_global_wired_mab" {
  source = "../../terraform/modules/policy-set"

  name                = "PS-global-wired-mab"
  description         = "Global wired MAB. Evaluated after wired 802.1X."
  rank                = 2
  state               = "disabled"
  service_name        = module.ap_wired_mab.name
  is_proxy            = false
  condition_id        = module.cnd_wired_mab_call_check.id
  condition_is_negate = false

  depends_on = [
    module.ap_wired_mab,
    module.cnd_wired_mab_call_check,
    module.ps_global_wired_8021x,
  ]
}