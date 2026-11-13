# Phases

One phase per branch. Merge to `main` when that phase is closed.

The only ISE this repo may write to is `environments/lab`.

## Phase 0 — Repo skeleton (done)

- `policy/`, `inventory/`, `environments/lab/`
- Naming, file map, phase, and blog-stop docs
- No ISE connection
- No Terraform provider block

Exit: repo clones, files open, nothing talks to ISE.

## Phase 1 — Read-only discovery (done)

- Python 3.12 export against **lab** ISE (ERS + OpenAPI)
- CSV under `exports/`
- Credentials from `.env`

Exit: CSVs generated from the lab ISE, including non-standard GUI objects.

## Phase 2 — Naming linter (done)

- Linter reads `lint/prefixes.yaml` + `lint/builtins.yaml` + `policy/` + `inventory/`
- Fails bad names, missing `state`, missing exception metadata, unknown NDG roots
- Empty scaffolds pass. `exports/` is not linted.

Exit: a bad name fails; a good name passes. ISE still untouched.

## Phase 3 — Terraform lab bootstrap (done)

- Pin `CiscoDevNet/ise` 0.4.1 under `environments/lab/`
- Module: `terraform/modules/sgt/`
- First object: `SGT_lab_bootstrap` / 1001 (underscores; ISE rejects hyphenated SGT names)
- Local Terraform state only

Exit met 2026-09-21: object created and destroyed via ERS. Unused SGT is deletable.

## Phase 4 — Policy building blocks (done)

Order: NDG → allowed protocols → conditions → authz profiles / DACLs → SGTs → EIGs.

Exit met 2026-10-01: each family has a YAML row, a thin module, a lab call, and a live object on lab ISE. NADs stayed in `inventory/` + `exports/`. No policy sets. Blog saved at `blog/cisco-ise-policy-as-code-part4/`.

## Phase 5 — Policy sets and ranks

Wired, VPN, wireless, infra, and the first business-unit pair closed 2026-10-05 on lab ISE. Sets stay disabled. Enable was not part of the close.

- Global sets are infra, wireless 802.1X, wireless MAB, VPN, wired 802.1X, wired MAB
- Business-unit sets are `PS-hr-wired` and `PS-guest-wired`
- YAML ranks at close were the old bands. ISE insert ranks were 0 through 7 for managed sets
- Wired global conditions require `DEVICE` `BusinessUnit` `BusinessUnit#global`. Guest and HR require `BusinessUnit#guest` and `BusinessUnit#hr`
- `AN-hr-wired` and `AN-guest-wired` search `Internal Endpoints` and continue if the MAC is unknown
- `AZ-hr-wired` returns `PR-hr-wired-mab` (VLAN 30) when `EIG-hr` matches. Guest returns VLAN 40
- Old GUI sets were not imported. They still occupy slots between managed sets
- Rank and band decision is in `docs/decisions.md`. YAML conversion is the next increment
- Blog saved 2026-10-06 at `blog/cisco-ise-policy-as-code-part5/`. Hero `ise-pac-part5-hero.jpg` is not generated in the post.

`it`, `PS-<bu>-vpn`, and `PS-<bu>-wireless` are not in this phase. A lab with nothing pointed at it does not gain a new pattern from those sets. Stop here. Do not rewrite the Phase 5 post.

## Rank conversion and YAML reader

Closed 2026-10-16. Rank conversion, every family reader, outputs, and the bootstrap SGT move are done. This is not exceptions. Sets stay disabled. No new sets. No ISE write in the YAML conversion.

- `policy/policy-sets.yaml` `rank` is the packed index. `band` is the label. Live order is the insert order in `docs/decisions.md`.
- `POLICY_SET_RANK_EXACT` is retired. The linter checks a packed rank and a contiguous band. The family sequence is not enforced.
- `scripts/read_policy.py` emits every managed family and `outputs.tf`. Do not hand-edit those files. Addresses stay `module.ps_*`, `module.an_*`, `module.az_*`, and the matching family prefixes. No `for_each`. Ids stay out of `policy/`. Map keys are derived from the YAML name only.
- `SGT_lab_bootstrap` / 1001 lives in `policy/sgt.yaml`. Address is `module.sgt_lab_bootstrap`. Map key is `lab_bootstrap`. State was moved. Hand-written main/variables/tfvars path is gone.
- Blog saved 2026-10-16 at `blog/cisco-ise-policy-as-code-part6/`. Hero `ise-pac-yaml-hero.jpg` is not generated in the post.
- Enable is a cutover, not this increment. Do not manage rank 99 Default. Do not import the old GUI sets.

## Phase 6 — Exceptions (done)

Closed 2026-10-16 on lab ISE. Local and global exception modules exist. Reader emits both scopes. Sets stay disabled.

- `EX-*` requires ticket, owner, and expiry. Linter fails missing or expired metadata.
- Local: `EX-vendor-wired-temp` rank 0 inside `PS-global-wired-mab`. Condition `CND-wired-mab`. Profile `PR-wired-lab-access`.
- Global: `EX-lab-global-monitor` rank 0, no policy set. Condition `CND-infra-f5-health`. Profile `PR-infra-permit`.
- Modules: `terraform/modules/authorization-exception-rule/` and `terraform/modules/authorization-global-exception-rule/`.
- `scripts/read_policy.py` emits `environments/lab/exceptions.tf` and the shared `ex_*` maps. Do not hand-edit.
- No SGT. No new sets. Enable is a cutover, not this phase.

## Phase 7 — Import (lab)

Closed 2026-10-19. Import map of `name → uuid → terraform address`. Only objects we are ready to own.

- `scripts/ise_client.py` is the shared GET-only client.
- `scripts/import_map.py` walks the families `read_policy.py` already emits. Loaders: `load_flat` (ERS), `load_openapi`, `load_rules`, `load_exceptions`, `load_ndg`.
- Purpose is state recovery and the ownership boundary. Not part of day-to-day apply. Terraform state already holds the UUIDs while it is healthy.
- Rank 99 Default, Default Network Access, old GUI sets, and NADs are not mapped.
- UUIDs stay out of `policy/` and `inventory/`. Sets stay disabled.

## Phase 8 — Git promotion path

Closed when the path is written and the secret-free gates run.

- `docs/promotion.md` is the checklist: branch → lint → validate → plan against lab → PR → approve → merge → apply lab.
- `.github/workflows/ci.yml` runs on pull requests. Secret-free only: lint, unit tests, `terraform fmt -check`, `terraform validate`. No plan, no apply, no ISE.
- `scripts/check.sh` is the local mirror of the same gates.
- Plan and apply stay local. They require the lab `.env`.
- Sets stay disabled. Enable is a cutover, not this path.
- `environments/stage/` is added only if a second ISE eval exists.

Exit: a PR that changes YAML fails CI if the name is bad or Terraform does not validate, and the checklist in `docs/promotion.md` matches the workflow and the script.

## Phase 9 — Drift

Closed 2026-10-28. GET-only comparison of `policy/` against live ISE, plus Terraform plan as the authoritative detector for owned objects.

- `scripts/drift.py` covers every family `read_policy.py` emits: SGT (name + tag), EIG, DACL, AP, PR, CND, PS, AN, AZ, EX, NDG.
- Rules and exceptions print as `parent-set | name` (global exceptions as `global | name`).
- Built-in `Default` rules and the names `Default` / `Default Network Access` are ignored.
- System exclusions live in `policy/system-exclusions.yaml`. Edit names there; do not hard-code them in the script.
- Non-owned remainder is printed. It does not fail the owned check, but it does fail the overall “all clean” summary.
- Terraform plan remains the authoritative detector. It stays local and requires the lab `.env`.
- Does not write to ISE. Does not run in CI. Sets stay disabled.

Exit: a reader can tell owned drift (plan or script missing/extra/mismatch) from observed extra objects (non-owned list). The script reports name-level differences for every owned family and does not write.

## Phase 10 — Shared client for export

Closed 2026-10-28. `scripts/export_ise.py` now uses the shared `IseClient` in `scripts/ise_client.py`.

- Local `IseClient` class and its pagination helpers removed from `export_ise.py`.
- `load_settings` calls `load_client`. CLI, CSV layout, resource list, and secret redaction unchanged.
- One GET path for export, import map, and drift. The client still refuses any method other than GET.
- Does not write to ISE. Does not change generated `.tf` files. Sets stay disabled.

Exit: `python scripts/export_ise.py` produces the same CSVs under `exports/` as before. No second HTTP implementation remains in the export script.

## Linter join (cleanup)

Closed 2026-10-28. A policy set whose band starts with `bu-` must be `PS-<business-unit>-<flow>`. The second token must be in `BusinessUnit.allowed_values`. Global and infra bands are not joined. An empty allow-list fails every `bu-*` set.

Exit: `PS-hr-wired` and `PS-guest-wired` pass. A `bu-*` set with a token that is not on the allow-list fails. A global set still passes without a business-unit token.

## Phase 11 — Deferred identity families

One family at a time. Sets stay disabled.

- **11a — ISS-** identity source sequences. Closed 2026-11-03. YAML, thin module, reader emission, linter. One lab object: `ISS_lab_internal` (`break_on_store_fail: false`, Internal Users then Internal Endpoints). No certificate profile. ISE rejects hyphens; name is `ISS_` + snake_case. Sets stay disabled.
- **11b — CAP_** certificate authentication profiles. Closed 2026-11-11. YAML, thin module, reader emission, linter. Two lab objects: `CAP_lab_subject_cn` (`SUBJECT_COMMON_NAME`) and `CAP_lab_subject_san` (`SUBJECT_ALTERNATIVE_NAME`). Name is `CAP_` + snake_case; ISE rejects hyphens. No live clients or internal CA required. Sets stay disabled.
- **LP-** logical profiles. Skipped. Potential future work if needed and the API write path is proven. Not in this phase.

## Phase 12 — Reporting

Closed. Report-only view of owned policy under reports/.

- `scripts/report_policy.py` reads `policy/policy-sets.yaml`, `policy/conditions.yaml`, `policy/authz-profiles.yaml`, and `inventory/vlans.yaml`.
- Emits `reports/policy-evaluation.md` (full) and optional filtered files via `--filter`.
- Shows each set’s rank, band, state, service, expanded condition, authentication rules, and authorization rules (with VLAN ids).
- No ISE connection, no UUIDs, no writes. Sets stay disabled.
- Generated `.md` files are gitignored; `reports/README.md` is tracked.

Exit: a reader can regenerate a human-readable evaluation report of the owned policy sets, their conditions, and their rules without talking to ISE.

## Phase 13 — External identity sources (LDAP)

Started 2026-11-13. Thin module and YAML for an LDAP identity source. The pinned CiscoDevNet/ise 0.4.1 provider has no LDAP resource, so the object is hand-built in the ISE GUI under the exact YAML name. The name is usable from ISS and authentication rules. Phase 15 will document the hand-build steps. Sets stay disabled.

- Prefix: `LDAP-` + kebab-case. First object: `LDAP-lab-stubbornpackets-uid`.
- `policy/ldap.yaml` holds the lab OpenLDAP settings and the selected groups.
- `terraform/modules/ldap/` is a skeleton (null_resource placeholder). Reader emits `environments/lab/ldap.tf` and the `ldap_*` maps.
- Do not hand-edit the generated file. Ids stay out of policy/.

## Phase 14 — Multi-instance readiness

Closed 2026-11-13. Scripts accept an environment label (default `lab`). Exports, drift, and import-map output show which environment they ran against. Still one write target (`environments/lab`). Removes the hard “lab” assumption without inventing stage or prod.

- Scripts accept `--environment` / `-e` (`lab`, `stage`, or `prod`; default `lab`).
- Credentials are read only as `<ENV>_ISE_URL`, `<ENV>_ISE_USERNAME`, `<ENV>_ISE_PASSWORD`, `<ENV>_ISE_INSECURE`. No fallback to plain `ISE_*`.
- Exports write to `exports/<environment>/` (created on first use).
- Drift, import-map, and the reader print or target the label.
- `read_policy.py` emits under `environments/<label>/` only when that directory already exists.
- `check.sh` accepts an optional environment argument (default `lab`). CI stays on `environments/lab`.
- No `environments/stage/` or `prod/` created. Sets stay disabled.

## Phase 15 — Operational documentation

Closed 2026-11-13. Documentation only. No new Terraform resources.

- `docs/operations.md` — nightly drift example (cron, systemd, or GitHub Actions) and optional notification if non-owned objects appear.
- `docs/getting-started.md` — benefits, what is needed (ISE version, API access, packages), starting small to fully managed, and the cutover pattern.
- `docs/ldap-hand-build.md` — GUI steps for `LDAP-lab-stubbornpackets-uid` (provider has no LDAP resource; object is hand-built under the exact YAML name).

Sets stay disabled. Enable is a cutover. 