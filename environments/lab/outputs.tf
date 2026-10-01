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

output "ndg_names" {
  value = {
    business_unit      = module.ndg_business_unit.name
    stage              = module.ndg_stage.name
    function           = module.ndg_function.name
    location_usa       = module.ndg_location_usa.name
    device_type_switch = module.ndg_device_type_switch.name
    business_unit_lab  = module.ndg_business_unit_lab.name
    stage_monitor      = module.ndg_stage_monitor.name
    function_lab       = module.ndg_function_lab.name
  }
  description = "NDG names stored on lab ISE."
}

output "ndg_ids" {
  value = {
    business_unit      = module.ndg_business_unit.id
    stage              = module.ndg_stage.id
    function           = module.ndg_function.id
    location_usa       = module.ndg_location_usa.id
    device_type_switch = module.ndg_device_type_switch.id
    business_unit_lab  = module.ndg_business_unit_lab.id
    stage_monitor      = module.ndg_stage_monitor.id
    function_lab       = module.ndg_function_lab.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "ap_names" {
  value = {
    wired_dot1x = module.ap_wired_dot1x.name
    wired_mab   = module.ap_wired_mab.name
  }
  description = "Allowed-protocols names stored on lab ISE."
}

output "ap_ids" {
  value = {
    wired_dot1x = module.ap_wired_dot1x.id
    wired_mab   = module.ap_wired_mab.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "cnd_names" {
  value = {
    wired_dot1x = module.cnd_wired_dot1x.name
    wired_mab   = module.cnd_wired_mab.name
  }
  description = "Library condition names stored on lab ISE."
}

output "cnd_ids" {
  value = {
    wired_dot1x = module.cnd_wired_dot1x.id
    wired_mab   = module.cnd_wired_mab.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "acl_names" {
  value = {
    permit_all = module.acl_permit_all.name
  }
  description = "Downloadable ACL names stored on lab ISE."
}

output "acl_ids" {
  value = {
    permit_all = module.acl_permit_all.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "pr_names" {
  value = {
    wired_lab_access = module.pr_wired_lab_access.name
  }
  description = "Authorization profile names stored on lab ISE."
}

output "pr_ids" {
  value = {
    wired_lab_access = module.pr_wired_lab_access.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "sgt_names" {
  value = {
    bootstrap   = module.sgt_bootstrap.name
    lab_users   = module.sgt_lab_users.name
    lab_devices = module.sgt_lab_devices.name
  }
  description = "SGT names stored on lab ISE."
}

output "sgt_ids" {
  value = {
    bootstrap   = module.sgt_bootstrap.id
    lab_users   = module.sgt_lab_users.id
    lab_devices = module.sgt_lab_devices.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "eig_names" {
  value = {
    printers = module.eig_printers.name
    lab_iot  = module.eig_lab_iot.name
  }
  description = "Endpoint identity group names stored on lab ISE."
}

output "eig_ids" {
  value = {
    printers = module.eig_printers.id
    lab_iot  = module.eig_lab_iot.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}