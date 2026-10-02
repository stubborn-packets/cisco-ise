# terraform/

Reusable write modules. They do not know which ISE they talk to.

The root that may apply them is `environments/lab/` only. There is no
`environments/stage/` or `prod/` in this repo.

## Layout

```text
terraform/modules/sgt/                  one ise_trustsec_security_group
terraform/modules/ndg/                  one ise_network_device_group
terraform/modules/allowed-protocols/    one ise_allowed_protocols
terraform/modules/condition/              one ise_network_access_condition
terraform/modules/dacl/                   one ise_downloadable_acl
terraform/modules/authorization-profile/  one ise_authorization_profile
terraform/modules/eig/                    one ise_endpoint_identity_group
terraform/modules/policy-set/             one ise_network_access_policy_set
environments/lab/                         provider pin, local state, module calls
```

Phase 3 SGT lives in `environments/lab/terraform.tfvars`, not in
`policy/sgt.yaml`. NDG allow-lists live in `policy/ndg.yaml`. Lab NDG
calls live in `environments/lab/ndg.tf`.

## Lab apply

Credentials: repo-root `.env` (`ISE_URL`, `ISE_USERNAME`, `ISE_PASSWORD`,
`ISE_INSECURE`). Terraform does not load `.env` by itself.

```bash
cd environments/lab
set -a && source ../../.env && set +a
terraform init
terraform plan
terraform apply
terraform output
terraform destroy
```

`terraform validate` checks syntax and types. It does not load
`terraform.tfvars` and will not fail a bad `SGT-` name. `terraform plan`
does.

State file: `environments/lab/terraform.tfstate` (gitignored).

Provider: `CiscoDevNet/ise` 0.4.1, pinned in
`environments/lab/versions.tf`.

## First object

| Field | Value |
| --- | --- |
| Terraform address | `module.sgt_bootstrap.ise_trustsec_security_group.this` |
| ISE name | `SGT_lab_bootstrap` |
| Tag | `1001` |
| GUI | Work Centers > TrustSec > Components > Security Groups |

Do not import an existing non-standard lab SGT as this address.
Do not put the UUID from `terraform output sgt_id` into `policy/` or
`inventory/`.

## Phase 4 SGTs

`policy/sgt.yaml` is the review surface. Bootstrap stays in tfvars.
Do not manage ISE built-in Unknown (tag 0).

| Terraform address | ISE name | Tag |
| --- | --- | --- |
| `module.sgt_lab_users.ise_trustsec_security_group.this` | `SGT_lab_users` | 1010 |
| `module.sgt_lab_devices.ise_trustsec_security_group.this` | `SGT_lab_devices` | 1020 |

Do not put `terraform output sgt_ids` into `policy/` or `inventory/`.

## NDG objects

ERS `name` must include `#`. Custom type container is `type#type`
(`BusinessUnit#BusinessUnit`) so the GUI row is `BusinessUnit`.
Custom leaf is `type#type#value`. Built-in Location / Device Type keep
`All Locations` / `All Device Types`. Bare `BusinessUnit` returns HTTP 400.
ISE rejects `<` and `>` in `description` (XSS validation).

| Terraform address | ISE name | Role |
| --- | --- | --- |
| `module.ndg_business_unit.ise_network_device_group.this` | `BusinessUnit#BusinessUnit` | type container |
| `module.ndg_stage.ise_network_device_group.this` | `Stage#Stage` | type container |
| `module.ndg_function.ise_network_device_group.this` | `Function#Function` | type container |
| `module.ndg_location_usa.ise_network_device_group.this` | `Location#All Locations#USA` | leaf |
| `module.ndg_device_type_switch.ise_network_device_group.this` | `Device Type#All Device Types#switch` | leaf |
| `module.ndg_business_unit_lab.ise_network_device_group.this` | `BusinessUnit#BusinessUnit#lab` | leaf |
| `module.ndg_stage_monitor.ise_network_device_group.this` | `Stage#Stage#monitor` | leaf |
| `module.ndg_function_lab.ise_network_device_group.this` | `Function#Function#lab` | leaf |

GUI: Administration > Network Resources > Network Device Groups.

Do not put `terraform output ndg_ids` into `policy/` or `inventory/`.
Do not manage NADs here.

## Allowed protocols

Do not manage Default Network Access. ISE 3.3 requires `allow_5g` on every
object and inner PEAP/TEAP/EAP-TLS settings when those parents are true.

| Terraform address | ISE name |
| --- | --- |
| `module.ap_wired_dot1x.ise_allowed_protocols.this` | `AP-wired-dot1x` |
| `module.ap_wired_mab.ise_allowed_protocols.this` | `AP-wired-mab` |

GUI: Policy > Policy Elements > Results > Authentication > Allowed Protocols.

Do not put `terraform output ap_ids` into `policy/` or `inventory/`.

## Library conditions

Attribute conditions only. AND/OR children later. Do not use the
Device Admin condition resource.

| Terraform address | ISE name |
| --- | --- |
| `module.cnd_wired_dot1x.ise_network_access_condition.this` | `CND-wired-dot1x` |
| `module.cnd_wired_mab.ise_network_access_condition.this` | `CND-wired-mab` |

GUI: Policy > Policy Elements > Conditions > Library Conditions.

Do not put `terraform output cnd_ids` into `policy/` or `inventory/`.

## Downloadable ACLs and authorization profiles

VLANs live in `inventory/vlans.yaml`. They are not ISE objects.
`vlan_tag_id` is the RADIUS tunnel tag (usually 1), not the VLAN ID.
First profile has no SGT.

| Terraform address | ISE name |
| --- | --- |
| `module.acl_permit_all.ise_downloadable_acl.this` | `ACL-permit-all` |
| `module.pr_wired_lab_access.ise_authorization_profile.this` | `PR-wired-lab-access` |

GUI: Policy > Policy Elements > Results > Authorization.

Do not put `terraform output acl_ids` or `pr_ids` into `policy/` or `inventory/`.

## Endpoint identity groups

Static groups only. Parent UUID is omitted; ISE hangs them off the root.
Do not manage Unknown, Profiled, Blacklist, GuestEndpoints, or RegisteredDevices.
Do not create endpoints here.

| Terraform address | ISE name |
| --- | --- |
| `module.eig_printers.ise_endpoint_identity_group.this` | `EIG-printers` |
| `module.eig_lab_iot.ise_endpoint_identity_group.this` | `EIG-lab-iot` |

GUI: Work Centers > Network Access > Identities > Endpoint Identity Groups.

Do not put `terraform output eig_ids` into `policy/` or `inventory/`.

## Policy sets

YAML rank is the design band. ISE rank is a packed insert index. This lab
rejected POST rank 40. The shell inserted disabled at 0, then 1.
`ise_network_access_policy_set_update_rank` is not wired. It is a later
reorder, used when an existing set must move. It cannot open a gap at 40.
Do not manage rank 99 Default. Do not manage Default Network Access.
Rules are separate resources. The parent sets stay disabled, so the rules
are not evaluated.

| Terraform address | ISE name | Insert rank | State |
| --- | --- | --- | --- |
| `module.ps_global_wired_8021x.ise_network_access_policy_set.this` | `PS-global-wired-8021x` | 0 | disabled |
| `module.ps_global_wired_mab.ise_network_access_policy_set.this` | `PS-global-wired-mab` | 1 | disabled |
| `module.an_wired_dot1x.ise_network_access_authentication_rule.this` | `AN-wired-dot1x` | 0 | enabled |
| `module.an_wired_mab.ise_network_access_authentication_rule.this` | `AN-wired-mab` | 0 | enabled |
| `module.az_wired_dot1x.ise_network_access_authorization_rule.this` | `AZ-wired-dot1x` | 0 | enabled |
| `module.az_wired_mab.ise_network_access_authorization_rule.this` | `AZ-wired-mab` | 0 | enabled |

`AN-wired-dot1x` uses `Internal Users`. `AN-wired-mab` uses `Internal Endpoints`
and `if_user_not_found = CONTINUE`. Both `AZ-` rules return `PR-wired-lab-access`.
No security group.

GUI: Policy > Policy Sets.

Do not put `terraform output ps_ids`, `an_ids`, or `az_ids` into `policy/` or `inventory/`.

## Out of scope here

- Enabling the two policy sets (cutover, not this write)
- `ise_network_access_policy_set_update_rank`
- NAD resources
- `netascode/nac-ise`
- remote state
- a second environment folder
