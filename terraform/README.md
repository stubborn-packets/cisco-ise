# terraform/

Reusable write modules. They do not know which ISE they talk to.

The root that may apply them is `environments/lab/` only. There is no
`environments/stage/` or `prod/` in this repo.

## Layout

```text
terraform/modules/sgt/     one ise_trustsec_security_group
environments/lab/          provider pin, local state, module call
```

Phase 3 object lives in `environments/lab/terraform.tfvars`, not in
`policy/sgt.yaml`. That YAML stays an empty scaffold until Phase 4.

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
| ISE name | `SGT-lab-bootstrap` |
| Tag | `1001` |
| GUI | Work Centers > TrustSec > Components > Security Groups |

Do not import an existing non-standard lab SGT as this address.
Do not put the UUID from `terraform output sgt_id` into `policy/` or
`inventory/`.

## Out of scope here

- NAD resources
- `netascode/nac-ise`
- remote state
- a second environment folder
