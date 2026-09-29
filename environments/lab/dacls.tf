# environments/lab/dacls.tf
# First downloadable ACL. Lab bring-up only. No for_each over policy/.

module "acl_permit_all" {
  source = "../../terraform/modules/dacl"

  name        = "ACL-permit-all"
  description = "Temporary wide-open DACL for lab bring-up only."
  dacl        = "permit ip any any"
  dacl_type   = "IPV4"
}