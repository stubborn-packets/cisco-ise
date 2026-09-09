# 0002 — Tech stack selection

## Status
Accepted

## Context
The goal is "Terraform as much as possible," with Python and Ansible where
needed — specifically for exporting current ISE data. Cisco publishes
several tools in this space; this ADR records which ones we're standardizing
on and why, so the choice doesn't get silently re-litigated in a later
phase.

## Decision

**Primary: [Cisco Network-as-Code `nac-ise` Terraform module](https://registry.terraform.io/modules/netascode/nac-ise/ise/latest)**
(built on top of the [`CiscoDevNet/ise` provider](https://registry.terraform.io/providers/CiscoDevNet/ise/latest)).
`nac-ise` follows Cisco's "Network as Code" pattern: policy objects are
described as **YAML data**, and the module turns that data into Terraform
resources — you don't hand-write HCL per object. This matters directly for
your naming-standard requirement: the linter (Phase 2) can validate the YAML
*before* Terraform ever runs, instead of trying to lint generated HCL or
live ISE state.

**Fallback: raw [`CiscoDevNet/ise` provider](https://registry.terraform.io/providers/CiscoDevNet/ise/latest) resources**,
for any object type `nac-ise` doesn't model yet. Same provider underneath,
just used directly instead of through the YAML layer.

**Export tooling (Phase 1, read-only): Python with Cisco's official
[`ciscoisesdk`](https://github.com/CiscoISE/ciscoisesdk) SDK** as the
primary tool, since it wraps ISE's REST APIs (ERS and the newer Open APIs)
in a way that's straightforward to script against — and it's the language
you're already comfortable with from network engineering work.

**Ansible (the [`cisco.ise`](https://github.com/CiscoISE/ansible-ise)
collection): used only where the SDK/Terraform path doesn't cleanly cover a
resource.** This keeps Ansible in its stated role — a gap-filler — rather
than a second, competing way to manage the same objects.

**Secrets management: your existing HashiCorp Vault setup**, rather than a
new pattern for this project. Terraform, Python, and Ansible all have
established Vault integrations, so this plugs into infrastructure you
already run.

**Git workflow: PR-based, with required review before merge to `main`**,
matching your org's existing requirement — enforced via branch protection
settings on your Git host, not via code in this repo.

## Alternatives considered

- **Hand-written Terraform HCL per policy object**, no `nac-ise` layer.
  Rejected as primary approach because it couples the naming linter to HCL
  parsing (or to live ISE API responses) instead of a simple YAML file —
  more brittle, and the data/code split `nac-ise` gives us "for free" is a
  better fit for how often policy objects actually change day to day. Kept
  as the fallback for coverage gaps.
- **Ansible as the primary configuration tool**, Terraform secondary.
  Rejected — you explicitly want Terraform-first, and Terraform's state
  model fits "detect drift, plan before apply" better than Ansible's
  imperative-by-default model for this use case.

## Consequences
- Everything after Phase 3 assumes policy objects are represented as YAML
  consumed by `nac-ise` (or, as a fallback, a `modules/` wrapper around the
  raw provider) — not hand-authored `.tf` files per object.
- If `nac-ise`'s coverage or maintenance status changes materially before
  we get there, that's worth a superseding ADR before Phase 3, not a silent
  swap.
