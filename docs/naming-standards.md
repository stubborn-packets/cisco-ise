# Naming Standards

**Status: draft, captured 2026-09-09.** Core pattern and prefix table are
solid enough to build Phase 2's linter against. Marked items under "Still
to come" are known gaps — flag Josh when the roadmap reaches the phase that
needs them.

## Pattern

```
{PREFIX}-<token>[-<token>...]
```

- `PREFIX` is uppercase, from the table below, followed by a single hyphen.
- Each token after the prefix is lowercase kebab-case: `[a-z0-9]`, single
  hyphens between tokens, no other characters.
- Example: `PS-corp-wireless-8021x` — a policy set (`PS-`) for corp wireless
  802.1X.

## Prefix table

| Prefix | Object type |
|---|---|
| `PS-` | Policy set |
| `AN-` | Authentication rule |
| `AZ-` | Authorization rule |
| `EX-` | Exception rule |
| `AP-` | Allowed protocols |
| `PR-` | Authorization profile |
| `ACL-` | Downloadable ACL |
| `SGT-` | Security group tag |
| `CND-` | Library condition |
| `ISS-` | Identity source sequence |
| `CAP-` | Certificate authentication profile |
| `EIG-` | Static endpoint identity group |
| `LP-` | Logical profile |
| `VIP-` | Load-balanced virtual IP name |

## Still to come

- **Policy-set evaluation order convention.** Needed before Phase 5 (pilot
  object import) — flag this when we get there if it hasn't shown up yet.
- **Additional naming patterns** Josh has in mind but hasn't detailed yet.
- **Where BU identity lives in the name, if at all.** This ISE instance
  serves multiple BUs under one global team, and some catalog files
  (`vlans.yaml`) are already scoped per-BU. Worth deciding before Phase 2's
  linter is written, since the linter enforces whatever's in this file —
  see `docs/data-model.md` for the open options.

## Legacy exceptions

None captured yet. Note any existing production object names here that
predate this standard and shouldn't fail the Phase 2 linter.
