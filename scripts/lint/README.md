# scripts/lint

The naming-standard linter, built in Phase 2 against whatever ends up in
`docs/naming-standards.md`.

Planned shape (not yet built):
- A standalone Python script first, runnable by hand against either the
  Phase 1 export or a proposed new `policies/` YAML file.
- Once trustworthy, wired into `pre-commit` and into the Phase 4 CI job so
  every PR gets checked automatically.

Nothing here yet — depends on `docs/naming-standards.md` being filled in
first.
