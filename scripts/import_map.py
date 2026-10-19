#!/usr/bin/env python3
"""Phase 7 import map: name → uuid → terraform address.

Read-only. Walks the families scripts/read_policy.py already emits.
Computes the same Terraform address the reader uses, then looks up the
live UUID by name on lab ISE. Does not write to ISE. Does not put UUIDs
into policy/ or inventory/.

Purpose. While state is healthy you do not need this. Terraform already
holds the UUIDs. The map is recovery and ownership tooling:

- State loss. terraform.tfstate is local and gitignored. If it is lost,
  the objects still exist on ISE. terraform import needs the address and
  the UUID. The map produces both from the YAML name.
- Ownership boundary. Only objects this repo is ready to own. Rank 99
  Default, Default Network Access, old GUI sets, and NADs are not mapped.
- Later import. A matching object created outside Terraform (GUI, backup,
  second eval) can be re-attached instead of duplicated.

Only objects this repo is ready to own. Rank 99 Default, Default Network
Access, and NADs are not mapped.

Usage (from the repo root):

    python3.12 scripts/import_map.py --family sgt
    python3.12 scripts/import_map.py --family eig
    python3.12 scripts/import_map.py --family allowed-protocols
    python3.12 scripts/import_map.py --family dacl
    python3.12 scripts/import_map.py --family authz-profile
    python3.12 scripts/import_map.py --family condition
    python3.12 scripts/import_map.py --family policy-set
    python3.12 scripts/import_map.py --family authn-rule
    python3.12 scripts/import_map.py --family authz-rule
    python3.12 scripts/import_map.py --family ndg
    python3.12 scripts/import_map.py --family exception

Add --dry-run to print addresses only and skip the ISE call.

Requires the same ISE_* environment as scripts/export_ise.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

import yaml

from ise_client import IseClient, load_client
from read_policy import derive_ndg_objects, load_ndg_roots

# Same prefix → stem map read_policy.py uses for module addresses.
ADDRESS = {
    "SGT_": "sgt_",
    "EIG-": "eig_",
    "AP-": "ap_",
    "ACL-": "acl_",
    "PR-": "pr_",
    "CND-": "cnd_",
    "PS-": "ps_",
    "AN-": "an_",
    "AZ-": "az_",
    "EX-": "ex_",
}

# Family → (YAML path, list key, ERS path, resource type inside the module).
# Flat ERS families only. NDGs and later OpenAPI families use their own loader.
FLAT: dict[str, tuple[str, str, str, str]] = {
    "sgt": (
        "policy/sgt.yaml",
        "sgts",
        "/ers/config/sgt",
        "ise_trustsec_security_group.this",
    ),
    "eig": (
        "policy/eig.yaml",
        "endpoint_identity_groups",
        "/ers/config/endpointgroup",
        "ise_endpoint_identity_group.this",
    ),
    "allowed-protocols": (
        "policy/allowed-protocols.yaml",
        "allowed_protocols",
        "/ers/config/allowedprotocols",
        "ise_allowed_protocols.this",
    ),
    "dacl": (
        "policy/authz-profiles.yaml",
        "downloadable_acls",
        "/ers/config/downloadableacl",
        "ise_downloadable_acl.this",
    ),
    "authz-profile": (
        "policy/authz-profiles.yaml",
        "authorization_profiles",
        "/ers/config/authorizationprofile",
        "ise_authorization_profile.this",
    ),
}

# Family → (YAML path, list key, OpenAPI path, resource type inside the module).
# Same shape as FLAT. Lookup uses get_openapi_pages instead of get_ers_pages.
OPENAPI: dict[str, tuple[str, str, str, str]] = {
    "condition": (
        "policy/conditions.yaml",
        "conditions",
        "/api/v1/policy/network-access/condition",
        "ise_network_access_condition.this",
    ),
    "policy-set": (
        "policy/policy-sets.yaml",
        "policy_sets",
        "/api/v1/policy/network-access/policy-set",
        "ise_network_access_policy_set.this",
    ),
}

# ERS path and resource for NDGs. Names and labels come from the reader.
NDG_PATH = "/ers/config/networkdevicegroup"
NDG_RESOURCE = "ise_network_device_group.this"

# Nested rule families. Parent is a policy set. Child path is under that set id.
RULES: dict[str, tuple[str, str, str]] = {
    "authn-rule": (
        "authentication_rules",
        "authentication",
        "ise_network_access_authentication_rule.this",
    ),
    "authz-rule": (
        "authorization_rules",
        "authorization",
        "ise_network_access_authorization_rule.this",
    ),
}

POLICY_SET_PATH = "/api/v1/policy/network-access/policy-set"

# Local exception lives under a policy set. Global has no policy set.
# Resource type differs. Address stem is the same (EX- → ex_).
LOCAL_EXCEPTION_RESOURCE = "ise_network_access_authorization_exception_rule.this"
GLOBAL_EXCEPTION_RESOURCE = "ise_network_access_authorization_global_exception_rule.this"
GLOBAL_EXCEPTION_PATH = "/api/v1/policy/network-access/policy-set/global-exception"

# One row of the map. uuid is empty on dry-run or when the name is missing.
Row = tuple[str, str, str]


def module_label(name: str) -> str:
    """Same rule as scripts/read_policy.py module_label."""
    for prefix, stem in ADDRESS.items():
        if name.startswith(prefix):
            rest = name[len(prefix):].replace("-", "_")
            if not rest:
                raise SystemExit(f"{name} has an empty token after {prefix}")
            return stem + rest
    raise SystemExit(f"{name} has no known prefix")


def terraform_address(name: str, resource: str) -> str:
    return f"module.{module_label(name)}.{resource}"


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


def lookup_ers(client: IseClient, path: str) -> dict[str, str]:
    """name → uuid from an ERS list. Empty string if the name is missing."""
    found: dict[str, str] = {}
    for item in client.get_ers_pages(path):
        name = item.get("name")
        uid = item.get("id")
        if isinstance(name, str) and isinstance(uid, str) and name and uid:
            found[name] = uid
    return found


def lookup_openapi(client: IseClient, path: str) -> dict[str, str]:
    """name → uuid from an OpenAPI list. Empty string if the name is missing."""
    found: dict[str, str] = {}
    for item in client.get_openapi_pages(path):
        name = item.get("name")
        uid = item.get("id")
        if isinstance(name, str) and isinstance(uid, str) and name and uid:
            found[name] = uid
    return found


def load_openapi(root: Path, client: IseClient | None, spec: tuple[str, str, str, str]) -> list[Row]:
    rel, key, path, resource = spec
    rows = load_rows(root, rel, key)
    live = lookup_openapi(client, path) if client is not None else {}
    out: list[Row] = []
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"{rel} row missing name: {row!r}")
        out.append((name, live.get(name, ""), terraform_address(name, resource)))
    return out


def load_flat(root: Path, client: IseClient | None, spec: tuple[str, str, str, str]) -> list[Row]:
    rel, key, path, resource = spec
    rows = load_rows(root, rel, key)
    live = lookup_ers(client, path) if client is not None else {}
    out: list[Row] = []
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"{rel} row missing name: {row!r}")
        out.append((name, live.get(name, ""), terraform_address(name, resource)))
    return out


def load_rules(root: Path, client: IseClient | None, spec: tuple[str, str, str]) -> list[Row]:
    """Rules nested under each policy set. Lookup needs the parent set id."""
    yaml_key, kind, resource = spec
    sets = load_rows(root, "policy/policy-sets.yaml", "policy_sets")
    set_ids: dict[str, str] = {}
    if client is not None:
        set_ids = lookup_openapi(client, POLICY_SET_PATH)
    out: list[Row] = []
    for parent in sets:
        parent_name = parent.get("name")
        if not isinstance(parent_name, str) or not parent_name:
            raise SystemExit(f"policy set missing name: {parent!r}")
        rules = parent.get(yaml_key) or []
        if not isinstance(rules, list):
            raise SystemExit(f"{parent_name} {yaml_key} must be a list")
        live: dict[str, str] = {}
        if client is not None:
            set_id = set_ids.get(parent_name, "")
            if set_id:
                child_path = f"{POLICY_SET_PATH}/{set_id}/{kind}"
                for item in client.get_openapi_pages(child_path):
                    inner = item.get("rule") or item
                    name = inner.get("name") or item.get("name")
                    uid = inner.get("id") or item.get("id")
                    if isinstance(name, str) and isinstance(uid, str) and name and uid:
                        live[name] = uid
        for rule in rules:
            name = rule.get("name")
            if not isinstance(name, str) or not name:
                raise SystemExit(f"{parent_name} rule missing name: {rule!r}")
            out.append((name, live.get(name, ""), terraform_address(name, resource)))
    return out


def load_exceptions(root: Path, client: IseClient | None, _spec: Any = None) -> list[Row]:
    """Local exceptions are under a policy set. Global exceptions are not."""
    rows = load_rows(root, "policy/exceptions.yaml", "exceptions")
    set_ids: dict[str, str] = {}
    global_live: dict[str, str] = {}
    if client is not None:
        set_ids = lookup_openapi(client, POLICY_SET_PATH)
        for item in client.get_openapi_pages(GLOBAL_EXCEPTION_PATH):
            inner = item.get("rule") or item
            name = inner.get("name") or item.get("name")
            uid = inner.get("id") or item.get("id")
            if isinstance(name, str) and isinstance(uid, str) and name and uid:
                global_live[name] = uid
    out: list[Row] = []
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"exception row missing name: {row!r}")
        parent = row.get("policy_set")
        if isinstance(parent, str) and parent:
            resource = LOCAL_EXCEPTION_RESOURCE
            live: dict[str, str] = {}
            if client is not None:
                set_id = set_ids.get(parent, "")
                if set_id:
                    child = f"{POLICY_SET_PATH}/{set_id}/exception"
                    for item in client.get_openapi_pages(child):
                        inner = item.get("rule") or item
                        item_name = inner.get("name") or item.get("name")
                        uid = inner.get("id") or item.get("id")
                        if isinstance(item_name, str) and isinstance(uid, str) and item_name and uid:
                            live[item_name] = uid
            out.append((name, live.get(name, ""), terraform_address(name, resource)))
        else:
            out.append((
                name,
                global_live.get(name, ""),
                terraform_address(name, GLOBAL_EXCEPTION_RESOURCE),
            ))
    return out


def load_ndg(root: Path, client: IseClient | None, _spec: Any = None) -> list[Row]:
    objects = derive_ndg_objects(load_ndg_roots(root))
    live = lookup_ers(client, NDG_PATH) if client is not None else {}
    out: list[Row] = []
    for obj in objects:
        name = obj["name"]
        label = obj["label"]
        out.append((name, live.get(name, ""), f"module.{label}.{NDG_RESOURCE}"))
    return out


# Family name → loader. Flat ERS share load_flat. OpenAPI flat share load_openapi.
# NDGs have their own. Later nested families register here the same way.
LOADERS: dict[str, Callable[[Path, IseClient | None, Any], list[Row]]] = {
    name: load_flat for name in FLAT
}
for name in OPENAPI:
    LOADERS[name] = load_openapi
for name in RULES:
    LOADERS[name] = load_rules
LOADERS["ndg"] = load_ndg
LOADERS["exception"] = load_exceptions

# Spec passed to the loader. Flat families use the tuple; NDGs and exceptions ignore it.
SPECS: dict[str, Any] = dict(FLAT)
SPECS.update(OPENAPI)
SPECS.update(RULES)
SPECS["ndg"] = None
SPECS["exception"] = None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--family",
        choices=tuple(LOADERS),
        required=True,
        help="Which family to map.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repo root (default: parent of scripts/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print addresses only. Do not call ISE.",
    )
    args = parser.parse_args()

    client = None if args.dry_run else load_client(args.root)
    rows = LOADERS[args.family](args.root, client, SPECS[args.family])

    print("# name\tuuid\tterraform_address")
    for name, uid, address in rows:
        print(f"{name}\t{uid}\t{address}")


if __name__ == "__main__":
    main()
