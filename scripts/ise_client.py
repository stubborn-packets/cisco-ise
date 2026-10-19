"""Thin GET-only ISE client shared by the Phase 1 export and Phase 7 import map.

Lab URL and basic auth come from the environment. The client refuses any
method other than GET. No family-specific paths live here.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

PAGE_SIZE = 100


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


def load_client(root: Path) -> IseClient:
    """Load ISE_* from <root>/.env and return a GET-only client."""
    load_dotenv(root / ".env")
    url = os.getenv("ISE_URL", "").strip()
    user = os.getenv("ISE_USERNAME", "").strip()
    password = os.getenv("ISE_PASSWORD", "")
    insecure = os.getenv("ISE_INSECURE", "true").strip().lower() in {"1", "true", "yes"}
    if not url or not user or not password:
        raise SystemExit("Set ISE_URL, ISE_USERNAME, and ISE_PASSWORD in .env")
    if insecure:
        requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    return IseClient(url, user, password, verify=not insecure)
