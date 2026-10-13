# lint/

Local naming checks. No ISE connection. No `exports/` read.

```bash
python3.12 scripts/lint_ise.py
python3.12 -m unittest tests.lint.test_lint_ise
```

This folder is the machine-readable half of `docs/naming.md`. Use it when adapting the model to another ISE (different prefixes, extra built-ins, more NDG roots). Do not commit employer hostnames, VIP addresses, NAD names, or ticket-system URLs here.

## What each file owns

| File | Owns | Does not own |
| --- | --- | --- |
| `prefixes.yaml` | Valid `PREFIX` tokens and rejected scopes (`tacacs`, `device-admin`) | Rank bands, kebab vs snake separator, which file maps to which prefix |
| `builtins.yaml` | ISE system names that skip `PREFIX-`; locked NDG roots; NAD `ndg:` key map; inventory-only `VLAN-` | User object names |
| `scripts/lint_ise.py` | Grammar regex, file → prefix map, packed rank, band, state / exception / UUID rules | Desired-state objects |
| `policy/*.yaml` | Objects you want ISE to have | The grammar those names must follow |

`lint/prefixes.yaml` answers: is `PS` / `SGT` a known prefix token?

`scripts/lint_ise.py` answers: is this policy set’s rank a packed index, and does its band stay contiguous?

`policy/policy-sets.yaml` is the list of sets. Changing comments there does not change what the linter accepts.

## Layers

```
docs/naming.md          human standard
docs/decisions.md       locked rank rule and NDG roots
lint/prefixes.yaml      PREFIX table
lint/builtins.yaml      built-ins + NDG lock
scripts/lint_ise.py     regex + packed rank + band + file map
policy/ + inventory/    desired / reference objects
```

Grammar enforced in code:

```text
NAME_RE  = PREFIX- + kebab-case [a-z0-9] tokens
SGT_RE   = SGT_ + snake_case [a-z0-9] tokens, length <= 32
KEBAB_RE = [a-z0-9]+(?:-[a-z0-9]+)*
SNAKE_RE = [a-z0-9]+(?:_[a-z0-9]+)*
```

`NAME_RE` is the default. That is why `PS-global-wired-8021x` passes and `PS-Global-Wired` fails.

SGT is the only exception (`docs/naming.md`). ISE ERS allows `[A-Za-z0-9_]`, max 32; a hyphen returns HTTP 400. YAML name equals the ISE name. There is no hyphen-to-underscore mapper.

- Pass: `SGT_lab_users`, `SGT_lab_bootstrap`
- Fail: `SGT-lab-users`, `SGT_Lab_Users`, `SGT_lab-users`

Policy-set rank is the packed ISE index. Band is a label. Terraform does not send band. Enforced in `_check_policy_set_rank` and `_check_policy_set_order`. `POLICY_SET_RANK_EXACT` is retired.

| Check | Rule |
| --- | --- |
| rank | integer, `>= 0`, required on a managed set |
| packed | managed ranks are unique and exactly `0..n-1` |
| band | required, and one of `POLICY_SET_BANDS` |
| contiguous | walking rank, a band that has ended does not come back |
| Default | name `Default`, rank `99`, no band. Not part of the packed sequence |
| rank 99 | Default only |

Known bands: `infra`, `global-vpn`, `global-wireless`, `global-wireless-mab`, `global-wired`, `global-wired-mab`, `bu-wired`, `bu-vpn`, `bu-wireless`.

The family sequence (infra, then VPN, then wireless, then wired, then business-unit) is not the live order. The linter does not enforce it. Live order is the insert order in `policy/policy-sets.yaml`.

`bu-vpn` and `bu-wireless` are labels only. Those sets are not written.

## Changing the shape

Work the layers in this order. Skip a step and the linter and the docs will disagree.

### Rename one policy set

Rank no longer selects the name. To rename `PS-global-wired-8021x`:

1. Put the new name in `policy/policy-sets.yaml`. Keep its rank and band.
2. Update any lab call or reader that still names the old object.
3. Update `tests/lint/test_lint_ise.py` if a fixture used the old name.
4. Run `python3.12 -m unittest tests.lint.test_lint_ise`.

Do not add the name to `POLICY_SET_RANK_EXACT`. That map is gone.

### Add a band

1. Write the label in `docs/naming.md` and `docs/decisions.md`.
2. Add the string to `POLICY_SET_BANDS` in `scripts/lint_ise.py`.
3. Add a test that passes the new band and one that still fails an unknown band.
4. Do not put the band in `prefixes.yaml`. That file has no rank or band column.
5. Only then put the band on a set in `policy/policy-sets.yaml`.

### Change the packed rule

Today managed ranks must be `0..n-1` with no gaps. Rank 99 is Default and is excluded. To change that:

1. Write the new rule in `docs/decisions.md`.
2. Change `_check_policy_set_order` in `scripts/lint_ise.py`.
3. Update `test_packed_rank_gap_fails` (or add the new case).
4. Do not put the rule in `prefixes.yaml`.

### Add a prefix (example: `ISS-`)

1. Add the row to the table in `docs/naming.md` and to `lint/prefixes.yaml`.
2. Add the YAML file (or list key) to `POLICY_COLLECTIONS` in `scripts/lint_ise.py`.
3. Add a good-name / wrong-prefix test.
4. Add objects under `policy/` only after the linter accepts the name.

Do not assume a new prefix uses a hyphen. SGT is `SGT_` + snake_case because ERS rejects `-`. Any other family that 400s on hyphen gets its own documented exception the same way. Do not add a mapper.

### Change SGT grammar

Today user SGTs must be `SGT_` + snake_case, max 32. To change that:

1. Edit the SGT exception in `docs/naming.md`.
2. Change `SGT_RE` in `scripts/lint_ise.py` (and the module regex only if ISE’s rule changed).
3. Update the SGT tests in `tests/lint/test_lint_ise.py`.
4. Run `python3.12 -m unittest tests.lint.test_lint_ise`.
5. Do not put the separator in `prefixes.yaml`. That file has tokens, not `-` vs `_`.

### Add an ISE built-in

Append the exact ISE spelling to `lint/builtins.yaml` `names:`. Do not invent a `PREFIX-` for it. Do not list leftover lab GUI names here.

### Add or rename an NDG root

1. Change the locked list in `docs/decisions.md` and `docs/naming.md`.
2. Update `ndg_roots`, `ndg_ise_roots`, and `ndg_nad_keys` in `lint/builtins.yaml`.
3. Add the root to `policy/ndg.yaml`.
4. A sixth root that exists only in `policy/ndg.yaml` fails as “unknown NDG root”.

### Point this model at another ISE later

Safe to change in that checkout (keep employer data out of the public repo and the blog):

- `lint/prefixes.yaml` — extra prefixes that ISE object type needs
- `lint/builtins.yaml` — extra system names that deployment must keep
- `policy/ndg.yaml` `allowed_values` — that site’s Location / Device Type / BU / Stage / Function lists
- Rank rule + `POLICY_SET_BANDS` — if that site’s evaluation order or labels differ

Leave alone until a later phase says so:

- `environments/lab/` as the only write target
- no `prod/` folder in this repo
- NADs stay in `inventory/`; they are not Terraform-managed here

## BusinessUnit vs policy-set name

`docs/naming.md` says `<business-unit>` is a token from the BusinessUnit NDG allow-list.

The Phase 2 linter does **not** join those yet. The old rank-band pattern (`PS-<bu>-wired` at 80–89) is retired with `POLICY_SET_RANK_EXACT`. A name is still `PREFIX-` + kebab-case. Rank is the packed index, not a band number.

| Check | Happens today? |
| --- | --- |
| `PS-Lab-wired` fails (token not kebab-case) | Yes |
| `PS-hr-wired` is a legal name at rank 0 with band `bu-wired` | Yes |
| `hr` must exist in `policy/ndg.yaml` → BusinessUnit → `allowed_values` | **No** |
| NAD `ndg.business_unit: lab` must be on that allow-list | Yes, once the list is non-empty |

Allow-lists start empty on purpose (`docs/decisions.md`). Filling `BusinessUnit.allowed_values` before Phase 4 is required before NDG writes. Wiring a `PS-<bu>-*` name to that same list is still a follow-up. Do not turn that on while the list is still `[]`, or every BU-scoped policy set will fail. Do not bring back the 80–89 rank pattern to do it.

NAD keys that *are* mapped today (`lint/builtins.yaml` `ndg_nad_keys`):

```text
location        → All Locations     (ISO 3166-1 alpha-3, or list if filled)
device_type     → All Device Types  (allow-list)
business_unit   → BusinessUnit      (allow-list)
stage           → Stage             (allow-list)
function        → Function          (allow-list)
```
