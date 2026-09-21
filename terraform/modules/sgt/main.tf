# terraform/modules/sgt/main.tf
# One TrustSec security group. Create + destroy is the Phase 3 proof.
# Resource address: module.<label>.ise_trustsec_security_group.this

resource "ise_trustsec_security_group" "this" {
  name              = var.name
  value             = var.value
  description       = var.description != "" ? var.description : null
  propogate_to_apic = var.propagate_to_apic
  is_read_only      = false
}