# ISE policy-as-code

Git-reviewed Network Access policy for Cisco ISE 3.3 patch 1. YAML is the review surface. Terraform is the writer against the home-lab ISE only.

## Current progress

| Phase | Status |
| --- | --- |
| 0 — Repo skeleton | Done |
| 1 — Read-only export (ERS + OpenAPI → `exports/*.csv`) | Done |
| 2 — Naming linter | Done |
| 3 — Terraform lab bootstrap (`CiscoDevNet/ise`) | In progress |
| 4–9 — Building blocks, policy sets, exceptions, import, Git path, drift | Later |

Phase 3 pins `CiscoDevNet/ise` 0.4.1 under `environments/lab/` and can create one SGT (`SGT-lab-bootstrap` / 1001). Local state only. Exit is still create-in-GUI then destroy. There is no `prod/` folder. `policy/sgt.yaml` stays empty until Phase 4.

Write-ups: 
- [Part 1 (0+1)](https://stubbornpackets.com/blog/cisco-ise-policy-as-code-part1)
- [Part 2 (linter)](https://stubbornpackets.com/blog/cisco-ise-policy-as-code-part2)
- Part 3 (terrform) | coming soon

## Planes

| Folder | Meaning | Applied? |
| --- | --- | --- |
| `policy/` | What ISE should look like | Yes, from Phase 4 |
| `inventory/` | Nodes, VLANs, curated NADs | No |
| `exports/` | What ISE actually returned | No (generated, gitignored) |
| `environments/lab/` | This checkout's only ISE | Wiring + Phase 3 bootstrap |
| `terraform/modules/` | Write modules | Called from lab only |

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

## Phase 2 linter

Reads `lint/prefixes.yaml`, `lint/builtins.yaml`, `policy/`, and `inventory/`. Does not read `exports/`. Does not connect to ISE.

```bash
python3.12 scripts/lint_ise.py
python3.12 -m unittest tests.lint.test_lint_ise
```

A bad name, missing `state`, missing exception metadata (`ticket`, `owner`, `expires_on`), or an unknown NDG root fails. ISE built-ins (`Default`, `Default Network Access`, `Unknown`, plus `lint/builtins.yaml`) pass. Empty scaffolds pass.

To change a prefix, a policy-set rank name, or an NDG root, follow `lint/README.md`. `docs/naming.md` is the human table; `scripts/lint_ise.py` is what the linter actually enforces.

## Phase 3 Terraform

Pin and modules: `environments/lab/versions.tf`, `terraform/modules/sgt/`.
How to run it: `terraform/README.md`.

```bash
cd environments/lab
set -a && source ../../.env && set +a
terraform init
terraform plan
terraform apply
```

`terraform validate` does not load `terraform.tfvars`. A bad `SGT-` name fails on `plan`.

Do not apply until the plan is one create of
`module.sgt_bootstrap.ise_trustsec_security_group.this`.
Confirm in the lab GUI, then `terraform destroy`. Keep the Phase 3 blog
post until that exit is met. Still no `prod/`.
