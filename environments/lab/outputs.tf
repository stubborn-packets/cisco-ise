# environments/lab/outputs.tf
# Re-export the module so `terraform output` matches the GUI.
# id is an ISE UUID. Do not copy it into policy/ or inventory/.

output "sgt_name" {
  value       = module.sgt_bootstrap.name
  description = "Name stored on lab ISE."
}

output "sgt_value" {
  value       = module.sgt_bootstrap.value
  description = "Numeric tag stored on lab ISE."
}

output "sgt_id" {
  value       = module.sgt_bootstrap.id
  description = "ISE UUID. State only."
}