#!/usr/bin/env python3
"""Shared definitions for test-run validation."""

from __future__ import annotations

import csv
from datetime import datetime
import re
from pathlib import Path
from typing import Any

from _harness import case_anchor, markdown_cell, read_json


H3 = ("执行结果", "测试目标", "测试步骤", "结果检查", "创建的资源", "关键日志输出")
INDEX_HEADER = "| 用例 ID | 用例名称 | 测试需求 | 执行结果 | 跳转 |"
REQUIRED_RESULT_FIELDS = (
    "case_id",
    "scenario_key",
    "title",
    "requirement_summary",
    "objective",
    "functional_status",
    "timing_status",
    "evidence_status",
    "cleanup_status",
    "diagnostic_status",
    "log_requirement",
)
PLACEHOLDERS = {"", "-", "--", "n/a", "na", "none", "null", "tbd", "unknown", "未命名"}
SCENARIO_KEY = re.compile(r"[A-Za-z0-9][A-Za-z0-9+_.:/-]{0,79}")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def valid_local_time(value: Any) -> bool:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return False
    return parsed.utcoffset() is not None


def case_text_errors(case: dict[str, Any]) -> list[str]:
    errors = []
    title = str(case.get("title", "")).strip()
    summary = str(case.get("requirement_summary", "")).strip()
    scenario_key = str(case.get("scenario_key", "")).strip()
    if title.lower() in PLACEHOLDERS or not CJK.search(title):
        errors.append("title must be a non-placeholder Chinese name")
    if not 2 <= len(title) <= 40 or "\n" in title:
        errors.append("title must be one line with 2-40 characters")
    if summary.lower() in PLACEHOLDERS or not CJK.search(summary):
        errors.append("requirement_summary must be a Chinese sentence")
    if not 6 <= len(summary) <= 60 or "\n" in summary:
        errors.append("requirement_summary must be one line with 6-60 characters")
    if len(re.findall(r"[。！？]", summary)) > 1:
        errors.append("requirement_summary must contain only one sentence")
    if not SCENARIO_KEY.fullmatch(scenario_key):
        errors.append("scenario_key must be a non-placeholder ASCII identifier")
    if title == scenario_key:
        errors.append("title must not reuse scenario_key")
    return errors


def validate_case_markdown(
    root: Path, case: dict[str, Any], findings: Findings
) -> None:
    case_id = case["case_id"]
    path = root / "cases" / case_id / "result.md"
    if not path.exists():
        findings.error(f"{case_id}: result.md missing")
        return
    text = path.read_text(encoding="utf-8")
    h2 = re.findall(r"^## (?!#)(.+)$", text, flags=re.MULTILINE)
    expected_h2 = f"{case_id} {case['title']}"
    if h2 != [expected_h2]:
        findings.error(f"{case_id}: result.md must contain exactly one expected H2")
    headings = re.findall(r"^### (.+)$", text, flags=re.MULTILINE)
    if tuple(headings) != H3:
        findings.error(f"{case_id}: H3 fields or order do not match contract")
    expected = "成功" if case["functional_status"] == "PASS" else "失败"
    section = text.split("### 执行结果", 1)[-1].split("### 测试目标", 1)[0]
    if expected not in section:
        findings.error(f"{case_id}: execution result disagrees with functional_status")
    target = text.split("### 测试目标", 1)[-1].split("### 测试步骤", 1)[0]
    if f"测试需求: {case['requirement_summary']}" not in target:
        findings.error(f"{case_id}: test requirement summary missing from target")
    if f"场景标识: `{case['scenario_key']}`" not in target:
        findings.error(f"{case_id}: scenario key missing from target")
    if "详细目标:" not in target:
        findings.error(f"{case_id}: detailed objective label missing from target")
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
    lines = summary.splitlines()
    if len(lines) < 3 or lines[2] != INDEX_HEADER:
        findings.error("summary.md index columns or order do not match contract")
    first_case = next(
        (index for index, line in enumerate(lines) if line.startswith("<a id=")),
        len(lines),
    )
    index_rows = [line for line in lines[3:first_case] if line.startswith("| ")]
    if len(index_rows) != len(cases):
        findings.error("summary.md index row count does not match case count")
    for case in cases:
        validate_summary_case(root, case, lines, summary, findings)
    validate_results_csv(csv_path, cases, findings)
    run = read_json(run_path, {})
    expected_counts = {
        "success": sum(case["functional_status"] == "PASS" for case in cases),
        "failure": sum(case["functional_status"] != "PASS" for case in cases),
    }
    if run.get("total_cases") != len(cases):
        findings.error("run.json total_cases mismatch")
    if run.get("result_counts") != expected_counts:
        findings.error("run.json result_counts mismatch")


def validate_summary_case(
    root: Path,
    case: dict[str, Any],
    lines: list[str],
    summary: str,
    findings: Findings,
) -> None:
    case_id = case["case_id"]
    link = f"[查看](#case-{case_anchor(case_id)})"
    expected = "成功" if case["functional_status"] == "PASS" else "失败"
    index_row = (
        f"| {markdown_cell(case_id)} | {markdown_cell(case['title'])} | "
        f"{markdown_cell(case['requirement_summary'])} | {expected} | {link} |"
    )
    if index_row not in lines:
        findings.error(f"{case_id}: strict summary index row mismatch")
    result_path = root / "cases" / case_id / "result.md"
    if result_path.exists():
        section = result_path.read_text(encoding="utf-8")
        if section.rstrip() not in summary:
            findings.error(f"{case_id}: result.md differs from summary.md")


def validate_results_csv(
    path: Path, cases: list[dict[str, Any]], findings: Findings
) -> None:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = {row["case_id"]: row for row in csv.DictReader(stream)}
    if set(rows) != {case["case_id"] for case in cases}:
        findings.error("results.csv case set does not match result records")
    for case in cases:
        case_id = case["case_id"]
        expected = "成功" if case["functional_status"] == "PASS" else "失败"
        row = rows.get(case_id, {})
        if row.get("execution_result") != expected:
            findings.error(f"{case_id}: results.csv result mismatch")
        for field in ("scenario_key", "title", "requirement_summary"):
            if row.get(field) != str(case[field]):
                findings.error(f"{case_id}: results.csv {field} mismatch")
