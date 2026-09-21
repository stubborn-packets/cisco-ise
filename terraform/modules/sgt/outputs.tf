# terraform/modules/sgt/outputs.tf
# Values to confirm the GUI without opening the state file.
# id is ISE's UUID. It belongs in state/output, never in policy/ or inventory/.

output "name" {
  value       = ise_trustsec_security_group.this.name
  description = "Name as stored on ISE."
}

output "value" {
  value       = ise_trustsec_security_group.this.value
  description = "Numeric tag as stored on ISE."
}

output "id" {
  value       = ise_trustsec_security_group.this.id
  description = "ISE UUID. State only."
}