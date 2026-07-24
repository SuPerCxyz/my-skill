#!/usr/bin/env python3
"""Execute exactly one immutable V3 contract action."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from _actions import bind_action, bind_text, capture_resources
from _artifacts import register_artifact
from _contract import case_by_id
from _events import append_event, load_events, project_state
from _harness import local_now, read_json, redact, safe_component
from _projections import sync_event_views
from _runner import PREVIEW_LIMIT, execute


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--result-root", required=True, type=Path)
    result.add_argument("--case-id", required=True)
    result.add_argument("--action-id", required=True)
    result.add_argument("--attempt", default="attempt-01")
    return result


def context(
    root: Path, case_id: str, action_id: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = read_json(root / "execution-contract.json")
    if not contract or contract.get("schema_version") != 3:
        raise ValueError("run-action requires a V3 execution contract")
    case = case_by_id(contract, case_id)
    action = next(
        (item for item in case["actions"] if item["id"] == action_id), None
    )
    if not action:
        raise ValueError(f"action not in contract: {action_id}")
    state = project_state(contract, load_events(root / "events.jsonl"))
    current = state["cases"][case_id]
    if current["phase"] != action["phase"]:
        raise ValueError(
            f"action phase is {action['phase']}, current phase is {current['phase']}"
        )
    expected = next(
        (
            item["id"] for item in case["actions"]
            if item["phase"] == current["phase"]
            and item["id"] not in current["step_statuses"]
        ),
        None,
    )
    if expected != action_id:
        raise ValueError(f"next action is {expected}, not {action_id}")
    return contract, case, action


def resource_records(
    root: Path,
    case_id: str,
    action_id: str,
    captures: list[dict[str, Any]],
    timestamp: str,
) -> list[dict[str, Any]]:
    existing = read_json(root / "resources-all.json", [])
    existing_ids = {item["id"] for item in existing}
    output = []
    for item in captures:
        if item["id"] in existing_ids:
            raise ValueError(f"captured resource already exists: {item['id']}")
        output.append(
            {
                **item,
                "case_id": case_id,
                "owning_step": action_id,
                "created_local": timestamp,
                "cleanup_result": "PENDING",
                "final_state": "PRESENT",
            }
        )
    return output


def run(args: argparse.Namespace) -> int:
    root = args.result_root.resolve()
    case_id = safe_component(args.case_id, "case ID")
    action_id = safe_component(args.action_id, "action ID")
    attempt = safe_component(args.attempt, "attempt")
    contract, case, action = context(root, case_id, action_id)
    resources = read_json(root / "resources-all.json", [])
    argv = bind_action(contract, action, resources)
    timeout = action.get("timeout_seconds") or case.get(
        "timeouts", {}
    ).get("operation_seconds", 1800)
    command_id = f"cmd-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    output_root = root / "cases" / case_id / attempt / action["kind"]
    stdout_path = output_root / f"{action_id}.{command_id}.stdout.log"
    stderr_path = output_root / f"{action_id}.{command_id}.stderr.log"
    started = local_now(contract["timezone"])
    monotonic_start = time.monotonic_ns()
    return_code, timed_out, stdout, stderr, request_ids = execute(
        argv, None, timeout, stdout_path, stderr_path
    )
    ended = local_now(contract["timezone"])
    duration_ms = (time.monotonic_ns() - monotonic_start) // 1_000_000
    allowed_codes = action["expected"]["return_codes"]
    status = "PASS" if not timed_out and return_code in allowed_codes else "FAIL"
    postprocess_errors: list[str] = []
    artifacts = [
        register_artifact(
            root, path, case_id=case_id, action_id=action_id,
            command_id=command_id, artifact_type=artifact_type,
        )
        for path, artifact_type in (
            (stdout_path, "command_stdout"),
            (stderr_path, "command_stderr"),
        )
    ]
    binding_context = {
        "profile": contract["environment_profile"],
        "resource": {
            item["key"]: item for item in resources if item.get("key")
        },
        "run": {"id": contract["run_id"]},
    }
    for spec in action.get("capture", {}).get("artifacts", []):
        pattern = bind_text(spec["glob"], binding_context)
        matches = [path for path in root.glob(pattern) if path.is_file()]
        if spec.get("required", True) and not matches:
            status = "FAIL"
            postprocess_errors.append(f"required artifact missing: {pattern}")
        for path in matches:
            if path in {stdout_path, stderr_path}:
                continue
            artifacts.append(
                register_artifact(
                    root, path, case_id=case_id, action_id=action_id,
                    command_id=command_id,
                    artifact_type=spec.get("type", "action_artifact"),
                )
            )
    captured = []
    if status == "PASS":
        try:
            captured = capture_resources(action, stdout, stderr)
        except (ValueError, json.JSONDecodeError) as error:
            status = "FAIL"
            postprocess_errors.append(str(error))
    try:
        created = resource_records(root, case_id, action_id, captured, ended)
    except ValueError as error:
        created = []
        status = "FAIL"
        postprocess_errors.append(str(error))
    updates = []
    if status == "PASS" and action["kind"] == "cleanup":
        by_key = {item.get("key"): item for item in resources}
        for key in action.get("cleanup_resources", []):
            if key not in by_key:
                status = "FAIL"
                postprocess_errors.append(f"cleanup resource key not found: {key}")
                continue
            updates.append(
                {
                    **by_key[key],
                    "cleanup_result": "DELETED",
                    "final_state": "DELETED",
                }
            )
    record = {
        "command_id": command_id,
        "case_id": case_id,
        "step_id": action_id,
        "action_id": action_id,
        "attempt": attempt,
        "kind": action["kind"],
        "description": action["description"],
        "command": redact(shlex.join(argv)),
        "bound_argv_sha256": hashlib.sha256(
            json.dumps(argv, ensure_ascii=False).encode()
        ).hexdigest(),
        "execute_location": action.get("execute_location", "local"),
        "start_local": started,
        "end_local": ended,
        "timezone": contract["timezone"],
        "duration_ms": duration_ms,
        "timeout_seconds": timeout,
        "timed_out": timed_out,
        "return_code": return_code,
        "allowed_return_codes": allowed_codes,
        "status": status,
        "result": "成功" if status == "PASS" else "失败",
        "request_ids": sorted(request_ids),
        "stdout_path": stdout_path.relative_to(root).as_posix(),
        "stderr_path": stderr_path.relative_to(root).as_posix(),
        "artifacts": artifacts,
        "postprocess_errors": postprocess_errors,
    }
    append_event(
        root, contract["timezone"], "ACTION_COMPLETED", case_id, action_id,
        {
            "command": record,
            "resources": created,
            "resource_updates": updates,
            "status": status,
        },
    )
    sync_event_views(root)
    from checkpoint import write_projection

    write_projection(root, contract)
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    if len(stdout) >= PREVIEW_LIMIT or len(stderr) >= PREVIEW_LIMIT:
        print("\n[output preview truncated; see evidence files]", file=sys.stderr)
    return 0 if status == "PASS" else 1


def main() -> int:
    args = parser().parse_args()
    try:
        return run(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"run-action error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
