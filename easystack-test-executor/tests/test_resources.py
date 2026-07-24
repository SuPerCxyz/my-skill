from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from _resources import create_resource, reconcile_resources, update_resource  # noqa: E402


class ResourceLedgerTest(unittest.TestCase):
    def test_dual_ledger_is_consistent_and_creation_is_immutable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ete-resource.") as temporary:
            root = Path(temporary)
            case_root = root / "cases" / "CASE-01"
            case_root.mkdir(parents=True)
            (root / "resources-all.json").write_text("[]\n", encoding="utf-8")
            (case_root / "resources.json").write_text("[]\n", encoding="utf-8")
            created = create_resource(
                root,
                "CASE-01",
                {
                    "type": "Volume",
                    "id": "volume-id",
                    "name": "test-case-01-volume-a1b2",
                    "owning_step": "STEP-01",
                },
                "2026-07-24T12:00:00+08:00",
            )
            update_resource(
                root,
                "CASE-01",
                "volume-id",
                {"cleanup_result": "DELETED", "final_state": "ABSENT"},
            )
            self.assertEqual([], reconcile_resources(root))
            items = json.loads(
                (case_root / "resources.json").read_text(encoding="utf-8")
            )
            self.assertEqual(created["created_local"], items[0]["created_local"])
            with self.assertRaises(ValueError):
                update_resource(
                    root,
                    "CASE-01",
                    "volume-id",
                    {"name": "changed"},
                )


if __name__ == "__main__":
    unittest.main()
