# terraform/modules/identity-source-sequence/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.

output "name" {
  value       = ise_identity_source_sequence.this.name
  description = "Name as stored on ISE."
}

output "id" {
  value       = ise_identity_source_sequence.this.id
  description = "ISE UUID. State only."
}