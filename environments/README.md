# environments/

One folder per ISE this repo is allowed to target.

| Folder | Status | Writes? |
| --- | --- | --- |
| `lab/` | Current home-lab eval | Yes, from Phase 3 |
| `stage/` | Not created | Would be a second eval, same `policy/` tree, separate state |

There is no `prod/` folder. A later remote environment would get its own folder and its own state file. It is not part of this checkout.

What belongs here:

- ISE version / patch notes
- `write_enabled`
- Terraform backend + provider files (Phase 3+)

What does not:

- Desired policy (that is `policy/`)
- NAD / VLAN / node inventory (that is `inventory/`)
- URLs, usernames, passwords (that is `.env`)