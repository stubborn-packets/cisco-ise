# terraform/modules/authorization-rule/main.tf
# One Network Access authorization rule. CiscoDevNet/ise 0.4.1.
# policy_set_id places the rule inside an existing set. This resource
# does not create the set.
# condition_type ConditionReference points at a library condition UUID
# from module.cnd_*.id. Do not inline the attribute condition.
# profiles is a set of profile names, not UUIDs.
# Do not set default. Do not set security_group. The first profile has no SGT.
# Resource address: module.<label>.ise_network_access_authorization_rule.this

resource "ise_network_access_authorization_rule" "this" {
  name                = var.name
  policy_set_id       = var.policy_set_id
  rank                = var.rank
  state               = var.state
  condition_type      = "ConditionReference"
  condition_id        = var.condition_id
  condition_is_negate = var.condition_is_negate
  profiles            = var.profiles
}