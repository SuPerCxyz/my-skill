#!/usr/bin/env python3
"""Validate durable state and deterministic report structure."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

from _harness import (
    case_anchor,
    load_jsonl,
    object_digest,
    read_json,
    safe_component,
    skill_digest,
)
from _validation import H3, REQUIRED_RESULT_FIELDS, Findings, valid_local_time


def validate_command_records(
    root: Path, case: dict[str, Any], findings: Findings
) -> None:
    case_id = case["case_id"]
    records = load_jsonl(root / "cases" / case_id / "commands.jsonl")
    required = (
        "step_id",
        "start_local",
        "end_local",
        "timezone",
        "duration_ms",
        "return_code",
        "result",
    )
    invalid = not records
    timezone = read_json(root / "execution-contract.json", {}).get("timezone")
    for index, record in enumerate(records, 1):
        missing = [field for field in required if field not in record]
        if missing:
            invalid = True
            findings.warning(
                f"{case_id}: command record {index} missing {','.join(missing)}"
            )
        duration = record.get("duration_ms")
        if not isinstance(duration, int) or duration < 0:
            invalid = True
            findings.warning(f"{case_id}: command record {index} has invalid duration")
        if not valid_local_time(record.get("start_local")) or not valid_local_time(
            record.get("end_local")
        ):
            invalid = True
            findings.warning(
                f"{case_id}: command record {index} has invalid local timestamp"
            )
        if record.get("timezone") != timezone:
            invalid = True
            findings.warning(
                f"{case_id}: command record {index} timezone differs from contract"
            )
    if invalid and case.get("timing_status") != "INVALID":
        findings.error(f"{case_id}: incomplete timing must set timing_status=INVALID")
    if case.get("timing_status") == "INVALID":
        findings.warning(f"{case_id}: 步骤时间记录异常")


def validate_evidence(
    root: Path, case: dict[str, Any], findings: Findings
) -> None:
    case_id = case["case_id"]
    requirement = case.get("log_requirement")
    status = case.get("evidence_status")
    has_logs = bool(case.get("logs"))
    invalid_logs = False
    required_fields = (
        "timestamp_local",
        "raw_timestamp",
        "service",
        "pod",
        "container",
        "request_or_resource_id",
        "source_path",
        "excerpt",
    )
    case_root = (root / "cases" / case_id).resolve()
    for index, log in enumerate(case.get("logs", []), 1):
        missing = [field for field in required_fields if not log.get(field)]
        evidence_path = case_root / str(log.get("source_path", ""))
        try:
            evidence_path.resolve().relative_to(case_root)
        except ValueError:
            missing.append("safe_source_path")
        if not evidence_path.is_file():
            missing.append("existing_source_path")
        if missing:
            invalid_logs = True
            findings.warning(
                f"{case_id}: log evidence {index} invalid: {','.join(missing)}"
            )
    if requirement == "required" and not has_logs:
        if status not in {"MISSING", "INVALID"}:
            findings.error(
                f"{case_id}: required logs absent; evidence_status must be MISSING or INVALID"
            )
        else:
            findings.warning(f"{case_id}: 关键日志未保存")
    elif requirement == "optional" and not has_logs:
        if status != "PARTIAL":
            findings.error(
                f"{case_id}: optional logs absent; evidence_status must be PARTIAL"
            )
        else:
            findings.warning(f"{case_id}: optional logs not collected")
    elif requirement == "none" and status != "NOT_APPLICABLE":
        findings.error(
            f"{case_id}: log_requirement=none requires evidence_status=NOT_APPLICABLE"
        )
    if invalid_logs and status not in {"PARTIAL", "MISSING", "INVALID"}:
        findings.error(
            f"{case_id}: incomplete log traceability requires a diagnostic evidence status"
        )


def validate_case(root: Path, path: Path, findings: Findings) -> dict[str, Any] | None:
    case = read_json(path)
    if not case:
        findings.error(f"{path}: empty or invalid JSON")
        return None
    case_id = case.get("case_id", path.parent.name)
    try:
        safe_component(case_id, "case ID")
    except ValueError as error:
        findings.error(str(error))
        return None
    if case_id != path.parent.name:
        findings.error(f"{case_id}: case ID does not match result directory")
        return None
    missing = [field for field in REQUIRED_RESULT_FIELDS if field not in case]
    if missing:
        findings.error(f"{case_id}: result.json missing {','.join(missing)}")
        return None
    if case["functional_status"] not in {"PASS", "FAIL"}:
        findings.error(f"{case_id}: functional_status must be PASS or FAIL")
    if case["timing_status"] not in {"VALID", "INVALID"}:
        findings.error(f"{case_id}: timing_status has no terminal value")
    if case["evidence_status"] not in {
        "COMPLETE",
        "PARTIAL",
        "MISSING",
        "INVALID",
        "NOT_APPLICABLE",
    }:
        findings.error(f"{case_id}: evidence_status has no terminal value")
    if case["cleanup_status"] not in {"COMPLETE", "PARTIAL", "PRESERVED"}:
        findings.error(f"{case_id}: cleanup_status has no terminal value")
    if case["diagnostic_status"] not in {
        "CONCLUSIVE",
        "INCONCLUSIVE",
        "BLOCKED",
    }:
        findings.error(f"{case_id}: diagnostic_status has no terminal value")
    if case["log_requirement"] not in {"required", "optional", "none"}:
        findings.error(f"{case_id}: invalid log_requirement")

    validate_command_records(root, case, findings)
    validate_evidence(root, case, findings)
    resources = read_json(root / "cases" / case_id / "resources.json", [])
    for index, resource in enumerate(resources, 1):
        required = ("type", "name", "uuid", "owning_case", "owning_step")
        absent = [field for field in required if not resource.get(field)]
        if absent:
            findings.error(
                f"{case_id}: resource {index} missing {','.join(absent)}"
            )
    return case


def validate_case_markdown(
    root: Path, case: dict[str, Any], findings: Findings
) -> None:
    case_id = case["case_id"]
    path = root / "cases" / case_id / "result.md"
    if not path.exists():
        findings.error(f"{case_id}: result.md missing")
        return
    text = path.read_text(encoding="utf-8")
    headings = re.findall(r"^### (.+)$", text, flags=re.MULTILINE)
    if tuple(headings) != H3:
        findings.error(f"{case_id}: H3 fields or order do not match contract")
    expected = "成功" if case["functional_status"] == "PASS" else "失败"
    section = text.split("### 执行结果", 1)[-1].split("### 测试目标", 1)[0]
    if expected not in section:
        findings.error(f"{case_id}: execution result disagrees with functional_status")
    note_required = case["timing_status"] == "INVALID" or case[
        "evidence_status"
    ] in {"PARTIAL", "MISSING", "INVALID"}
    if note_required and "说明:" not in section:
        findings.error(f"{case_id}: execution result warning note missing")


def validate_run_files(
    root: Path, cases: list[dict[str, Any]], findings: Findings
) -> None:
    summary_path = root / "summary.md"
    csv_path = root / "results.csv"
    run_path = root / "run.json"
    for path in (summary_path, csv_path, run_path):
        if not path.exists():
            findings.error(f"{path.name} missing")
    if not summary_path.exists() or not csv_path.exists() or not run_path.exists():
        return
    summary = summary_path.read_text(encoding="utf-8")
    if len(re.findall(r"^# ", summary, flags=re.MULTILINE)) != 1:
        findings.error("summary.md must contain exactly one H1")
    for case in cases:
        link = f"[查看](#case-{case_anchor(case['case_id'])})"
        if link not in summary:
            findings.error(f"{case['case_id']}: summary index link missing")
        result_path = root / "cases" / case["case_id"] / "result.md"
        if result_path.exists():
            section = result_path.read_text(encoding="utf-8")
            if section.rstrip() not in summary:
                findings.error(f"{case['case_id']}: result.md differs from summary.md")

    with csv_path.open(encoding="utf-8", newline="") as stream:
        rows = {row["case_id"]: row for row in csv.DictReader(stream)}
    for case in cases:
        expected = "成功" if case["functional_status"] == "PASS" else "失败"
        if rows.get(case["case_id"], {}).get("execution_result") != expected:
            findings.error(f"{case['case_id']}: results.csv result mismatch")

    run = read_json(run_path, {})
    expected_counts = {
        "success": sum(case["functional_status"] == "PASS" for case in cases),
        "failure": sum(case["functional_status"] != "PASS" for case in cases),
    }
    if run.get("total_cases") != len(cases):
        findings.error("run.json total_cases mismatch")
    if run.get("result_counts") != expected_counts:
        findings.error("run.json result_counts mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.result_root.resolve()
    findings = Findings()
    contract = read_json(root / "execution-contract.json")
    state = read_json(root / "run-state.json")
    if not contract or not state:
        print("validation error: contract or run state missing", file=sys.stderr)
        return 2

    current_digest = skill_digest(Path(__file__).resolve().parents[1])
    if contract.get("skill_sha256") != current_digest:
        findings.error("skill content changed after run initialization")
    if state.get("contract_sha256") != object_digest(contract):
        findings.error("execution contract changed after run initialization")
    paths = sorted((root / "cases").glob("*/result.json"))
    cases = [
        case
        for path in paths
        if (case := validate_case(root, path, findings)) is not None
    ]
    expected_ids = set(contract.get("case_ids", []))
    started_ids = set(state.get("cases", {}))
    result_ids = {case.get("case_id") for case in cases}
    missing_results = (expected_ids | started_ids) - result_ids
    if missing_results:
        findings.error(f"case results missing: {','.join(sorted(missing_results))}")
    for case_id, case_state in state.get("cases", {}).items():
        if case_state.get("phase") != "COMPLETE":
            findings.error(f"{case_id}: checkpoint phase is not COMPLETE")
    for case in cases:
        validate_case_markdown(root, case, findings)
    validate_run_files(root, cases, findings)
    for warning in findings.warnings:
        print(f"WARNING: {warning}")
    for error in findings.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(
        f"validated cases={len(cases)} errors={len(findings.errors)} "
        f"warnings={len(findings.warnings)}"
    )
    return 1 if findings.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
