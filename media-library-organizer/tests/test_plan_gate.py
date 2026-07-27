from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plan-gate.py"


class PlanGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="media-plan.")
        self.root = Path(self.temporary.name)
        self.media = self.root / "media"
        self.source = self.media / "incoming"
        self.target = self.media / "library"
        self.source.mkdir(parents=True)
        self.target.mkdir()
        self.video = self.source / "episode.mkv"
        self.video.write_bytes(b"video")
        self.input = self.root / "input.json"
        self.plan = self.root / "plan.json"
        self.data = {
            "source_root": str(self.source),
            "media_root": str(self.media),
            "target_root": str(self.target),
            "options": {"dry_run": True, "conflict_policy": "skip"},
            "mappings": [
                {
                    "operation": "move",
                    "old": str(self.video),
                    "new": str(self.target / "S01E01.mkv"),
                }
            ],
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_gate(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stderr)
        return completed

    def build(self) -> str:
        self.input.write_text(json.dumps(self.data), encoding="utf-8")
        completed = self.run_gate(
            "build", "--input", str(self.input), "--output", str(self.plan)
        )
        return completed.stdout.strip()

    def test_build_and_validate_are_stable(self) -> None:
        plan_id = self.build()
        completed = self.run_gate("validate", "--plan", str(self.plan))
        self.assertEqual(plan_id, completed.stdout.strip())

    def test_inventory_change_invalidates_confirmation(self) -> None:
        self.build()
        self.video.write_bytes(b"changed")
        completed = self.run_gate(
            "validate", "--plan", str(self.plan), expected=2
        )
        self.assertIn("changed", completed.stderr)

    def test_target_escape_is_rejected(self) -> None:
        self.data["mappings"][0]["new"] = str(self.root / "outside.mkv")
        self.input.write_text(json.dumps(self.data), encoding="utf-8")
        completed = self.run_gate(
            "build", "--input", str(self.input), "--output", str(self.plan), expected=2
        )
        self.assertIn("escapes media boundary", completed.stderr)


if __name__ == "__main__":
    unittest.main()
