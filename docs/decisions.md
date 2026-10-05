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

Superseded 2026-10-05 by the rank and band decision below. The 1–50 / 60+ / 99 table was a spacing convention. ISE does not store those numbers.

## Policy set rank and band

Recorded 2026-10-05. Lab ISE rejected POST rank 40. Legal create rank was a packed index. This lab will not have 99 policy sets, so the design-band numbers will never become ISE slots.

- `rank` in `policy/policy-sets.yaml` is the index ISE stores. Lower is evaluated first. It is packed: 0, 1, 2, with no gaps.
- `band` is a label, not a number Terraform sends. The linter uses it to group and order families: infra, then VPN, then wireless, then wired, then business-unit sets. Default is not a band and is not managed.
- Inserting a set means editing `rank` on the sets that shift. That edit is the order change. There is no second hidden rank.
- The lab call sends `rank`. It does not send `band`. `ps_ranks` should match the YAML rank.
- `ise_network_access_policy_set_update_rank` stays unused. It cannot open a gap, and the YAML no longer asks for one.
- The exact 10 / 40 / 50 linter check is retired when the YAML is converted. Do not convert it in the wireless write.

Current lab order, which the converted YAML should show:

| rank | name | band |
| --- | --- | --- |
| 0 | `PS-global-vpn` | `global-vpn` |
| 1 | `PS-global-wired-8021x` | `global-wired` |
| 2 | `PS-global-wired-mab` | `global-wired-mab` |

## YAML is the source the root will read

Recorded 2026-10-05. Copied lab calls were the first-write rule so a bad row could not create an object without a reviewed `.tf` diff. That rule is not the end state.

- One YAML file per family under `policy/`. Names and ranks live there. Ids do not.
- Thin modules stay. A later root reads the YAML and calls those modules. `condition: CND-vpn` resolves to the condition module output inside the root.
- Do not build that root in the wireless write. The YAML shape is still moving.
- Until that root exists, the lab call is still copied. The copy is the drift this decision is meant to end.

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