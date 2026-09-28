# terraform/modules/ndg/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.

output "name" {
  value       = ise_network_device_group.this.name
  description = "Full hierarchy as stored on ISE."
}

output "root_group" {
  value       = ise_network_device_group.this.root_group
  description = "ISE type / root_group as stored on ISE."
}

output "id" {
  value       = ise_network_device_group.this.id
  description = "ISE UUID. State only."
}