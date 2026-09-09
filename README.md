# ISE Policy-as-Code

Migrating an existing, in-production Cisco ISE deployment to policy-as-code —
without ever putting that production deployment at risk.

## How to read this repo right now

This is **Phase 0: Foundations & Guardrails**. Nothing in here talks to ISE
yet — there is no Terraform provider config, no working scripts, no CI
pipeline. This phase is scaffolding and decisions only, so that every phase
after it has a clear place to land.

Start here:

1. [`docs/ROADMAP.md`](docs/ROADMAP.md) — the full phased plan, in order,
   with an exit criteria for each phase. **We build one phase at a time.**
   This repo currently implements Phase 0 only.
2. [`docs/adr/`](docs/adr/) — architecture decision records: the *why*
   behind each significant choice (tech stack, workflow), not just the
   *what*. Read `0001` first (why we keep ADRs at all), then `0002` (why
   this tech stack).
3. [`docs/naming-standards.md`](docs/naming-standards.md) — placeholder for
   your naming convention. This gets filled in before Phase 2 (the linter)
   is built.

## Layout

| Path | Purpose | Populated in |
|---|---|---|
| `environments/lab/` | Sandbox/CML ISE — safe to break, first target for everything | Phase 3+ |
| `environments/nonprod/` | Non-production ISE — real-ish data, still not production | Phase 7 |
| `environments/prod/` | Your production ISE — **inert until Phase 8**, and even then one object type at a time | Phase 8+ |
| `modules/` | Reusable Terraform modules (or wrappers around Cisco's `nac-ise` module) | Phase 3+ |
| `policies/` | Policy objects as data (YAML), the thing you'll actually edit day to day | Phase 5+ |
| `scripts/export/` | Read-only export tooling (Python/Ansible) that pulls current ISE state into version control | Phase 1 |
| `scripts/lint/` | The naming-standard linter | Phase 2 |
| `docs/` | Roadmap, ADRs, naming standards, and anything else durable | ongoing |

## Guardrails baked into this structure

- **Environment separation is physical, not just logical.** `environments/prod/`
  exists as an empty, documented placeholder specifically so that later
  phases have to deliberately opt in to touching it — there's no shared
  "default" environment a mistake could fall into.
- **Data lives apart from code.** Policy objects will be described as YAML
  in `policies/`, consumed by Terraform modules in `modules/` — not
  hand-written HCL per object. This is what makes the naming-standard
  linter possible: it lints the YAML *before* Terraform ever runs.
- **Nothing merges without review.** This repo assumes branch protection +
  required PR approval on `main` (configured in your Git host's settings,
  not in code) from the start, per your existing workflow.

## What's next

Once you've cloned this locally and reviewed the roadmap and ADRs, the next
step (Phase 1) is a read-only export of your current ISE configuration —
no writes, nothing that can affect production. We'll build that as its own
single step when you're ready.
