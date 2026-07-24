#!/usr/bin/env python3
"""Artifact hashing and manifest reconciliation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from _harness import load_jsonl


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def register_artifact(
    root: Path,
    path: Path,
    *,
    case_id: str,
    action_id: str,
    command_id: str,
    artifact_type: str,
) -> dict[str, Any]:
    resolved = path.resolve()
    resolved.relative_to(root.resolve())
    record = {
        "path": resolved.relative_to(root.resolve()).as_posix(),
        "sha256": file_digest(resolved),
        "size_bytes": resolved.stat().st_size,
        "case_id": case_id,
        "action_id": action_id,
        "command_id": command_id,
        "artifact_type": artifact_type,
    }
    return record


def validate_artifacts(root: Path) -> list[str]:
    errors: list[str] = []
    records = load_jsonl(root / "artifact-manifest.jsonl")
    paths = [item.get("path") for item in records]
    if len(paths) != len(set(paths)):
        errors.append("artifact manifest contains duplicate paths")
    for item in records:
        path = root / str(item.get("path", ""))
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            errors.append(f"artifact path escapes result root: {item.get('path')}")
            continue
        if not path.is_file():
            errors.append(f"artifact missing: {item.get('path')}")
            continue
        if path.stat().st_size != item.get("size_bytes"):
            errors.append(f"artifact size changed: {item.get('path')}")
        if file_digest(path) != item.get("sha256"):
            errors.append(f"artifact digest changed: {item.get('path')}")
    return errors
