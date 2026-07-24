#!/usr/bin/env python3
"""Resource ledger helpers with case/global reconciliation."""

from __future__ import annotations

import fcntl
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from _harness import atomic_json


TERMINAL_CLEANUP_RESULTS = {"DELETED", "PRESERVED", "NOT_APPLICABLE", "FAILED"}


@contextmanager
def ledger_lock(result_root: Path) -> Iterator[None]:
    lock_path = result_root / ".resources.lock"
    lock_path.touch(mode=0o600, exist_ok=True)
    lock_path.chmod(0o600)
    with lock_path.open("r+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def load_resources(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def _find(resources: list[dict[str, Any]], resource_id: str) -> dict[str, Any] | None:
    return next((item for item in resources if item.get("id") == resource_id), None)


def create_resource(
    result_root: Path,
    case_id: str,
    record: dict[str, Any],
    local_time: str,
) -> dict[str, Any]:
    resource_id = str(record.get("id", "")).strip()
    if not resource_id:
        raise ValueError("resource id is required")
    case_path = result_root / "cases" / case_id / "resources.json"
    global_path = result_root / "resources-all.json"
    with ledger_lock(result_root):
        case_items = load_resources(case_path)
        global_items = load_resources(global_path)
        if _find(case_items, resource_id) or _find(global_items, resource_id):
            raise ValueError(f"resource already exists: {resource_id}")
        item = {
            "case_id": case_id,
            "type": record["type"],
            "id": resource_id,
            "name": record["name"],
            "created_local": local_time,
            "owning_step": record["owning_step"],
            "dependencies": record.get("dependencies", []),
            "cleanup_policy": record.get("cleanup_policy", "delete"),
            "cleanup_result": "PENDING",
            "final_state": "PRESENT",
        }
        case_items.append(item)
        global_items.append(item.copy())
        atomic_json(case_path, case_items)
        atomic_json(global_path, global_items)
    return item


def update_resource(
    result_root: Path,
    case_id: str,
    resource_id: str,
    changes: dict[str, Any],
) -> dict[str, Any]:
    immutable = {"id", "case_id", "created_local", "type", "name"}
    forbidden = immutable.intersection(changes)
    if forbidden:
        raise ValueError(f"immutable resource fields: {', '.join(sorted(forbidden))}")
    case_path = result_root / "cases" / case_id / "resources.json"
    global_path = result_root / "resources-all.json"
    with ledger_lock(result_root):
        case_items = load_resources(case_path)
        global_items = load_resources(global_path)
        case_item = _find(case_items, resource_id)
        global_item = _find(global_items, resource_id)
        if not case_item or not global_item:
            raise ValueError(f"resource not found in both ledgers: {resource_id}")
        case_item.update(changes)
        global_item.update(changes)
        atomic_json(case_path, case_items)
        atomic_json(global_path, global_items)
    return case_item


def reconcile_resources(result_root: Path) -> list[str]:
    errors: list[str] = []
    global_items = load_resources(result_root / "resources-all.json")
    resource_ids = [item.get("id") for item in global_items]
    if len(resource_ids) != len(set(resource_ids)):
        errors.append("global resource IDs are not unique")
    global_map = {(item.get("case_id"), item.get("id")): item for item in global_items}
    case_map: dict[tuple[Any, Any], dict[str, Any]] = {}
    for case_dir in sorted((result_root / "cases").glob("*")):
        if not case_dir.is_dir():
            continue
        for item in load_resources(case_dir / "resources.json"):
            key = (item.get("case_id"), item.get("id"))
            if key in case_map:
                errors.append(f"duplicate case resource: {key}")
            case_map[key] = item
    if global_map.keys() != case_map.keys():
        errors.append("case and global resource ledger keys differ")
    for key in global_map.keys() & case_map.keys():
        if global_map[key] != case_map[key]:
            errors.append(f"resource ledger content differs: {key}")
    return errors


def cleanup_quality(resources: list[dict[str, Any]], cleanup_policy: str) -> str:
    if not resources:
        return "COMPLETE"
    results = {str(item.get("cleanup_result", "PENDING")) for item in resources}
    if cleanup_policy == "preserve_all":
        return "PRESERVED" if results <= {"PRESERVED"} else "PARTIAL"
    if "FAILED" in results or "PENDING" in results:
        return "PARTIAL"
    if results <= TERMINAL_CLEANUP_RESULTS:
        return "PRESERVED" if "PRESERVED" in results else "COMPLETE"
    return "PARTIAL"


def local_timestamp(timezone_name: str) -> str:
    from zoneinfo import ZoneInfo

    return datetime.now(ZoneInfo(timezone_name)).isoformat(timespec="seconds")
