# environments/prod

**Do not add a Terraform provider configuration here before Phase 8.**

This folder is intentionally empty. It exists now, at Phase 0, purely so
that "which environment does this touch" is a folder you have to
deliberately open and edit — not a default anything could fall into by
accident.

When Phase 8 starts, this environment gets populated **one object type at a
time**, each gated by a verified zero-diff `terraform import` (see
`docs/ROADMAP.md`). It is never a bulk `terraform apply` against everything
at once.
