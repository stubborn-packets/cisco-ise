# Roadmap

Each phase is a single, self-contained step. We do not start a phase until
the previous one's exit criteria are met and you've said go. Phases 0–6 never
touch production ISE. Phase 8 is the only phase that does, and it does so one
object type at a time, never wholesale.

## Phase 0 — Foundations & Guardrails *(this delivery)*

**Goal:** Repo scaffold, roadmap, ADRs, and a naming-standards placeholder,
with environment folders that make "which ISE am I touching" an explicit,
visible choice rather than an assumption.

**Exit criteria:** You can clone this, understand the layout without
explanation, and know what Phase 1 will build.

## Phase 1 — Discovery & Baseline Export (read-only)

**Goal:** Export your *current* production ISE configuration, read-only,
into structured, version-controlled data (YAML/JSON) — the "ground truth"
snapshot everything else gets checked against. Python (`ciscoisesdk`) does
the heavy lifting; Ansible (`cisco.ise` collection) fills in anywhere the SDK
doesn't have a clean read call.

**Exit criteria:** Every in-scope object type has a version-controlled
export. Zero write calls made anywhere. Git history shows exactly one
commit per export run, so drift over time is visible.

## Phase 2 — Naming-Standard Linter

**Goal:** A standalone script that checks a policy object's proposed name
against your naming convention (from `docs/naming-standards.md`). Runs
on its own first; gets wired into `pre-commit` once it's trustworthy.

**Exit criteria:** The linter passes on the Phase 1 baseline (or explicitly
documents legacy exceptions) and fails a set of intentionally-bad test
names you write together with it.

## Phase 3 — Lab Terraform Foundation

**Goal:** Stand up Terraform against a **lab-only** ISE instance — provider
authentication, a remote state backend, and one trivial resource (e.g. a
single Network Device Group) applied and then destroyed, to prove the
plumbing end to end.

There's no official lab or non-prod ISE yet, and this whole project is
partly a proof of concept to get one approved. So "lab" here means an ISE
eval instance run at home, on Proxmox — good enough to prove the pattern
works, not a stand-in for real non-prod data. Once this phase (and ideally
5–6) works cleanly against the home lab, that becomes the evidence used to
request an actual ISE lab/non-prod instance at work, which is what Phase 7
then targets. Keep the eval license's time limit in mind when sequencing
Phases 3–6 — re-deploying the eval instance mid-sequence is a possibility
worth planning around, not a blocker.

**Exit criteria:** `terraform plan` / `apply` / `destroy` all work cleanly
against the home lab. This phase never points at anything but that lab.

## Phase 4 — Git Workflow & CI Gate

**Goal:** Branch protection + required PR approval on `main` (configured in
your Git host), plus a CI job that runs `terraform fmt -check`,
`terraform validate`, and the Phase 2 linter on every PR, posting the
`terraform plan` output for human review. Apply stays manual, lab-only.

**Exit criteria:** A PR cannot merge without passing lint + plan and getting
a human approval — the review step you already require becomes real, not
just policy.

## Phase 5 — Pilot Object Import (Lab)

**Goal:** Pick the single lowest-risk object type. Hand-write its Terraform
config to match the lab export exactly, `terraform import` it, and confirm
`terraform plan` shows **zero diff**.

**Exit criteria:** One object type is fully Terraform-managed in lab, with a
proven zero-diff import — the pattern every later object type and every
later environment will repeat.

## Phase 6 — Automated Apply + Drift Detection (Lab)

**Goal:** CI applies automatically on merge to `main`, targeting lab only.
A separate scheduled job runs `terraform plan` (never apply) against lab and
alerts if it finds unexpected drift.

**Exit criteria:** The pipeline has run unattended long enough, and caught
enough drift correctly, that you trust it before it ever points at anything
real.

## Phase 7 — Non-Prod Rollout

**Prerequisite:** an actual non-prod/lab ISE instance at work has been
requested and granted — using the home-lab results from Phases 3–6 as the
evidence for that request.

**Goal:** Repeat Phases 5–6 against the non-prod ISE instance with real
(non-production) data, expanding coverage to a few more object types.

**Exit criteria:** Non-prod is mostly or fully Terraform-managed, and the
process (export → author → import → zero-diff check → automate) is
documented well enough to repeat without re-deriving it.

## Phase 8 — Production Migration (Phased, Per Object Type)

**Goal:** For each in-scope object type, in increasing order of risk:
export → write matching Terraform → `terraform import` → verify **zero
diff** → freeze manual edits to that object type in the ISE GUI → only then
allow Terraform-driven changes to it. One object type at a time. A failed
zero-diff check stops that object type's migration — it does not roll
forward.

**Exit criteria:** All in-scope object types are migrated, one at a time,
with production never touched by anything except verified zero-diff
imports until this phase — and even then, never in bulk.

## Phase 9 — Full Ownership & Steady State

**Goal:** Manual ISE GUI changes to migrated objects are treated as
incidents, not a parallel path. All policy changes flow through a PR.
Naming-standard and drift audits run on a schedule.

**Exit criteria:** Policy-as-code is simply how policy changes happen —
not a special case running alongside the old way.
