# environments/lab/ndg.tf
# First NDG writes. Type containers for custom roots, then a lab leaf subset.
# Custom type container uses the type token twice (BusinessUnit#BusinessUnit)
# so the GUI row is BusinessUnit. Built-in Location / Device Type keep
# All Locations / All Device Types. Leaves are type#container#value.
# No for_each over policy/. No NAD module.

## Root type containers
module "ndg_business_unit" {
  source = "../../terraform/modules/ndg"

  name        = "BusinessUnit#BusinessUnit"
  root_group  = "BusinessUnit"
  is_root     = true
  description = "Custom NDG type container for lab BusinessUnit leaves."
}

module "ndg_stage" {
  source = "../../terraform/modules/ndg"

  name        = "Stage#Stage"
  root_group  = "Stage"
  is_root     = true
  description = "Custom NDG type container for lab Stage leaves."
}

module "ndg_function" {
  source = "../../terraform/modules/ndg"

  name        = "Function#Function"
  root_group  = "Function"
  is_root     = true
  description = "Custom NDG type container for lab Function leaves."
}

## Location sub-leaves
module "ndg_location_usa" {
  source = "../../terraform/modules/ndg"

  name        = "Location#All Locations#USA"
  root_group  = "Location"
  description = "Lab location leaf."
}

## Device Type sub-leaves
module "ndg_device_type_switch" {
  source = "../../terraform/modules/ndg"

  name        = "Device Type#All Device Types#switch"
  root_group  = "Device Type"
  description = "Lab device-type leaf."
}

module "ndg_device_type_load_balancer" {
  source = "../../terraform/modules/ndg"

  name        = "Device Type#All Device Types#load-balancer"
  root_group  = "Device Type"
  description = "F5 and other load-balancer NADs."
}

## Business Unit sub-leaves
module "ndg_business_unit_lab" {
  source = "../../terraform/modules/ndg"

  name        = "BusinessUnit#BusinessUnit#lab"
  root_group  = "BusinessUnit"
  description = "Lab business-unit leaf."

  depends_on = [module.ndg_business_unit]
}

## Stage sub-leaves
module "ndg_stage_monitor" {
  source = "../../terraform/modules/ndg"

  name        = "Stage#Stage#monitor"
  root_group  = "Stage"
  description = "Lab stage leaf."

  depends_on = [module.ndg_stage]
}

## Function sub-leaves
module "ndg_function_lab" {
  source = "../../terraform/modules/ndg"

  name        = "Function#Function#lab"
  root_group  = "Function"
  description = "Lab function leaf."

  depends_on = [module.ndg_function]
}