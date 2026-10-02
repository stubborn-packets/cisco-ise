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

Wired subset met 2026-10-02 on lab ISE. Sets stay disabled. Enable is the cutover, not this write.

- `PS-global-wired-8021x` and `PS-global-wired-mab` created disabled
- YAML rank stays 40 and 50. ISE stores a packed insert index (0 and 1 on this lab)
- Services are `AP-wired-dot1x` and `AP-wired-mab`
- Set conditions are `CND-wired-dot1x-framed` and `CND-wired-mab-call-check`
- `AN-wired-dot1x` searches `Internal Users` (`REJECT` / `DROP` / `REJECT`)
- `AN-wired-mab` searches `Internal Endpoints` (`REJECT` / `DROP` / `CONTINUE`)
- `AZ-wired-dot1x` and `AZ-wired-mab` return `PR-wired-lab-access`. No SGT
- `CND-wired-mab` is the MAB authentication-rule condition. It is illegal on a policy set
- Do not import existing non-standard lab policy sets as desired state
- Do not manage rank 99 Default, or the built-in Default rule inside a set
- Old GUI sets were shifted down, not renamed
- `ise_network_access_policy_set_update_rank` is not wired. Add it when a later apply must move an existing set

VPN, wireless, infra, and `PS-<bu>-*` wait until those services exist. Blog waits until the phase is closed.

## Phase 6 — Exceptions

`EX-*` requires ticket, owner, expiry. Linter fails expired exceptions.

## Phase 7 — Import (lab)

Import map of `name → uuid → terraform address`. Only objects we are ready to own.

## Phase 8 — Git promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

`environments/stage/` is added only if a second ISE eval exists.

## Phase 9 — Drift

Nightly export vs `policy/` + `inventory/`. Terraform plan as drift detector.