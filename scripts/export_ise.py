#!/usr/bin/env python3
"""Phase 1 — GET-only export from lab ISE into exports/*.csv.

Why this exists
---------------
policy/ is desired state. exports/ is observed state. This script fills
exports/ so you can see the names already on the lab ISE, including the
non-standard GUI objects, without changing anything.

ISE 3.x splits reads across two APIs:
  ERS      /ers/config/...                         inventory-style objects
  OpenAPI  /api/v1/policy/network-access/...       policy sets and rules

Both are GET. The HTTP helper refuses any other method.

Usage (from the repo root):

    python3.12 -m venv .venv
    source .venv/bin/activate
    pip install -r scripts/requirements.txt
    cp .env.example .env          # then edit ISE_URL / user / password
    python scripts/export_ise.py

Optional:

    python scripts/export_ise.py --resource nads
    python scripts/export_ise.py --no-details

Requires on the lab ISE:
  Administration > System > Settings > API Settings
    ERS enabled, OpenAPI enabled, API Gateway enabled
  An admin that can GET both APIs (Super Admin, or ERS Operator + Open API)

ISE 3.3, Python 3.12. Network Access only — no TACACS calls.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTS = REPO_ROOT / "exports"
PAGE_SIZE = 100

ERS_RESOURCES = {
    "nads": "/ers/config/networkdevice",
    "ndg": "/ers/config/networkdevicegroup",
    "authz-profiles": "/ers/config/authorizationprofile",
    "allowed-protocols": "/ers/config/allowedprotocols",
    "downloadable-acls": "/ers/config/downloadableacl",
    "sgt": "/ers/config/sgt",
    "eig": "/ers/config/endpointgroup",
}

OPENAPI_POLICY_SETS = "/api/v1/policy/network-access/policy-set"
OPENAPI_CONDITIONS = "/api/v1/policy/network-access/condition"

SECRET_KEYS = {
    "radiusSharedSecret",
    "secondRadiusSharedSecret",
    "enableKeyWrap",
    "keyEncryptionKey",
    "messageAuthenticatorCodeKey",
    "encryptionKey",
    "sharedSecret",
    "sgaDevicePassword",
    "enableModePassword",
    "execModePassword",
    "snmpAuthPassword",
    "snmpPrivPassword",
    "roCommunity",
    "rwCommunity",
    "password",
}

NDG_ROOT_COLUMNS = {
    "location": "ndg_location",
    "device type": "ndg_device_type",
    "devicetype": "ndg_device_type",
    "businessunit": "ndg_business_unit",
    "business unit": "ndg_business_unit",
    "stage": "ndg_stage",
    "function": "ndg_function",
}

NAD_NDG_FIELDS = [
    "ndg_location",
    "ndg_device_type",
    "ndg_business_unit",
    "ndg_stage",
    "ndg_function",
    "ndg_other",
    "ndg_raw",
]

NDG_SYSTEM_PREFIXES = {
    "ndg_location": "All Locations#",
    "ndg_device_type": "All Device Types#",
}

class IseClient:
    """Thin GET-only client. Lab URL and basic auth come from the environment."""

    def __init__(self, base_url: str, username: str, password: str, verify: bool) -> None:
        parsed = urlparse(base_url if "://" in base_url else f"https://{base_url}")
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SystemExit(f"ISE_URL is not a usable URL: {base_url}")
        self.base = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = verify
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.timeout = int(os.getenv("ISE_REQUEST_TIMEOUT", "60"))

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        if response.status_code == 401:
            raise SystemExit(
                "401 Unauthorized. Check ISE_USERNAME / ISE_PASSWORD and that "
                "the account can GET ERS and OpenAPI."
            )
        if response.status_code == 403:
            raise SystemExit(
                f"403 Forbidden on {path}. Enable ERS / OpenAPI / API Gateway "
                "and confirm the account role."
            )
        if response.status_code == 404:
            raise FileNotFoundError(path)
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    def get_ers_pages(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self.get(path, params={"page": page, "size": PAGE_SIZE})
            resources = (
                payload.get("SearchResult", {}).get("resources")
                or payload.get("searchResult", {}).get("resources")
                or []
            )
            items.extend(resources)
            total = int(
                payload.get("SearchResult", {}).get("total")
                or payload.get("searchResult", {}).get("total")
                or 0
            )
            if not resources or len(items) >= total:
                break
            page += 1
        return items

    def get_openapi_pages(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self.get(path, params={"page": page, "size": PAGE_SIZE})
            batch = payload.get("response")
            if batch is None:
                batch = payload if isinstance(payload, list) else []
            if not isinstance(batch, list):
                break
            items.extend(batch)
            if len(batch) < PAGE_SIZE:
                break
            page += 1
        return items


def load_settings() -> tuple[IseClient, bool]:
    load_dotenv(REPO_ROOT / ".env")
    url = os.getenv("ISE_BASE_URL", "").strip()
    user = os.getenv("ISE_USERNAME", "").strip()
    password = os.getenv("ISE_PASSWORD", "")
    insecure = os.getenv("ISE_INSECURE", "true").strip().lower() in {"1", "true", "yes"}
    if not url or not user or not password:
        raise SystemExit("Set ISE_URL, ISE_USERNAME, and ISE_PASSWORD in .env")
    if insecure:
        requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    client = IseClient(url, user, password, verify=not insecure)
    return client, insecure


def write_csv(name: str, rows: list[dict[str, Any]], fieldnames: list[str]) -> Path:
    EXPORTS.mkdir(exist_ok=True)
    path = EXPORTS / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return path


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def ers_summary_rows(items: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        rows.append(
            {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "source": source,
            }
        )
    return rows


def export_ers_list(client: IseClient, key: str) -> list[dict[str, Any]]:
    path = ERS_RESOURCES[key]
    try:
        items = client.get_ers_pages(path)
    except FileNotFoundError:
        print(f"skip {key}: {path} returned 404", file=sys.stderr)
        return []
    return ers_summary_rows(items, "ers")


def format_ip_entry(entry: Any) -> str:
    if isinstance(entry, dict):
        address = entry.get("ipaddress") or entry.get("ipAddress") or ""
        mask = entry.get("mask", "")
        if not address:
            return ""
        return f"{address}/{mask}" if mask != "" else str(address)
    return str(entry) if entry else ""


def format_ips(detail: dict[str, Any]) -> str:
    """All NAD IPs, joined with |. Mask stays on each entry (32 = host)."""
    ip_list = (
        detail.get("NetworkDeviceIPList")
        or detail.get("networkDeviceIPList")
        or []
    )
    if isinstance(ip_list, dict):
        ip_list = [ip_list]
    if not ip_list:
        return ""
    parts = []
    for entry in ip_list:
        formatted = format_ip_entry(entry)
        if formatted:
            parts.append(formatted)
    return "|".join(parts)


def parse_ndg_list(groups: Any) -> dict[str, str]:
    """Split ISE NDG paths onto one column per locked root."""
    columns = {name: "" for name in NAD_NDG_FIELDS}
    if not groups:
        return columns
    if isinstance(groups, str):
        items = [groups]
    elif isinstance(groups, list):
        items = groups
    else:
        items = [groups]

    raw_paths: list[str] = []
    for item in items:
        if isinstance(item, dict):
            path = str(item.get("name") or item.get("NetworkDeviceGroup") or item)
        else:
            path = str(item)
        path = path.strip()
        if not path:
            continue
        raw_paths.append(path)
        head, sep, tail = path.partition("#")
        root = head.strip().lower()
        column = NDG_ROOT_COLUMNS.get(root)
        if column is None:
            column = "ndg_other"
            value = path
        else:
            value = tail if sep else path
            prefix = NDG_SYSTEM_PREFIXES.get(column)
            if prefix and value.lower().startswith(prefix.lower()):
                value = value[len(prefix):]
        if columns[column]:
            columns[column] = f"{columns[column]}|{value}"
        else:
            columns[column] = value
    columns["ndg_raw"] = "|".join(raw_paths)
    return columns


def export_nads(client: IseClient, details: bool) -> list[dict[str, Any]]:
    items = client.get_ers_pages(ERS_RESOURCES["nads"])
    rows = []
    for item in items:
        row = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "ip": "",
            "ndg_location": "",
            "ndg_device_type": "",
            "ndg_business_unit": "",
            "ndg_stage": "",
            "ndg_function": "",
            "ndg_other": "",
            "ndg_raw": "",
            "source": "ers",
        }
        if details and item.get("id"):
            try:
                raw = client.get(f"{ERS_RESOURCES['nads']}/{item['id']}")
            except FileNotFoundError:
                raw = {}
            body = raw.get("NetworkDevice") or raw.get("networkDevice") or raw
            for secret in SECRET_KEYS:
                body.pop(secret, None)
            if isinstance(body.get("authenticationSettings"), dict):
                for secret in SECRET_KEYS:
                    body["authenticationSettings"].pop(secret, None)
            row["ip"] = format_ips(body)
            row.update(
                parse_ndg_list(
                    body.get("NetworkDeviceGroupList")
                    or body.get("networkDeviceGroupList")
                    or []
                )
            )
            row["description"] = body.get("description") or row["description"]
        rows.append(row)
    return rows


def export_authz_details(client: IseClient, details: bool) -> list[dict[str, Any]]:
    items = client.get_ers_pages(ERS_RESOURCES["authz-profiles"])
    rows = []
    for item in items:
        row = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "access_type": "",
            "vlan": "",
            "dacl": "",
            "sgt": "",
            "source": "ers",
        }
        if details and item.get("id"):
            try:
                raw = client.get(f"{ERS_RESOURCES['authz-profiles']}/{item['id']}")
            except FileNotFoundError:
                raw = {}
            body = raw.get("AuthorizationProfile") or raw.get("authorizationProfile") or raw
            row["access_type"] = body.get("accessType") or ""
            vlan = body.get("vlan") or {}
            if isinstance(vlan, dict):
                row["vlan"] = vlan.get("nameID") or vlan.get("nameId") or ""
            else:
                row["vlan"] = flatten(vlan)
            row["dacl"] = body.get("daclName") or body.get("acl") or ""
            row["sgt"] = body.get("securityGroup") or ""
            row["description"] = body.get("description") or row["description"]
        rows.append(row)
    return rows


def export_dacl_details(client: IseClient, details: bool) -> list[dict[str, Any]]:
    items = client.get_ers_pages(ERS_RESOURCES["downloadable-acls"])
    rows = []
    for item in items:
        row = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "dacl": "",
            "dacl_type": "",
            "source": "ers",
        }
        if details and item.get("id"):
            try:
                raw = client.get(f"{ERS_RESOURCES['downloadable-acls']}/{item['id']}")
            except FileNotFoundError:
                raw = {}
            body = raw.get("DownloadableAcl") or raw.get("downloadableAcl") or raw
            row["dacl"] = body.get("dacl") or ""
            row["dacl_type"] = body.get("daclType") or ""
            row["description"] = body.get("description") or row["description"]
        rows.append(row)
    return rows


def export_sgt_details(client: IseClient, details: bool) -> list[dict[str, Any]]:
    items = client.get_ers_pages(ERS_RESOURCES["sgt"])
    rows = []
    for item in items:
        row = {
            "id": item.get("id", ""),
            "name": item.get("name", ""),
            "description": item.get("description", ""),
            "value": "",
            "source": "ers",
        }
        if details and item.get("id"):
            try:
                raw = client.get(f"{ERS_RESOURCES['sgt']}/{item['id']}")
            except FileNotFoundError:
                raw = {}
            body = raw.get("Sgt") or raw.get("sgt") or raw
            row["value"] = body.get("value", "")
            row["description"] = body.get("description") or row["description"]
        rows.append(row)
    return rows


def condition_summary(condition: Any) -> str:
    if not isinstance(condition, dict):
        return flatten(condition)
    name = condition.get("name")
    if name:
        return str(name)
    ctype = condition.get("conditionType") or condition.get("type") or ""
    dict_name = condition.get("dictionaryName") or ""
    attr = condition.get("attributeName") or ""
    op = condition.get("operator") or ""
    value = condition.get("attributeValue") or ""
    parts = [p for p in (ctype, dict_name, attr, op, str(value)) if p]
    return " ".join(parts)


def export_policy_sets(client: IseClient) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    sets = client.get_openapi_pages(OPENAPI_POLICY_SETS)
    policy_rows: list[dict[str, Any]] = []
    authn_rows: list[dict[str, Any]] = []
    authz_rows: list[dict[str, Any]] = []
    except_rows: list[dict[str, Any]] = []

    for item in sets:
        set_id = item.get("id", "")
        set_name = item.get("name", "")
        policy_rows.append(
            {
                "id": set_id,
                "name": set_name,
                "rank": item.get("rank", ""),
                "state": item.get("state", ""),
                "service_name": item.get("serviceName", ""),
                "is_default": item.get("default", ""),
                "description": item.get("description", ""),
                "condition": condition_summary(item.get("condition")),
                "source": "openapi",
            }
        )
        if not set_id:
            continue
        for kind, bucket in (
            ("authentication", authn_rows),
            ("authorization", authz_rows),
            ("exception", except_rows),
        ):
            try:
                rules = client.get_openapi_pages(
                    f"{OPENAPI_POLICY_SETS}/{set_id}/{kind}"
                )
            except FileNotFoundError:
                continue
            for rule in rules:
                inner = rule.get("rule") or rule
                bucket.append(
                    {
                        "policy_set_id": set_id,
                        "policy_set_name": set_name,
                        "id": inner.get("id") or rule.get("id") or "",
                        "name": inner.get("name") or rule.get("name") or "",
                        "rank": inner.get("rank", ""),
                        "state": inner.get("state", ""),
                        "default": inner.get("default", ""),
                        "identity_source": rule.get("identitySourceName")
                        or inner.get("identitySourceName")
                        or "",
                        "profiles": flatten(rule.get("profile") or rule.get("profiles")),
                        "sgt": rule.get("securityGroup") or "",
                        "condition": condition_summary(inner.get("condition")),
                        "source": "openapi",
                    }
                )
    return policy_rows, authn_rows, authz_rows, except_rows


def export_conditions(client: IseClient) -> list[dict[str, Any]]:
    try:
        items = client.get_openapi_pages(OPENAPI_CONDITIONS)
    except FileNotFoundError:
        print("skip conditions: OpenAPI library conditions returned 404", file=sys.stderr)
        return []
    rows = []
    for item in items:
        rows.append(
            {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "condition_type": item.get("conditionType") or item.get("type") or "",
                "description": item.get("description", ""),
                "summary": condition_summary(item),
                "source": "openapi",
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GET-only ISE export to exports/")
    parser.add_argument(
        "--resource",
        choices=[
            "all",
            "nads",
            "ndg",
            "authz-profiles",
            "allowed-protocols",
            "downloadable-acls",
            "sgt",
            "eig",
            "policy-sets",
            "conditions",
        ],
        default="all",
        help="Export one family instead of everything.",
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Skip per-object GETs (faster, fewer columns).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client, insecure = load_settings()
    details = not args.no_details
    wanted = args.resource
    print(f"target {client.base}  tls_verify={not insecure}  details={details}")

    writers: list[tuple[str, list[str], list[dict[str, Any]]]] = []

    if wanted in {"all", "nads"}:
        writers.append(
            (
                "nads.csv",
                [
                    "id", "name", "description", "ip",
                    "ndg_location", "ndg_device_type", "ndg_business_unit",
                    "ndg_stage", "ndg_function", "ndg_other", "ndg_raw",
                    "source",
                ],
                export_nads(client, details),
            )
        )
    if wanted in {"all", "ndg"}:
        writers.append(
            (
                "ndg.csv",
                ["id", "name", "description", "source"],
                export_ers_list(client, "ndg"),
            )
        )
    if wanted in {"all", "authz-profiles"}:
        writers.append(
            (
                "authz-profiles.csv",
                ["id", "name", "description", "access_type", "vlan", "dacl", "sgt", "source"],
                export_authz_details(client, details),
            )
        )
    if wanted in {"all", "allowed-protocols"}:
        writers.append(
            (
                "allowed-protocols.csv",
                ["id", "name", "description", "source"],
                export_ers_list(client, "allowed-protocols"),
            )
        )
    if wanted in {"all", "downloadable-acls"}:
        writers.append(
            (
                "downloadable-acls.csv",
                ["id", "name", "description", "dacl", "dacl_type", "source"],
                export_dacl_details(client, details),
            )
        )
    if wanted in {"all", "sgt"}:
        writers.append(
            (
                "sgt.csv",
                ["id", "name", "description", "value", "source"],
                export_sgt_details(client, details),
            )
        )
    if wanted in {"all", "eig"}:
        writers.append(
            (
                "eig.csv",
                ["id", "name", "description", "source"],
                export_ers_list(client, "eig"),
            )
        )
    if wanted in {"all", "policy-sets"}:
        policy_rows, authn_rows, authz_rows, except_rows = export_policy_sets(client)
        writers.append(
            (
                "policy-sets.csv",
                ["id", "name", "rank", "state", "service_name", "is_default", "description", "condition", "source"],
                policy_rows,
            )
        )
        writers.append(
            (
                "authentication-rules.csv",
                ["policy_set_id", "policy_set_name", "id", "name", "rank", "state", "default", "identity_source", "condition", "source"],
                authn_rows,
            )
        )
        writers.append(
            (
                "authorization-rules.csv",
                ["policy_set_id", "policy_set_name", "id", "name", "rank", "state", "default", "profiles", "sgt", "condition", "source"],
                authz_rows,
            )
        )
        writers.append(
            (
                "exceptions.csv",
                ["policy_set_id", "policy_set_name", "id", "name", "rank", "state", "default", "profiles", "sgt", "condition", "source"],
                except_rows,
            )
        )
    if wanted in {"all", "conditions"}:
        writers.append(
            (
                "conditions.csv",
                ["id", "name", "condition_type", "description", "summary", "source"],
                export_conditions(client),
            )
        )

    for filename, fields, rows in writers:
        path = write_csv(filename, rows, fields)
        print(f"wrote {path.relative_to(REPO_ROOT)}  ({len(rows)} rows)")

    print("done. Compare names in exports/ against docs/naming.md. Do not edit the CSVs.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        if exc.response is not None:
            print(exc.response.text[:500], file=sys.stderr)
        raise SystemExit(1)