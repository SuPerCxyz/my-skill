from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "validate-profile.py"
)
COMPILE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "compile-profile.py"
)
PROFILE_ROOT = Path("/tmp/easystack-test-executor-profiles")


def profile() -> dict:
    now = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
    return {
        "profile_version": 2,
        "captured_at_local": now,
        "last_verified_at_local": now,
        "environment": {
            "target": "test-env",
            "region": "RegionOne",
            "timezone": "Asia/Shanghai",
        },
        "authentication": {
            "project_id": "project-id",
            "execution_location": "busybox-openstack",
        },
        "kubernetes": {"namespace": "openstack"},
        "fingerprint": {
            "cluster_uid": "cluster-id",
            "openstack_release": "release",
            "openstackclient_version": "1.0",
            "backend_fingerprint": "backend-hash",
        },
        "nova": {
            "images": [{"id": "image-id"}],
            "flavors": [{"id": "flavor-id"}],
            "networks": [{"id": "network-id"}],
        },
        "cinder": {
            "volume_types": [{"name": "hdd"}],
            "backends": [{"name": "backend"}],
        },
    }


class ProfileTest(unittest.TestCase):
    def setUp(self) -> None:
        PROFILE_ROOT.mkdir(mode=0o700, exist_ok=True)
        os.chmod(PROFILE_ROOT, 0o700)
        self.directory = Path(
            tempfile.mkdtemp(
                prefix="ete-profile.",
                dir=PROFILE_ROOT,
            )
        )
        os.chmod(self.directory, 0o700)

    def tearDown(self) -> None:
        for path in self.directory.iterdir():
            path.unlink()
        self.directory.rmdir()

    def validate(self, data: dict, expected: int) -> subprocess.CompletedProcess[str]:
        path = self.directory / "profile.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        os.chmod(path, 0o600)
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--profile", str(path)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stderr)
        return completed

    def test_valid_profile_prints_stable_key(self) -> None:
        completed = self.validate(profile(), 0)
        self.assertIn("profile_key=env-", completed.stdout)

    def test_plaintext_secret_is_rejected(self) -> None:
        data = profile()
        data["authentication"]["password"] = "do-not-store"
        completed = self.validate(data, 1)
        self.assertIn("plaintext secrets", completed.stderr)

    def test_compile_profile_uses_stable_tmp_path(self) -> None:
        source = self.directory / "capture.json"
        source.write_text(json.dumps(profile()), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(COMPILE_SCRIPT), "--input", str(source)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        destination = Path(completed.stdout.strip())
        self.assertEqual(PROFILE_ROOT, destination.parent)
        self.assertEqual(0o600, destination.stat().st_mode & 0o777)
        destination.unlink()


if __name__ == "__main__":
    unittest.main()
