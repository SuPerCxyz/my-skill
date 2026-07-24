#!/usr/bin/env python3
"""Render the fixed Chinese Markdown report from structured case records."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Any

from _harness import (
    atomic_json,
    atomic_text,
    case_anchor,
    load_jsonl,
    local_now,
    markdown_cell,
    read_json,
    redact,
    safe_component,
)


H3 = ("执行结果", "测试目标", "测试步骤", "结果检查", "创建的资源", "关键日志输出")


def execution_result(case: dict[str, Any]) -> str:
    return "成功" if case.get("functional_status") == "PASS" else "失败"


def result_note(case: dict[str, Any]) -> str:
    notes = []
    if case.get("timing_status") == "INVALID":
        notes.append("步骤时间记录异常")
    if case.get("evidence_status") in {"PARTIAL", "MISSING", "INVALID"}:
        notes.append("关键日志未完整保存")
    return f"\n\n说明: {'; '.join(notes)}。" if notes else ""


def table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("-" * (len(header) + 2) for header in headers) + "|",
    ]
    output.extend(
        "| " + " | ".join(markdown_cell(value) for value in row) + " |"
        for row in rows
    )
    return output


def render_steps(root: Path, case_id: str, case: dict[str, Any]) -> list[str]:
    records = load_jsonl(root / "cases" / case_id / "commands.jsonl")
    if not records:
        records = case.get("steps", [])
    rows = []
    for step in records:
        operation = step.get("description") or step.get("command", "")
        rows.append(
            [
                step.get("step_id", ""),
                redact(operation),
                step.get("start_local", ""),
                step.get("end_local", ""),
                step.get("duration_ms", ""),
                step.get("return_code", ""),
                step.get("result", ""),
            ]
        )
    if not rows:
        rows = [["-", "未记录", "-", "-", "-", "-", "失败"]]
    return table(
        ["Step", "详细操作或命令", "Start local", "End local", "Duration ms", "Return code", "结果"],
        rows,
    )


def render_checks(case: dict[str, Any]) -> list[str]:
    rows = [
        [
            item.get("check", ""),
            item.get("expected", ""),
            item.get("actual", ""),
            item.get("result", ""),
            item.get("evidence", ""),
        ]
        for item in case.get("checks", [])
    ]
    if not rows:
        rows = [["功能结果", "符合用例预期", "未记录", "失败", "无"]]
    return table(["检查项", "Expected", "Actual", "结果", "Evidence"], rows)


def render_resources(root: Path, case_id: str, case: dict[str, Any]) -> list[str]:
    resources = read_json(root / "cases" / case_id / "resources.json")
    if resources is None:
        resources = case.get("resources", [])
    rows = [
        [
            item.get("type", ""),
            item.get("name", ""),
            item.get("uuid", ""),
            item.get("created_local", ""),
            item.get("owning_step", ""),
            item.get("host_backend", ""),
            item.get("final_state") or item.get("status", ""),
            item.get("cleanup_result") or item.get("cleanup_policy", ""),
        ]
        for item in resources
    ]
    if not rows:
        return ["本用例未创建资源。"]
    return table(
        [
            "Type",
            "Name",
            "UUID",
            "Created local",
            "所属 Step",
            "Host 或 Backend",
            "Final state",
            "Cleanup",
        ],
        rows,
    )


def render_logs(case: dict[str, Any]) -> list[str]:
    logs = case.get("logs", [])
    if not logs:
        if case.get("log_requirement") == "none":
            return ["不适用: 本用例无需日志验证。"]
        return ["未保存可追溯的关键日志。"]
    rows = [
        [
            item.get("timestamp_local", ""),
            item.get("raw_timestamp", ""),
            "/".join(
                filter(
                    None,
                    (
                        item.get("service"),
                        item.get("pod"),
                        item.get("container"),
                    ),
                )
            ),
            item.get("request_or_resource_id", ""),
            item.get("source_path", ""),
        ]
        for item in logs
    ]
    output = table(
        [
            "Local time",
            "Raw timestamp",
            "Service/Pod/Container",
            "Request 或 Resource ID",
            "证据路径",
        ],
        rows,
    )
    excerpts = [
        redact(str(item.get("excerpt", ""))).replace("```", "` ` `")
        for item in logs
        if item.get("excerpt")
    ]
    if excerpts:
        output.extend(["", "```text", "\n".join(excerpts), "```"])
    return output


def render_case(root: Path, case: dict[str, Any]) -> str:
    case_id = safe_component(case["case_id"], "case ID")
    lines = [
        f'<a id="case-{case_anchor(case_id)}"></a>',
        f"## {case_id} {case['title']}",
        "",
        "### 执行结果",
        "",
        execution_result(case) + result_note(case),
        "",
        "### 测试目标",
        "",
        case.get("objective", "未记录"),
        "",
        "### 测试步骤",
        "",
        *render_steps(root, case_id, case),
        "",
        "### 结果检查",
        "",
        *render_checks(case),
        "",
        "### 创建的资源",
        "",
        *render_resources(root, case_id, case),
        "",
        "### 关键日志输出",
        "",
        *render_logs(case),
    ]
    return "\n".join(lines).rstrip() + "\n"


def load_cases(root: Path) -> list[dict[str, Any]]:
    cases = []
    for path in sorted((root / "cases").glob("*/result.json")):
        case = read_json(path)
        if case:
            safe_component(case["case_id"], "case ID")
            cases.append(case)
    return sorted(cases, key=lambda item: item["case_id"])


def write_results_csv(root: Path, cases: list[dict[str, Any]]) -> None:
    fields = [
        "case_id",
        "title",
        "execution_result",
        "functional_status",
        "evidence_status",
        "timing_status",
        "cleanup_status",
        "diagnostic_status",
        "started_local",
        "ended_local",
        "result_link",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for case in cases:
        writer.writerow(
            {
                **{field: case.get(field, "") for field in fields},
                "execution_result": execution_result(case),
                "result_link": f"#case-{case_anchor(case['case_id'])}",
            }
        )
    atomic_text(root / "results.csv", buffer.getvalue())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    cases = load_cases(root)
    if not contract or not cases:
        print("render-report error: contract or case results missing", file=sys.stderr)
        return 2

    sections = []
    index_rows = []
    for case in cases:
        section = render_case(root, case)
        case_root = root / "cases" / case["case_id"]
        case_root.mkdir(parents=True, exist_ok=True)
        atomic_text(case_root / "result.md", section)
        sections.append(section)
        index_rows.append(
            [
                case["case_id"],
                case["title"],
                execution_result(case),
                f"[查看](#case-{case_anchor(case['case_id'])})",
            ]
        )
    summary = ["# 详细结果", "", *table(["用例 ID", "用例名称", "执行结果", "跳转"], index_rows), ""]
    summary.extend(section.rstrip() + "\n" for section in sections)
    atomic_text(root / "summary.md", "\n".join(summary).rstrip() + "\n")
    write_results_csv(root, cases)

    run = read_json(root / "run.json", {})
    run.update(
        {
            "run_id": contract["run_id"],
            "result_root": str(root),
            "timezone": contract["timezone"],
            "total_cases": len(cases),
            "result_counts": {
                "success": sum(execution_result(case) == "成功" for case in cases),
                "failure": sum(execution_result(case) == "失败" for case in cases),
            },
            "summary_path": "summary.md",
            "results_csv_path": "results.csv",
            "report_generated_local": local_now(contract["timezone"]),
        }
    )
    atomic_json(root / "run.json", run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
