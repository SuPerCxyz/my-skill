#!/usr/bin/env python3
"""Derive a case result from contract checks and durable evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _actions import evaluate
from _case_gate import derived_diagnostic, derived_quality
from _contract import case_by_id
from _events import append_event, load_events, project_state
from _harness import (
    atomic_json, load_jsonl, local_now, object_digest, read_json, safe_component,
)
from _resources import cleanup_quality, load_resources
from _validation import valid_local_time


OBSERVATION_RESULTS = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
RESULT_LABELS = {
    "PASS": "成功",
    "FAIL": "失败",
    "UNKNOWN": "未确认",
    "NOT_APPLICABLE": "不适用",
}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--result-root", required=True, type=Path)
    result.add_argument("--case-id", required=True)
    result.add_argument("--observations", type=Path)
    result.add_argument("--stage", choices=("verdict", "result"), default="result")
    return result


def normalize_observations(
    case: dict[str, Any], observations: dict[str, Any], case_root: Path
) -> list[dict[str, Any]]:
    supplied = {
        item.get("check_id"): item
        for item in observations.get("checks", [])
        if isinstance(item, dict) and item.get("check_id")
    }
    output = []
    for definition in case["verification"]:
        item = supplied.get(definition["id"], {})
        status = str(item.get("status", "UNKNOWN")).upper()
        if status not in OBSERVATION_RESULTS:
            status = "UNKNOWN"
        actual = str(item.get("actual", "")).strip()
        evidence = str(item.get("evidence", "")).strip()
        if status in {"PASS", "FAIL"} and (not actual or not evidence):
            status = "UNKNOWN"
        if status in {"PASS", "FAIL"} and (
            "/" in evidence or evidence.endswith((".log", ".json"))
        ):
            evidence_path = case_root / evidence
            try:
                evidence_path.resolve().relative_to(case_root.resolve())
            except ValueError:
                status = "UNKNOWN"
            else:
                if not evidence_path.is_file():
                    status = "UNKNOWN"
        output.append(
            {
                "check_id": definition["id"],
                "check_type": definition["check_type"],
                "required": definition["required"],
                "check": definition.get("check", definition["id"]),
                "expected": definition["expected"],
                "actual": actual or "未记录",
                "status": status,
                "result": RESULT_LABELS[status],
                "evidence": evidence or "无",
            }
        )
    return output


def derive_checks(
    root: Path,
    case: dict[str, Any],
    commands: list[dict[str, Any]],
    observations: dict[str, Any],
    case_root: Path,
) -> list[dict[str, Any]]:
    manual = {
        item["check_id"]: item
        for item in normalize_observations(case, observations, case_root)
    }
    records = {
        item["action_id"]: item
        for item in commands
        if item.get("action_id")
    }
    output = []
    for definition in case["verification"]:
        evaluator = definition["evaluator"]
        if evaluator["type"] == "manual":
            item = manual[definition["id"]]
            actual, status, evidence = (
                item["actual"], item["status"], item["evidence"]
            )
        else:
            status, actual, evidence = evaluate(root, evaluator, records)
        output.append(
            {
                "check_id": definition["id"],
                "check_type": definition["check_type"],
                "required": definition["required"],
                "check": definition.get("check", definition["id"]),
                "expected": definition["expected"],
                "actual": actual,
                "status": status,
                "result": RESULT_LABELS[status],
                "evidence": evidence,
                "evaluator": evaluator,
            }
        )
    return output


def derive_functional(checks: list[dict[str, Any]]) -> str:
    required = [
        item
        for item in checks
        if item["check_type"] == "functional" and item["required"]
    ]
    return "PASS" if required and all(item["status"] == "PASS" for item in required) else "FAIL"


def valid_command(root: Path, record: dict[str, Any]) -> bool:
    fields = (
        "command_id",
        "step_id",
        "start_local",
        "end_local",
        "duration_ms",
        "return_code",
        "stdout_path",
        "stderr_path",
    )
    if any(field not in record for field in fields):
        return False
    if not isinstance(record["duration_ms"], int) or record["duration_ms"] < 0:
        return False
    if not valid_local_time(record["start_local"]) or not valid_local_time(record["end_local"]):
        return False
    return all((root / record[field]).is_file() for field in ("stdout_path", "stderr_path"))


def derive_timing(
    root: Path,
    case: dict[str, Any],
    state: dict[str, Any],
    commands: list[dict[str, Any]],
) -> str:
    by_step: dict[str, list[dict[str, Any]]] = {}
    for record in commands:
        by_step.setdefault(record.get("step_id", ""), []).append(record)
    statuses = state["cases"][case["id"]]["step_statuses"]
    for step in case["actions"]:
        if step["phase"] == "APPLY_CLEANUP_POLICY":
            continue
        if step["id"] not in statuses:
            return "INVALID"
        if statuses[step["id"]].get("status") in {
            "SKIPPED_BY_PLAN", "NOT_APPLICABLE",
        }:
            if not all(
                statuses[step["id"]].get(field)
                for field in ("start_local", "end_local")
            ):
                return "INVALID"
            continue
        records = by_step.get(step["id"], [])
        if not records or not all(valid_command(root, record) for record in records):
            return "INVALID"
    return "VALID"


def derive_evidence(
    case: dict[str, Any], case_root: Path
) -> tuple[str, list[dict[str, Any]]]:
    requirement = case["log_requirement"]
    if requirement == "none":
        return "NOT_APPLICABLE", []
    collection = read_json(case_root / "logs" / "collection-status.json", {})
    logs = collection.get("evidence", []) if isinstance(collection, dict) else []
    status = collection.get("evidence_status") if isinstance(collection, dict) else None
    allowed = {"COMPLETE", "PARTIAL", "MISSING", "INVALID"}
    if requirement == "optional" and not collection:
        return "OPTIONAL_NOT_COLLECTED", []
    if status not in allowed:
        return "MISSING" if requirement == "required" else "OPTIONAL_NOT_COLLECTED", logs
    return status, logs


def case_times(
    contract: dict[str, Any], commands: list[dict[str, Any]]
) -> tuple[str, str]:
    starts = sorted(
        record["start_local"] for record in commands if valid_local_time(record.get("start_local"))
    )
    ends = sorted(
        record["end_local"] for record in commands if valid_local_time(record.get("end_local"))
    )
    fallback = contract["created_local"]
    return (starts[0] if starts else fallback, ends[-1] if ends else fallback)


def finalize_result(
    root: Path,
    contract: dict[str, Any],
    case: dict[str, Any],
    state: dict[str, Any],
) -> None:
    case_id = case["id"]
    if state["cases"][case_id]["phase"] != "FINALIZE_RESULT":
        raise ValueError("case must be in FINALIZE_RESULT phase")
    case_root = root / "cases" / case_id
    result_path = case_root / "result.json"
    if result_path.exists():
        raise ValueError("result.json already exists")
    verdict = read_json(case_root / "case-verdict.json")
    if not verdict or not verdict.get("derived_by_harness"):
        raise ValueError("case-verdict.json missing")
    resources = load_resources(case_root / "resources.json")
    cleanup_policy = (
        contract["cleanup_policy"]
        if case["cleanup_policy"] == "inherit"
        else case["cleanup_policy"]
    )
    cleanup = cleanup_quality(resources, cleanup_policy)
    result = {
        **verdict,
        "derivation_version": contract["harness_version"],
        "scenario_key": case["scenario_key"],
        "title": case["title"],
        "requirement_summary": case["requirement_summary"],
        "objective": case["objective"],
        "log_requirement": case["log_requirement"],
        "cleanup_status": cleanup,
        "execution_quality": derived_quality(
            verdict["timing_status"], verdict["evidence_status"], cleanup
        ),
        "ended_local": local_now(contract["timezone"]),
        "run_fingerprint": {
            "contract_sha256": contract["contract_sha256"],
            "profile_sha256": contract["environment_profile_sha256"],
            "skill_sha256": contract["skill_sha256"],
        },
        "remaining_resources": [
            item for item in resources if item.get("final_state") != "DELETED"
        ],
    }
    atomic_json(result_path, result)
    append_event(
        root, contract["timezone"], "CASE_RESULT_DERIVED", case_id,
        payload={
            **{
                key: result[key] for key in (
                    "functional_status", "timing_status", "evidence_status",
                    "cleanup_status", "diagnostic_status", "execution_quality",
                )
            },
            "result_sha256": object_digest(result),
        },
    )


def finalize(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    if not contract:
        raise ValueError("execution-contract.json not found")
    case_id = safe_component(args.case_id, "case ID")
    case = case_by_id(contract, case_id)
    events = load_events(root / "events.jsonl")
    state = project_state(contract, events)
    case_root = root / "cases" / case_id
    if args.stage == "verdict":
        if state["cases"][case_id]["phase"] != "DERIVE_VERDICT":
            raise ValueError("case must be in DERIVE_VERDICT phase")
        path = case_root / "case-verdict.json"
        if path.exists():
            raise ValueError("case-verdict.json already exists")
        observations = read_json(
            args.observations or case_root / "observations.json", {}
        )
        if not isinstance(observations, dict):
            raise ValueError("observations must be a JSON object")
        commands = load_jsonl(case_root / "commands.jsonl")
        checks = derive_checks(root, case, commands, observations, case_root)
        timing = derive_timing(root, case, state, commands)
        evidence, logs = derive_evidence(case, case_root)
        started, ended = case_times(contract, commands)
        verdict = {
            "schema_version": contract["schema_version"],
            "derived_by_harness": True,
            "contract_sha256": contract["contract_sha256"],
            "case_id": case_id,
            "functional_status": derive_functional(checks),
            "timing_status": timing,
            "evidence_status": evidence,
            "diagnostic_status": derived_diagnostic(
                checks, list(state["cases"][case_id]["step_statuses"].values())
            ),
            "started_local": started,
            "verdict_ended_local": ended,
            "timezone": contract["timezone"],
            "checks": checks,
            "logs": logs,
        }
        atomic_json(path, verdict)
        append_event(
            root, contract["timezone"], "CASE_VERDICT_DERIVED", case_id,
            payload={
                **{
                    key: verdict[key] for key in (
                        "functional_status", "timing_status",
                        "evidence_status", "diagnostic_status",
                    )
                },
                "verdict_sha256": object_digest(verdict),
            },
        )
        return
    finalize_result(root, contract, case, state)


def main() -> int:
    args = parser().parse_args()
    try:
        finalize(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"finalize-case error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
