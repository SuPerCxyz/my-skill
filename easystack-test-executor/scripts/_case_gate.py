#!/usr/bin/env python3
"""Structural CASE_GATE checks that do not require rendered reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from _harness import load_jsonl, read_json
from _resources import reconcile_resources


def command_records_for_step(
    root: Path, case_id: str, step_id: str
) -> list[dict[str, Any]]:
    return [
        item
        for item in load_jsonl(root / "cases" / case_id / "commands.jsonl")
        if item.get("step_id") == step_id
    ]


def failed_dependencies(root: Path, case: dict[str, Any]) -> list[str]:
    return [
        dependency
        for dependency in case.get("dependencies", [])
        if read_json(root / "cases" / dependency / "result.json", {}).get(
            "functional_status"
        )
        != "PASS"
    ]


def derived_diagnostic(
    checks: list[dict[str, Any]], step_statuses: list[dict[str, Any]]
) -> str:
    if any(item.get("status") == "BLOCKED" for item in step_statuses):
        return "BLOCKED"
    if any(
        item.get("status") == "UNKNOWN"
        for item in checks
        if item.get("required")
    ):
        return "INCONCLUSIVE"
    return "CONCLUSIVE"


def derived_quality(timing: str, evidence: str, cleanup: str) -> str:
    warning = (
        timing == "INVALID"
        or evidence in {"PARTIAL", "MISSING", "INVALID"}
        or cleanup == "PARTIAL"
    )
    return "COMPLETE_WITH_WARNINGS" if warning else "COMPLETE"


def case_gate_errors(
    root: Path,
    contract: dict[str, Any],
    case: dict[str, Any],
    state: dict[str, Any],
) -> list[str]:
    case_id = case["id"]
    errors = reconcile_resources(root)
    result = read_json(root / "cases" / case_id / "result.json", {})
    if not result.get("derived_by_harness"):
        errors.append("result is not harness-derived")
        return errors
    if result.get("contract_sha256") != contract["contract_sha256"]:
        errors.append("result contract digest differs")
    definitions = {item["id"]: item for item in case["verification"]}
    checks = {item.get("check_id"): item for item in result.get("checks", [])}
    if checks.keys() != definitions.keys():
        errors.append("result checks differ from contract")
    required = [
        checks.get(item["id"], {})
        for item in case["verification"]
        if item["check_type"] == "functional" and item["required"]
    ]
    functional = (
        "PASS"
        if required and all(item.get("status") == "PASS" for item in required)
        else "FAIL"
    )
    if result.get("functional_status") != functional:
        errors.append(f"functional_status must be {functional}")
    statuses = state["cases"][case_id]["step_statuses"]
    missing = [item["id"] for item in case["actions"] if item["id"] not in statuses]
    if missing:
        errors.append(f"steps not terminal: {','.join(missing)}")
    command_steps = {
        item.get("step_id")
        for item in load_jsonl(root / "cases" / case_id / "commands.jsonl")
    }
    skipped_steps = {
        step_id for step_id, payload in statuses.items()
        if payload.get("status") in {"SKIPPED_BY_PLAN", "NOT_APPLICABLE"}
    }
    timing = (
        "VALID"
        if all(
            item["id"] in command_steps or item["id"] in skipped_steps
            for item in case["actions"]
        )
        else "INVALID"
    )
    if result.get("timing_status") != timing:
        errors.append(f"timing_status must be {timing}")
    if result.get("evidence_status") == "PENDING":
        errors.append("evidence_status is not terminal")
    if result.get("cleanup_status") == "PENDING":
        errors.append("cleanup_status is not terminal")
    return errors
