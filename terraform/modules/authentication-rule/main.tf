# terraform/modules/authentication-rule/main.tf
# One Network Access authentication rule. CiscoDevNet/ise 0.4.1.
# policy_set_id places the rule inside an existing set. This resource
# does not create the set.
# condition_type ConditionReference points at a library condition UUID
# from module.cnd_*.id. Do not inline the attribute condition.
# Do not set default. That flag owns the built-in Default rule.
# Resource address: module.<label>.ise_network_access_authentication_rule.this

resource "ise_network_access_authentication_rule" "this" {
  name                 = var.name
  policy_set_id        = var.policy_set_id
  rank                 = var.rank
  state                = var.state
  condition_type       = "ConditionReference"
  condition_id         = var.condition_id
  condition_is_negate  = var.condition_is_negate
  identity_source_name = var.identity_source_name
  if_auth_fail         = var.if_auth_fail
  if_process_fail      = var.if_process_fail
  if_user_not_found    = var.if_user_not_found
}