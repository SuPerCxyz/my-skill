#!/usr/bin/env python3
"""Shared helpers for the resumable EasyStack test harness."""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


REDACTIONS = (
    re.compile(r"(?i)(OS_PASSWORD|password|token|secret)=('[^']*'|\"[^\"]*\"|[^\s]+)"),
    re.compile(r"(?i)(--password|--token|--secret)\s+([^\s]+)"),
    re.compile(
        r'(?i)("(?:password|token|secret)"\s*:\s*)("[^"]*"|[^,\s}]+)'
    ),
    re.compile(r"(?i)(X-Auth-Token\s*:\s*)([^\s,]+)"),
    re.compile(r"(?i)(Authorization\s*:\s*Bearer\s+)([^\s,]+)"),
)
SAFE_COMPONENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def local_now(timezone: str) -> str:
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="milliseconds")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def atomic_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        os.chmod(path, 0o600)
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.write(json.dumps(data, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def redact(value: str) -> str:
    result = value
    for pattern in REDACTIONS:
        result = pattern.sub(lambda match: f"{match.group(1)}=<redacted>", result)
    return result


def skill_digest(skill_root: Path) -> str:
    digest = hashlib.sha256()
    paths: Iterable[Path] = sorted(
        path
        for path in skill_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )
    for path in paths:
        digest.update(path.relative_to(skill_root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def object_digest(data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def case_anchor(case_id: str) -> str:
    anchor = re.sub(r"[^a-z0-9-]+", "-", case_id.lower())
    return re.sub(r"-+", "-", anchor).strip("-")


def markdown_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", r"\|").replace(
        "\n", "<br>"
    )


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("-" * (len(header) + 2) for header in headers) + "|",
    ]
    output.extend(
        "| " + " | ".join(markdown_cell(value) for value in row) + " |"
        for row in rows
    )
    return output


def safe_component(value: str, label: str) -> str:
    if not SAFE_COMPONENT.fullmatch(value):
        raise ValueError(f"invalid {label}: {value!r}")
    return value
