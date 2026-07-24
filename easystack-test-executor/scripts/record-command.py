#!/usr/bin/env python3
"""Execute one contract step with timeout and immutable evidence paths."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, TextIO

from _contract import case_by_id
from _events import append_event, load_events, project_state
from _harness import append_jsonl, local_now, read_json, redact, safe_component


REQUEST_ID = re.compile(r"\breq-[0-9a-f-]{16,}\b", re.IGNORECASE)
PREVIEW_LIMIT = 64 * 1024


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--result-root", required=True, type=Path)
    result.add_argument("--case-id", required=True)
    result.add_argument("--step-id", required=True)
    result.add_argument("--description")
    result.add_argument("--execute-location", default="local")
    result.add_argument("--attempt", default="attempt-01")
    result.add_argument("--timeout-seconds", type=int)
    result.add_argument("--cwd", type=Path)
    result.add_argument("command", nargs=argparse.REMAINDER)
    return result


def step_context(root: Path, case_id: str, step_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = read_json(root / "execution-contract.json")
    if not contract:
        raise ValueError("execution-contract.json not found")
    raise ValueError(
        "record-command is disabled; use run-action.py for V3 and keep V2 read-only"
    )
    case = case_by_id(contract, case_id)
    failed_dependencies = [
        dependency
        for dependency in case.get("dependencies", [])
        if read_json(root / "cases" / dependency / "result.json", {}).get(
            "functional_status"
        )
        != "PASS"
    ]
    if failed_dependencies:
        raise ValueError(
            f"failed dependencies require SKIPPED_BY_PLAN: {','.join(failed_dependencies)}"
        )
    step = next((item for item in case["actions"] if item["id"] == step_id), None)
    if not step:
        raise ValueError(f"step not in contract: {step_id}")
    state = project_state(contract, load_events(root / "events.jsonl"))
    phase = state["cases"][case_id]["phase"]
    if phase != step["phase"]:
        raise ValueError(f"step phase is {step['phase']}, current phase is {phase}")
    statuses = state["cases"][case_id]["step_statuses"]
    expected = next(
        (
            item["id"]
            for item in case["actions"]
            if item["phase"] == phase and item["id"] not in statuses
        ),
        None,
    )
    if step_id != expected:
        raise ValueError(f"next planned step is {expected}, not {step_id}")
    if step_id in state["cases"][case_id]["step_statuses"]:
        raise ValueError(f"step already terminal: {step_id}")
    return contract, case, step


def pump(
    source: TextIO,
    destination: TextIO,
    preview: list[str],
    preview_size: list[int],
    request_ids: set[str],
) -> None:
    for raw_line in source:
        line = redact(raw_line)
        destination.write(line)
        destination.flush()
        request_ids.update(REQUEST_ID.findall(line))
        remaining = PREVIEW_LIMIT - preview_size[0]
        if remaining > 0:
            preview.append(line[:remaining])
            preview_size[0] += min(len(line), remaining)


def terminate(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    except ProcessLookupError:
        pass


def execute(
    command: list[str],
    cwd: Path | None,
    timeout: int,
    stdout_path: Path,
    stderr_path: Path,
) -> tuple[int, bool, str, str, set[str]]:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    request_ids: set[str] = set()
    stdout_preview: list[str] = []
    stderr_preview: list[str] = []
    stdout_size = [0]
    stderr_size = [0]
    with stdout_path.open("x", encoding="utf-8") as stdout_file, stderr_path.open(
        "x", encoding="utf-8"
    ) as stderr_file:
        os.chmod(stdout_path, 0o600)
        os.chmod(stderr_path, 0o600)
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                start_new_session=True,
            )
        except OSError as error:
            stderr_file.write(redact(str(error)) + "\n")
            return 127, False, "", redact(str(error)), request_ids
        threads = [
            threading.Thread(
                target=pump,
                args=(process.stdout, stdout_file, stdout_preview, stdout_size, request_ids),
            ),
            threading.Thread(
                target=pump,
                args=(process.stderr, stderr_file, stderr_preview, stderr_size, request_ids),
            ),
        ]
        for thread in threads:
            thread.start()
        timed_out = False
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate(process)
            return_code = 124
        for thread in threads:
            thread.join()
    return (
        return_code,
        timed_out,
        "".join(stdout_preview),
        "".join(stderr_preview),
        request_ids,
    )


def main() -> int:
    args = parser().parse_args()
    try:
        case_id = safe_component(args.case_id, "case ID")
        step_id = safe_component(args.step_id, "step ID")
        attempt = safe_component(args.attempt, "attempt")
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            raise ValueError("command is required after --")
        root = args.result_root.resolve()
        contract, case, step = step_context(root, case_id, step_id)
        default_timeout = case.get("timeouts", {}).get("operation_seconds", 1800)
        timeout = args.timeout_seconds or step.get("timeout_seconds") or default_timeout
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("timeout must be a positive integer")
    except (OSError, ValueError) as error:
        print(f"record-command error: {error}", file=sys.stderr)
        return 2

    command_id = f"cmd-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    output_root = root / "cases" / case_id / attempt / "openstack"
    stdout_path = output_root / f"{step_id}.{command_id}.stdout.log"
    stderr_path = output_root / f"{step_id}.{command_id}.stderr.log"
    started = local_now(contract["timezone"])
    monotonic_start = time.monotonic_ns()
    return_code, timed_out, stdout, stderr, request_ids = execute(
        command, args.cwd, timeout, stdout_path, stderr_path
    )
    duration_ms = (time.monotonic_ns() - monotonic_start) // 1_000_000
    ended = local_now(contract["timezone"])
    record = {
        "command_id": command_id,
        "case_id": case_id,
        "step_id": step_id,
        "attempt": attempt,
        "description": args.description or step["description"],
        "command": redact(shlex.join(command)),
        "execute_location": args.execute_location,
        "start_local": started,
        "end_local": ended,
        "timezone": contract["timezone"],
        "duration_ms": duration_ms,
        "timeout_seconds": timeout,
        "timed_out": timed_out,
        "return_code": return_code,
        "result": "成功" if return_code == 0 else "失败",
        "request_ids": sorted(request_ids),
        "stdout_path": stdout_path.relative_to(root).as_posix(),
        "stderr_path": stderr_path.relative_to(root).as_posix(),
    }
    case_root = root / "cases" / case_id
    append_jsonl(case_root / "commands.jsonl", record)
    append_event(
        root,
        contract["timezone"],
        "COMMAND_RECORDED",
        case_id,
        step_id,
        record,
    )
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)
    if len(stdout) >= PREVIEW_LIMIT or len(stderr) >= PREVIEW_LIMIT:
        print("\n[output preview truncated; see evidence files]", file=sys.stderr)
    return return_code if 0 <= return_code <= 255 else 1


if __name__ == "__main__":
    raise SystemExit(main())
