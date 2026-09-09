# modules

Reusable Terraform modules live here — most likely a thin wrapper around
Cisco's [`nac-ise`](https://registry.terraform.io/modules/netascode/nac-ise/ise/latest)
module (see `docs/adr/0002-tech-stack-selection.md`), plus small
hand-written modules for anything `nac-ise` doesn't cover via the raw
[`CiscoDevNet/ise`](https://registry.terraform.io/providers/CiscoDevNet/ise/latest) provider.

Nothing here yet — first module arrives in Phase 3 as the "hello world"
proof against lab.
