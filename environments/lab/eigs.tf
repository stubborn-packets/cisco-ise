# environments/lab/eigs.tf
# First static endpoint identity groups.
# No parent UUID. No endpoints. No for_each over policy/.

module "eig_printers" {
  source = "../../terraform/modules/eig"

  name        = "EIG-printers"
  description = "Statically classified printers."
}

module "eig_lab_iot" {
  source = "../../terraform/modules/eig"

  name        = "EIG-lab-iot"
  description = "Statically classified lab IoT devices."
}