# 0001 — Record architecture decisions

## Status
Accepted

## Context
This project will be built incrementally, one phase/feature at a time, over
a long period. Decisions made early (tech stack, workflow, structure) need
to stay legible to whoever revisits them later — including Josh, months from
now, without this conversation in front of him.

## Decision
We keep lightweight Architecture Decision Records (ADRs) under `docs/adr/`.
Each one is numbered, immutable once accepted (a changed decision gets a
*new* ADR that supersedes the old one, rather than an edit), and answers:
what was decided, what else was considered, and why this option won.

## Consequences
- Every non-trivial choice in this repo should be traceable to an ADR.
- ADRs are short. They record the *why*, not a tutorial on the *how* — the
  README and phase docs cover how to actually use things.
