# environments/lab/providers.tf
# Plane: environment wiring. Tells Terraform which ISE this root may talk to.
# Values come from the process environment, not from this file.

provider "ise" {
  # url      <- ISE_URL
  # username <- ISE_USERNAME
  # password <- ISE_PASSWORD
  # insecure <- ISE_INSECURE (provider default: true)
}