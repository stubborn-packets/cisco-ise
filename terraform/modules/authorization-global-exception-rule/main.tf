# terraform/modules/authorization-global-exception-rule/main.tf
# One Network Access authorization global exception rule. CiscoDevNet/ise 0.4.1.
# No policy_set_id. The rule is evaluated for every policy set.
# Local exceptions still win over a global exception.
# condition_type ConditionReference points at a library condition UUID
# from module.cnd_*.id. Do not inline the attribute condition.
# profiles is a set of profile names, not UUIDs.
# Do not set default. Do not set security_group. The first global exception has no SGT.
# Resource address: module.<label>.ise_network_access_authorization_global_exception_rule.this

resource "ise_network_access_authorization_global_exception_rule" "this" {
  name                = var.name
  rank                = var.rank
  state               = var.state
  condition_type      = "ConditionReference"
  condition_id        = var.condition_id
  condition_is_negate = var.condition_is_negate
  profiles            = var.profiles
}