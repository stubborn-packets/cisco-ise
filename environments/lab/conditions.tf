# environments/lab/conditions.tf
# First library-condition writes. Two attribute conditions.
# No AND/OR children. No Device Admin condition. No for_each over policy/.

module "cnd_wired_dot1x" {
  source = "../../terraform/modules/condition"

  name            = "CND-wired-dot1x"
  description     = "Wired 802.1X via NAS-Port-Type Ethernet."
  dictionary_name = "Radius"
  attribute_name  = "NAS-Port-Type"
  operator        = "equals"
  attribute_value = "Ethernet"
}

module "cnd_wired_mab" {
  source = "../../terraform/modules/condition"

  name            = "CND-wired-mab"
  description     = "Wired MAB via Network Access AuthenticationMethod Lookup."
  dictionary_name = "Network Access"
  attribute_name  = "AuthenticationMethod"
  operator        = "equals"
  attribute_value = "Lookup"
}