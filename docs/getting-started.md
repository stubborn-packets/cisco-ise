# Getting started

Production-oriented guide for the ISE policy-as-code model. Documentation only. No new Terraform resources. Sets stay disabled until a deliberate cutover. Enable is not part of this guide.

## Benefits

- YAML under `policy/` is the review surface. A PR shows the intended name, rank, band, and result before any write.
- Thin modules and a reader (`scripts/read_policy.py`) keep Terraform calls consistent. Do not hand-edit the generated `.tf` files.
- Naming is enforced by the linter before a plan. Bad names and expired exceptions fail closed.
- Drift has two signals: `terraform plan` for owned objects, `scripts/drift.py` for the wider observed view. Neither runs in CI.
- The only write target in this repo is `environments/lab`. Promotion is branch → check → plan → PR → merge → apply. See `docs/promotion.md`.

## What is needed

- ISE 3.3 patch 1 (or the same major.minor you pin). Network Access only. No TACACS, no Device Administration.
- ERS and OpenAPI access from the machine that will run Terraform and the Python scripts. The account needs read for export, drift, and import-map; write only for the apply step.
- Python 3.12. Packages from `requirements.txt`.
- Terraform and the pinned `CiscoDevNet/ise` 0.4.1 provider (see `environments/lab/versions.tf`).
- A `.env` (or environment-specific `<ENV>_ISE_*` variables after Phase 14) that is never committed. Bind passwords and shared secrets stay outside the repo.
- Git. One branch per phase or feature. CI runs only the secret-free gates (`scripts/check.sh` / `.github/workflows/ci.yml`).

## Starting small

Do not import the existing GUI policy sets. Create new standard objects beside them.

1. Clone the repo. Run `bash scripts/check.sh`. It must pass with no ISE connection.
2. Pick one family (for example a single SGT or a single authorization profile). Add the row to the matching file under `policy/`.
3. Run the reader so it emits the lab call. Do not hand-edit the generated file.
4. Plan against the lab. The diff must match the YAML row. Apply. Confirm the object exists and is in the state you declared (`enabled` or `disabled`).
5. Repeat for the next family. Policy sets come after the building blocks they reference. Keep every new set disabled.
6. Use `scripts/drift.py --environment lab` and `terraform plan` after each apply. Non-owned names are expected; do not import them to silence the report.

## Cutover pattern

When the managed sets are complete and the bake period is over:

1. Move test traffic (or a single NAD) to the new objects. Confirm authentication and authorization behave as the YAML describes.
2. Disable the old GUI sets that occupied the same slots. Do not delete them yet.
3. In a separate change, set `state: enabled` on the managed sets you are ready to evaluate. Plan, review, apply. Rank stays the packed index; Default is not moved.
4. After another bake period, delete the old objects. Export and drift should then show only the owned names plus the system exclusions.

Enable is the cutover. It is not part of the phase that created the set. Rank 99 Default and Default Network Access stay unmanaged. NADs stay in `inventory/`.

## What this repo does not do

- Does not install or upgrade ISE nodes.
- Does not manage Device Administration or TACACS.
- Does not create `environments/stage/` or `prod/`. Add a second environment directory only if a second eval ISE exists.
- Does not put UUIDs in `policy/` or `inventory/`.
- Does not publish hostnames, shared secrets, or internal IPs.

Start with `docs/phases.md`, and `docs/decisions.md`. Then follow the family order in `docs/phases.md`.