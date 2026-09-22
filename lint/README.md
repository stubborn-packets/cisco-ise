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
| `scripts/lint_ise.py` | Grammar regex, file → prefix map, policy-set rank → name, state / exception / UUID rules | Desired-state objects |
| `policy/*.yaml` | Objects you want ISE to have | The grammar those names must follow |

`lint/prefixes.yaml` answers: is `PS` / `SGT` a known prefix token?

`scripts/lint_ise.py` answers: does this policy set’s name match the rank band we locked?

`policy/policy-sets.yaml` is the list of sets. Changing comments there does not change what the linter accepts.

## Layers

```
docs/naming.md          human standard
docs/decisions.md       locked rank bands and NDG roots
lint/prefixes.yaml      PREFIX table
lint/builtins.yaml      built-ins + NDG lock
scripts/lint_ise.py     regex + rank map + file map
policy/ + inventory/    desired / reference objects
```

Grammar enforced in code:

```text
NAME_RE  = PREFIX- + kebab-case [a-z0-9] tokens
SGT_RE   = SGT_ + snake_case [a-z0-9] tokens, length <= 32
KEBAB_RE = [a-z0-9]+(?:-[a-z0-9]+)*
SNAKE_RE = [a-z0-9]+(?:_[a-z0-9]+)*
```

That is why `PS-global-wired-8021x` passes and `PS-Global-Wired` fails.

Policy-set ranks enforced in `_check_policy_set_rank` / `POLICY_SET_RANK_EXACT`:

| Rank | Required name |
| --- | --- |
| 1–9 | `PS-infra-health-checks` |
| 10 | `PS-global-vpn` |
| 20 | `PS-global-wireless-8021x` |
| 30 | `PS-global-wireless-mab` |
| 40 | `PS-global-wired-8021x` |
| 50 | `PS-global-wired-mab` |
| 60–69 | `PS-<bu>-vpn` |
| 70–79 | `PS-<bu>-wireless` |
| 80–89 | `PS-<bu>-wired` |
| 99 | `Default` |

`<bu>` must be kebab-case. It is **not** checked against the BusinessUnit NDG allow-list yet (see below).

## Changing the shape

Work the layers in this order. Skip a step and the linter and the docs will disagree.

### Rename one global policy set (example: rank 40)

Today rank 40 must be `PS-global-wired-8021x`. To make it `PS-campus-wired-dot1x`:

1. Edit the rank table in `docs/naming.md`.
2. Change `POLICY_SET_RANK_EXACT[40]` in `scripts/lint_ise.py`.
3. Update `tests/lint/test_lint_ise.py` (`test_good_name_passes` uses the old name).
4. Run `python3.12 -m unittest tests.lint.test_lint_ise`.
5. Only then put the new name in `policy/policy-sets.yaml`.

### Loosen a rank from one exact name to a pattern

Example: allow any `PS-global-*` at rank 40.

1. Write the new rule in `docs/naming.md`.
2. Replace the `POLICY_SET_RANK_EXACT[40]` entry with a pattern check (same idea as `_matches_bu_pattern`).
3. Add a test that passes a new valid name and one that still fails a bad name.
4. Do not put that rule in `prefixes.yaml`. That file has no rank column.

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
- Rank table + `POLICY_SET_RANK_EXACT` — if that site’s evaluation order is different

Leave alone until a later phase says so:

- `environments/lab/` as the only write target
- no `prod/` folder in this repo
- NADs stay in `inventory/`; they are not Terraform-managed here

## BusinessUnit vs policy-set name

`docs/naming.md` says `<business-unit>` is a token from the BusinessUnit NDG allow-list.

The Phase 2 linter does **not** join those yet.

| Check | Happens today? |
| --- | --- |
| `PS-Lab-wired` fails (token not kebab-case) | Yes |
| `PS-lab-wired` at rank 80 matches `PS-<bu>-wired` | Yes |
| `lab` must exist in `policy/ndg.yaml` → BusinessUnit → `allowed_values` | **No** |
| NAD `ndg.business_unit: lab` must be on that allow-list | Yes, once the list is non-empty |

Allow-lists start empty on purpose (`docs/decisions.md`). Filling `BusinessUnit.allowed_values` before Phase 4 is required before NDG writes. Wiring `PS-<bu>-*` to that same list is a small follow-up in `_check_policy_set_rank`: take the middle token and require it in `self.ndg_by_name["BusinessUnit"]["allowed_values"]`. Do not turn that on while the list is still `[]`, or every BU-scoped policy set will fail.

NAD keys that *are* mapped today (`lint/builtins.yaml` `ndg_nad_keys`):

```text
location        → All Locations     (ISO 3166-1 alpha-3, or list if filled)
device_type     → All Device Types  (allow-list)
business_unit   → BusinessUnit      (allow-list)
stage           → Stage             (allow-list)
function        → Function          (allow-list)
```
