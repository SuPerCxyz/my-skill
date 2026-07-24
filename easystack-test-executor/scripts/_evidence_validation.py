#!/usr/bin/env python3
"""Validate log target coverage and correlation evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from _harness import load_jsonl, read_json
from _validation import Findings


def target_name(target: Any) -> str:
    if isinstance(target, str):
        return target
    if isinstance(target, dict):
        return str(target.get("name") or target.get("service") or "")
    return ""


def validate_logs(
    root: Path,
    case: dict[str, Any],
    result: dict[str, Any],
    findings: Findings,
) -> None:
    case_id = case["id"]
    requirement = case["log_requirement"]
    status = result["evidence_status"]
    collection = read_json(
        root / "cases" / case_id / "logs" / "collection-status.json", {}
    )
    if requirement == "none" and status != "NOT_APPLICABLE":
        findings.error(f"{case_id}: logs=none requires NOT_APPLICABLE")
    if requirement == "optional" and not collection:
        if status != "OPTIONAL_NOT_COLLECTED":
            findings.error(f"{case_id}: absent optional logs require OPTIONAL_NOT_COLLECTED")
        return
    if requirement == "required" and not collection:
        if status != "MISSING":
            findings.error(f"{case_id}: absent required logs require MISSING")
        return
    expected_targets = {
        target_name(item)
        for item in case["log_targets"]
        if not isinstance(item, dict) or item.get("required", True)
    }
    collected_targets = {
        target_name(item)
        for item in collection.get("targets", [])
        if item.get("status") == "COLLECTED"
    }
    if status == "COMPLETE" and expected_targets - collected_targets:
        findings.error(f"{case_id}: COMPLETE logs do not cover all targets")
    if requirement == "required" and status == "COMPLETE" and not result.get("logs"):
        findings.error(f"{case_id}: COMPLETE required logs lack correlated evidence")
    case_root = (root / "cases" / case_id).resolve()
    manifested = {
        item.get("path") for item in load_jsonl(root / "artifact-manifest.jsonl")
    }
    known_ids = set(collection.get("correlation_ids", []))
    for index, log in enumerate(result.get("logs", []), 1):
        source = case_root / str(log.get("source_path", ""))
        try:
            source.resolve().relative_to(case_root)
        except ValueError:
            findings.error(f"{case_id}: log {index} path escapes case directory")
            continue
        if not source.is_file():
            findings.error(f"{case_id}: log {index} source file missing")
        relative_to_root = source.resolve().relative_to(root.resolve()).as_posix()
        if relative_to_root not in manifested:
            findings.error(f"{case_id}: log {index} is not in artifact manifest")
        if requirement == "required" and not log.get("request_or_resource_id"):
            findings.error(f"{case_id}: log {index} lacks correlation ID")
        if log.get("request_or_resource_id") not in known_ids:
            findings.error(f"{case_id}: log {index} uses an unknown correlation ID")
        for field in ("pod_uid", "pod", "container", "selector"):
            if not log.get(field):
                findings.error(f"{case_id}: log {index} lacks target {field}")
