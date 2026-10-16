# terraform/modules/authorization-global-exception-rule/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.
# rank is exposed so the reader can emit a ranks map from the module.

output "name" {
  value       = ise_network_access_authorization_global_exception_rule.this.name
  description = "Name as stored on ISE."
}

output "id" {
  value       = ise_network_access_authorization_global_exception_rule.this.id
  description = "ISE UUID. State only."
}

output "rank" {
  value       = ise_network_access_authorization_global_exception_rule.this.rank
  description = "Rank as stored on ISE. Lower is first."
}

output "state" {
  value       = ise_network_access_authorization_global_exception_rule.this.state
  description = "State as stored on ISE."
}