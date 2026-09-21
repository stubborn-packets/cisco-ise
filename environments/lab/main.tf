# environments/lab/main.tf
# The only root that may call a write module.
# One object. No NAD module. No for_each over policy/.

module "sgt_bootstrap" {
  source = "../../terraform/modules/sgt"

  name              = var.sgt_name
  value             = var.sgt_value
  description       = var.sgt_description
  propagate_to_apic = var.sgt_propagate_to_apic
}