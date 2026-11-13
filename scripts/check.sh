#!/usr/bin/env bash
# Secret-free promotion checks. Mirror of .github/workflows/ci.yml.
# Run from the repo root. Does not load .env or talk to ISE.
#
# Usage:
#   bash scripts/check.sh          # validates environments/lab
#   bash scripts/check.sh stage    # validates environments/stage (when it exists)

set -euo pipefail

ENVIRONMENT="${1:-lab}"
case "$ENVIRONMENT" in
  lab|stage|prod) ;;
  *)
    echo "unknown environment: $ENVIRONMENT" >&2
    echo "choose one of: lab stage prod" >&2
    exit 1
    ;;
esac

ENV_DIR="environments/$ENVIRONMENT"
if [[ ! -d "$ENV_DIR" ]]; then
  echo "$ENV_DIR does not exist. Create it only when a second ISE is ready." >&2
  exit 1
fi

cd "$(dirname "$0")/.."

echo "=== lint_ise.py ==="
python3.12 scripts/lint_ise.py

echo "=== unit tests ==="
python3.12 -m unittest tests.lint.test_lint_ise

echo "=== terraform fmt ==="
terraform fmt -check -recursive

echo "=== terraform init + validate ($ENVIRONMENT) ==="
cd "$ENV_DIR"
terraform init -backend=false
terraform validate

echo "=== check.sh: ok ($ENVIRONMENT) ==="