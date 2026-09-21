# environments/lab/terraform.tfvars
# Non-secret desired values for the one Phase 3 object.
# Not policy/sgt.yaml — that file stays empty until Phase 4.

sgt_name              = "SGT_lab_bootstrap"
sgt_value             = 1001
sgt_description       = "Phase 3 bootstrap object. Safe to destroy."
sgt_propagate_to_apic = false