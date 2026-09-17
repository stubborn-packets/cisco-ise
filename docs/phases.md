# Phases

One phase per branch. Merge to `main` when that phase is closed.

The only ISE this repo may write to is `environments/lab`.

## Phase 0 — Repo skeleton (done)

- `policy/`, `inventory/`, `environments/lab/`
- Naming, file map, phase, and blog-stop docs
- No ISE connection
- No Terraform provider block

Exit: repo clones, files open, nothing talks to ISE.

## Phase 1 — Read-only discovery (done)

- Python 3.12 export against **lab** ISE (ERS + OpenAPI)
- CSV under `exports/`
- Credentials from `.env`

Exit: CSVs generated from the lab ISE, including non-standard GUI objects.

## Phase 2 — Naming linter

- Linter reads `lint/prefixes.yaml` + `policy/` + `inventory/`
- Fails bad names, missing `state`, missing exception metadata, unknown NDG roots

Exit: a bad name fails; a good name passes. ISE still untouched.

## Phase 3 — Terraform lab bootstrap

- Pin `CiscoDevNet/ise` under `environments/lab/`
- Modules live in `terraform/modules/`
- First apply is one low-risk lab object (NDG, SGT, or allowed-protocols)
- Local Terraform state only

Exit: one object created in the lab GUI and destroyed (or documented if the API cannot delete it).

## Phase 4 — Policy building blocks

Order: NDG → allowed protocols → conditions → authz profiles / DACLs → SGTs → EIGs.

NADs stay in `inventory/` + `exports/` unless a later increment opens NAD writes.

## Phase 5 — Policy sets and ranks

- Create **new** standard policy sets at the locked ranks
- Do not import existing non-standard lab policy sets as desired state
- Leave old GUI sets in place until traffic is cut over
- Then disable, then delete

## Phase 6 — Exceptions

`EX-*` requires ticket, owner, expiry. Linter fails expired exceptions.

## Phase 7 — Import (lab)

Import map of `name → uuid → terraform address`. Only objects we are ready to own.

## Phase 8 — Git promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

`environments/stage/` is added only if a second ISE eval exists.

## Phase 9 — Drift

Nightly export vs `policy/` + `inventory/`. Terraform plan as drift detector.