# inventory/

Reference data. Terraform does not apply this folder.

- `nodes.yaml` — personas, version, VIPs. Never applied.
- `nads.yaml` — curated NAD list. Live list is under `exports/`. Not managed by Terraform.
- `vlans.yaml` — named VLANs per business unit. Referenced by authorization profiles.

UUIDs do not belong here. Phase 14 did not change this plane.