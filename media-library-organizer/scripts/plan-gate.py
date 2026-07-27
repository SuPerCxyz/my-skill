#!/usr/bin/env python3
"""Build and validate deterministic media-library dry-run plans."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ALLOWED_OPERATIONS = {"create", "move", "rename", "replace_backup", "rmdir"}


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


def inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"{label} escapes media boundary: {path}") from error
    return resolved


def required_path(data: dict[str, Any], key: str) -> Path:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty path")
    return Path(value)


def roots(data: dict[str, Any]) -> tuple[Path, Path, Path]:
    source = required_path(data, "source_root").resolve()
    media = required_path(data, "media_root").resolve()
    target = required_path(data, "target_root").resolve(strict=False)
    if not source.is_dir() or not media.is_dir():
        raise ValueError("source_root and media_root must be existing directories")
    inside(source, media, "source_root")
    inside(target, media, "target_root")
    return source, media, target


def inventory(source: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(source).as_posix()
        if path.is_symlink():
            inside(path, source, f"symlink {relative}")
            stat = path.lstat()
            records.append(
                {
                    "path": relative,
                    "type": "symlink",
                    "target": os.readlink(path),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            )
        elif path.is_file():
            stat = path.stat()
            records.append(
                {
                    "path": relative,
                    "type": "file",
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            )
    return records


def normalized_mappings(
    values: Any, source: Path, media: Path
) -> list[dict[str, str]]:
    if not isinstance(values, list):
        raise ValueError("mappings must be a list")
    output: list[dict[str, str]] = []
    for index, item in enumerate(values):
        if not isinstance(item, dict) or item.get("operation") not in ALLOWED_OPERATIONS:
            raise ValueError(f"mapping {index}: invalid operation")
        operation = item["operation"]
        record = {"operation": operation}
        if operation in {"move", "rename", "replace_backup", "rmdir"}:
            old_root = media if operation == "replace_backup" else source
            old = inside(required_path(item, "old"), old_root, f"mapping {index} old")
            record["old"] = str(old)
        if operation in {"create", "move", "rename", "replace_backup"}:
            new = inside(required_path(item, "new"), media, f"mapping {index} new")
            record["new"] = str(new)
        output.append(record)
    return sorted(
        output,
        key=lambda item: (item.get("old", ""), item.get("new", ""), item["operation"]),
    )


def payload(data: dict[str, Any]) -> dict[str, Any]:
    source, media, target = roots(data)
    options = data.get("options", {})
    if not isinstance(options, dict):
        raise ValueError("options must be an object")
    mappings = normalized_mappings(data.get("mappings"), source, media)
    return {
        "schema_version": 1,
        "source_root": str(source),
        "media_root": str(media),
        "target_root": str(target),
        "options": options,
        "inventory": inventory(source),
        "mappings": mappings,
    }


def digest(value: dict[str, Any]) -> str:
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build(input_path: Path, output_path: Path) -> str:
    data = load_object(input_path)
    source, _, _ = roots(data)
    try:
        output_path.resolve(strict=False).relative_to(source)
    except ValueError:
        pass
    else:
        raise ValueError("plan output must be outside source_root")
    normalized = payload(data)
    plan_id = digest(normalized)
    atomic_json(output_path, {"plan_id": plan_id, "payload": normalized})
    return plan_id


def validate(plan_path: Path) -> str:
    plan = load_object(plan_path)
    saved = plan.get("payload")
    if not isinstance(saved, dict):
        raise ValueError("plan payload is missing")
    expected = plan.get("plan_id")
    if expected != digest(saved):
        raise ValueError("plan content does not match plan_id")
    current_input = {
        key: saved[key]
        for key in ("source_root", "media_root", "target_root", "options", "mappings")
    }
    current = payload(current_input)
    if current != saved:
        raise ValueError("source inventory, options, roots, or mappings changed")
    return str(expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--input", required=True, type=Path)
    create.add_argument("--output", required=True, type=Path)
    check = commands.add_parser("validate")
    check.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    try:
        plan_id = (
            build(args.input, args.output)
            if args.command == "build"
            else validate(args.plan)
        )
        print(plan_id)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"plan-gate error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
