#!/usr/bin/env python3
"""Create and update durable state for a long EasyStack test run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from _harness import (
    atomic_json,
    atomic_text,
    local_now,
    object_digest,
    read_json,
    safe_component,
    skill_digest,
)


PHASES = (
    "DISCOVER_CASE_CONTEXT",
    "OPEN_LOG_WINDOW",
    "SNAPSHOT_SERVICE_INSTANCES",
    "PREPARE",
    "EXECUTE",
    "WAIT",
    "VERIFY",
    "CLOSE_LOG_WINDOW",
    "COLLECT_LOGS",
    "COLLECT_RESOURCES",
    "RECORD_RESULT",
    "CASE_GATE",
    "APPLY_CLEANUP_POLICY",
    "ADVANCE_LOG_CURSOR",
    "COMPLETE",
)
STATUSES = {
    "functional_status": ("PASS", "FAIL", "UNKNOWN"),
    "timing_status": ("VALID", "INVALID", "PENDING"),
    "evidence_status": (
        "COMPLETE",
        "PARTIAL",
        "MISSING",
        "INVALID",
        "NOT_APPLICABLE",
        "PENDING",
    ),
    "cleanup_status": ("COMPLETE", "PARTIAL", "PRESERVED", "PENDING"),
    "diagnostic_status": ("CONCLUSIVE", "INCONCLUSIVE", "BLOCKED", "PENDING"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    init = commands.add_parser("init")
    init.add_argument("--result-root", required=True, type=Path)
    init.add_argument("--run-id", required=True)
    init.add_argument("--timezone", required=True)
    init.add_argument("--cleanup-policy", default="preserve_on_failure")
    init.add_argument("--case", action="append", default=[])

    update = commands.add_parser("update")
    update.add_argument("--result-root", required=True, type=Path)
    update.add_argument("--case-id", required=True)
    update.add_argument("--phase", required=True, choices=PHASES)
    update.add_argument("--next-action", required=True)
    for name, choices in STATUSES.items():
        update.add_argument(f"--{name.replace('_', '-')}", choices=choices)

    resource = commands.add_parser("resource")
    resource.add_argument("--result-root", required=True, type=Path)
    resource.add_argument("--case-id", required=True)
    resource.add_argument("--step-id", required=True)
    resource.add_argument("--type", required=True)
    resource.add_argument("--name", required=True)
    resource.add_argument("--uuid", required=True)
    resource.add_argument("--project", default="")
    resource.add_argument("--status", default="")
    resource.add_argument("--host-backend", default="")
    resource.add_argument("--cleanup-policy", default="inherit")
    resource.add_argument("--final-state", default="")

    show = commands.add_parser("show")
    show.add_argument("--result-root", required=True, type=Path)
    return parser


def write_resume(root: Path, state: dict) -> None:
    current = state.get("current_case") or "未开始"
    case = state.get("cases", {}).get(current, {})
    lines = [
        "# Test Run Resume",
        "",
        f"- Run ID: `{state['run_id']}`",
        f"- Timezone: `{state['timezone']}`",
        f"- Current case: `{current}`",
        f"- Current phase: `{case.get('phase', '未开始')}`",
        f"- Next action: {case.get('next_action', '选择首个用例')}",
        f"- Last checkpoint: `{state['updated_local']}`",
        "",
        "恢复时先读取 `execution-contract.json` 和 `run-state.json`, "
        "再执行上面的 Next action. 不从对话历史推断遗漏状态.",
    ]
    atomic_text(root / "resume.md", "\n".join(lines) + "\n")


def init_run(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError(f"result root is not empty: {root}")
    ZoneInfo(args.timezone)
    for case_id in args.case:
        safe_component(case_id, "case ID")
    root.mkdir(parents=True, exist_ok=True)
    (root / "cases").mkdir()
    skill_root = Path(__file__).resolve().parents[1]
    started = local_now(args.timezone)
    contract = {
        "schema_version": 1,
        "run_id": args.run_id,
        "timezone": args.timezone,
        "cleanup_policy": args.cleanup_policy,
        "case_ids": args.case,
        "required_h3": [
            "执行结果",
            "测试目标",
            "测试步骤",
            "结果检查",
            "创建的资源",
            "关键日志输出",
        ],
        "execution_result_mapping": {
            "PASS": "成功",
            "OTHER": "失败",
        },
        "skill_sha256": skill_digest(skill_root),
        "created_local": started,
    }
    atomic_json(root / "execution-contract.json", contract)
    state = {
        "schema_version": 1,
        "run_id": args.run_id,
        "timezone": args.timezone,
        "cleanup_policy": args.cleanup_policy,
        "contract_sha256": object_digest(contract),
        "started_local": started,
        "updated_local": started,
        "current_case": None,
        "cases": {},
    }
    atomic_json(root / "run-state.json", state)
    atomic_json(root / "resources-all.json", [])
    write_resume(root, state)


def update_case(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    state = read_json(root / "run-state.json")
    if not state:
        raise ValueError("run-state.json not found; run init first")
    safe_component(args.case_id, "case ID")
    now = local_now(state["timezone"])
    case = state["cases"].setdefault(args.case_id, {})
    case.update(
        {
            "phase": args.phase,
            "next_action": args.next_action,
            "updated_local": now,
        }
    )
    for name in STATUSES:
        value = getattr(args, name)
        if value:
            case[name] = value
    state["current_case"] = args.case_id
    state["updated_local"] = now
    atomic_json(root / "run-state.json", state)
    write_resume(root, state)


def record_resource(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    state = read_json(root / "run-state.json")
    if not state:
        raise ValueError("run-state.json not found; run init first")
    safe_component(args.case_id, "case ID")
    safe_component(args.step_id, "step ID")
    item = {
        "type": args.type,
        "name": args.name,
        "uuid": args.uuid,
        "project": args.project,
        "status": args.status,
        "host_backend": args.host_backend,
        "created_local": local_now(state["timezone"]),
        "timezone": state["timezone"],
        "owning_case": args.case_id,
        "owning_step": args.step_id,
        "cleanup_policy": args.cleanup_policy,
        "final_state": args.final_state,
    }
    case_path = root / "cases" / args.case_id / "resources.json"
    all_path = root / "resources-all.json"
    for path in (case_path, all_path):
        resources = read_json(path, [])
        resources = [entry for entry in resources if entry.get("uuid") != args.uuid]
        resources.append(item)
        atomic_json(path, resources)
    state["current_case"] = args.case_id
    state["updated_local"] = item["created_local"]
    case = state["cases"].setdefault(args.case_id, {})
    case["updated_local"] = item["created_local"]
    case["next_action"] = "继续当前 phase, 资源已写入台账"
    atomic_json(root / "run-state.json", state)
    write_resume(root, state)


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.action == "init":
            init_run(args)
        elif args.action == "update":
            update_case(args)
        elif args.action == "resource":
            record_resource(args)
        else:
            state = read_json(args.result_root.resolve() / "run-state.json")
            if not state:
                raise ValueError("run-state.json not found")
            print(json.dumps(state, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        print(f"checkpoint error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
