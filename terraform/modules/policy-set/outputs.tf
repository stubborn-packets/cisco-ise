# terraform/modules/policy-set/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.
# Rule resources, later in this phase, take this id as policy_set_id.

output "name" {
  value       = ise_network_access_policy_set.this.name
  description = "Name as stored on ISE."
}

output "id" {
  value       = ise_network_access_policy_set.this.id
  description = "ISE UUID. State only. Pass to a rule resource as policy_set_id."
}

output "rank" {
  value       = ise_network_access_policy_set.this.rank
  description = "Rank as stored on ISE. Lower is evaluated first."
}

output "state" {
  value       = ise_network_access_policy_set.this.state
  description = "State as stored on ISE."
}