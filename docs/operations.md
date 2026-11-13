# Operations

Nightly drift example and optional notification. Documentation only. No new Terraform resources. Sets stay disabled. Enable is a cutover, not this document.

`scripts/drift.py` is the GET-only name (and SGT tag) comparison. It covers every family `read_policy.py` emits. It does not write. It does not call Terraform. Terraform plan remains the authoritative detector for owned objects. See `docs/drift.md`.

Phase 14: the script accepts `--environment` / `-e` (`lab`, `stage`, or `prod`; default `lab`). Credentials are read only as `<ENV>_ISE_URL`, `<ENV>_ISE_USERNAME`, `<ENV>_ISE_PASSWORD`, `<ENV>_ISE_INSECURE`. There is no fallback to plain `ISE_*`. Exports write under `exports/<environment>/`. The reader emits under `environments/<label>/` only when that directory already exists. CI stays on `environments/lab`. Still one write target.

## Credentials after Phase 14

Terraform (CiscoDevNet/ise) still reads the plain names. The empty provider block in `environments/lab/providers.tf` depends on them:

- `ISE_URL`
- `ISE_USERNAME`
- `ISE_PASSWORD`
- `ISE_INSECURE`

The scripts (`export_ise.py`, `drift.py`, `import_map.py`) read the environment-specific names when `--environment` is used:

- `LAB_ISE_URL`
- `LAB_ISE_USERNAME`
- `LAB_ISE_PASSWORD`
- `LAB_ISE_INSECURE`

(and the same pattern for `STAGE_` / `PROD_` if those directories are ever created).

Keep both. The one-line mapping that lets a single `.env` satisfy both is:

```bash
# in .env (never commit)
LAB_ISE_URL=https://ise.lab.example
LAB_ISE_USERNAME=ers-admin
LAB_ISE_PASSWORD=...
LAB_ISE_INSECURE=true

# plain names for Terraform (same values)
ISE_URL=${LAB_ISE_URL}
ISE_USERNAME=${LAB_ISE_USERNAME}
ISE_PASSWORD=${LAB_ISE_PASSWORD}
ISE_INSECURE=${LAB_ISE_INSECURE}
```

Or, before a Terraform command 

```bash
export ISE_URL="$LAB_ISE_URL"
export ISE_USERNAME="$LAB_ISE_USERNAME"
export ISE_PASSWORD="$LAB_ISE_PASSWORD"
export ISE_INSECURE="$LAB_ISE_INSECURE"
cd environments/lab
terraform plan
```

Do not change the provider block. Do not add Terraform variables for the URL or password. The plain names stay the ones the provider already looks for.

That keeps the empty `provider "ise" {}` working and gives the scripts the prefixed form Phase 14 described. If the real Phase 14 scripts still fall back to plain `ISE_*` when the prefixed variables are unset, the mapping is optional; if they do not fall back, the mapping is required for Terraform.

## Local run

From the repo root, with the matching environment variables already exported:

```bash
python3.12 scripts/drift.py --environment lab
```

A clean run prints no unexpected names. Non-owned remainder is expected (old GUI sets, objects never imported, names listed in `policy/system-exclusions.yaml`). Do not import them to empty the report.

## Nightly example — cron

```cron
# /etc/cron.d/ise-drift (or user crontab)
# Adjust paths and the environment label. Secrets stay in the environment, not in the crontab.
0 2 * * * cd /path/to/cisco-ise && \
  LAB_ISE_URL=... LAB_ISE_USERNAME=... LAB_ISE_PASSWORD=... LAB_ISE_INSECURE=true \
  python3.12 scripts/drift.py --environment lab \
  > /var/log/ise-drift.log 2>&1
```

The job must not be run from CI. CI never loads secrets and never talks to ISE.

## Nightly example — systemd timer

```ini
[Unit]
Description=Nightly ISE drift

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`/etc/ise/lab.env` holds only the four `LAB_ISE_*` keys. It is not committed.

## Nightly example — GitHub Actions (optional)

A scheduled workflow can call the same script if the repository is private and the four secrets are stored as Actions secrets. It must not be the promotion CI. The existing `.github/workflows/ci`.yml stays secret-free and does not run drift.

```yaml
# .github/workflows/nightly-drift.yml (example only; do not merge into ci.yml)
name: nightly-drift
on:
  schedule:
    - cron: "0 2 * * *"
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - env:
          LAB_ISE_URL: ${{ secrets.LAB_ISE_URL }}
          LAB_ISE_USERNAME: ${{ secrets.LAB_ISE_USERNAME }}
          LAB_ISE_PASSWORD: ${{ secrets.LAB_ISE_PASSWORD }}
          LAB_ISE_INSECURE: ${{ secrets.LAB_ISE_INSECURE }}
        run: python3.12 scripts/drift.py --environment lab
```

## Optional notification

If the script exits non-zero or prints a non-owned remainder, the same job can mail or post a short summary. The check itself stays GET-only. Do not fail the promotion path on non-owned names. A typical pattern:

```bash
python3.12 scripts/drift.py --environment lab > /tmp/drift.out 2>&1 || true
if grep -q "non-owned\|unexpected" /tmp/drift.out; then
  mail -s "ISE lab non-owned objects" ops@example.com < /tmp/drift.out
fi
```

Adjust the grep to the actual output format of the script. The point is visibility, not enforcement. Owned drift is still detected by `terraform plan` under `environments/lab`.

## What this does not do

- Does not enable a policy set.
- Does not import old GUI sets.
- Does not manage rank 99 Default or Default Network Access.
- Does not put UUIDs in `policy/` or `inventory/`.
- Does not create `environments/stage/` or `prod/`.