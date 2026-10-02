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

Wired subset and VPN family closed 2026-10-02 on lab ISE. Sets stay disabled. Enable was not part of the close.

- `PS-global-vpn`, `PS-global-wired-8021x`, and `PS-global-wired-mab` created disabled
- YAML rank stays 10, 40, and 50. ISE insert ranks on this lab are 0, 1, and 2
- VPN service is `AP-vpn` (EAP-TLS, PEAP, TEAP, PAP). Condition is `CND-vpn`
- `AN-vpn` searches `Internal Users`. `AZ-vpn` returns `PR-global-vpn`
- `PR-global-vpn` returns `ACL-permit-all`, Class `ou=GP-global-vpn`, session timeout 28800, no VLAN
- Wired services, conditions, and rules are unchanged from the wired close
- Old GUI sets were shifted down, not renamed
- Blog not written. It waits until the rest of Phase 5 is closed

Wireless, infra, and `PS-<bu>-*` still wait.

## Phase 6 — Exceptions

`EX-*` requires ticket, owner, expiry. Linter fails expired exceptions.

## Phase 7 — Import (lab)

Import map of `name → uuid → terraform address`. Only objects we are ready to own.

## Phase 8 — Git promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

`environments/stage/` is added only if a second ISE eval exists.

## Phase 9 — Drift

Nightly export vs `policy/` + `inventory/`. Terraform plan as drift detector.