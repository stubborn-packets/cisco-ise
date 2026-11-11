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
CONDITIONS_PATH = REPO_ROOT / "policy" / "conditions.yaml"
PROFILES_PATH = REPO_ROOT / "policy" / "authz-profiles.yaml"
VLANS_PATH = REPO_ROOT / "inventory" / "vlans.yaml"
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


def load_named(path: Path, key: str) -> dict[str, dict]:
    """Return a name → object map. Empty dict if the file is missing."""
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    items = data.get(key) or []
    return {item["name"]: item for item in items if isinstance(item, dict) and "name" in item}


def load_vlans(path: Path) -> dict[str, int]:
    """Return name → vlan_id. Empty dict if the file is missing."""
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    items = data.get("vlans") or []
    return {
        item["name"]: item["vlan_id"]
        for item in items
        if isinstance(item, dict) and "name" in item and "vlan_id" in item
    }


def render_condition(name: str, conditions: dict[str, dict], indent: str = "  ") -> list[str]:
    """Name plus a short readable form of the condition."""
    lines = [f"{indent}- **Condition:** `{name}`"]
    cnd = conditions.get(name)
    if not cnd:
        lines.append(f"{indent}  _(not found in conditions.yaml)_")
        return lines
    ctype = cnd.get("type", "")
    if ctype == "LibraryConditionAndBlock":
        lines[0] += " (AND)"
        for child in cnd.get("children") or []:
            if child.get("type") == "ConditionAttributes":
                lines.append(
                    f"{indent}  - {child.get('dictionary_name')} "
                    f"{child.get('attribute_name')} {child.get('operator')} "
                    f"{child.get('attribute_value')}"
                )
    elif ctype == "LibraryConditionAttributes":
        lines.append(
            f"{indent}  {cnd.get('dictionary_name')} "
            f"{cnd.get('attribute_name')} {cnd.get('operator')} "
            f"{cnd.get('attribute_value')}"
        )
    return lines


def render_profile(name: str, profiles: dict[str, dict], vlans: dict[str, int],
                  indent: str = "  ") -> list[str]:
    """Name plus the result fields that matter."""
    lines = [f"{indent}- **Profile:** `{name}`"]
    pr = profiles.get(name)
    if not pr:
        lines.append(f"{indent}  _(not found in authz-profiles.yaml)_")
        return lines
    parts = [pr.get("access_type", "ACCESS_ACCEPT")]
    if pr.get("vlan"):
        vlan_name = pr["vlan"]
        vlan_id = vlans.get(vlan_name)
        if vlan_id is not None:
            parts.append(f"VLAN {vlan_name} ({vlan_id})")
        else:
            parts.append(f"VLAN {vlan_name} (id not in inventory/vlans.yaml)")
    if pr.get("dacl"):
        parts.append(f"DACL {pr['dacl']}")
    if pr.get("asa_vpn"):
        parts.append(f"Class `{pr['asa_vpn']}`")
    if pr.get("reauth_timer"):
        conn = pr.get("reauth_connectivity", "")
        parts.append(f"reauth {pr['reauth_timer']} ({conn})")
    lines.append(f"{indent}  {', '.join(parts)}")
    return lines


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


def render_set(policy_set: dict, conditions: dict[str, dict], profiles: dict[str, dict],
               vlans: dict[str, int]) -> list[str]:
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
    ]
    lines.extend(render_condition(condition, conditions, indent=""))
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
            lines.append(f"#### {rule.get('name', '?')} (rank {rule.get('rank', '?')})")
            lines.append("")
            lines.extend(render_condition(rule.get("condition", ""), conditions, indent=""))
            lines.extend([
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
            lines.append(f"#### {rule.get('name', '?')} (rank {rule.get('rank', '?')})")
            lines.append("")
            lines.extend(render_condition(rule.get("condition", ""), conditions, indent=""))
            lines.extend(render_profile(rule.get("profile", ""), profiles, vlans, indent=""))
            lines.append("")

    lines.append("---")
    lines.append("")
    return lines


def render_report(policy_sets: list[dict], keyword: str | None,
                  conditions: dict[str, dict], profiles: dict[str, dict],
                  vlans: dict[str, int]) -> str:
    """Build the full Markdown document."""
    header = [
        "# Policy evaluation report",
        "",
        "Report-only view of owned Network Access policy sets.",
        "Rank 99 Default is not managed.",
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
        body.extend(render_set(ps, conditions, profiles, vlans))
    return "\n".join(header + body)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sets = load_policy_sets(POLICY_SETS_PATH)
    conditions = load_named(CONDITIONS_PATH, "conditions")
    profiles = load_named(PROFILES_PATH, "authorization_profiles")
    vlans = load_vlans(VLANS_PATH)
    if args.filter:
        sets = [s for s in sets if matches_filter(s, args.filter)]
    report = render_report(sets, args.filter, conditions, profiles, vlans)
    out = output_path(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
