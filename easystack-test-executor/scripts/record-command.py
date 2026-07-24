#!/usr/bin/env python3
"""Execute one command and durably record its timing and output."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from _harness import append_jsonl, local_now, read_json, redact, safe_component


REQUEST_ID = re.compile(r"\breq-[0-9a-f-]{16,}\b", re.IGNORECASE)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--result-root", required=True, type=Path)
    result.add_argument("--case-id", required=True)
    result.add_argument("--step-id", required=True)
    result.add_argument("--description", required=True)
    result.add_argument("--execute-location", default="local")
    result.add_argument("--attempt", default="attempt-01")
    result.add_argument("--cwd", type=Path)
    result.add_argument("command", nargs=argparse.REMAINDER)
    return result


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(content), encoding="utf-8")
    os.chmod(path, 0o600)


def main() -> int:
    args = parser().parse_args()
    try:
        safe_component(args.case_id, "case ID")
        safe_component(args.step_id, "step ID")
        safe_component(args.attempt, "attempt")
    except ValueError as error:
        print(f"record-command error: {error}", file=sys.stderr)
        return 2
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("record-command error: command is required after --", file=sys.stderr)
        return 2

    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    if not contract:
        print("record-command error: execution-contract.json not found", file=sys.stderr)
        return 2
    timezone = contract["timezone"]
    case_root = root / "cases" / args.case_id
    output_root = case_root / args.attempt / "openstack"
    stdout_path = output_root / f"{args.step_id}.stdout.log"
    stderr_path = output_root / f"{args.step_id}.stderr.log"

    started = local_now(timezone)
    monotonic_start = time.monotonic_ns()
    try:
        completed = subprocess.run(
            command,
            cwd=args.cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        return_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except OSError as error:
        return_code = 127
        stdout = ""
        stderr = str(error)
    duration_ms = (time.monotonic_ns() - monotonic_start) // 1_000_000
    ended = local_now(timezone)

    write_output(stdout_path, stdout)
    write_output(stderr_path, stderr)
    combined = f"{stdout}\n{stderr}"
    record = {
        "case_id": args.case_id,
        "step_id": args.step_id,
        "attempt": args.attempt,
        "description": args.description,
        "command": redact(shlex.join(command)),
        "execute_location": args.execute_location,
        "start_local": started,
        "end_local": ended,
        "timezone": timezone,
        "duration_ms": duration_ms,
        "return_code": return_code,
        "result": "成功" if return_code == 0 else "失败",
        "request_ids": sorted(set(REQUEST_ID.findall(combined))),
        "stdout_path": stdout_path.relative_to(root).as_posix(),
        "stderr_path": stderr_path.relative_to(root).as_posix(),
    }
    append_jsonl(case_root / "commands.jsonl", record)
    command_log = case_root / "commands.log"
    command_log.parent.mkdir(parents=True, exist_ok=True)
    with command_log.open("a", encoding="utf-8") as stream:
        stream.write(
            f"[{started}] {args.step_id} {record['result']} "
            f"rc={return_code} duration_ms={duration_ms}\n"
        )
        stream.write(f"$ {record['command']}\n")
        if record["request_ids"]:
            stream.write(f"request_ids={','.join(record['request_ids'])}\n")

    if stdout:
        print(redact(stdout), end="")
    if stderr:
        print(redact(stderr), end="", file=sys.stderr)
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
