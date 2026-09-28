# terraform/modules/allowed-protocols/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.

output "name" {
  value       = ise_allowed_protocols.this.name
  description = "Name as stored on ISE."
}

output "id" {
  value       = ise_allowed_protocols.this.id
  description = "ISE UUID. State only."
}