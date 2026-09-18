#!/usr/bin/env python3
"""Phase 2 linter checks. No ISE connection."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lint_ise import Linter  # noqa: E402  # type: ignore[import-not-found]


LOCKED_NDG = """
roots:
  - name: All Locations
    ise_root: Location
    value_type: iso-3166-1-alpha-3
    allowed_values: {locations}
  - name: All Device Types
    ise_root: Device Type
    value_type: allow-list
    allowed_values: {device_types}
  - name: BusinessUnit
    ise_root: BusinessUnit
    value_type: allow-list
    allowed_values: {business_units}
  - name: Stage
    ise_root: Stage
    value_type: allow-list
    allowed_values: {stages}
  - name: Function
    ise_root: Function
    value_type: allow-list
    allowed_values: {functions}
"""


def _dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Fixture:
    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="ise-lint-"))
        shutil.copytree(REPO_ROOT / "lint", self.dir / "lint")
        (self.dir / "policy").mkdir()
        (self.dir / "inventory").mkdir()
        self.set_ndg()
        _dump(self.dir / "policy" / "allowed-protocols.yaml", {"allowed_protocols": []})
        _dump(
            self.dir / "policy" / "authz-profiles.yaml",
            {"authorization_profiles": [], "downloadable_acls": []},
        )
        _dump(self.dir / "policy" / "conditions.yaml", {"conditions": []})
        _dump(self.dir / "policy" / "eig.yaml", {"endpoint_identity_groups": []})
        _dump(self.dir / "policy" / "exceptions.yaml", {"exceptions": []})
        _dump(self.dir / "policy" / "logical-profiles.yaml", {"logical_profiles": []})
        _dump(self.dir / "policy" / "policy-sets.yaml", {"policy_sets": []})
        _dump(self.dir / "policy" / "sgt.yaml", {"sgts": []})
        _dump(self.dir / "inventory" / "nads.yaml", {"nads": []})
        _dump(self.dir / "inventory" / "nodes.yaml", {"nodes": [], "vips": []})
        _dump(self.dir / "inventory" / "vlans.yaml", {"vlans": []})

    def set_ndg(
        self,
        locations: list[str] | None = None,
        device_types: list[str] | None = None,
        business_units: list[str] | None = None,
        stages: list[str] | None = None,
        functions: list[str] | None = None,
    ) -> None:
        def flow(values: list[str] | None) -> str:
            return yaml.safe_dump(values or [], default_flow_style=True).strip()

        text = LOCKED_NDG.format(
            locations=flow(locations),
            device_types=flow(device_types),
            business_units=flow(business_units),
            stages=flow(stages),
            functions=flow(functions),
        )
        _write(self.dir / "policy" / "ndg.yaml", text)

    def put_policy(self, filename: str, data: dict) -> None:
        _dump(self.dir / "policy" / filename, data)

    def put_inventory(self, filename: str, data: dict) -> None:
        _dump(self.dir / "inventory" / filename, data)

    def lint(self) -> Linter:
        linter = Linter(self.dir)
        linter.run()
        return linter

    def messages(self) -> list[str]:
        linter = self.lint()
        return [str(f) for f in linter.errors]

    def cleanup(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


class RepoScaffoldTest(unittest.TestCase):
    def test_current_repo_scaffolds_pass(self) -> None:
        linter = Linter(REPO_ROOT)
        code = linter.run()
        self.assertEqual(code, 0, [str(f) for f in linter.errors])
        self.assertEqual(linter.errors, [])


class EmptyScaffoldTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_empty_desired_state_passes(self) -> None:
        linter = self.fx.lint()
        self.assertEqual(linter.errors, [])


class NameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_good_name_passes(self) -> None:
        self.fx.put_policy(
            "allowed-protocols.yaml",
            {
                "allowed_protocols": [
                    {
                        "name": "AP-wired-dot1x",
                        "state": "enabled",
                        "description": "802.1X for wired campus",
                    }
                ]
            },
        )
        self.fx.put_policy(
            "policy-sets.yaml",
            {
                "policy_sets": [
                    {
                        "name": "PS-global-wired-8021x",
                        "rank": 40,
                        "state": "enabled",
                        "service": "Default Network Access",
                        "authentication_rules": [
                            {"name": "AN-dot1x-ad", "state": "enabled"}
                        ],
                        "authorization_rules": [
                            {"name": "AZ-wired-corp", "state": "disabled"}
                        ],
                    }
                ]
            },
        )
        self.fx.put_policy(
            "authz-profiles.yaml",
            {
                "authorization_profiles": [
                    {
                        "name": "PR-wired-corp-access",
                        "state": "enabled",
                        "vlan": "VLAN-lab-data",
                    }
                ],
                "downloadable_acls": [
                    {"name": "ACL-permit-all", "state": "enabled"}
                ],
            },
        )
        self.assertEqual(self.fx.messages(), [])

    def test_builtin_names_pass(self) -> None:
        self.fx.put_policy(
            "policy-sets.yaml",
            {
                "policy_sets": [
                    {
                        "name": "Default",
                        "rank": 99,
                        "state": "enabled",
                    }
                ]
            },
        )
        self.fx.put_policy(
            "sgt.yaml",
            {"sgts": [{"name": "Unknown", "state": "enabled", "value": 0}]},
        )
        self.fx.put_policy(
            "allowed-protocols.yaml",
            {
                "allowed_protocols": [
                    {"name": "Default Network Access", "state": "enabled"}
                ]
            },
        )
        self.assertEqual(self.fx.messages(), [])

    def test_bad_name_spaces_fails(self) -> None:
        self.fx.put_policy(
            "authz-profiles.yaml",
            {
                "authorization_profiles": [
                    {"name": "Corp Users VLAN", "state": "enabled"}
                ],
                "downloadable_acls": [],
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("Corp Users VLAN" in m for m in msgs), msgs)

    def test_lowercase_prefix_fails(self) -> None:
        self.fx.put_policy(
            "policy-sets.yaml",
            {
                "policy_sets": [
                    {"name": "ps-global-wired-8021x", "rank": 40, "state": "enabled"}
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("ps-global-wired-8021x" in m for m in msgs), msgs)

    def test_underscore_name_fails(self) -> None:
        self.fx.put_policy(
            "policy-sets.yaml",
            {
                "policy_sets": [
                    {"name": "PS_global_wired", "rank": 40, "state": "enabled"}
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("PS_global_wired" in m for m in msgs), msgs)

    def test_uppercase_token_fails(self) -> None:
        self.fx.put_policy(
            "policy-sets.yaml",
            {
                "policy_sets": [
                    {"name": "PS-Global-Wired", "rank": 40, "state": "enabled"}
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("PS-Global-Wired" in m for m in msgs), msgs)

    def test_wrong_prefix_for_collection_fails(self) -> None:
        self.fx.put_policy(
            "allowed-protocols.yaml",
            {"allowed_protocols": [{"name": "PS-wired-dot1x", "state": "enabled"}]},
        )
        msgs = self.fx.messages()
        self.assertTrue(any("expected prefix AP-" in m for m in msgs), msgs)

    def test_unknown_prefix_fails(self) -> None:
        self.fx.put_policy(
            "conditions.yaml",
            {"conditions": [{"name": "FOO-wired-dot1x", "state": "enabled"}]},
        )
        msgs = self.fx.messages()
        self.assertTrue(any("unknown prefix FOO-" in m for m in msgs), msgs)


class StateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_missing_state_fails(self) -> None:
        self.fx.put_policy(
            "sgt.yaml",
            {"sgts": [{"name": "SGT-lab-users", "value": 1001}]},
        )
        msgs = self.fx.messages()
        self.assertTrue(any("missing state" in m for m in msgs), msgs)

    def test_invalid_state_fails(self) -> None:
        self.fx.put_policy(
            "sgt.yaml",
            {"sgts": [{"name": "SGT-lab-users", "value": 1001, "state": "active"}]},
        )
        msgs = self.fx.messages()
        self.assertTrue(any("enabled or disabled" in m for m in msgs), msgs)


class ExceptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def _ex(self, **overrides: str) -> dict[str, str]:
        base: dict[str, str] = {
            "name": "EX-vendor-wired-temp",
            "state": "enabled",
            "policy_set": "PS-global-wired-mab",
            "ticket": "CHG0001234",
            "owner": "lab",
            "expires_on": "2099-12-31",
        }
        base.update(overrides)
        return base

    def test_complete_exception_passes(self) -> None:
        self.fx.put_policy("exceptions.yaml", {"exceptions": [self._ex()]})
        self.assertEqual(self.fx.messages(), [])

    def test_missing_ticket_fails(self) -> None:
        row = self._ex()
        del row["ticket"]
        self.fx.put_policy("exceptions.yaml", {"exceptions": [row]})
        msgs = self.fx.messages()
        self.assertTrue(any("ticket" in m for m in msgs), msgs)

    def test_missing_owner_fails(self) -> None:
        row = self._ex()
        del row["owner"]
        self.fx.put_policy("exceptions.yaml", {"exceptions": [row]})
        msgs = self.fx.messages()
        self.assertTrue(any("owner" in m for m in msgs), msgs)

    def test_missing_expiry_fails(self) -> None:
        row = self._ex()
        del row["expires_on"]
        self.fx.put_policy("exceptions.yaml", {"exceptions": [row]})
        msgs = self.fx.messages()
        self.assertTrue(any("expires_on" in m for m in msgs), msgs)

    def test_expired_exception_fails(self) -> None:
        self.fx.put_policy(
            "exceptions.yaml",
            {"exceptions": [self._ex(expires_on="2020-01-01")]},
        )
        msgs = self.fx.messages()
        self.assertTrue(any("expired" in m for m in msgs), msgs)


class NdgTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_unknown_ndg_root_fails(self) -> None:
        raw = (self.fx.dir / "policy" / "ndg.yaml").read_text(encoding="utf-8")
        raw += (
            "\n  - name: All Security Groups\n"
            "    ise_root: Security Group\n"
            "    value_type: allow-list\n"
            "    allowed_values: []\n"
        )
        (self.fx.dir / "policy" / "ndg.yaml").write_text(raw, encoding="utf-8")
        msgs = self.fx.messages()
        self.assertTrue(any("unknown NDG root" in m for m in msgs), msgs)

    def test_nad_unknown_ndg_key_fails(self) -> None:
        self.fx.put_inventory(
            "nads.yaml",
            {
                "nads": [
                    {
                        "name": "lab-sw-01",
                        "ndg": {"security_group": "prod"},
                    }
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("unknown NDG root key" in m for m in msgs), msgs)

    def test_nad_value_not_on_allow_list_fails(self) -> None:
        self.fx.set_ndg(device_types=["switch"])
        self.fx.put_inventory(
            "nads.yaml",
            {
                "nads": [
                    {
                        "name": "lab-sw-01",
                        "ndg": {"device_type": "toaster"},
                    }
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("toaster" in m for m in msgs), msgs)

    def test_iso_location_pattern_passes_when_list_empty(self) -> None:
        self.fx.put_inventory(
            "nads.yaml",
            {
                "nads": [
                    {
                        "name": "lab-sw-01",
                        "ndg": {"location": "USA"},
                    }
                ]
            },
        )
        self.assertEqual(self.fx.messages(), [])

    def test_bad_iso_location_fails(self) -> None:
        self.fx.put_inventory(
            "nads.yaml",
            {
                "nads": [
                    {
                        "name": "lab-sw-01",
                        "ndg": {"location": "usa"},
                    }
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("usa" in m for m in msgs), msgs)


class HygieneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.cleanup()

    def test_uuid_in_policy_fails(self) -> None:
        self.fx.put_policy(
            "sgt.yaml",
            {
                "sgts": [
                    {
                        "name": "SGT-lab-users",
                        "state": "enabled",
                        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    }
                ]
            },
        )
        msgs = self.fx.messages()
        self.assertTrue(any("UUID" in m for m in msgs), msgs)

    def test_vip_and_vlan_names(self) -> None:
        self.fx.put_inventory(
            "nodes.yaml",
            {
                "nodes": [{"name": "ise-lab-1"}],
                "vips": [{"name": "VIP-lab-psn", "state": "enabled"}],
            },
        )
        self.fx.put_inventory(
            "vlans.yaml",
            {"vlans": [{"name": "VLAN-lab-data", "vlan_id": 20}]},
        )
        self.assertEqual(self.fx.messages(), [])


if __name__ == "__main__":
    unittest.main()