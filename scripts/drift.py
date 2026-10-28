#!/usr/bin/env python3
"""Phase 9 drift: GET-only comparison of policy/ against live ISE.

Covers every family scripts/read_policy.py emits.
Does not write to ISE. Does not call Terraform. UUIDs stay out of the report.

Usage (from the repo root):

    python3.12 scripts/drift.py

Requires the same ISE_* environment as scripts/import_map.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ise_client import IseClient, load_client
from read_policy import derive_ndg_objects, load_ndg_roots

# --- paths -----------------------------------------------------------------

SGT_PATH = "/ers/config/sgt"
SGT_YAML = "policy/sgt.yaml"
SGT_KEY = "sgts"

EIG_PATH = "/ers/config/endpointgroup"
EIG_YAML = "policy/eig.yaml"
EIG_KEY = "endpoint_identity_groups"

DACL_PATH = "/ers/config/downloadableacl"
DACL_YAML = "policy/authz-profiles.yaml"
DACL_KEY = "downloadable_acls"

AP_PATH = "/ers/config/allowedprotocols"
AP_YAML = "policy/allowed-protocols.yaml"
AP_KEY = "allowed_protocols"

PR_PATH = "/ers/config/authorizationprofile"
PR_YAML = "policy/authz-profiles.yaml"
PR_KEY = "authorization_profiles"

CND_PATH = "/api/v1/policy/network-access/condition"
CND_YAML = "policy/conditions.yaml"
CND_KEY = "conditions"

PS_PATH = "/api/v1/policy/network-access/policy-set"
PS_YAML = "policy/policy-sets.yaml"
PS_KEY = "policy_sets"

NDG_PATH = "/ers/config/networkdevicegroup"

EX_YAML = "policy/exceptions.yaml"
EX_KEY = "exceptions"
GLOBAL_EXCEPTION_PATH = "/api/v1/policy/network-access/policy-set/global-exception"

EXCLUSIONS_YAML = "policy/system-exclusions.yaml"

# Built-ins we never treat as owned or as unexpected non-owned.
ALWAYS_IGNORE = {"Default", "Default Network Access"}


def load_rows(root: Path, rel: str, key: str) -> list[dict[str, Any]]:
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"{rel} is missing")
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        raise SystemExit(f"{rel} is not a mapping")
    rows = doc.get(key)
    if not isinstance(rows, list):
        raise SystemExit(f"{key} must be a list")
    return rows


def load_exclusions(root: Path) -> dict[str, set[str]]:
    """family label → set of names to hide from the non-owned report."""
    path = root / EXCLUSIONS_YAML
    if not path.is_file():
        raise SystemExit(f"{EXCLUSIONS_YAML} is missing")
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(doc, dict):
        raise SystemExit(f"{EXCLUSIONS_YAML} is not a mapping")
    out: dict[str, set[str]] = {}
    for family, names in doc.items():
        if not isinstance(names, list):
            raise SystemExit(f"{family} must be a list of names")
        out[family] = {n for n in names if isinstance(n, str) and n}
    return out


def names_only(rows: list[dict[str, Any]], rel: str) -> dict[str, None]:
    """name → None. Used by every family that is name-only."""
    out: dict[str, None] = {}
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"{rel} row missing name: {row!r}")
        out[name] = None
    return out


def desired_sgts(rows: list[dict[str, Any]]) -> dict[str, int]:
    """name → tag value. SGTs are the only family that compares an attribute."""
    out: dict[str, int] = {}
    for row in rows:
        name = row.get("name")
        value = row.get("value")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"{SGT_YAML} row missing name: {row!r}")
        if not isinstance(value, int):
            raise SystemExit(f"{name} value must be an int: {value!r}")
        out[name] = value
    return out


def live_ers_names(client: IseClient, path: str) -> dict[str, None]:
    out: dict[str, None] = {}
    for item in client.get_ers_pages(path):
        name = item.get("name")
        if isinstance(name, str) and name:
            out[name] = None
    return out


def live_openapi_names(client: IseClient, path: str) -> dict[str, None]:
    out: dict[str, None] = {}
    for item in client.get_openapi_pages(path):
        name = item.get("name")
        if isinstance(name, str) and name:
            out[name] = None
    return out


def live_sgts(client: IseClient) -> dict[str, int]:
    """name → tag. Value is on the detail object, not the list."""
    out: dict[str, int] = {}
    for item in client.get_ers_pages(SGT_PATH):
        name = item.get("name")
        uid = item.get("id")
        if not isinstance(name, str) or not name or not isinstance(uid, str):
            continue
        try:
            raw = client.get(f"{SGT_PATH}/{uid}")
        except FileNotFoundError:
            continue
        body = raw.get("Sgt") or raw.get("sgt") or raw
        value = body.get("value")
        if isinstance(value, int):
            out[name] = value
    return out


def live_rules(
    client: IseClient,
    set_ids: dict[str, str],
    kind: str,
) -> dict[str, None]:
    """rule display key → None. Key is 'parent-set | rule-name'."""
    out: dict[str, None] = {}
    for parent_name, set_id in set_ids.items():
        if not set_id or parent_name in ALWAYS_IGNORE:
            continue
        child = f"{PS_PATH}/{set_id}/{kind}"
        try:
            items = client.get_openapi_pages(child)
        except FileNotFoundError:
            continue
        for item in items:
            inner = item.get("rule") or item
            name = inner.get("name") or item.get("name")
            if isinstance(name, str) and name and name != "Default":
                out[f"{parent_name} | {name}"] = None
    return out


def live_exceptions(
    client: IseClient,
    set_ids: dict[str, str],
) -> dict[str, None]:
    """Local exceptions under each set plus the global exception list.

    Local key is 'parent-set | name'. Global key is 'global | name'.
    """
    out: dict[str, None] = {}
    for parent_name, set_id in set_ids.items():
        if not set_id or parent_name in ALWAYS_IGNORE:
            continue
        child = f"{PS_PATH}/{set_id}/exception"
        try:
            items = client.get_openapi_pages(child)
        except FileNotFoundError:
            continue
        for item in items:
            inner = item.get("rule") or item
            name = inner.get("name") or item.get("name")
            if isinstance(name, str) and name:
                out[f"{parent_name} | {name}"] = None
    try:
        for item in client.get_openapi_pages(GLOBAL_EXCEPTION_PATH):
            inner = item.get("rule") or item
            name = inner.get("name") or item.get("name")
            if isinstance(name, str) and name:
                out[f"global | {name}"] = None
    except FileNotFoundError:
        pass
    return out


def desired_rules(sets: list[dict[str, Any]], yaml_key: str) -> dict[str, None]:
    """rule display key → None. Key is 'parent-set | rule-name'."""
    out: dict[str, None] = {}
    for parent in sets:
        parent_name = parent.get("name")
        if not isinstance(parent_name, str) or not parent_name:
            continue
        rules = parent.get(yaml_key) or []
        if not isinstance(rules, list):
            continue
        for rule in rules:
            name = rule.get("name")
            if isinstance(name, str) and name:
                out[f"{parent_name} | {name}"] = None
    return out


def desired_exceptions(rows: list[dict[str, Any]]) -> dict[str, None]:
    """Local key is 'policy_set | name'. Global key is 'global | name'."""
    out: dict[str, None] = {}
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"{EX_YAML} row missing name: {row!r}")
        parent = row.get("policy_set")
        if isinstance(parent, str) and parent:
            out[f"{parent} | {name}"] = None
        else:
            out[f"global | {name}"] = None
    return out


def desired_ndg(root: Path) -> dict[str, None]:
    objects = derive_ndg_objects(load_ndg_roots(root))
    return {obj["name"]: None for obj in objects}


def report_family(
    label: str,
    desired: dict[str, Any],
    live: dict[str, Any],
    prefix: str,
    exclusions: set[str],
) -> bool:
    """Print missing, extra (prefix only), value mismatches, and non-owned remainder.

    Return True only when owned is clean and the non-owned list is empty.
    Names in ALWAYS_IGNORE are dropped from both extra and non-owned.
    """
    live_owned = {n: v for n, v in live.items() if n not in ALWAYS_IGNORE}
    missing = sorted(set(desired) - set(live_owned))
    extra = sorted(
        name
        for name in set(live_owned) - set(desired)
        if (name.split(" | ")[-1] if " | " in name else name).startswith(prefix)
    )
    mismatched = sorted(
        name
        for name in set(desired) & set(live_owned)
        if desired[name] != live_owned[name]
    )
    non_owned = sorted(
        name
        for name in set(live) - set(desired)
        if not (name.split(" | ")[-1] if " | " in name else name).startswith(prefix)
        and name not in exclusions
        and name not in ALWAYS_IGNORE
    )

    print(f"{label} drift")
    print(f"  desired: {len(desired)}")
    print(f"  live:    {len(live)}")
    owned_clean = not missing and not extra and not mismatched
    if owned_clean:
        print("  owned clean")
    else:
        for name in missing:
            print(f"  missing on ISE: {name} (YAML {desired[name]!r})")
        for name in extra:
            print(f"  extra on ISE:   {name} (live {live[name]!r})")
        for name in mismatched:
            print(
                f"  value mismatch: {name} "
                f"YAML {desired[name]!r} live {live[name]!r}"
            )
    excluded = len(
        [
            n
            for n in set(live) - set(desired)
            if not (n.split(" | ")[-1] if " | " in n else n).startswith(prefix)
            and n in exclusions
        ]
    )
    print(f"  non-owned (excluded {excluded} system):")
    if non_owned:
        for name in non_owned:
            print(f"    {name}")
    else:
        print("    (none)")
    return owned_clean and not non_owned


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    client = load_client(root)
    exclusions = load_exclusions(root)

    results: list[bool] = []

    # SGTs (attribute)
    sgt_desired = desired_sgts(load_rows(root, SGT_YAML, SGT_KEY))
    sgt_live = live_sgts(client)
    results.append(
        report_family("SGT", sgt_desired, sgt_live, "SGT_", exclusions.get("SGT", set()))
    )

    # EIGs
    eig_desired = names_only(load_rows(root, EIG_YAML, EIG_KEY), EIG_YAML)
    eig_live = live_ers_names(client, EIG_PATH)
    results.append(
        report_family("EIG", eig_desired, eig_live, "EIG-", exclusions.get("EIG", set()))
    )

    # DACLs
    dacl_desired = names_only(load_rows(root, DACL_YAML, DACL_KEY), DACL_YAML)
    dacl_live = live_ers_names(client, DACL_PATH)
    results.append(
        report_family("DACL", dacl_desired, dacl_live, "ACL-", exclusions.get("DACL", set()))
    )

    # Allowed protocols
    ap_desired = names_only(load_rows(root, AP_YAML, AP_KEY), AP_YAML)
    ap_live = live_ers_names(client, AP_PATH)
    results.append(
        report_family("AP", ap_desired, ap_live, "AP-", exclusions.get("AP", set()))
    )

    # Authorization profiles
    pr_desired = names_only(load_rows(root, PR_YAML, PR_KEY), PR_YAML)
    pr_live = live_ers_names(client, PR_PATH)
    results.append(
        report_family("PR", pr_desired, pr_live, "PR-", exclusions.get("PR", set()))
    )

    # Conditions (OpenAPI)
    cnd_desired = names_only(load_rows(root, CND_YAML, CND_KEY), CND_YAML)
    cnd_live = live_openapi_names(client, CND_PATH)
    results.append(
        report_family("CND", cnd_desired, cnd_live, "CND-", exclusions.get("CND", set()))
    )

    # Policy sets (OpenAPI). Default is ignored via ALWAYS_IGNORE.
    ps_rows = load_rows(root, PS_YAML, PS_KEY)
    ps_desired = names_only(ps_rows, PS_YAML)
    ps_live = live_openapi_names(client, PS_PATH)
    results.append(
        report_family("PS", ps_desired, ps_live, "PS-", exclusions.get("PS", set()))
    )

    # Policy-set id map for nested families.
    set_ids: dict[str, str] = {}
    for item in client.get_openapi_pages(PS_PATH):
        name = item.get("name")
        uid = item.get("id")
        if isinstance(name, str) and isinstance(uid, str) and name and uid:
            set_ids[name] = uid

    # Authentication rules
    an_desired = desired_rules(ps_rows, "authentication_rules")
    an_live = live_rules(client, set_ids, "authentication")
    results.append(
        report_family("AN", an_desired, an_live, "AN-", exclusions.get("AN", set()))
    )

    # Authorization rules
    az_desired = desired_rules(ps_rows, "authorization_rules")
    az_live = live_rules(client, set_ids, "authorization")
    results.append(
        report_family("AZ", az_desired, az_live, "AZ-", exclusions.get("AZ", set()))
    )

    # Exceptions (local + global)
    ex_desired = desired_exceptions(load_rows(root, EX_YAML, EX_KEY))
    ex_live = live_exceptions(client, set_ids)
    results.append(
        report_family("EX", ex_desired, ex_live, "EX-", exclusions.get("EX", set()))
    )

    # NDGs (derived names, no simple prefix — pass a prefix that will not match)
    ndg_desired = desired_ndg(root)
    ndg_live = live_ers_names(client, NDG_PATH)
    results.append(
        report_family("NDG", ndg_desired, ndg_live, "NDG-NO-PREFIX-", exclusions.get("NDG", set()))
    )

    if all(results):
        print("all clean")
    else:
        print("owned clean, non-owned present")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
