# environments/lab/variables.tf
# Pass-through into module.sgt_bootstrap.
# Grammar is enforced in terraform/modules/sgt, not here.

variable "sgt_name" {
  type        = string
  description = "ISE SGT name for the Phase 3 bootstrap object."
}

variable "sgt_value" {
  type        = number
  description = "Numeric tag. 1001 for this proof. -1 lets ISE assign."
}

variable "sgt_description" {
  type        = string
  default     = ""
  description = "ISE description. Not ownership metadata."
}

variable "sgt_propagate_to_apic" {
  type        = bool
  default     = false
  description = "ACI propagate flag. Lab stays false."
}