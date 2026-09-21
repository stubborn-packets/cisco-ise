# environments/lab/backend.tf
# Plane: environment wiring. One state file, this ISE only.
# Path is relative to this directory. Gitignored (see repo .gitignore).

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}