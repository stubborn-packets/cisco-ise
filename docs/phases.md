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

## Phase 2 — Naming linter (done)

- Linter reads `lint/prefixes.yaml` + `lint/builtins.yaml` + `policy/` + `inventory/`
- Fails bad names, missing `state`, missing exception metadata, unknown NDG roots
- Empty scaffolds pass. `exports/` is not linted.

Exit: a bad name fails; a good name passes. ISE still untouched.

## Phase 3 — Terraform lab bootstrap (done)

- Pin `CiscoDevNet/ise` 0.4.1 under `environments/lab/`
- Module: `terraform/modules/sgt/`
- First object: `SGT_lab_bootstrap` / 1001 (underscores; ISE rejects hyphenated SGT names)
- Local Terraform state only

Exit met 2026-09-21: object created and destroyed via ERS. Unused SGT is deletable.

## Phase 4 — Policy building blocks (done)

Order: NDG → allowed protocols → conditions → authz profiles / DACLs → SGTs → EIGs.

Exit met 2026-10-01: each family has a YAML row, a thin module, a lab call, and a live object on lab ISE. NADs stayed in `inventory/` + `exports/`. No policy sets. Blog saved at `blog/cisco-ise-policy-as-code-part4/`.

## Phase 5 — Policy sets and ranks

Wired, VPN, wireless, infra, and the first business-unit pair closed 2026-10-05 on lab ISE. Sets stay disabled. Enable was not part of the close.

- Global sets are infra, wireless 802.1X, wireless MAB, VPN, wired 802.1X, wired MAB
- Business-unit sets are `PS-hr-wired` and `PS-guest-wired`
- YAML ranks stay the old bands. ISE insert ranks are 0 through 7 for managed sets
- Wired global conditions require `DEVICE` `BusinessUnit` `BusinessUnit#global`. Guest and HR require `BusinessUnit#guest` and `BusinessUnit#hr`
- `AN-hr-wired` and `AN-guest-wired` search `Internal Endpoints` and continue if the MAC is unknown
- `AZ-hr-wired` returns `PR-hr-wired-mab` (VLAN 30) when `EIG-hr` matches. Guest returns VLAN 40
- Old GUI sets were not imported. They still occupy slots between managed sets
- Rank and band decision is in `docs/decisions.md`. YAML conversion is a later phase
- Blog not written. It waits until the rest of Phase 5 is closed

`it`, wireless business-unit sets, and the YAML-reading root still wait.

## Phase 6 — Exceptions

`EX-*` requires ticket, owner, expiry. Linter fails expired exceptions.

## Phase 7 — Import (lab)

Import map of `name → uuid → terraform address`. Only objects we are ready to own.

## Phase 8 — Git promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

`environments/stage/` is added only if a second ISE eval exists.

## Phase 9 — Drift

Nightly export vs `policy/` + `inventory/`. Terraform plan as drift detector.