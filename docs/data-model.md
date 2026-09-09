# Data Model & Catalog (draft)

**Status: draft, captured 2026-09-09 — most of this is expected to change**
as Phase 1 (export) and Phase 5 (pilot import) surface real constraints.
Recorded now so the thinking isn't lost, not as a locked design.

## Source formatting

- **YAML** for hierarchical ISE objects and anything that maps into
  Terraform.
- **CSV** for flat lists and for exports meant for business/audit review
  rather than for Terraform to consume.

## YAML conventions

- Object names inside the prefix table use kebab-case (see
  `docs/naming-standards.md`).
- Comment every entry with a short line explaining intent — not just what
  the object is, but why it exists.
- Give policy objects an explicit `state: enabled` / `state: disabled`
  field rather than relying on presence/absence in the file.

## Proposed catalog file map

A reference map of the YAML/CSV files this project is expected to need,
for documentation purposes — not yet tied to a folder location (see open
question below):

| File | Contents |
|---|---|
| `nodes.yaml` | ISE nodes, personas, VIPs, versions |
| `ndg.yaml` | Allowed Network Device Group values per root |
| `nads.yaml` | All Network Access Devices, for reference |
| `policy-sets.yaml` | Policy set order, conditions, allowed protocols |
| `allowed-protocols.yaml` | Services and enabled EAP methods |
| `authz-profiles.yaml` | Authorization (result) profiles |
| `sgt.yaml` | Security Group Tags — tag value and owner |
| `eig.yaml` | Approved static endpoint identity groups |
| `logical-profiles.yaml` | Logical profile policies |
| `vlans.yaml` | Named VLANs, per BU |
| `exceptions.yaml` | Exception rules — ticket number, owner, expiry |
| `exports/*.csv` | Generated, read-only extracts for audit or CMDB |

## Open question: where does this map live?

Two reasonable options once we're past Phase 0 — worth deciding when Phase
1 (export) actually starts writing files, not now:

**Option A — everything flat under `policies/`.** Simple, one place to
look. Downside: it blurs "things Terraform actually manages/creates"
(`policy-sets.yaml`, `authz-profiles.yaml`, `sgt.yaml`, `eig.yaml`,
`logical-profiles.yaml`, `exceptions.yaml`) together with "read-only
inventory of things that already exist and Terraform mostly just
references" (`nodes.yaml`, `ndg.yaml`, `nads.yaml`, `vlans.yaml`).

**Option B — split `catalog/` (inventory/reference data, human-governed,
not necessarily Terraform-managed) from `policies/` (objects Terraform
creates and owns).** `catalog/nodes.yaml`, `catalog/ndg.yaml`,
`catalog/nads.yaml`, `catalog/vlans.yaml` vs. `policies/policy-sets.yaml`,
`policies/authz-profiles.yaml`, etc. Slightly more folders, but it makes
"can I safely let Terraform manage this file's contents" answerable by
which directory a file is in, which matters more once Phase 8 starts
freezing manual edits object-type by object-type.

Leaning towards **Option B** for that reason, but it's cheap to change
before any Terraform code exists to depend on it — revisit at Phase 1.

## Open question: committed exports vs. throwaway exports

The current repo `.gitignore` treats `scripts/export/output/` as
throwaway/uncommitted working output. But `exports/*.csv` here is
described as a deliberate, committed audit/CMDB artifact — a different
thing. Phase 1 should probably end up with **two** export destinations:
a git-ignored scratch area for exports still being reviewed, and a
committed `exports/` (or `catalog/exports/`) directory for the ones meant
to stick around. Worth confirming against Option A/B above at the same
time.
