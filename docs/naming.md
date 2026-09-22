# Naming standard

User-created ISE names, except SGTs:

{PREFIX}- + kebab-case tokens

- Prefix stays uppercase.
- Tokens after the first hyphen are [a-z0-9] separated by a single hyphen.
- No spaces, underscores, or extra punctuation in the name.
- state: enabled or state: disabled is required on policy objects.

Pass: PS-global-wired-8021x, AN-dot1x-ad, PR-wired-corp-access

Fail: Corp Users VLAN, ps-global-wired-8021x, PS_global_wired, PS-Global-Wired

SGTs are the one exception. ISE ERS stores `[A-Za-z0-9_]` only, max 32.
Hyphens return HTTP 400. YAML name equals the ISE name. No mapper.

SGT_ + snake_case tokens

- Prefix stays `SGT_`.
- Tokens after the first underscore are [a-z0-9] separated by a single underscore.
- No hyphens, spaces, or extra punctuation. Do not Title-Case tokens (`SGT_Lab_Users`).
- Max 32 characters.

Pass: SGT_lab_users, SGT_lab_bootstrap

Fail: SGT-lab-users, SGT_Lab_Users, SGT_lab-users

## Prefix table

| Prefix | Object | In scope |
| --- | --- | --- |
| PS- | Policy set | Yes |
| AN- | Authentication rule | Yes |
| AZ- | Authorization rule | Yes |
| EX- | Exception rule | Yes |
| AP- | Allowed protocols | Yes |
| PR- | Authorization profile | Yes |
| ACL- | Downloadable ACL | Yes |
| SGT_ | Security group tag | Yes (snake_case; ISE rejects hyphen) |
| CND- | Library condition | Yes |
| ISS- | Identity source sequence | Yes |
| CAP- | Certificate authentication profile | Yes |
| EIG- | Static endpoint identity group | Yes |
| LP- | Logical profile | Policy docs until API is proven |
| VIP- | Load-balanced virtual IP name | Inventory only |

Machine-readable copy: lint/prefixes.yaml.

## Names that do not get a prefix

ISE built-ins stay as ISE named them: Default, Default Network Access, Unknown, and other system groups. The Phase 2 linter allow-lists these in `lint/builtins.yaml`.

## Policy set name pattern

| Rank | Name pattern |
| --- | --- |
| 1–9 | PS-infra-health-checks |
| 10 | PS-global-vpn |
| 20 | PS-global-wireless-8021x |
| 30 | PS-global-wireless-mab |
| 40 | PS-global-wired-8021x |
| 50 | PS-global-wired-mab |
| 60+ | PS-<business-unit>-vpn |
| 70+ | PS-<business-unit>-wireless |
| 80+ | PS-<business-unit>-wired |
| 99 | Default (built-in) |

<business-unit> is a kebab-case token from the BusinessUnit NDG allow-list.

The Phase 2 linter checks that token is kebab-case. It does not yet require it to appear in `policy/ndg.yaml` BusinessUnit `allowed_values`. NAD `ndg.business_unit` values *are* checked against that list once it is non-empty. How to turn the policy-set join on, and how to change ranks or prefixes, is in `lint/README.md`.

## NDG values

Roots keep ISE names (Location, Device Type, plus custom BusinessUnit, Stage, Function).

- Location leaves = ISO 3166-1 alpha-3 (USA, CAN)
- Other leaves = kebab-case allow-list entries in policy/ndg.yaml