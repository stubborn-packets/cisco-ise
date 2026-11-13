# exports/

Observed state. Generated from a live ISE read.

- Do not edit these files by hand.
- This is what ISE *has*, including non-standard GUI objects.
- `policy/` is what we *want*. Diff the two; do not merge them.
- After Phase 14, CSVs land in `exports/<environment>/` (created on first use). `*.csv` is gitignored.
- If a report must be snapshotted for a change ticket, attach a copy to the PR.
- Drift (`scripts/drift.py`) and the import map also write or print under the same environment label. Neither runs in CI.