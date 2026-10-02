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