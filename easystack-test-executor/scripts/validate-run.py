#!/usr/bin/env python3
"""Validate contract, events, evidence, derived results, and report files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from _actions import bind_action
from _artifacts import validate_artifacts
from _case_gate import derived_diagnostic, derived_quality
from _contract import case_by_id, contract_digest
from _evidence_validation import validate_logs
from _events import EventError, load_events, project_state, verify_phase_events
from _harness import case_anchor, load_jsonl, object_digest, read_json, skill_digest
from _projections import projection_errors
from _resources import cleanup_quality, reconcile_resources
from _validation import (
    REQUIRED_RESULT_FIELDS,
    Findings,
    case_text_errors,
    valid_local_time,
    validate_case_markdown,
    validate_run_files,
)


EVIDENCE_STATUSES = {
    "COMPLETE",
    "PARTIAL",
    "MISSING",
    "INVALID",
    "NOT_APPLICABLE",
    "OPTIONAL_NOT_COLLECTED",
}


def command_valid(root: Path, record: dict[str, Any], timezone: str) -> bool:
    required = (
        "command_id",
        "step_id",
        "start_local",
        "end_local",
        "timezone",
        "duration_ms",
        "timeout_seconds",
        "timed_out",
        "return_code",
        "stdout_path",
        "stderr_path",
    )
    if any(field not in record for field in required):
        return False
    if record["timezone"] != timezone:
        return False
    if not isinstance(record["duration_ms"], int) or record["duration_ms"] < 0:
        return False
    if not valid_local_time(record["start_local"]) or not valid_local_time(record["end_local"]):
        return False
    return all((root / record[field]).is_file() for field in ("stdout_path", "stderr_path"))


def validate_steps(
    root: Path,
    case: dict[str, Any],
    result: dict[str, Any],
    state: dict[str, Any],
    contract: dict[str, Any],
    findings: Findings,
) -> None:
    case_id = case["id"]
    records = load_jsonl(root / "cases" / case_id / "commands.jsonl")
    command_ids = [item.get("command_id") for item in records]
    if len(command_ids) != len(set(command_ids)):
        findings.error(f"{case_id}: duplicate command_id")
    output_paths = [
        item.get(field)
        for item in records
        for field in ("stdout_path", "stderr_path")
    ]
    if len(output_paths) != len(set(output_paths)):
        findings.error(f"{case_id}: command evidence path was reused")
    by_step: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_step.setdefault(str(record.get("step_id", "")), []).append(record)
    statuses = state["cases"][case_id]["step_statuses"]
    invalid = False
    for step in case["actions"]:
        step_id = step["id"]
        if step_id not in statuses:
            findings.error(f"{case_id}: planned step not terminal: {step_id}")
            invalid = True
            continue
        commands = by_step.get(step_id, [])
        status = statuses.get(step_id, {}).get("status")
        skipped = status in {"SKIPPED_BY_PLAN", "NOT_APPLICABLE"}
        if (not skipped and not commands) or not all(
            command_valid(root, item, result["timezone"]) for item in commands
        ):
            invalid = True
            findings.warning(f"{case_id}: step timing incomplete: {step_id}")
        for command in commands if contract.get("schema_version") == 3 else []:
            try:
                argv = bind_action(
                    contract, step, read_json(root / "resources-all.json", [])
                )
                digest = hashlib.sha256(
                    json.dumps(argv, ensure_ascii=False).encode()
                ).hexdigest()
                if command.get("bound_argv_sha256") != digest:
                    findings.error(f"{case_id}: bound argv differs for {step_id}")
            except ValueError as error:
                findings.error(f"{case_id}: cannot bind {step_id}: {error}")
    unknown = set(by_step) - {item["id"] for item in case["actions"]}
    if unknown:
        findings.error(f"{case_id}: commands reference unknown steps: {','.join(sorted(unknown))}")
    expected = "INVALID" if invalid else "VALID"
    if result["timing_status"] != expected:
        findings.error(f"{case_id}: timing_status must be derived as {expected}")


def validate_checks(
    root: Path, case: dict[str, Any], result: dict[str, Any], findings: Findings
) -> None:
    case_id = case["id"]
    definitions = {item["id"]: item for item in case["verification"]}
    checks = {item.get("check_id"): item for item in result.get("checks", [])}
    if checks.keys() != definitions.keys():
        findings.error(f"{case_id}: result checks differ from contract")
    for check_id, definition in definitions.items():
        item = checks.get(check_id, {})
        for field in ("check_type", "required", "expected"):
            if item.get(field) != definition.get(field):
                findings.error(f"{case_id}/{check_id}: check {field} differs from contract")
        if item.get("status") in {"PASS", "FAIL"}:
            if item.get("actual") in {"", "未记录"} or item.get("evidence") in {"", "无"}:
                findings.error(f"{case_id}/{check_id}: terminal check lacks evidence")
            evidence = str(item.get("evidence", ""))
            if "/" in evidence or evidence.endswith((".log", ".json")):
                case_root = (root / "cases" / case_id).resolve()
                path = root / evidence
                if not path.is_file():
                    path = case_root / evidence
                try:
                    path.resolve().relative_to(case_root)
                except ValueError:
                    findings.error(f"{case_id}/{check_id}: evidence path escapes case")
                else:
                    if not path.is_file():
                        findings.error(f"{case_id}/{check_id}: evidence file missing")
    required = [
        checks.get(item["id"], {})
        for item in case["verification"]
        if item["check_type"] == "functional" and item["required"]
    ]
    expected = "PASS" if required and all(item.get("status") == "PASS" for item in required) else "FAIL"
    if result["functional_status"] != expected:
        findings.error(f"{case_id}: functional_status must be derived as {expected}")


def validate_result(
    root: Path,
    case: dict[str, Any],
    state: dict[str, Any],
    contract: dict[str, Any],
    findings: Findings,
) -> dict[str, Any] | None:
    case_id = case["id"]
    path = root / "cases" / case_id / "result.json"
    result = read_json(path)
    if not result:
        findings.error(f"{case_id}: result.json missing")
        return None
    missing = [field for field in REQUIRED_RESULT_FIELDS if field not in result]
    if missing:
        findings.error(f"{case_id}: result fields missing: {','.join(missing)}")
        return None
    if not result.get("derived_by_harness"):
        findings.error(f"{case_id}: result was not derived by harness")
    if result.get("contract_sha256") != contract["contract_sha256"]:
        findings.error(f"{case_id}: result contract digest mismatch")
    if contract.get("schema_version") == 3:
        verdict = read_json(root / "cases" / case_id / "case-verdict.json", {})
        for field in (
            "functional_status", "timing_status", "evidence_status",
            "diagnostic_status", "checks", "logs",
        ):
            if result.get(field) != verdict.get(field):
                findings.error(
                    f"{case_id}: result changed immutable verdict field {field}"
                )
        events = load_events(root / "events.jsonl")
        verdict_event = next(
            (
                item for item in events
                if item["event_type"] == "CASE_VERDICT_DERIVED"
                and item.get("case_id") == case_id
            ),
            {},
        )
        result_event = next(
            (
                item for item in events
                if item["event_type"] == "CASE_RESULT_DERIVED"
                and item.get("case_id") == case_id
            ),
            {},
        )
        if verdict_event.get("payload", {}).get("verdict_sha256") != object_digest(
            verdict
        ):
            findings.error(f"{case_id}: verdict digest differs from events")
        if result_event.get("payload", {}).get("result_sha256") != object_digest(
            result
        ):
            findings.error(f"{case_id}: result digest differs from events")
    for field in ("scenario_key", "title", "requirement_summary", "objective"):
        if result.get(field) != case.get(field):
            findings.error(f"{case_id}: result {field} differs from contract")
    for error in case_text_errors(result):
        findings.error(f"{case_id}: {error}")
    if result.get("evidence_status") not in EVIDENCE_STATUSES:
        findings.error(f"{case_id}: invalid evidence_status")
    if result.get("timezone") != contract["timezone"]:
        findings.error(f"{case_id}: result timezone differs from contract")
    if not valid_local_time(result.get("started_local")) or not valid_local_time(
        result.get("ended_local")
    ):
        findings.error(f"{case_id}: result timestamps are invalid")
    validate_steps(root, case, result, state, contract, findings)
    validate_checks(root, case, result, findings)
    validate_logs(root, case, result, findings)
    resources = read_json(root / "cases" / case_id / "resources.json", [])
    step_ids = {item["id"] for item in case["actions"]}
    for resource in resources:
        if resource.get("owning_step") not in step_ids:
            findings.error(f"{case_id}: resource has invalid owning_step")
        for field in ("type", "name", "id", "created_local", "cleanup_result"):
            if not resource.get(field):
                findings.error(f"{case_id}: resource missing {field}")
        if resource.get("cleanup_result") not in {
            "DELETED",
            "PRESERVED",
            "NOT_APPLICABLE",
            "FAILED",
        }:
            findings.error(f"{case_id}: resource cleanup_result is not terminal")
        if not valid_local_time(resource.get("created_local")):
            findings.error(f"{case_id}: resource created_local is invalid")
    cleanup_policy = (
        contract["cleanup_policy"]
        if case["cleanup_policy"] == "inherit"
        else case["cleanup_policy"]
    )
    cleanup = cleanup_quality(resources, cleanup_policy)
    if result.get("cleanup_status") != cleanup:
        findings.error(f"{case_id}: cleanup_status must be derived as {cleanup}")
    diagnostic = derived_diagnostic(
        result.get("checks", []),
        list(state["cases"][case_id]["step_statuses"].values()),
    )
    if result.get("diagnostic_status") != diagnostic:
        findings.error(f"{case_id}: diagnostic_status must be derived as {diagnostic}")
    quality = derived_quality(
        result.get("timing_status"), result.get("evidence_status"), cleanup
    )
    if result.get("execution_quality") != quality:
        findings.error(f"{case_id}: execution_quality must be derived as {quality}")
    return result


def validate_contract(
    root: Path, contract: dict[str, Any], state: dict[str, Any], findings: Findings
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if contract.get("contract_sha256") != contract_digest(contract):
        findings.error("execution contract content or digest changed")
    if contract.get("schema_version") == 3:
        if contract.get("environment_profile_sha256") != object_digest(
            contract.get("environment_profile")
        ):
            findings.error("environment profile digest differs from contract")
    if state.get("contract_sha256") != contract.get("contract_sha256"):
        findings.error("run state points to a different contract")
    current_skill = skill_digest(Path(__file__).resolve().parents[1])
    if contract.get("skill_sha256") != current_skill:
        findings.warning("skill changed after initialization; frozen contract remains authoritative")
    try:
        events = load_events(root / "events.jsonl")
    except (EventError, json.JSONDecodeError) as error:
        findings.error(f"event ledger invalid: {error}")
        events = []
    for error in verify_phase_events(contract, events):
        findings.error(error)
    projected = project_state(contract, events)
    if state != projected and {**projected, "next_instruction": state.get("next_instruction")} != state:
        findings.error("run-state.json differs from event projection")
    return events, projected


def main() -> int:
    args = argparse.ArgumentParser()
    args.add_argument("--result-root", required=True, type=Path)
    args.add_argument("--allow-partial", action="store_true")
    parsed = args.parse_args()
    root = parsed.result_root.resolve()
    findings = Findings()
    contract = read_json(root / "execution-contract.json")
    state = read_json(root / "run-state.json")
    if not contract or not state:
        print("validation error: contract or run state missing", file=sys.stderr)
        return 2
    _, projected = validate_contract(root, contract, state, findings)
    results = []
    anchors = [case_anchor(case_id) for case_id in contract["case_order"]]
    if len(anchors) != len(set(anchors)):
        findings.error("case IDs produce duplicate Markdown anchors")
    actual_results = {
        path.parent.name for path in (root / "cases").glob("*/result.json")
    }
    extra_results = actual_results - set(contract["case_order"])
    if extra_results:
        findings.error(f"results outside contract: {','.join(sorted(extra_results))}")
    for case_id in contract["case_order"]:
        case = case_by_id(contract, case_id)
        if projected["cases"][case_id]["phase"] != "COMPLETE":
            if parsed.allow_partial:
                findings.warning(f"{case_id}: phase is not COMPLETE")
                continue
            findings.error(f"{case_id}: phase is not COMPLETE")
        result = validate_result(root, case, projected, contract, findings)
        if result:
            results.append(result)
            validate_case_markdown(root, result, findings)
    for error in reconcile_resources(root):
        findings.error(error)
    if contract.get("schema_version") == 3:
        for error in projection_errors(root):
            findings.error(error)
        for error in validate_artifacts(root):
            findings.error(error)
    validate_run_files(root, results, findings)
    for warning in findings.warnings:
        print(f"WARNING: {warning}")
    for error in findings.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(
        f"validated cases={len(results)} errors={len(findings.errors)} "
        f"warnings={len(findings.warnings)}"
    )
    return 1 if findings.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
