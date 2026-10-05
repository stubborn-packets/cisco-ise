# environments/lab/authz-rules.tf
# First authorization rules. One per wired policy set.
# Names copied from policy/policy-sets.yaml. Terraform does not read that file.
# policy_set_id and condition_id are module UUIDs. They stay in state.
# profiles is the profile name, not a UUID. No security_group.
# Do not set default. The parent sets stay disabled.
# No for_each.

module "az_wired_dot1x" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-wired-dot1x"
  policy_set_id       = module.ps_global_wired_8021x.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_wired_dot1x_framed.id
  condition_is_negate = false
  profiles            = ["PR-wired-lab-access"]

  depends_on = [module.ps_global_wired_8021x, module.cnd_wired_dot1x_framed, module.pr_wired_lab_access]
}

module "az_wired_mab" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-wired-mab"
  policy_set_id       = module.ps_global_wired_mab.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_wired_mab_call_check.id
  condition_is_negate = false
  profiles            = ["PR-wired-lab-access"]

  depends_on = [module.ps_global_wired_mab, module.cnd_wired_mab_call_check, module.pr_wired_lab_access]
}

module "az_vpn" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-vpn"
  policy_set_id       = module.ps_global_vpn.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_vpn.id
  condition_is_negate = false
  profiles            = ["PR-global-vpn"]

  depends_on = [module.ps_global_vpn, module.cnd_vpn, module.pr_global_vpn]
}

module "az_wireless_dot1x" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-wireless-dot1x"
  policy_set_id       = module.ps_global_wireless_8021x.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_wireless_dot1x_framed.id
  condition_is_negate = false
  profiles            = ["PR-wired-lab-access"]

  depends_on = [module.ps_global_wireless_8021x, module.cnd_wireless_dot1x_framed, module.pr_wired_lab_access]
}

module "az_wireless_mab" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-wireless-mab"
  policy_set_id       = module.ps_global_wireless_mab.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_wireless_mab_call_check.id
  condition_is_negate = false
  profiles            = ["PR-wired-lab-access"]

  depends_on = [module.ps_global_wireless_mab, module.cnd_wireless_mab_call_check, module.pr_wired_lab_access]
}

module "az_infra_f5_health" {
  source = "../../terraform/modules/authorization-rule"

  name                = "AZ-infra-f5-health"
  policy_set_id       = module.ps_infra_health_checks.id
  rank                = 0
  state               = "enabled"
  condition_id        = module.cnd_infra_f5_health.id
  condition_is_negate = false
  profiles            = ["PR-infra-permit"]

  depends_on = [module.ps_infra_health_checks, module.cnd_infra_f5_health, module.pr_infra_permit]
}