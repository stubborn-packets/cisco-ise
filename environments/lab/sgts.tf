# environments/lab/sgts.tf
# Phase 4 SGTs. Bootstrap stays in main.tf / terraform.tfvars.
# No for_each over policy/. Do not manage ISE Unknown (tag 0).

module "sgt_lab_users" {
  source = "../../terraform/modules/sgt"

  name              = "SGT_lab_users"
  value             = 1010
  description       = "Lab user endpoints."
  propagate_to_apic = false
}

module "sgt_lab_devices" {
  source = "../../terraform/modules/sgt"

  name              = "SGT_lab_devices"
  value             = 1020
  description       = "Lab device endpoints."
  propagate_to_apic = false
}