# environments/lab

The **only** environment allowed to be a Terraform target through Phase 6.

Currently points at a home-lab ISE eval instance running on Proxmox — there
is no official work lab or non-prod ISE yet. Proving this out here is
intentional: it's the proof of concept used to request a real lab/non-prod
instance at work (see `docs/ROADMAP.md`, Phase 7's prerequisite). Never
points at production, and never at the eventual work non-prod either —
that's `environments/nonprod/`.

Nothing here yet. Phase 3 adds the Terraform provider configuration and
remote state backend for this environment.
