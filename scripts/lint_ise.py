#!/usr/bin/env python3
"""Phase 2 — naming linter for policy/ and inventory/.

Reads lint/prefixes.yaml + lint/builtins.yaml and walks the desired-state
and inventory YAML. Does not talk to ISE. Does not read exports/.

Fails on:
  - names that are not PREFIX- + kebab-case (unless allow-listed built-ins)
  - missing state on policy objects
  - missing or expired exception metadata (ticket, owner, expires_on)
  - NDG roots that are not in the locked set
  - NDG / NAD values that are not on the allow-list (or ISO pattern)
  - UUIDs in policy/ or inventory/
  - TACACS / Device Admin keys or scopes

Usage (from the repo root):

    python3.12 scripts/lint_ise.py
    python3.12 scripts/lint_ise.py --root .
    python3.12 -m unittest tests.lint.test_lint_ise
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

NAME_RE = re.compile(r"^([A-Z]+)-([a-z0-9]+(?:-[a-z0-9]+)*)$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_ALPHA3_RE = re.compile(r"^[A-Z]{3}$")
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
REJECTED_KEY_RE = re.compile(r"(tacacs|device[-_]?admin)", re.IGNORECASE)

EXCEPTION_REQUIRED = ("ticket", "owner")
EXPIRY_FIELDS = ("expires_on", "expiry", "expires")
STATE_VALUES = {"enabled", "disabled"}

# policy/<file> → list of (top-level key, expected prefix or None)
POLICY_COLLECTIONS: dict[str, list[tuple[str, str | None]]] = {
    "allowed-protocols.yaml": [("allowed_protocols", "AP")],
    "authz-profiles.yaml": [
        ("authorization_profiles", "PR"),
        ("downloadable_acls", "ACL"),
    ],
    "conditions.yaml": [("conditions", "CND")],
    "eig.yaml": [("endpoint_identity_groups", "EIG")],
    "exceptions.yaml": [("exceptions", "EX")],
    "logical-profiles.yaml": [("logical_profiles", "LP")],
    "policy-sets.yaml": [("policy_sets", "PS")],
    "sgt.yaml": [("sgts", "SGT")],
}

NESTED_RULES = {
    "authentication_rules": "AN",
    "authorization_rules": "AZ",
    "local_exceptions": "EX",
    "exception_rules": "EX",
}

POLICY_SET_RANK_EXACT = {
    10: "PS-global-vpn",
    20: "PS-global-wireless-8021x",
    30: "PS-global-wireless-mab",
    40: "PS-global-wired-8021x",
    50: "PS-global-wired-mab",
    99: "Default",
}


class Finding:
    __slots__ = ("path", "name", "message")

    def __init__(self, path: str, name: str | None, message: str) -> None:
        self.path = path
        self.name = name or ""
        self.message = message

    def __str__(self) -> str:
        loc = self.path
        if self.name:
            loc = f"{self.path}: {self.name}"
        return f"{loc}: {self.message}"


class Linter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.policy = root / "policy"
        self.inventory = root / "inventory"
        self.errors: list[Finding] = []
        self.objects_seen = 0
        self.prefixes: dict[str, dict[str, str]] = {}
        self.rejected_scopes: set[str] = set()
        self.builtins: set[str] = set()
        self.ndg_roots: list[str] = []
        self.ndg_ise_roots: dict[str, str] = {}
        self.ndg_nad_keys: dict[str, str] = {}
        self.inventory_prefixes: dict[str, dict[str, str]] = {}
        self.ndg_by_name: dict[str, dict[str, Any]] = {}

    def error(self, path: str, name: str | None, message: str) -> None:
        self.errors.append(Finding(path, name, message))

    def load_config(self) -> None:
        prefixes_path = self.root / "lint" / "prefixes.yaml"
        builtins_path = self.root / "lint" / "builtins.yaml"
        prefixes_doc = _load_yaml(prefixes_path)
        builtins_doc = _load_yaml(builtins_path)
        if not isinstance(prefixes_doc, dict):
            self.error(_rel(self.root, prefixes_path), None, "prefixes.yaml is not a mapping")
            return
        if not isinstance(builtins_doc, dict):
            self.error(_rel(self.root, builtins_path), None, "builtins.yaml is not a mapping")
            return
        raw_prefixes = prefixes_doc.get("prefixes") or {}
        if not isinstance(raw_prefixes, dict):
            self.error(_rel(self.root, prefixes_path), None, "prefixes.prefixes must be a mapping")
        else:
            self.prefixes = raw_prefixes
        self.rejected_scopes = set(prefixes_doc.get("rejected_scopes") or [])
        self.builtins = set(builtins_doc.get("names") or [])
        self.ndg_roots = list(builtins_doc.get("ndg_roots") or [])
        self.ndg_ise_roots = dict(builtins_doc.get("ndg_ise_roots") or {})
        self.ndg_nad_keys = dict(builtins_doc.get("ndg_nad_keys") or {})
        self.inventory_prefixes = dict(builtins_doc.get("inventory_prefixes") or {})

    def run(self) -> int:
        self.load_config()
        if not self.policy.is_dir():
            self.error("policy/", None, "policy/ directory is missing")
        if not self.inventory.is_dir():
            self.error("inventory/", None, "inventory/ directory is missing")
        if self.errors and not self.prefixes:
            return 1
        self._scan_plane(self.policy, plane="policy")
        self._scan_plane(self.inventory, plane="inventory")
        self._check_ndg_file()
        self._check_nads_ndg()
        return 1 if self.errors else 0

    def _scan_plane(self, directory: Path, plane: str) -> None:
        if not directory.is_dir():
            return
        for path in sorted(directory.glob("*.yaml")):
            rel = _rel(self.root, path)
            doc = _load_yaml(path)
            self._scan_rejected(doc, rel)
            self._scan_uuids(doc, rel)
            if path.name == "ndg.yaml":
                continue
            self._scan_named_objects(doc, rel, plane, path.name)

    def _scan_named_objects(
        self, doc: Any, rel: str, plane: str, filename: str
    ) -> None:
        if plane == "policy" and filename in POLICY_COLLECTIONS:
            for key, expected_prefix in POLICY_COLLECTIONS[filename]:
                items = _as_list((doc or {}).get(key) if isinstance(doc, dict) else None)
                for item in items:
                    if not isinstance(item, dict):
                        self.error(rel, None, f"{key} entry is not a mapping")
                        continue
                    self._lint_object(item, rel, plane, expected_prefix)
                    self._lint_nested_rules(item, rel, plane)
            return
        if plane == "inventory":
            self._scan_inventory_file(doc, rel, filename)
            return
        # Unknown policy yaml: still walk mappings with a name.
        self._walk_named(doc, rel, plane)

    def _scan_inventory_file(self, doc: Any, rel: str, filename: str) -> None:
        if not isinstance(doc, dict):
            return
        if filename == "nads.yaml":
            for item in _as_list(doc.get("nads")):
                self._lint_inventory_named(item, rel, required_prefix=None)
        elif filename == "nodes.yaml":
            for item in _as_list(doc.get("nodes")):
                self._lint_inventory_named(item, rel, required_prefix=None)
            for item in _as_list(doc.get("vips")):
                self._lint_inventory_named(item, rel, required_prefix="VIP")
        elif filename == "vlans.yaml":
            for item in _as_list(doc.get("vlans")):
                self._lint_inventory_named(item, rel, required_prefix="VLAN")
        else:
            self._walk_named(doc, rel, "inventory")

    def _walk_named(self, node: Any, rel: str, plane: str) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("name"), str):
                prefix = _prefix_of(node["name"])
                self._lint_object(node, rel, plane, prefix)
            for value in node.values():
                self._walk_named(value, rel, plane)
        elif isinstance(node, list):
            for item in node:
                self._walk_named(item, rel, plane)

    def _lint_nested_rules(self, item: dict[str, Any], rel: str, plane: str) -> None:
        for key, prefix in NESTED_RULES.items():
            for rule in _as_list(item.get(key)):
                if not isinstance(rule, dict):
                    self.error(rel, item.get("name"), f"{key} entry is not a mapping")
                    continue
                self._lint_object(rule, rel, plane, prefix)
                self._lint_nested_rules(rule, rel, plane)

    def _lint_object(
        self,
        obj: dict[str, Any],
        rel: str,
        plane: str,
        expected_prefix: str | None,
    ) -> None:
        name = obj.get("name")
        if not isinstance(name, str) or not name.strip():
            self.error(rel, None, "object is missing a name")
            return
        self.objects_seen += 1
        self._check_name(name, rel, expected_prefix, plane)
        if plane == "policy":
            self._check_state(obj, rel, name)
        if (expected_prefix == "EX") or _prefix_of(name) == "EX":
            self._check_exception(obj, rel, name)
        if expected_prefix == "PS" or _prefix_of(name) == "PS":
            self._check_policy_set_rank(obj, rel, name)
        self._check_scope(obj, rel, name)

    def _lint_inventory_named(
        self, obj: Any, rel: str, required_prefix: str | None
    ) -> None:
        if not isinstance(obj, dict):
            self.error(rel, None, "inventory entry is not a mapping")
            return
        name = obj.get("name")
        if not isinstance(name, str) or not name.strip():
            self.error(rel, None, "inventory object is missing a name")
            return
        self.objects_seen += 1
        if name in self.builtins:
            return
        parsed = NAME_RE.fullmatch(name)
        if required_prefix:
            self._check_name(name, rel, required_prefix, plane="inventory")
            return
        if parsed:
            # Prefixed inventory name must be a known prefix (VIP, VLAN, …).
            self._check_name(name, rel, parsed.group(1), plane="inventory")
            return
        if not KEBAB_RE.fullmatch(name):
            self.error(
                rel,
                name,
                "inventory name must be kebab-case [a-z0-9] tokens, or a known PREFIX-",
            )

    def _check_name(
        self,
        name: str,
        rel: str,
        expected_prefix: str | None,
        plane: str,
    ) -> None:
        if name in self.builtins:
            if expected_prefix and name != "Default" and _prefix_of(name) not in (
                None,
                expected_prefix,
            ):
                # Built-ins like Default are allowed even when the collection
                # normally wants PS- / AP- / SGT-.
                pass
            return
        match = NAME_RE.fullmatch(name)
        if not match:
            self.error(
                rel,
                name,
                "name must be PREFIX- + kebab-case [a-z0-9] "
                "(e.g. PS-global-wired-8021x)",
            )
            return
        prefix, _rest = match.group(1), match.group(2)
        known = self._prefix_meta(prefix)
        if known is None:
            self.error(rel, name, f"unknown prefix {prefix}-")
            return
        scope = (known.get("scope") or "").strip()
        if scope in self.rejected_scopes:
            self.error(rel, name, f"prefix {prefix}- is out of scope ({scope})")
            return
        if expected_prefix and prefix != expected_prefix:
            self.error(
                rel,
                name,
                f"expected prefix {expected_prefix}- for this object, found {prefix}-",
            )

    def _prefix_meta(self, prefix: str) -> dict[str, str] | None:
        if prefix in self.prefixes:
            meta = self.prefixes[prefix]
            return meta if isinstance(meta, dict) else {}
        if prefix in self.inventory_prefixes:
            meta = self.inventory_prefixes[prefix]
            return meta if isinstance(meta, dict) else {}
        return None

    def _check_state(self, obj: dict[str, Any], rel: str, name: str) -> None:
        state = obj.get("state")
        if state is None or (isinstance(state, str) and not state.strip()):
            self.error(rel, name, "missing state (enabled|disabled)")
            return
        if not isinstance(state, str) or state not in STATE_VALUES:
            self.error(rel, name, f"state must be enabled or disabled, not {state!r}")

    def _check_exception(self, obj: dict[str, Any], rel: str, name: str) -> None:
        for field in EXCEPTION_REQUIRED:
            value = obj.get(field)
            if not isinstance(value, str) or not value.strip():
                self.error(rel, name, f"missing exception metadata '{field}'")
        expiry_raw = None
        expiry_field = None
        for field in EXPIRY_FIELDS:
            if field in obj:
                expiry_field = field
                expiry_raw = obj.get(field)
                break
        if expiry_field is None:
            self.error(rel, name, "missing exception metadata 'expires_on'")
            return
        if not isinstance(expiry_raw, str) or not expiry_raw.strip():
            self.error(rel, name, f"missing exception metadata '{expiry_field}'")
            return
        try:
            expiry = dt.date.fromisoformat(expiry_raw.strip())
        except ValueError:
            self.error(
                rel,
                name,
                f"{expiry_field} must be YYYY-MM-DD, not {expiry_raw!r}",
            )
            return
        if expiry < dt.date.today():
            self.error(rel, name, f"exception expired on {expiry.isoformat()}")

    def _check_policy_set_rank(self, obj: dict[str, Any], rel: str, name: str) -> None:
        if "rank" not in obj:
            return
        rank = obj.get("rank")
        if not isinstance(rank, int):
            self.error(rel, name, "rank must be an integer")
            return
        exact = POLICY_SET_RANK_EXACT.get(rank)
        if exact and name != exact:
            self.error(rel, name, f"rank {rank} must be named {exact}")
            return
        if 1 <= rank <= 9 and name != "PS-infra-health-checks":
            self.error(rel, name, "ranks 1-9 must be named PS-infra-health-checks")
            return
        if 60 <= rank <= 69 and not _matches_bu_pattern(name, "vpn"):
            self.error(rel, name, "ranks 60-69 must match PS-<business-unit>-vpn")
            return
        if 70 <= rank <= 79 and not _matches_bu_pattern(name, "wireless"):
            self.error(rel, name, "ranks 70-79 must match PS-<business-unit>-wireless")
            return
        if 80 <= rank <= 89 and not _matches_bu_pattern(name, "wired"):
            self.error(rel, name, "ranks 80-89 must match PS-<business-unit>-wired")

    def _check_scope(self, obj: dict[str, Any], rel: str, name: str) -> None:
        scope = obj.get("scope")
        if isinstance(scope, str) and scope in self.rejected_scopes:
            self.error(rel, name, f"scope {scope} is out of scope")

    def _check_ndg_file(self) -> None:
        path = self.policy / "ndg.yaml"
        rel = _rel(self.root, path)
        if not path.is_file():
            self.error(rel, None, "policy/ndg.yaml is missing")
            return
        doc = _load_yaml(path)
        roots = _as_list(doc.get("roots") if isinstance(doc, dict) else None)
        seen: set[str] = set()
        locked = set(self.ndg_roots)
        for root in roots:
            if not isinstance(root, dict):
                self.error(rel, None, "NDG root entry is not a mapping")
                continue
            name = root.get("name")
            if not isinstance(name, str) or not name.strip():
                self.error(rel, None, "NDG root is missing a name")
                continue
            if name not in locked:
                self.error(rel, name, "unknown NDG root")
                continue
            if name in seen:
                self.error(rel, name, "duplicate NDG root")
            seen.add(name)
            self.ndg_by_name[name] = root
            expected_ise = self.ndg_ise_roots.get(name)
            ise_root = root.get("ise_root")
            if expected_ise and ise_root and ise_root != expected_ise:
                self.error(
                    rel,
                    name,
                    f"ise_root must be {expected_ise}, not {ise_root}",
                )
            self._check_ndg_values(root, rel, name)
        missing = [name for name in self.ndg_roots if name not in seen]
        for name in missing:
            self.error(rel, name, "locked NDG root is not defined")

    def _check_ndg_values(self, root: dict[str, Any], rel: str, name: str) -> None:
        value_type = root.get("value_type")
        values = root.get("allowed_values") or []
        if values is None:
            values = []
        if not isinstance(values, list):
            self.error(rel, name, "allowed_values must be a list")
            return
        for raw in values:
            if not isinstance(raw, str) or not raw.strip():
                self.error(rel, name, "allowed value must be a non-empty string")
                continue
            if value_type == "iso-3166-1-alpha-3":
                if not ISO_ALPHA3_RE.fullmatch(raw):
                    self.error(
                        rel,
                        name,
                        f"location value {raw!r} is not ISO 3166-1 alpha-3",
                    )
            else:
                if not KEBAB_RE.fullmatch(raw):
                    self.error(
                        rel,
                        name,
                        f"NDG value {raw!r} must be kebab-case [a-z0-9]",
                    )

    def _check_nads_ndg(self) -> None:
        path = self.inventory / "nads.yaml"
        if not path.is_file():
            return
        rel = _rel(self.root, path)
        doc = _load_yaml(path)
        nads = _as_list(doc.get("nads") if isinstance(doc, dict) else None)
        for nad in nads:
            if not isinstance(nad, dict):
                continue
            nad_name = nad.get("name") if isinstance(nad.get("name"), str) else None
            ndg = nad.get("ndg")
            if ndg is None:
                continue
            if not isinstance(ndg, dict):
                self.error(rel, nad_name, "ndg must be a mapping")
                continue
            for key, value in ndg.items():
                root_name = self.ndg_nad_keys.get(key)
                if root_name is None:
                    self.error(rel, nad_name, f"unknown NDG root key '{key}'")
                    continue
                if not isinstance(value, str) or not value.strip():
                    self.error(rel, nad_name, f"NDG {key} value is empty")
                    continue
                root = self.ndg_by_name.get(root_name) or {}
                value_type = root.get("value_type")
                allowed = [v for v in (root.get("allowed_values") or []) if isinstance(v, str)]
                if value_type == "iso-3166-1-alpha-3":
                    if value not in allowed and not ISO_ALPHA3_RE.fullmatch(value):
                        self.error(
                            rel,
                            nad_name,
                            f"location value {value!r} is not ISO 3166-1 alpha-3",
                        )
                    elif allowed and value not in allowed and ISO_ALPHA3_RE.fullmatch(value):
                        self.error(
                            rel,
                            nad_name,
                            f"location value {value!r} is not in All Locations allowed_values",
                        )
                else:
                    if value not in allowed:
                        self.error(
                            rel,
                            nad_name,
                            f"NDG value {value!r} is not in {root_name} allowed_values",
                        )

    def _scan_uuids(self, node: Any, rel: str, name_hint: str | None = None) -> None:
        if isinstance(node, dict):
            hint = node.get("name") if isinstance(node.get("name"), str) else name_hint
            for key, value in node.items():
                if key.lower() in {"id", "uuid"} and isinstance(value, str) and UUID_RE.fullmatch(value):
                    self.error(rel, hint, "UUIDs do not belong in policy/ or inventory/")
                else:
                    self._scan_uuids(value, rel, hint)
        elif isinstance(node, list):
            for item in node:
                self._scan_uuids(item, rel, name_hint)
        elif isinstance(node, str) and UUID_RE.fullmatch(node.strip()):
            self.error(rel, name_hint, "UUIDs do not belong in policy/ or inventory/")

    def _scan_rejected(self, node: Any, rel: str, name_hint: str | None = None) -> None:
        if isinstance(node, dict):
            hint = node.get("name") if isinstance(node.get("name"), str) else name_hint
            for key, value in node.items():
                if REJECTED_KEY_RE.search(str(key)):
                    self.error(rel, hint, f"out-of-scope key '{key}' (Network Access only)")
                self._scan_rejected(value, rel, hint)
        elif isinstance(node, list):
            for item in node:
                self._scan_rejected(item, rel, name_hint)
        elif isinstance(node, str) and node.strip() in self.rejected_scopes:
            self.error(rel, name_hint, f"out-of-scope value '{node}' (Network Access only)")

    def report(self, stream: Any = sys.stdout) -> None:
        if self.errors:
            print(
                f"lint_ise: {len(self.errors)} error(s), {self.objects_seen} object(s)",
                file=stream,
            )
            for finding in self.errors:
                print(f"  {finding}", file=stream)
            return
        print(f"lint_ise: ok ({self.objects_seen} object(s))", file=stream)


def _load_yaml(path: Path) -> Any:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    loaded = yaml.safe_load(text)
    return {} if loaded is None else loaded


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _prefix_of(name: str) -> str | None:
    match = NAME_RE.fullmatch(name)
    return match.group(1) if match else None


def _matches_bu_pattern(name: str, suffix: str) -> bool:
    prefix = f"PS-"
    end = f"-{suffix}"
    if not name.startswith(prefix) or not name.endswith(end):
        return False
    middle = name[len(prefix) : len(name) - len(end)]
    return bool(middle) and KEBAB_RE.fullmatch(middle) is not None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint ISE policy/ and inventory/ names.")
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root containing policy/, inventory/, lint/",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    linter = Linter(root)
    code = linter.run()
    linter.report()
    return code


if __name__ == "__main__":
    sys.exit(main())