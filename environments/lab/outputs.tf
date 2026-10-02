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
    vpn         = module.ap_vpn.name
  }
  description = "Allowed-protocols names stored on lab ISE."
}

output "ap_ids" {
  value = {
    wired_dot1x = module.ap_wired_dot1x.id
    wired_mab   = module.ap_wired_mab.id
    vpn         = module.ap_vpn.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "cnd_names" {
  value = {
    wired_dot1x          = module.cnd_wired_dot1x.name
    wired_mab            = module.cnd_wired_mab.name
    wired_dot1x_framed   = module.cnd_wired_dot1x_framed.name
    wired_mab_call_check = module.cnd_wired_mab_call_check.name
    vpn                  = module.cnd_vpn.name
  }
  description = "Library condition names stored on lab ISE."
}

output "cnd_ids" {
  value = {
    wired_dot1x          = module.cnd_wired_dot1x.id
    wired_mab            = module.cnd_wired_mab.id
    wired_dot1x_framed   = module.cnd_wired_dot1x_framed.id
    wired_mab_call_check = module.cnd_wired_mab_call_check.id
    vpn                  = module.cnd_vpn.id
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
    global_vpn       = module.pr_global_vpn.name
  }
  description = "Authorization profile names stored on lab ISE."
}

output "pr_ids" {
  value = {
    wired_lab_access = module.pr_wired_lab_access.id
    global_vpn       = module.pr_global_vpn.id
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

output "ps_names" {
  value = {
    wired_8021x = module.ps_global_wired_8021x.name
    wired_mab   = module.ps_global_wired_mab.name
    global_vpn  = module.ps_global_vpn.name
  }
  description = "Policy set names stored on lab ISE."
}

output "ps_ranks" {
  value = {
    wired_8021x   = module.ps_global_wired_8021x.rank
    wired_mab     = module.ps_global_wired_mab.rank
    global_vpn    = module.ps_global_vpn.rank
  }
  description = "Policy set ranks stored on lab ISE. Lower is evaluated first."
}

output "ps_ids" {
  value = {
    wired_8021x   = module.ps_global_wired_8021x.id
    wired_mab     = module.ps_global_wired_mab.id
    global_vpn    = module.ps_global_vpn.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "ps_states" {
  value = {
    wired_8021x   = module.ps_global_wired_8021x.state
    wired_mab     = module.ps_global_wired_mab.state
    global_vpn    = module.ps_global_vpn.state
  }
  description = "Policy set states stored on ISE."
}

output "an_names" {
  value = {
    wired_dot1x = module.an_wired_dot1x.name
    wired_mab   = module.an_wired_mab.name
    vpn         = module.an_vpn.name
  }
  description = "Authentication rule names stored on lab ISE."
}

output "an_states" {
  value = {
    wired_dot1x = module.an_wired_dot1x.state
    wired_mab   = module.an_wired_mab.state
    vpn         = module.an_vpn.state
  }
  description = "Authentication rule states stored on ISE."
}

output "an_ids" {
  value = {
    wired_dot1x = module.an_wired_dot1x.id
    wired_mab   = module.an_wired_mab.id
    vpn         = module.an_vpn.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}

output "az_names" {
  value = {
    wired_dot1x = module.az_wired_dot1x.name
    wired_mab   = module.az_wired_mab.name
    vpn         = module.az_vpn.name
  }
  description = "Authorization rule names stored on lab ISE."
}

output "az_states" {
  value = {
    wired_dot1x = module.az_wired_dot1x.state
    wired_mab   = module.az_wired_mab.state
    vpn         = module.az_vpn.state
  }
  description = "Authorization rule states stored on ISE."
}

output "az_ids" {
  value = {
    wired_dot1x = module.az_wired_dot1x.id
    wired_mab   = module.az_wired_mab.id
    vpn         = module.az_vpn.id
  }
  description = "ISE UUIDs. State only. Do not copy into policy/ or inventory/."
}