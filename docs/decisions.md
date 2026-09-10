# Decisions locked in Phase 0

Recorded 2026-09-10. Change these with a PR.

## Scope

- Network Access only. No TACACS. No Device Administration.
- One home-lab ISE (`environments/lab`). That is the only write target.
- No `prod/` environment in this repo.
- `environments/stage/` is optional later, only if a second eval ISE is built.

## Versions

- Lab: ISE 3.3 patch 1
- A later remote environment would pin the same major.minor before any promote demo
- Terraform provider target when Phase 3 starts: `CiscoDevNet/ise`

## Policy set evaluation order

See `policy/policy-sets.yaml` and `docs/naming.md`.

Ranks 1–50 are global. Ranks 60+ are per business unit. Rank 99 is ISE Default.

## NDG roots

- All Locations — ISO 3166-1 alpha-3
- All Device Types — allow-list
- BusinessUnit — allow-list
- Stage — NAD enforcement type
- Function — role or project when Device Type + BU cannot describe the NAD

Allow-lists start empty. Fill them before Phase 4 writes NDGs.

## Planes

- `policy/` — desired state Terraform will enforce
- `inventory/` — reference data Terraform will not apply (nodes, NADs, VLANs)
- `exports/` — observed state from a live GET
- `environments/` — which ISE and which state file

## NADs

- Curated list in `inventory/nads.yaml`
- Live list from Phase 1 in `exports/nads.csv`
- Not managed by Terraform in this PoC

## Lab objects that already exist (non-standard)

Do not import those names as desired state. Do not rename them in place as the first write.

Do:

1. Export them in Phase 1
2. Create new standard objects beside them
3. Move test traffic to the new objects
4. Disable the old objects
5. Delete the old objects after a bake period

## Engine

- Desired state in YAML under `policy/`
- Thin Terraform in Phase 3+
- `netascode/nac-ise` is a fallback if the custom mapper becomes the bottleneck

## Git

- One branch per phase (or per feature inside a phase)
- PR + approval before `main`
- `main` is last approved lab desired state, not a remote production ISE

## Public repo hygiene

- No employer hostnames, VIP addresses, or NAD names
- No employee or ticket-system URLs
- Example objects use `lab` / fictional names only
- Secrets only in `.env`