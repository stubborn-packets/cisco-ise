# terraform/modules/ndg/variables.tf
# Inputs that map to ise_network_device_group.
# owner / bu live in policy YAML. ISE has no fields for them.
# Allow-list grammar stays in lint_ise.py + policy/ndg.yaml.

variable "name" {
  type        = string
  description = "ISE name. Type node: BusinessUnit. Leaf: BusinessUnit#it or Location#All Locations#USA."

  validation {
    condition = var.is_root ? (
      var.name == var.root_group
    ) : (
      can(regex("^[^#]+(#[^#]+)+$", var.name)) &&
      startswith(var.name, "${var.root_group}#")
    )
    error_message = "Leaf: type#leaf or type#parent#leaf, starting with root_group#. Type node: name must equal root_group and is_root must be true."
  }
}

variable "root_group" {
  type        = string
  description = "ISE root_group. Must match policy/ndg.yaml ise_root."

  validation {
    condition = contains(
      ["Location", "Device Type", "BusinessUnit", "Stage", "Function"],
      var.root_group
    )
    error_message = "root_group must be one of Location, Device Type, BusinessUnit, Stage, Function."
  }
}

variable "is_root" {
  type        = bool
  default     = false
  description = "True when this object is the custom type node (name == root_group). Location and Device Type already exist on ISE."

  validation {
    condition = (
      !var.is_root ||
      contains(["BusinessUnit", "Stage", "Function"], var.root_group)
    )
    error_message = "is_root is only for BusinessUnit, Stage, Function. Do not manage built-in Location or Device Type roots."
  }
}

variable "description" {
  type        = string
  default     = ""
  description = "Optional ISE description. Ownership notes belong in policy YAML, not here."
}