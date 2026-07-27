from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "validate-evals.py"


class EvalDefinitionTest(unittest.TestCase):
    def run_validator(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stderr)
        return completed

    def test_definitions_are_valid(self) -> None:
        completed = self.run_validator()
        self.assertIn('"valid": true', completed.stdout)

    def test_three_outputs_per_eval_are_required(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ete-evals.") as temporary:
            completed = self.run_validator(
                "--results", temporary, expected=1
            )
        self.assertIn("missing model output", completed.stderr)


if __name__ == "__main__":
    unittest.main()
