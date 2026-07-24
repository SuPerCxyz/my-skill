from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"


def plan() -> dict:
    return {
        "impact_analysis": {
            "id": "IMPACT-01",
            "obligations": [{"id": "IMPACT-01", "services": ["cinder"]}],
        },
        "authorization": {
            "scope": "test project",
            "destructive_operations": ["volume.force_delete"],
        },
        "cases": [
            {
                "id": "CASE-01",
                "scenario_key": "volume-basic",
                "title": "创建并查询云硬盘",
                "requirement_summary": "验证云硬盘创建后能够查询到预期状态",
                "domain": "cinder",
                "objective": "验证执行契约和结果自动派生",
                "impact_refs": ["IMPACT-01"],
                "capability_status": "SUPPORTED",
                "destructive_operations": ["volume.force_delete"],
                "dependencies": [],
                "actions": [
                    {
                        "id": "STEP-01",
                        "phase": "EXECUTE",
                        "kind": "openstack",
                        "description": "模拟创建云硬盘",
                        "command": [
                            sys.executable,
                            "-c",
                            "import json; print(json.dumps("
                            "{'id':'volume-001','name':'ete-volume'}))",
                        ],
                        "expected": {"return_codes": [0]},
                        "capture": {
                            "resources": [
                                {
                                    "key": "volume",
                                    "type": "Volume",
                                    "id": {
                                        "source": "stdout",
                                        "format": "json",
                                        "path": "id",
                                    },
                                    "name": {
                                        "source": "stdout",
                                        "format": "json",
                                        "path": "name",
                                    },
                                }
                            ]
                        },
                        "timeout_seconds": 5,
                    },
                    {
                        "id": "STEP-02",
                        "phase": "VERIFY",
                        "kind": "openstack",
                        "description": "模拟查询云硬盘",
                        "command": [
                            sys.executable,
                            "-c",
                            "import json; print(json.dumps({'status':'available'}))",
                        ],
                        "expected": {"return_codes": [0]},
                        "timeout_seconds": 5,
                    },
                    {
                        "id": "STEP-03",
                        "phase": "APPLY_CLEANUP_POLICY",
                        "kind": "cleanup",
                        "description": "模拟删除云硬盘",
                        "command": [sys.executable, "-c", "raise SystemExit(0)"],
                        "expected": {"return_codes": [0]},
                        "cleanup_resources": ["volume"],
                        "destructive_operation": "volume.force_delete",
                    },
                ],
                "verification": [
                    {
                        "id": "CHECK-01",
                        "check_type": "functional",
                        "required": True,
                        "check": "云硬盘状态",
                        "expected": "状态为 available",
                        "evaluator": {
                            "type": "json_path",
                            "action_id": "STEP-02",
                            "source": "stdout",
                            "path": "status",
                            "value": "available",
                        },
                    }
                ],
                "log_requirement": "none",
                "log_targets": [],
                "cleanup_policy": "inherit",
            }
        ]
    }


class HarnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ete-test.")
        self.base = Path(self.temporary.name)
        self.plan_path = self.base / "plan.json"
        plan_data = plan()
        if self._testMethodName == "test_failed_check_derives_functional_failure":
            plan_data["cases"][0]["actions"][1]["command"][-1] = (
                "import json; print(json.dumps({'status':'error'}))"
            )
        if self._testMethodName == "test_timeout_is_recorded_without_overwriting_output":
            plan_data["cases"][0]["actions"][0]["command"] = [
                sys.executable, "-c", "import time; time.sleep(5)"
            ]
            plan_data["cases"][0]["actions"][0]["timeout_seconds"] = 1
        if self._testMethodName == "test_expected_nonzero_is_action_pass":
            plan_data["cases"][0]["actions"][1]["command"] = [
                sys.executable, "-c", "raise SystemExit(4)"
            ]
            plan_data["cases"][0]["actions"][1]["expected"] = {
                "return_codes": [4]
            }
        if self._testMethodName == "test_preserve_all_skips_cleanup":
            plan_data["cases"][0]["cleanup_policy"] = "preserve_all"
        self.plan_path.write_text(
            json.dumps(plan_data, ensure_ascii=False), encoding="utf-8"
        )
        self.root = self.base / "run"
        profile_root = Path("/tmp/easystack-test-executor-profiles")
        profile_root.mkdir(mode=0o700, exist_ok=True)
        profile_root.chmod(0o700)
        self.profile_path = profile_root / f"test-{self.base.name}.json"
        now = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()
        profile = {
            "profile_version": 2,
            "captured_at_local": now,
            "last_verified_at_local": now,
            "environment": {
                "target": "unit-test", "region": "RegionOne",
                "timezone": "Asia/Shanghai",
            },
            "authentication": {
                "project_id": "project-001", "execution_location": "local",
            },
            "kubernetes": {"namespace": "openstack"},
            "nova": {
                "images": [{"id": "image-001"}],
                "flavors": [{"id": "flavor-001"}],
                "networks": [{"id": "network-001"}],
            },
            "cinder": {
                "volume_types": [{"name": "hdd"}],
                "backends": [{"name": "backend-001"}],
            },
            "fingerprint": {
                "cluster_uid": "cluster-001", "openstack_release": "test",
                "openstackclient_version": "test",
                "backend_fingerprint": "backend-hash",
            },
        }
        self.profile_path.write_text(json.dumps(profile), encoding="utf-8")
        self.profile_path.chmod(0o600)
        self.execute(
            "compile-plan.py",
            "--plan",
            str(self.plan_path),
            "--result-root",
            str(self.root),
            "--run-id",
            "R20260724120000",
            "--timezone",
            "Asia/Shanghai",
            "--profile",
            str(self.profile_path),
        )

    def tearDown(self) -> None:
        self.profile_path.unlink(missing_ok=True)
        self.temporary.cleanup()

    def execute(
        self, script: str, *arguments: str, expected: int = 0
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            expected,
            completed.returncode,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return completed

    def next(self) -> dict:
        completed = self.execute(
            "checkpoint.py", "next", "--result-root", str(self.root)
        )
        return json.loads(completed.stdout)

    def advance(self) -> None:
        instruction = self.next()
        self.execute(
            "checkpoint.py",
            "advance",
            "--result-root",
            str(self.root),
            "--case-id",
            instruction["case_id"],
        )

    def run_current_action(self, expected: int = 0) -> None:
        instruction = self.next()
        self.execute(
            "run-action.py",
            "--result-root",
            str(self.root),
            "--case-id",
            instruction["case_id"],
            "--action-id",
            instruction["planned_action"]["id"],
            expected=expected,
        )

    def complete_until_verdict(self) -> None:
        while True:
            instruction = self.next()
            if instruction["current_phase"] == "DERIVE_VERDICT":
                return
            if instruction["allowed_action"] == "run_action":
                self.run_current_action()
            else:
                self.advance()

    def finish(self) -> None:
        self.complete_until_verdict()
        self.execute(
            "finalize-case.py",
            "--result-root",
            str(self.root),
            "--case-id",
            "CASE-01",
            "--stage",
            "verdict",
        )
        self.advance()
        instruction = self.next()
        if instruction["allowed_action"] == "run_action":
            self.run_current_action()
        elif instruction["allowed_action"] == "skip_action":
            completed = subprocess.run(
                instruction["launcher_argv"], text=True, capture_output=True
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
        self.advance()
        self.execute(
            "finalize-case.py", "--result-root", str(self.root),
            "--case-id", "CASE-01", "--stage", "result",
        )
        while self.next()["allowed_action"] != "run_complete":
            self.advance()
        self.execute("render-report.py", "--result-root", str(self.root))

    def test_full_run_passes_validation(self) -> None:
        self.finish()
        result = json.loads(
            (self.root / "cases" / "CASE-01" / "result.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("PASS", result["functional_status"])
        self.assertEqual("VALID", result["timing_status"])
        self.assertEqual("NOT_APPLICABLE", result["evidence_status"])
        self.execute("validate-run.py", "--result-root", str(self.root))

    def test_failed_check_derives_functional_failure(self) -> None:
        self.finish()
        result = json.loads(
            (self.root / "cases" / "CASE-01" / "result.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("FAIL", result["functional_status"])
        summary = (self.root / "summary.md").read_text(encoding="utf-8")
        self.assertIn("| CASE-01 | 创建并查询云硬盘 |", summary)
        self.assertIn("| 失败 | [查看](#case-case-01) |", summary)

    def test_timeout_is_recorded_without_overwriting_output(self) -> None:
        while self.next()["current_phase"] != "EXECUTE":
            self.advance()
        instruction = self.next()
        completed = self.execute(
            "run-action.py",
            "--result-root",
            str(self.root),
            "--case-id",
            "CASE-01",
            "--action-id",
            instruction["planned_action"]["id"],
            expected=1,
        )
        self.assertEqual("", completed.stdout)
        records = [
            json.loads(line)
            for line in (
                self.root / "cases" / "CASE-01" / "commands.jsonl"
            ).read_text(encoding="utf-8").splitlines()
        ]
        self.assertTrue(records[0]["timed_out"])
        self.assertEqual(124, records[0]["return_code"])
        self.assertTrue((self.root / records[0]["stdout_path"]).exists())

    def test_contract_tampering_is_detected(self) -> None:
        contract_path = self.root / "execution-contract.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["timezone"] = "UTC"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        completed = self.execute(
            "validate-run.py",
            "--result-root",
            str(self.root),
            expected=1,
        )
        self.assertIn("execution contract content or digest changed", completed.stderr)

    def test_expected_nonzero_is_action_pass(self) -> None:
        while self.next()["current_phase"] != "EXECUTE":
            self.advance()
        self.run_current_action()
        self.advance()
        while self.next()["current_phase"] != "VERIFY":
            self.advance()
        self.run_current_action()
        record = json.loads(
            (
                self.root / "cases" / "CASE-01" / "commands.jsonl"
            ).read_text(encoding="utf-8").splitlines()[-1]
        )
        self.assertEqual(4, record["return_code"])
        self.assertEqual("PASS", record["status"])

    def test_artifact_tampering_is_detected(self) -> None:
        self.finish()
        record = json.loads(
            (
                self.root / "cases" / "CASE-01" / "commands.jsonl"
            ).read_text(encoding="utf-8").splitlines()[0]
        )
        (self.root / record["stdout_path"]).write_text("tampered\n", encoding="utf-8")
        completed = self.execute(
            "validate-run.py", "--result-root", str(self.root), expected=1
        )
        self.assertIn("artifact", completed.stderr)

    def test_aborted_run_renders_partial_report(self) -> None:
        self.execute(
            "checkpoint.py", "abort", "--result-root", str(self.root),
            "--reason", "test interruption",
        )
        self.execute(
            "render-report.py", "--result-root", str(self.root), "--allow-partial"
        )
        summary = (self.root / "summary.md").read_text(encoding="utf-8")
        self.assertIn("任务状态为 NOT_RUN", summary)

    def test_preserve_all_skips_cleanup(self) -> None:
        self.finish()
        result = json.loads(
            (
                self.root / "cases" / "CASE-01" / "result.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual("PRESERVED", result["cleanup_status"])
        resources = json.loads(
            (
                self.root / "cases" / "CASE-01" / "resources.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual("PRESERVED", resources[0]["cleanup_result"])


if __name__ == "__main__":
    unittest.main()
