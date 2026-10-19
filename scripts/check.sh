#!/usr/bin/env bash
# Secret-free promotion checks. Mirror of .github/workflows/ci.yml.
# Run from the repo root. Does not load .env or talk to ISE.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== lint_ise.py ==="
python3.12 scripts/lint_ise.py

echo "=== unit tests ==="
python3.12 -m unittest tests.lint.test_lint_ise

echo "=== terraform fmt ==="
terraform fmt -check -recursive

echo "=== terraform init + validate ==="
cd environments/lab
terraform init -backend=false
terraform validate

echo "=== check.sh: ok ==="