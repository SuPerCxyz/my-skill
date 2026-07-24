#!/usr/bin/env python3
"""Build command and resource views from the append-only event ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _events import load_events
from _harness import atomic_json, atomic_text, load_jsonl


def event_views(
    events: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    commands: dict[str, list[dict[str, Any]]] = {}
    resources: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        case_id = event.get("case_id")
        if event["event_type"] == "ACTION_COMPLETED" and case_id:
            payload = event["payload"]
            commands.setdefault(case_id, []).append(payload["command"])
            for resource in payload.get("resources", []):
                key = (case_id, resource["id"])
                if key in resources:
                    raise ValueError(f"duplicate captured resource: {resource['id']}")
                resources[key] = resource
            for resource in payload.get("resource_updates", []):
                key = (case_id, resource["id"])
                if key not in resources:
                    raise ValueError(
                        f"action updated unknown resource: {resource['id']}"
                    )
                resources[key] = resource
        elif event["event_type"] == "RESOURCE_UPDATED" and case_id:
            resource = event["payload"]
            key = (case_id, resource["id"])
            if key not in resources:
                raise ValueError(f"resource update without capture: {resource['id']}")
            resources[key] = resource
    return commands, list(resources.values())


def sync_event_views(root: Path) -> None:
    commands, resources = event_views(load_events(root / "events.jsonl"))
    artifacts = [
        artifact
        for records in commands.values()
        for record in records
        for artifact in record.get("artifacts", [])
    ]
    atomic_text(
        root / "artifact-manifest.jsonl",
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in artifacts),
    )
    case_ids = {
        path.name for path in (root / "cases").iterdir() if path.is_dir()
    }
    for case_id in case_ids:
        records = commands.get(case_id, [])
        content = "".join(
            json.dumps(item, ensure_ascii=False) + "\n" for item in records
        )
        atomic_text(root / "cases" / case_id / "commands.jsonl", content)
        atomic_json(
            root / "cases" / case_id / "resources.json",
            [item for item in resources if item["case_id"] == case_id],
        )
    atomic_json(root / "resources-all.json", resources)


def projection_errors(root: Path) -> list[str]:
    errors: list[str] = []
    commands, resources = event_views(load_events(root / "events.jsonl"))
    expected_artifacts = [
        artifact
        for records in commands.values()
        for record in records
        for artifact in record.get("artifacts", [])
    ]
    if load_jsonl(root / "artifact-manifest.jsonl") != expected_artifacts:
        errors.append("artifact manifest differs from events")
    for case_id, expected in commands.items():
        actual = load_jsonl(root / "cases" / case_id / "commands.jsonl")
        if actual != expected:
            errors.append(f"{case_id}: command projection differs from events")
    actual_resources = json.loads(
        (root / "resources-all.json").read_text(encoding="utf-8")
    )
    if actual_resources != resources:
        errors.append("resource projection differs from events")
    for case_dir in (root / "cases").iterdir():
        if not case_dir.is_dir():
            continue
        expected = [item for item in resources if item["case_id"] == case_dir.name]
        actual = json.loads((case_dir / "resources.json").read_text(encoding="utf-8"))
        if actual != expected:
            errors.append(f"{case_dir.name}: resource projection differs from events")
    return errors
