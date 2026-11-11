#!/usr/bin/env python3.12
"""Report-only view of owned Network Access policy.

Reads policy/policy-sets.yaml and writes a Markdown evaluation report.
No ISE connection. No UUIDs. Sets stay disabled.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. It is already in the repo requirements.", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_SETS_PATH = REPO_ROOT / "policy" / "policy-sets.yaml"
REPORTS_DIR = REPO_ROOT / "reports"

def load_policy_sets(path: Path) -> list[dict]:
    """Load and return the policy_sets list. Fail hard on missing or empty data."""
    if not path.is_file():
        print(f"policy sets file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    sets = data.get("policy_sets")
    if not isinstance(sets, list):
        print("policy/policy-sets.yaml has no policy_sets list", file=sys.stderr)
        sys.exit(1)
    return sets


def matches_filter(policy_set: dict, keyword: str) -> bool:
    """True if name, band, or description contains the keyword (case-insensitive)."""
    if not keyword:
        return True
    needle = keyword.lower()
    for field in ("name", "band", "description"):
        value = policy_set.get(field) or ""
        if needle in str(value).lower():
            return True
    return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a Markdown report of owned policy sets, conditions, and rules."
    )
    parser.add_argument(
        "--filter",
        metavar="KEYWORD",
        help="Only include sets whose name, band, or description contains KEYWORD "
             "(case-insensitive). Writes reports/policy-evaluation-KEYWORD.md",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Override the output path (default depends on --filter).",
    )
    return parser.parse_args(argv)


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    if args.filter:
        safe = args.filter.lower().replace(" ", "-")
        return REPORTS_DIR / f"policy-evaluation-{safe}.md"
    return REPORTS_DIR / "policy-evaluation.md"


def render_set(policy_set: dict) -> list[str]:
    """Return Markdown lines for one policy set."""
    name = policy_set.get("name", "?")
    rank = policy_set.get("rank", "?")
    band = policy_set.get("band", "")
    state = policy_set.get("state", "")
    service = policy_set.get("service", "")
    condition = policy_set.get("condition", "")
    description = policy_set.get("description", "")

    lines = [
        f"## {rank} — {name}",
        "",
        f"- **Band:** {band}",
        f"- **State:** {state}",
        f"- **Service:** {service}",
        f"- **Set condition:** {condition}",
    ]
    if description:
        lines.append(f"- **Description:** {description}")
    lines.append("")

    # Authentication rules
    lines.append("### Authentication rules")
    lines.append("")
    an_rules = policy_set.get("authentication_rules") or []
    if not an_rules:
        lines.append("_None._")
        lines.append("")
    else:
        for rule in an_rules:
            lines.extend([
                f"#### {rule.get('name', '?')} (rank {rule.get('rank', '?')})",
                "",
                f"- Condition: {rule.get('condition', '')}",
                f"- Identity source: {rule.get('identity_source', '')}",
                f"- if_auth_fail: {rule.get('if_auth_fail', '')}",
                f"- if_process_fail: {rule.get('if_process_fail', '')}",
                f"- if_user_not_found: {rule.get('if_user_not_found', '')}",
                "",
            ])

    # Authorization rules
    lines.append("### Authorization rules")
    lines.append("")
    az_rules = policy_set.get("authorization_rules") or []
    if not az_rules:
        lines.append("_None._")
        lines.append("")
    else:
        for rule in az_rules:
            lines.extend([
                f"#### {rule.get('name', '?')} (rank {rule.get('rank', '?')})",
                "",
                f"- Condition: {rule.get('condition', '')}",
                f"- Profile: {rule.get('profile', '')}",
                "",
            ])

    lines.append("---")
    lines.append("")
    return lines


def render_report(policy_sets: list[dict], keyword: str | None) -> str:
    """Build the full Markdown document."""
    header = [
        "# Policy evaluation report",
        "",
        "Report-only view of owned Network Access policy sets.",
        "Sets stay disabled. Rank 99 Default is not managed.",
        "Generated from `policy/policy-sets.yaml`. No ISE connection.",
        "",
    ]
    if keyword:
        header.append(f"**Filter:** sets matching `{keyword}`")
        header.append("")
    header.append(f"**Sets shown:** {len(policy_sets)}")
    header.append("")

    if not policy_sets:
        header.append("_No policy sets matched the filter._")
        header.append("")
        return "\n".join(header)

    body: list[str] = []
    for ps in sorted(policy_sets, key=lambda s: s.get("rank", 999)):
        body.extend(render_set(ps))
    return "\n".join(header + body)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sets = load_policy_sets(POLICY_SETS_PATH)
    if args.filter:
        sets = [s for s in sets if matches_filter(s, args.filter)]
    report = render_report(sets, args.filter)
    out = output_path(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())