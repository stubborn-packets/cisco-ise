# environments/lab/authz-profiles.tf
# First authorization profile. DACL must exist first.
# VLAN 20 is inventory VLAN-lab-data. No SGT. No for_each over policy/.

module "pr_wired_lab_access" {
  source = "../../terraform/modules/authorization-profile"

  name         = "PR-wired-lab-access"
  description  = "Lab wired access. VLAN from inventory/vlans.yaml."
  access_type  = "ACCESS_ACCEPT"
  dacl_name    = module.acl_permit_all.name
  vlan_name_id = "20"
  vlan_tag_id  = 1

  depends_on = [module.acl_permit_all]
}

module "pr_global_vpn" {
  source = "../../terraform/modules/authorization-profile"

  name                   = "PR-global-vpn"
  description            = "Lab VPN access. ASA group policy via Class ou=GP-global-vpn."
  access_type            = "ACCESS_ACCEPT"
  dacl_name              = module.acl_permit_all.name
  asa_vpn                = "ou=GP-global-vpn"
  reauthentication_timer = 28800
  reauthentication_connectivity = "DEFAULT"

  depends_on = [module.acl_permit_all]
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