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

module "cnd_wired_dot1x_framed" {
  source = "../../terraform/modules/condition"

  name           = "CND-wired-dot1x-framed"
  description    = "Policy set condition. Wired 802.1X. Ethernet and Service-Type Framed."
  condition_type = "LibraryConditionAndBlock"

  children = [
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "NAS-Port-Type"
      operator        = "equals"
      attribute_value = "Ethernet"
    },
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "Service-Type"
      operator        = "equals"
      attribute_value = "Framed"
    },
  ]
}

module "cnd_wired_mab_call_check" {
  source = "../../terraform/modules/condition"

  name           = "CND-wired-mab-call-check"
  description    = "Policy set condition. Wired MAB. Ethernet and Service-Type Call Check."
  condition_type = "LibraryConditionAndBlock"

  children = [
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "NAS-Port-Type"
      operator        = "equals"
      attribute_value = "Ethernet"
    },
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "Service-Type"
      operator        = "equals"
      attribute_value = "Call Check"
    },
  ]
}

module "cnd_vpn" {
  source = "../../terraform/modules/condition"

  name            = "CND-vpn"
  description     = "VPN via NAS-Port-Type Virtual."
  dictionary_name = "Radius"
  attribute_name  = "NAS-Port-Type"
  operator        = "equals"
  attribute_value = "Virtual"
}

module "cnd_wireless_dot1x_framed" {
  source = "../../terraform/modules/condition"

  name           = "CND-wireless-dot1x-framed"
  description    = "Policy set condition. Wireless 802.1X. IEEE 802.11 and Service-Type Framed."
  condition_type = "LibraryConditionAndBlock"

  children = [
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "NAS-Port-Type"
      operator        = "equals"
      attribute_value = "Wireless - IEEE 802.11"
    },
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "Service-Type"
      operator        = "equals"
      attribute_value = "Framed"
    },
  ]
}

module "cnd_wireless_mab_call_check" {
  source = "../../terraform/modules/condition"

  name           = "CND-wireless-mab-call-check"
  description    = "Policy set condition. Wireless MAB. IEEE 802.11 and Service-Type Call Check."
  condition_type = "LibraryConditionAndBlock"

  children = [
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "NAS-Port-Type"
      operator        = "equals"
      attribute_value = "Wireless - IEEE 802.11"
    },
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "Service-Type"
      operator        = "equals"
      attribute_value = "Call Check"
    },
  ]
}

module "cnd_infra_f5_health" {
  source = "../../terraform/modules/condition"

  name           = "CND-infra-f5-health"
  description    = "F5 health check. Load-balancer NAD and RADIUS user svc-ise-f5-health."
  condition_type = "LibraryConditionAndBlock"

  children = [
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "DEVICE"
      attribute_name  = "Device Type"
      operator        = "equals"
      attribute_value = "All Device Types#load-balancer"
    },
    {
      condition_type  = "ConditionAttributes"
      dictionary_name = "Radius"
      attribute_name  = "User-Name"
      operator        = "equals"
      attribute_value = "svc-ise-f5-health"
    },
  ]

  depends_on = [module.ndg_device_type_load_balancer]
}