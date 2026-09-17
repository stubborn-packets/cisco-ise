# ISE policy-as-code

Git-reviewed Network Access policy for Cisco ISE 3.3 patch 1. YAML is the review surface. Terraform becomes the writer later, and only against the home-lab ISE.

## Current progress

| Phase | Status |
| --- | --- |
| 0 — Repo skeleton | Done |
| 1 — Read-only export (ERS + OpenAPI → `exports/*.csv`) | Done |
| 2 — Naming linter | This increment |
| 3 — Terraform lab bootstrap (`CiscoDevNet/ise`) | Not started |
| 4–9 — Building blocks, policy sets, exceptions, import, Git path, drift | Later |

Nothing has been written to ISE. There is no Terraform provider block yet. Lab (`environments/lab/`) is the only write target when Phase 3 starts. There is no `prod/` folder.

Write-up for 0 + 1: [Cisco ISE Policy-as-Code Migration - Part 1](https://stubbornpackets.com/blog/cisco-ise-policy-as-code-part1)

## Planes

| Folder | Meaning | Applied? |
| --- | --- | --- |
| `policy/` | What ISE should look like | Yes, from Phase 3+ |
| `inventory/` | Nodes, VLANs, curated NADs | No |
| `exports/` | What ISE actually returned | No (generated, gitignored) |
| `environments/lab/` | This checkout's only ISE | Wiring |

`environments/stage/` does not exist. Add it only if a second eval ISE is built.

## What this is not

- Not a node installer
- Not Device Admin / TACACS
- Not a remote-production apply pipeline
- Not Terraform-managed NADs

## Git flow

One branch per phase. PR + approval. Merge to `main` when `docs/phases.md` exit criteria are met. `main` is last approved lab desired state, not a remote production ISE.

## Start here

- `docs/handoff.md` — closed work and the next increment
- `docs/decisions.md` — scope locked in Phase 0
- `docs/naming.md` — prefixes and ranks
- `docs/file-map.md` — which file owns which object
- `docs/phases.md` — milestones
- `docs/blog-stops.md` — when to write it up

## Phase 1 export

On the lab ISE enable ERS, OpenAPI, and API Gateway
(`Administration > System > Settings > API Settings`).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
cp .env.example .env    # set ISE_URL, ISE_USERNAME, ISE_PASSWORD
python scripts/export_ise.py
```

The exporter is GET-only (`requests`, not `ciscoisesdk`). CSVs land in `exports/` and are gitignored. Compare `name` columns to `docs/naming.md`. Do not edit the CSVs.

Single family:

```bash
python scripts/export_ise.py --resource policy-sets
python scripts/export_ise.py --resource nads --no-details
```

## Next increment

Phase 2 — naming linter against `lint/prefixes.yaml`, `policy/`, and `inventory/`. Still no ISE writes.
