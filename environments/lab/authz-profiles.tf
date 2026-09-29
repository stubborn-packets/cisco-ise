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