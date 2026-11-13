# policy/

Desired state. YAML is the review surface. `scripts/read_policy.py` emits the lab calls from these files. Do not hand-edit the generated `.tf` files.

UUIDs do not belong here. Sets stay disabled. Enable is a cutover.

See `docs/file-map.md` for which file owns which family, and `docs/naming.md` for the prefix rules (including the SGT / ISS / CAP snake_case exceptions).