# scripts/export

Read-only tooling that pulls your **current** ISE configuration into
version-controlled YAML/JSON — the Phase 1 baseline everything else gets
compared against.

Planned approach (built in Phase 1, not yet):
- Python using Cisco's official [`ciscoisesdk`](https://github.com/CiscoISE/ciscoisesdk)
  for anything the SDK covers cleanly.
- The [`cisco.ise`](https://github.com/CiscoISE/ansible-ise) Ansible
  collection as a fallback only where the SDK doesn't have a clean read
  call for a given object type.
- Exports write to `scripts/export/output/` (git-ignored — see repo-root
  `.gitignore`) until reviewed, then get committed intentionally as the
  baseline snapshot.

**No write/update/delete calls belong in this directory, ever** — export
only.

Nothing here yet.
