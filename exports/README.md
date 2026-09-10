# exports/

Observed state. Generated from a live ISE read (Phase 1+).

- Do not edit these files by hand.
- This is what ISE *has*, including non-standard GUI objects.
- `policy/` is what we *want*. Diff the two; do not merge them.
- `*.csv` is gitignored so a live dump cannot be committed by accident.
- If a report must be snapshotted for a change ticket, attach a copy to the PR.