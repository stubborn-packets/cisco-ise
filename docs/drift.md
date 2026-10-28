# Drift

Terraform plan is the detector for objects we own.  
An export comparison is the wider observed view.  
Neither runs in CI. Sets stay disabled.

## Two signals

| Signal | What it sees | When it is clean | What it does not see |
| --- | --- | --- | --- |
| `terraform plan` (local, lab `.env`) | Objects in Terraform state that match the generated `.tf` files | No creates, no updates, no destroys | Rank 99 Default, Default Network Access, old GUI sets, NADs, anything never imported |
| Export / `scripts/drift.py` (GET-only) | Live names and selected attributes for families we choose to compare | Live names match `policy/` (and inventory where referenced) | UUIDs (they stay out of YAML), full ISE configuration, objects we deliberately do not own |

A clean plan means the lab matches the last applied desired state for owned objects.  
An export diff can still show unmanaged objects. That is expected. Do not import them to make the diff empty.

## Family notes

- SGTs: compare name and integer tag (`value`). Tag is on the detail object, not the list. Built-ins that do not start with `SGT_` are ignored.
- EIGs: compare name only. ERS detail returns `description`, `id`, `link`, `name`, `systemDefined`. It does not return a parent. The YAML parent name is intent. The Terraform module omits `parent_endpoint_identity_group_id`. Built-ins that do not start with `EIG-` are ignored.
- System exclusions live in `policy/system-exclusions.yaml`. The script loads that file. Edit names there; do not hard-code them in `scripts/drift.py`. Owned names are never listed.
- Families covered: SGT (name + tag), EIG, DACL, AP, PR, CND, PS, AN, AZ, EX, NDG. All name-only except SGTs. Nested rules and exceptions walk policy-set ids. NDGs use derived names. `Default` and `Default Network Access` are always ignored.

- Rank 99 Default. Not managed. Not in the packed rank sequence.
- Default Network Access. Not managed.
- Old GUI policy sets that still occupy slots. Not imported.
- NADs. Stay in `inventory/nads.yaml`. Terraform does not apply them.
- Any UUID. They live in Terraform state only.

## How to run (local only)

1. Secret-free gates first:

   ```bash
   bash scripts/check.sh
   ```

2. Load lab credentials and plan:

   ```bash
   cd environments/lab
   set -a && source ../../.env && set +a
   terraform plan
   ```

   The plan must be clean, or the diff must match an intentional YAML change that has not been applied yet. No surprise creates. No rank 99. No Default Network Access.

3. Optional wider view (after `scripts/drift.py` exists):

   ```bash
   python3.12 scripts/drift.py
   ```

   This is GET-only. It does not write to ISE and does not call Terraform.

## What CI never does

- Connect to ISE.
- Load the lab `.env`.
- Run plan or apply.
- Enable a policy set.
- Treat an export CSV as desired state.

## Exit for this phase

A reader can tell the difference between owned drift (plan) and observed extra objects (export).  
The comparison script, when it exists, reports name-level differences for one family at a time and does not write.  
`docs/handoff.md` is updated only when the increment closes.
