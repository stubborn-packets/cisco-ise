# Promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

Lab ISE is the only write target. Sets stay disabled. Enable is a cutover, not this path. There is no `environments/stage/` or `prod/`.

## Before the PR

1. Branch from `main`. One branch per phase or per feature inside a phase.
2. Edit YAML under `policy/` (or inventory). Do not hand-edit generated `.tf` files.
3. Run the secret-free checks:

   ```bash
   bash scripts/check.sh
   ```

   This runs `lint_ise.py`, the unit tests, `terraform fmt -check`, and `terraform validate` in `environments/lab`.
4. Load lab credentials and plan:

   ```bash
   cd environments/lab
   set -a && source ../../.env && set +a
   terraform plan
   ```

   The plan must be clean or the diff must match the YAML change. No surprise creates, no rank 99, no Default Network Access.
5. Open the PR. The description must show:
   - The YAML change (or the reason a generated file changed).
   - The output of `scripts/check.sh`.
   - The relevant `terraform plan` lines.

## On the PR

CI (`.github/workflows/ci.yml`) runs the same secret-free checks. It does not run plan or apply. A green CI means the name, the grammar, and the Terraform syntax are acceptable. It does not mean the lab is ready for the change.

Approve only when the plan matches the intent and the sets remain disabled.

## After merge

1. Pull `main`.
2. Load credentials and apply:

   ```bash
   cd environments/lab
   set -a && source ../../.env && set +a
   terraform apply
   ```

3. Confirm the new objects are disabled. Update `docs/handoff.md` when the increment exits.

## What stays local

- `terraform plan` and `terraform apply` require the lab `.env`. They are not in CI.
- UUIDs stay out of `policy/` and `inventory/`.
- Rank 99 Default and Default Network Access are not managed.
- NADs stay in `inventory/`.

## What CI never does

- Connect to ISE.
- Load secrets.
- Run plan or apply.
- Enable a policy set.
