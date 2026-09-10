# ISE policy-as-code

Git-reviewed Network Access policy for Cisco ISE 3.3. YAML is the review surface. Terraform becomes the writer later, and only against the home-lab ISE.

## Current increment

**Phase 0 — repo skeleton.** Desired policy, inventory, and lab environment wiring. No ISE session. No Terraform provider.

## Planes

| Folder | Meaning | Applied? |
| --- | --- | --- |
| `policy/` | What ISE should look like | Yes, from Phase 3+ |
| `inventory/` | Nodes, VLANs, curated NADs | No |
| `exports/` | What ISE actually returned | No (generated) |
| `environments/lab/` | This checkout's only ISE | Wiring |

`environments/stage/` does not exist. Add it only if a second eval ISE is built. There is no `prod/` folder.

## What this is not

- Not a node installer
- Not Device Admin / TACACS
- Not a remote-production apply pipeline
- Not Terraform-managed NADs

## Git flow

One branch per phase. PR + approval. Merge to `main` when `docs/phases.md` exit criteria are met.

## Start here

- `docs/decisions.md` — scope locked in Phase 0
- `docs/naming.md` — prefixes and ranks
- `docs/file-map.md` — which file owns which object
- `docs/phases.md` — milestones
- `docs/blog-stops.md` — when to write it up

## Next increment

Phase 1 — read-only Python export from the lab ISE to `exports/*.csv`. First socket to ISE. GET only.