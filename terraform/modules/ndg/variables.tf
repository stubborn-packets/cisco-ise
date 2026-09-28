# terraform/modules/ndg/variables.tf
# Inputs that map to ise_network_device_group.
# owner / bu live in policy YAML. ISE has no fields for them.
# Allow-list grammar stays in lint_ise.py + policy/ndg.yaml.
#
# ERS requires name to contain type(othername) and name, delimited by #.
# A custom type container is type#type (BusinessUnit#BusinessUnit).
# Built-in Location / Device Type keep type#All Xs. Bare type token 400s.

variable "name" {
  type        = string
  description = "ISE hierarchy. Custom type container: BusinessUnit#BusinessUnit. Custom leaf: BusinessUnit#BusinessUnit#lab. Built-in leaf: Location#All Locations#USA."

  validation {
    condition = var.is_root ? (
      var.name == "${var.root_group}#${var.root_group}"
    ) : (
      can(regex("^[^#]+#[^#]+#[^#]+$", var.name)) &&
      startswith(var.name, "${var.root_group}#")
    )
    error_message = "Custom type container (is_root): name must be root_group#root_group. Leaf: type#parent#leaf starting with root_group#."
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
  description = "True when this object is the custom type container (type#type). Location and Device Type already exist on ISE."

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
  description = "Optional ISE description. Ownership notes belong in policy YAML, not here. ISE ERS rejects < and > (XSS validation)."

  validation {
    condition     = !can(regex("[<>]", var.description))
    error_message = "ISE ERS rejects < and > in NDG description (XSS validation)."
  }
}