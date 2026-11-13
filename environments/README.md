# environments/

One folder per ISE this repo is allowed to target.

| Folder | Status | Writes? |
| --- | --- | --- |
| `lab/` | Current home-lab eval. Only write target. | Yes, from Phase 3 |
| `stage/` | Not created | Would be a second eval, same `policy/` tree, separate state. Add only if a second eval ISE exists. |

There is no `prod/` folder. Phase 14 made the scripts environment-aware (`--environment` / `-e`, credentials as `<ENV>_ISE_*`) without creating stage or prod directories. `read_policy.py` emits under `environments/<label>/` only when that directory already exists. CI stays on `environments/lab`.

What belongs here:

- ISE version / patch notes
- `write_enabled`
- Terraform backend + provider files
- Generated `.tf` files (do not hand-edit)

What does not:

- Desired policy (that is `policy/`)
- NAD / VLAN / node inventory (that is `inventory/`)
- URLs, usernames, passwords (that is `.env` or the environment-specific `<ENV>_ISE_*` variables)