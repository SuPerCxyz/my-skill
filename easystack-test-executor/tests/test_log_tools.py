from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from _log_tools import redact_file, related_evidence  # noqa: E402


class LogToolsTest(unittest.TestCase):
    def test_redaction_and_end_window_filter(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ete-log.") as temporary:
            raw = Path(temporary) / "worker.log"
            raw.write_text(
                "2026-07-24T06:00:00Z OS_PASSWORD=secret "
                "req-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee clone\n"
                "2026-07-24T07:00:00Z "
                "req-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee late\n"
                "2026-07-24T06:10:00Z "
                "req-11111111-2222-3333-4444-555555555555 unrelated\n",
                encoding="utf-8",
            )
            redact_file(raw)
            text = raw.read_text(encoding="utf-8")
            self.assertNotIn("secret", text)
            evidence = related_evidence(
                raw,
                "logs/raw/worker.log",
                {"name": "cinder-volume", "selector": "component=volume"},
                {
                    "pod": "worker-0", "pod_uid": "pod-uid",
                    "container": "cinder-volume", "container_id": "container-id",
                },
                {"req-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
                "Asia/Shanghai",
                "2026-07-24T06:30:00Z",
            )
            self.assertEqual(1, len(evidence))
            self.assertEqual(
                "2026-07-24T14:00:00.000+08:00",
                evidence[0]["timestamp_local"],
            )
            self.assertEqual("pod-uid", evidence[0]["pod_uid"])


if __name__ == "__main__":
    unittest.main()
