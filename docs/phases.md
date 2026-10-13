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
- YAML ranks at close were the old bands. ISE insert ranks were 0 through 7 for managed sets
- Wired global conditions require `DEVICE` `BusinessUnit` `BusinessUnit#global`. Guest and HR require `BusinessUnit#guest` and `BusinessUnit#hr`
- `AN-hr-wired` and `AN-guest-wired` search `Internal Endpoints` and continue if the MAC is unknown
- `AZ-hr-wired` returns `PR-hr-wired-mab` (VLAN 30) when `EIG-hr` matches. Guest returns VLAN 40
- Old GUI sets were not imported. They still occupy slots between managed sets
- Rank and band decision is in `docs/decisions.md`. YAML conversion is the next increment
- Blog saved 2026-10-06 at `blog/cisco-ise-policy-as-code-part5/`. Hero `ise-pac-part5-hero.jpg` is not generated in the post.

`it`, `PS-<bu>-vpn`, and `PS-<bu>-wireless` are not in this phase. A lab with nothing pointed at it does not gain a new pattern from those sets. Stop here. Do not rewrite the Phase 5 post.

## Rank conversion and YAML reader

Started 2026-10-13. This is not exceptions. Sets stay disabled. No new sets. No ISE write in the YAML conversion.

- `policy/policy-sets.yaml` `rank` is the packed index. `band` is the label. Live order is the insert order in `docs/decisions.md`.
- `POLICY_SET_RANK_EXACT` is retired. The linter checks a packed rank and a contiguous band. The family sequence is not enforced.
- `docs/naming.md` and `docs/decisions.md` no longer call YAML rank the design band.
- The root that reads `policy/` and calls the thin modules is not written yet. Until it exists, `environments/lab/*.tf` is still the copied source.
- Enable is a cutover, not this increment. Do not manage rank 99 Default. Do not import the old GUI sets.

## Phase 6 — Exceptions

`EX-*` requires ticket, owner, expiry. Linter fails expired exceptions.

## Phase 7 — Import (lab)

Import map of `name → uuid → terraform address`. Only objects we are ready to own.

## Phase 8 — Git promotion path

Branch → lint → validate → plan against lab → PR → approve → merge → apply lab.

`environments/stage/` is added only if a second ISE eval exists.

## Phase 9 — Drift

Nightly export vs `policy/` + `inventory/`. Terraform plan as drift detector.