"""Phase 9 drift comparison for SGTs and EIGs. No live ISE."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from drift import desired_sgts, names_only, report_family  # noqa: E402  # type: ignore[import-not-found]


class DesiredRows(unittest.TestCase):
    def test_desired_sgts_rejects_missing_name(self) -> None:
        with self.assertRaises(SystemExit):
            desired_sgts([{"value": 1001}])

    def test_desired_sgts_rejects_non_int_value(self) -> None:
        with self.assertRaises(SystemExit):
            desired_sgts([{"name": "SGT_lab_bootstrap", "value": "1001"}])

    def test_desired_sgts_builds_map(self) -> None:
        rows = [
            {"name": "SGT_lab_bootstrap", "value": 1001},
            {"name": "SGT_lab_users", "value": 1010},
        ]
        self.assertEqual(
            desired_sgts(rows),
            {"SGT_lab_bootstrap": 1001, "SGT_lab_users": 1010},
        )

    def test_desired_eigs_builds_map(self) -> None:
        rows = [
            {"name": "EIG-printers", "parent": "Endpoint Identity Groups"},
            {"name": "EIG-guest", "parent": "Endpoint Identity Groups"},
        ]
        self.assertEqual(
            names_only(rows, "policy/eig.yaml"),
            {"EIG-printers": None, "EIG-guest": None},
        )


class ReportFamily(unittest.TestCase):
    def _capture(self, label: str, desired: dict, live: dict, prefix: str) -> tuple[str, bool]:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            clean = report_family(label, desired, live, prefix, set())
        return buf.getvalue(), clean

    def test_clean(self) -> None:
        desired = {"SGT_lab_bootstrap": 1001}
        live = {"SGT_lab_bootstrap": 1001}
        text, clean = self._capture("SGT", desired, live, "SGT_")
        self.assertTrue(clean)
        self.assertIn("owned clean", text)
        self.assertNotIn("missing", text)
        self.assertNotIn("extra", text)

    def test_missing(self) -> None:
        desired = {"SGT_lab_bootstrap": 1001, "SGT_lab_users": 1010}
        live = {"SGT_lab_bootstrap": 1001}
        text, clean = self._capture("SGT", desired, live, "SGT_")
        self.assertFalse(clean)
        self.assertIn("missing on ISE: SGT_lab_users", text)

    def test_extra_with_prefix(self) -> None:
        desired = {"SGT_lab_bootstrap": 1001}
        live = {"SGT_lab_bootstrap": 1001, "SGT_old_gui": 999}
        text, clean = self._capture("SGT", desired, live, "SGT_")
        self.assertFalse(clean)
        self.assertIn("extra on ISE:   SGT_old_gui", text)

    def test_extra_without_prefix_is_non_owned(self) -> None:
        desired = {"SGT_lab_bootstrap": 1001}
        live = {"SGT_lab_bootstrap": 1001, "Unknown": 0}
        text, clean = self._capture("SGT", desired, live, "SGT_")
        self.assertFalse(clean)
        self.assertIn("non-owned", text)
        self.assertIn("Unknown", text)

    def test_value_mismatch(self) -> None:
        desired = {"SGT_lab_bootstrap": 1001}
        live = {"SGT_lab_bootstrap": 1002}
        text, clean = self._capture("SGT", desired, live, "SGT_")
        self.assertFalse(clean)
        self.assertIn("value mismatch: SGT_lab_bootstrap", text)
        self.assertIn("1001", text)
        self.assertIn("1002", text)

    def test_eig_name_only(self) -> None:
        desired = {"EIG-printers": None}
        live = {"EIG-printers": None, "Unknown": None}
        text, clean = self._capture("EIG", desired, live, "EIG-")
        self.assertFalse(clean)
        self.assertIn("owned clean", text)


if __name__ == "__main__":
    unittest.main()
