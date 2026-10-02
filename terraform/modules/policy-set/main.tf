# terraform/modules/policy-set/main.tf
# One Network Access policy set. CiscoDevNet/ise 0.4.1.
# condition_type ConditionReference points at a library condition UUID
# from module.cnd_*.id. Do not inline the attribute condition.
# Do not set default. Rank 99 / name Default is rejected in variables.tf.
# Authentication and authorization rules are separate resources.
# Resource address: module.<label>.ise_network_access_policy_set.this

resource "ise_network_access_policy_set" "this" {
  name                = var.name
  description         = var.description != "" ? var.description : null
  rank                = var.rank
  state               = var.state
  service_name        = var.service_name
  is_proxy            = var.is_proxy
  condition_type      = "ConditionReference"
  condition_id        = var.condition_id
  condition_is_negate = var.condition_is_negate
}