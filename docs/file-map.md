# File map

Three planes. Do not mix them.

| Plane | Folder | Question | Terraform apply? |
| --- | --- | --- | --- |
| Desired policy | `policy/` | What should ISE be? | Yes, from Phase 3+ |
| Inventory | `inventory/` | What exists around ISE? | No |
| Observed | `exports/` | What did the API return? | No (generated) |
| Environment | `environments/lab/` | Which ISE, which state? | Wiring only |

## policy/ — desired state

| File | Object | First write phase |
| --- | --- | --- |
| `ndg.yaml` | Allowed NDG roots and values | 4 |
| `allowed-protocols.yaml` | Services and EAP methods | 4 |
| `conditions.yaml` | Library conditions | 4 |
| `authz-profiles.yaml` | Result profiles and DACLs | 4 |
| `sgt.yaml` | SGTs | 4 |
| `eig.yaml` | Static EIGs | 4 |
| `logical-profiles.yaml` | Profiler logical profiles | TBD |
| `policy-sets.yaml` | Policy set order and rules | 5 |
| `exceptions.yaml` | Ticketed exception rules | 6 |

## inventory/ — reference

| File | Object | Notes |
| --- | --- | --- |
| `nodes.yaml` | Personas, version, VIPs | Never applied |
| `nads.yaml` | Curated NAD list | Report aid; live list is `exports/nads.csv` |
| `vlans.yaml` | Named VLANs per BU | Referenced by authz profiles |

## environments/

| Folder | Meaning |
| --- | --- |
| `lab/` | Home-lab eval. Only write target. |
| `stage/` | Not created. Add only if a second eval exists. |

## lint/

| File | Owns |
| --- | --- |
| `lint/prefixes.yaml` | PREFIX- table and rejected scopes |
| `lint/builtins.yaml` | ISE built-in names and locked NDG roots |
| `scripts/lint_ise.py` | Phase 2 naming linter (policy/ + inventory/ only) |

## YAML conventions

- kebab-case object names inside the prefix table
- comments explain intent
- explicit `state` on policy objects
- UUIDs do not belong in `policy/` or `inventory/`
- ownership (`owner`, `bu`) lives in YAML even when ISE has no field for it