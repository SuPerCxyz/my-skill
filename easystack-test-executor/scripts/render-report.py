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
    markdown_table as table,
    read_json,
    redact,
    safe_component,
)
from _validation import case_text_errors
def execution_result(case: dict[str, Any]) -> str:
    return "成功" if case.get("functional_status") == "PASS" else "失败"


def result_note(case: dict[str, Any]) -> str:
    notes = ["步骤时间记录异常"] if case.get("timing_status") == "INVALID" else []
    evidence = case.get("evidence_status")
    notes += ["关键日志未完整保存"] if evidence in {"PARTIAL", "MISSING", "INVALID"} else []
    if case.get("partial_status"):
        notes.append(f"任务状态为 {case['partial_status']}")
    return f"\n\n说明: {'; '.join(notes)}。" if notes else ""


def render_steps(root: Path, case_id: str, case: dict[str, Any]) -> list[str]:
    records = load_jsonl(root / "cases" / case_id / "commands.jsonl")
    by_action: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_action.setdefault(record.get("action_id") or record.get("step_id", ""), []).append(record)
    statuses = case.get("action_statuses", {})
    rows = []
    for action in case.get("contract_actions", []):
        attempts = by_action.get(action["id"], [])
        if not attempts:
            status = statuses.get(action["id"], {})
            rows.append([
                action["id"], "-", "-", redact(action["description"]),
                status.get("start_local", "-"), status.get("end_local", "-"),
                status.get("duration_ms", "-"), "-",
                status.get("status", "NOT_RUN"),
            ])
        for record in attempts:
            rows.append([
                action["id"], record.get("attempt", ""),
                record.get("command_id", ""),
                redact(record.get("description") or record.get("command", "")),
                record.get("start_local", ""), record.get("end_local", ""),
                record.get("duration_ms", ""), record.get("return_code", ""),
                record.get("result", ""),
            ])
    if not rows:
        rows = [["-", "-", "-", "未记录", "-", "-", "-", "-", "失败"]]
    return table(
        [
            "Step", "Attempt", "Command ID", "详细操作或命令", "Start local",
            "End local", "Duration ms", "Return code", "结果",
        ],
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
            item.get("id") or item.get("uuid", ""),
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
        if case.get("evidence_status") == "OPTIONAL_NOT_COLLECTED":
            return ["可选日志未收集, 不影响功能结果。"]
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
        f"测试需求: {case['requirement_summary']}",
        "",
        f"场景标识: `{case['scenario_key']}`",
        "",
        f"详细目标: {case.get('objective') or '同测试需求'}",
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


def load_cases(
    root: Path, contract: dict[str, Any], allow_partial: bool
) -> list[dict[str, Any]]:
    cases = []
    state = read_json(root / "run-state.json", {})
    definitions = {item["id"]: item for item in contract["cases"]}
    for case_id in contract["case_order"]:
        path = root / "cases" / case_id / "result.json"
        case = read_json(path)
        if not case:
            if not allow_partial:
                raise ValueError(f"{case_id}: result.json missing")
            definition = definitions[case_id]
            case_state = state.get("cases", {}).get(case_id, {})
            phase = case_state.get("phase", "NOT_STARTED")
            case = {
                "case_id": case_id,
                "scenario_key": definition["scenario_key"],
                "title": definition["title"],
                "requirement_summary": definition["requirement_summary"],
                "objective": definition["objective"],
                "functional_status": "FAIL",
                "timing_status": "INVALID",
                "evidence_status": "MISSING",
                "cleanup_status": "PENDING",
                "diagnostic_status": "BLOCKED",
                "log_requirement": definition["log_requirement"],
                "checks": [],
                "logs": [],
                "partial_status": case_state.get(
                    "status", "NOT_RUN" if phase == "NOT_STARTED" else "RUN_ABORTED"
                ),
            }
        definition = definitions[case_id]
        case["contract_actions"] = definition["actions"]
        case["action_statuses"] = state.get("cases", {}).get(case_id, {}).get(
            "step_statuses", {}
        )
        safe_component(case["case_id"], "case ID")
        errors = case_text_errors(case)
        if errors:
            raise ValueError(f"{case['case_id']}: {'; '.join(errors)}")
        cases.append(case)
    return cases


def write_results_csv(root: Path, cases: list[dict[str, Any]]) -> None:
    fields = [
        "case_id",
        "scenario_key",
        "title",
        "requirement_summary",
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
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    try:
        cases = load_cases(root, contract, args.allow_partial)
    except (KeyError, ValueError) as error:
        print(f"render-report error: {error}", file=sys.stderr)
        return 2
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
                case["requirement_summary"],
                execution_result(case),
                f"[查看](#case-{case_anchor(case['case_id'])})",
            ]
        )
    headers = ["用例 ID", "用例名称", "测试需求", "执行结果", "跳转"]
    summary = ["# 详细结果", "", *table(headers, index_rows), ""]
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
            "run_fingerprint": {
                "contract_sha256": contract["contract_sha256"],
                "profile_sha256": contract.get("environment_profile_sha256", ""),
                "skill_sha256": contract["skill_sha256"],
            },
            "remaining_resources": [
                item for item in read_json(root / "resources-all.json", [])
                if item.get("final_state") != "DELETED"
            ],
        }
    )
    atomic_json(root / "run.json", run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
