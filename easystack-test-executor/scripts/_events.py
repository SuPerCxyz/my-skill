#!/usr/bin/env python3
"""Append-only event ledger and deterministic state projection."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
from typing import Any

from _harness import local_now, object_digest


GENESIS_HASH = "0" * 64


class EventError(ValueError):
    """Raised when the event ledger is malformed."""


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    previous = GENESIS_HASH
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            event = json.loads(line)
            event_hash = event.pop("event_hash", None)
            if event.get("sequence") != len(events) + 1:
                raise EventError(f"event {number}: invalid sequence")
            if event.get("previous_event_hash") != previous:
                raise EventError(f"event {number}: invalid previous hash")
            expected = object_digest(event)
            if event_hash != expected:
                raise EventError(f"event {number}: invalid event hash")
            event["event_hash"] = event_hash
            previous = event_hash
            events.append(event)
    return events


def append_event(
    root: Path,
    timezone: str,
    event_type: str,
    case_id: str | None = None,
    step_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = root / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        os.chmod(path, 0o600)
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        lines = [line for line in stream if line.strip()]
        previous = GENESIS_HASH
        if lines:
            last = json.loads(lines[-1])
            previous = last["event_hash"]
        event = {
            "sequence": len(lines) + 1,
            "previous_event_hash": previous,
            "timestamp_local": local_now(timezone),
            "event_type": event_type,
            "case_id": case_id,
            "step_id": step_id,
            "payload": payload or {},
        }
        event["event_hash"] = object_digest(event)
        stream.seek(0, os.SEEK_END)
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    return event


def initial_state(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": contract["schema_version"],
        "harness_version": contract["harness_version"],
        "run_id": contract["run_id"],
        "timezone": contract["timezone"],
        "cleanup_policy": contract["cleanup_policy"],
        "contract_sha256": contract["contract_sha256"],
        "started_local": contract["created_local"],
        "updated_local": contract["created_local"],
        "current_case": contract["case_order"][0],
        "run_status": "RUNNING",
        "abort_reason": "",
        "cases": {
            case_id: {
                "phase": "NOT_STARTED",
                "status": "NOT_RUN",
                "step_statuses": {},
                "execution_quality": "PENDING",
            }
            for case_id in contract["case_order"]
        },
    }


def project_state(
    contract: dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    state = initial_state(contract)
    for event in events:
        case_id = event.get("case_id")
        payload = event.get("payload", {})
        if event["event_type"] == "PHASE_ADVANCED" and case_id:
            state["cases"][case_id]["phase"] = payload["to_phase"]
            state["cases"][case_id]["status"] = (
                "COMPLETE" if payload["to_phase"] == "COMPLETE" else "RUNNING"
            )
            state["current_case"] = case_id
        elif event["event_type"] == "STEP_STATUS" and case_id:
            state["cases"][case_id]["step_statuses"][event["step_id"]] = payload
            state["current_case"] = case_id
        elif event["event_type"] == "ACTION_COMPLETED" and case_id:
            state["cases"][case_id]["step_statuses"][event["step_id"]] = {
                "status": payload["status"],
                "reason": "",
                "command_id": payload["command"]["command_id"],
            }
            state["current_case"] = case_id
            state["cases"][case_id]["status"] = "RUNNING"
        elif event["event_type"] == "ACTION_SKIPPED" and case_id:
            state["cases"][case_id]["step_statuses"][event["step_id"]] = {
                **payload,
                "start_local": event["timestamp_local"],
                "end_local": event["timestamp_local"],
                "duration_ms": 0,
            }
            if str(payload.get("reason", "")).startswith("failed dependencies:"):
                state["cases"][case_id]["status"] = "CASE_BLOCKED"
            state["current_case"] = case_id
        elif event["event_type"] == "RUN_ABORTED":
            state["run_status"] = "RUN_ABORTED"
            state["abort_reason"] = payload.get("reason", "")
            for item in state["cases"].values():
                if item["status"] == "RUNNING":
                    item["status"] = "RUN_ABORTED"
        elif event["event_type"] == "CASE_QUALITY" and case_id:
            state["cases"][case_id]["execution_quality"] = payload["status"]
        state["updated_local"] = event["timestamp_local"]
    state["current_case"] = None
    if state["run_status"] == "RUN_ABORTED":
        return state
    for case_id in contract["case_order"]:
        if state["cases"][case_id]["phase"] != "COMPLETE":
            state["current_case"] = case_id
            break
    return state


def verify_phase_events(
    contract: dict[str, Any], events: list[dict[str, Any]]
) -> list[str]:
    errors = []
    current = {case_id: "NOT_STARTED" for case_id in contract["case_order"]}
    phase_order = ["NOT_STARTED", *contract["phase_order"]]
    for event in events:
        if event["event_type"] != "PHASE_ADVANCED":
            continue
        case_id = event.get("case_id")
        if case_id not in current:
            errors.append(f"event {event['sequence']}: unknown case")
            continue
        payload = event["payload"]
        from_phase = payload.get("from_phase")
        to_phase = payload.get("to_phase")
        expected_index = phase_order.index(current[case_id]) + 1
        expected = phase_order[expected_index] if expected_index < len(phase_order) else None
        if from_phase != current[case_id] or to_phase != expected:
            errors.append(
                f"{case_id}: invalid transition {from_phase}->{to_phase}, "
                f"expected {current[case_id]}->{expected}"
            )
        else:
            current[case_id] = to_phase
    return errors
