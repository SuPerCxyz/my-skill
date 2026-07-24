#!/usr/bin/env python3
"""Shared Kubernetes log collection helpers."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from _harness import load_jsonl, read_json, redact


REQUEST_ID = re.compile(r"\breq-[0-9a-f-]{16,}\b", re.IGNORECASE)


def parse_target(value: str) -> dict[str, str]:
    parts = value.split("|")
    if len(parts) != 3 or not all(parts):
        raise ValueError("--target must be SERVICE|LABEL_SELECTOR|CONTAINER")
    return {"name": parts[0], "selector": parts[1], "container": parts[2]}


def run_json(command: list[str], timeout: int = 60) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode:
        raise ValueError(redact(completed.stderr.strip() or "kubectl failed"))
    return json.loads(completed.stdout)


def terminate(process: subprocess.Popen[Any]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    except ProcessLookupError:
        pass


def collect_one(
    command: list[str], raw_path: Path, error_path: Path, timeout: int
) -> tuple[int, bool]:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_path.open("x", encoding="utf-8") as output, error_path.open(
        "x", encoding="utf-8"
    ) as error:
        process = subprocess.Popen(
            command,
            text=True,
            stdout=output,
            stderr=error,
            start_new_session=True,
        )
        try:
            result = (process.wait(timeout=timeout), False)
        except subprocess.TimeoutExpired:
            terminate(process)
            result = (124, True)
    redact_file(raw_path)
    redact_file(error_path)
    return result


def redact_file(path: Path) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with path.open(encoding="utf-8", errors="replace") as source, os.fdopen(
            descriptor, "w", encoding="utf-8"
        ) as destination:
            for line in source:
                destination.write(redact(line))
            destination.flush()
            os.fsync(destination.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def correlation_ids(root: Path, case_id: str) -> set[str]:
    identifiers = {
        value
        for record in load_jsonl(root / "cases" / case_id / "commands.jsonl")
        for value in record.get("request_ids", [])
    }
    identifiers.update(
        str(item["id"])
        for item in read_json(root / "cases" / case_id / "resources.json", [])
        if item.get("id")
    )
    return identifiers


def timestamp_fields(line: str, timezone_name: str) -> tuple[str, str]:
    raw = line.split(maxsplit=1)[0] if line else ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        local = parsed.astimezone(ZoneInfo(timezone_name)).isoformat(timespec="milliseconds")
        return local, raw
    except ValueError:
        return "", raw


def related_evidence(
    raw_path: Path,
    relative_path: str,
    target: dict[str, Any],
    instance: dict[str, Any],
    identifiers: set[str],
    timezone_name: str,
    end_time: str,
) -> list[dict[str, Any]]:
    evidence = []
    window_end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    with raw_path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            matched = next((value for value in identifiers if value in line), None)
            if not matched:
                continue
            local, raw = timestamp_fields(line, timezone_name)
            try:
                instant = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if instant > window_end:
                    continue
            except ValueError:
                pass
            evidence.append(
                {
                    "timestamp_local": local,
                    "raw_timestamp": raw,
                    "source_timezone": "UTC" if raw.endswith("Z") else "unknown",
                    "service": target["name"],
                    "pod": instance["pod"],
                    "container": instance["container"],
                    "container_id": instance.get("container_id", ""),
                    "pod_uid": instance.get("pod_uid", ""),
                    "selector": target.get("selector", ""),
                    "request_or_resource_id": matched,
                    "source_path": relative_path,
                    "excerpt": redact(line.strip())[:1000],
                }
            )
            if len(evidence) >= 100:
                break
    return evidence


def instance_map(snapshot_data: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    output = {}
    for target in snapshot_data.get("targets", []):
        for instance in target.get("instances", []):
            output[(target["name"], instance["pod_uid"])] = {
                **instance,
                "target": target,
            }
    return output


def target_name(target: Any) -> str:
    if isinstance(target, str):
        return target
    return str(target.get("name") or target.get("service"))
