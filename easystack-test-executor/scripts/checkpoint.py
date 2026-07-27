#!/usr/bin/env python3
"""Advance a test run only through contract-authorized transitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from _actions import bind_action
from _case_gate import (
    case_gate_errors,
    failed_dependencies,
)
from _contract import (
    STEP_PHASES,
    case_by_id,
)
from _events import append_event, load_events, project_state, verify_phase_events
from _harness import atomic_json, atomic_text, read_json, safe_component
from _resources import reconcile_resources
from _projections import sync_event_views


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="action", required=True)
    for name in ("next", "show"):
        command = commands.add_parser(name)
        command.add_argument("--result-root", required=True, type=Path)
    advance = commands.add_parser("advance")
    advance.add_argument("--result-root", required=True, type=Path)
    advance.add_argument("--case-id", required=True)
    skip = commands.add_parser("skip")
    skip.add_argument("--result-root", required=True, type=Path)
    skip.add_argument("--case-id", required=True)
    skip.add_argument("--action-id", required=True)
    skip.add_argument("--reason", required=True)
    abort = commands.add_parser("abort")
    abort.add_argument("--result-root", required=True, type=Path)
    abort.add_argument("--reason", required=True)
    return root

def load_run(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    contract = read_json(root / "execution-contract.json")
    if not contract:
        raise ValueError("execution-contract.json not found; run compile-plan.py first")
    events = load_events(root / "events.jsonl")
    if contract.get("schema_version") == 3:
        sync_event_views(root)
    errors = verify_phase_events(contract, events)
    if errors:
        raise ValueError("; ".join(errors))
    return contract, events, project_state(contract, events)

def incomplete_step(case: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    phase = state["phase"]
    for step in case["actions"]:
        if step["phase"] == phase and step["id"] not in state["step_statuses"]:
            return step
    return None

def next_instruction(
    contract: dict[str, Any], state: dict[str, Any], root: Path | None = None
) -> dict[str, Any]:
    case_id = state["current_case"]
    if contract.get("schema_version") != 3:
        return {
            "allowed_action": "legacy_read_only",
            "reason": "V2 runs may only be rendered or validated",
        }
    case = case_by_id(contract, case_id)
    current = state["cases"][case_id]
    step = incomplete_step(case, current)
    phases = ["NOT_STARTED", *contract["phase_order"]]
    next_phase = phases[phases.index(current["phase"]) + 1] if current["phase"] != "COMPLETE" else None
    blocked = failed_dependencies(root, case) if root and case.get("dependencies") else []
    bound_argv = None
    gate_reasons: list[str] = []
    script_root = Path(__file__).resolve().parent
    if state.get("run_status") == "RUN_ABORTED":
        return {"allowed_action": "run_aborted", "reason": state["abort_reason"]}
    action_type = "advance_phase"
    launcher = [
        sys.executable, str(script_root / "checkpoint.py"), "advance",
        "--result-root", str(root), "--case-id", case_id,
    ] if root else []
    if step:
        policy = (
            contract["cleanup_policy"]
            if case["cleanup_policy"] == "inherit"
            else case["cleanup_policy"]
        )
        functional = (
            read_json(
                root / "cases" / case_id / "case-verdict.json", {}
            ).get("functional_status")
            if root else None
        )
        preserve_cleanup = bool(
            step["phase"] == "APPLY_CLEANUP_POLICY"
            and (
                policy == "preserve_all"
                or (
                    functional == "FAIL"
                    and policy in {"preserve_on_failure", "cleanup_on_success"}
                )
            )
        )
        should_skip = bool(blocked or preserve_cleanup)
        action_type = "skip_action" if should_skip else "run_action"
        script = "checkpoint.py" if should_skip else "run-action.py"
        launcher = [
            sys.executable, str(script_root / script),
            "skip" if should_skip else "--result-root",
        ]
        if should_skip:
            reason = (
                f"failed dependencies: {','.join(blocked)}"
                if blocked else f"cleanup preserved by policy: {policy}"
            )
            launcher += [
                "--result-root", str(root), "--case-id", case_id,
                "--action-id", step["id"], "--reason",
                reason,
            ]
        else:
            launcher += [
                str(root), "--case-id", case_id, "--action-id", step["id"],
            ]
            try:
                if root is None:
                    raise ValueError("result root is required to bind action")
                bound_argv = bind_action(
                    contract, step, read_json(root / "resources-all.json", [])
                )
            except ValueError as error:
                action_type = "blocked_contract"
                launcher = []
                gate_reasons.append(str(error))
    elif current["phase"] == "DERIVE_VERDICT" and root and not (
        root / "cases" / case_id / "case-verdict.json"
    ).exists():
        action_type = "derive_verdict"
        launcher = [
            sys.executable, str(script_root / "finalize-case.py"),
            "--result-root", str(root), "--case-id", case_id,
            "--stage", "verdict",
        ]
    elif current["phase"] == "FINALIZE_RESULT" and root and not (
        root / "cases" / case_id / "result.json"
    ).exists():
        action_type = "finalize_result"
        launcher = [
            sys.executable, str(script_root / "finalize-case.py"),
            "--result-root", str(root), "--case-id", case_id,
            "--stage", "result",
        ]
    return {
        "case_id": case_id,
        "case_title": case["title"],
        "current_phase": current["phase"],
        "next_phase": next_phase,
        "planned_action": step,
        "planned_step": step,
        "allowed_action": action_type,
        "launcher_argv": launcher,
        "bound_argv": bound_argv,
        "gate_reasons": gate_reasons,
        "blocked_by_failed_dependencies": blocked,
    }

def write_projection(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    state = project_state(contract, load_events(root / "events.jsonl"))
    instruction = next_instruction(contract, state, root) if state["current_case"] else {}
    state["next_instruction"] = instruction
    atomic_json(root / "run-state.json", state)
    lines = [
        "# Test Run Resume",
        "",
        f"- Run ID: `{state['run_id']}`",
        f"- Current case: `{instruction.get('case_id', '全部完成')}`",
        f"- Current phase: `{instruction.get('current_phase', 'COMPLETE')}`",
        f"- Allowed action: `{instruction.get('allowed_action', 'none')}`",
        f"- Planned action: `{(instruction.get('planned_action') or {}).get('id', '-')}`",
        "",
        "恢复时先运行:",
        "",
        "```bash",
        f"{sys.executable} {Path(__file__).resolve()} next --result-root {root}",
        "```",
        "",
        "只执行新返回的 `launcher_argv`, 不直接执行本文件缓存的旧动作.",
        "不得从对话历史推断进度或手工跳转 phase.",
    ]
    atomic_text(root / "resume.md", "\n".join(lines) + "\n")
    return state


def phase_gate(root: Path, contract: dict[str, Any], state: dict[str, Any], case_id: str) -> None:
    case = case_by_id(contract, case_id)
    phase = state["cases"][case_id]["phase"]
    if phase == "NOT_STARTED":
        incomplete = [
            dep for dep in case.get("dependencies", [])
            if state["cases"][dep]["phase"] != "COMPLETE"
        ]
        if incomplete:
            raise ValueError(f"dependencies not complete: {','.join(incomplete)}")
    if phase in STEP_PHASES:
        planned = [step for step in case["actions"] if step["phase"] == phase]
        statuses = state["cases"][case_id]["step_statuses"]
        missing = [step["id"] for step in planned if step["id"] not in statuses]
        if missing:
            raise ValueError(f"planned steps not terminal: {','.join(missing)}")
    case_root = root / "cases" / case_id
    if phase == "COLLECT_LOGS" and case["log_requirement"] == "required":
        if not (case_root / "logs" / "collection-status.json").exists():
            raise ValueError("required log collection status missing")
    if phase == "COLLECT_RESOURCES":
        errors = reconcile_resources(root)
        if errors:
            raise ValueError("; ".join(errors))
    if phase == "DERIVE_VERDICT":
        verdict = read_json(case_root / "case-verdict.json")
        if not verdict or not verdict.get("derived_by_harness"):
            raise ValueError("harness-derived case-verdict.json missing")
    if phase in {"FINALIZE_RESULT", "CASE_GATE"}:
        result = read_json(case_root / "result.json")
        if not result or not result.get("derived_by_harness"):
            raise ValueError("harness-derived result.json missing")
    if phase == "CASE_GATE":
        errors = case_gate_errors(root, contract, case, state)
        if errors:
            raise ValueError("; ".join(errors))
    if phase == "APPLY_CLEANUP_POLICY":
        resources = read_json(case_root / "resources.json", [])
        pending = [item["id"] for item in resources if item.get("cleanup_result") == "PENDING"]
        if pending:
            raise ValueError(f"resource cleanup still pending: {','.join(pending)}")


def skip_action(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract, _, state = load_run(root)
    case_id = safe_component(args.case_id, "case ID")
    action_id = safe_component(args.action_id, "action ID")
    case = case_by_id(contract, case_id)
    action = incomplete_step(case, state["cases"][case_id])
    if not action or action["id"] != action_id:
        raise ValueError("only the next action may be skipped")
    blocked = failed_dependencies(root, case)
    policy = (
        contract["cleanup_policy"]
        if case["cleanup_policy"] == "inherit"
        else case["cleanup_policy"]
    )
    functional = read_json(
        root / "cases" / case_id / "case-verdict.json", {}
    ).get("functional_status")
    cleanup_preserved = (
        action["phase"] == "APPLY_CLEANUP_POLICY"
        and (
            policy == "preserve_all"
            or (
                functional == "FAIL"
                and policy in {"preserve_on_failure", "cleanup_on_success"}
            )
        )
    )
    if not blocked and not cleanup_preserved:
        raise ValueError("action is not eligible for automatic skip")
    append_event(
        root, contract["timezone"], "ACTION_SKIPPED", case_id, action_id,
        {"status": "SKIPPED_BY_PLAN", "reason": args.reason},
    )
    if cleanup_preserved:
        for resource in read_json(root / "cases" / case_id / "resources.json", []):
            updated = {
                **resource,
                "cleanup_result": "PRESERVED",
                "final_state": "PRESENT",
            }
            append_event(
                root, contract["timezone"], "RESOURCE_UPDATED",
                case_id, action_id, updated,
            )
        sync_event_views(root)
    write_projection(root, contract)


def abort_run(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract, _, state = load_run(root)
    if state.get("run_status") == "RUN_ABORTED":
        raise ValueError("run is already aborted")
    append_event(
        root, contract["timezone"], "RUN_ABORTED",
        payload={"reason": args.reason.strip()},
    )
    write_projection(root, contract)


def advance(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract, _, state = load_run(root)
    if contract.get("schema_version") != 3:
        raise ValueError("V2 runs are read-only")
    case_id = safe_component(args.case_id, "case ID")
    case_by_id(contract, case_id)
    if case_id != state["current_case"]:
        raise ValueError(f"only current case may advance: {state['current_case']}")
    phase_gate(root, contract, state, case_id)
    phases = ["NOT_STARTED", *contract["phase_order"]]
    current = state["cases"][case_id]["phase"]
    if current == "COMPLETE":
        raise ValueError("case already complete")
    target = phases[phases.index(current) + 1]
    append_event(
        root, contract["timezone"], "PHASE_ADVANCED", case_id,
        payload={"from_phase": current, "to_phase": target},
    )
    write_projection(root, contract)


def main() -> int:
    args = parser().parse_args()
    try:
        root = args.result_root.resolve()
        if args.action == "skip":
            skip_action(args)
        elif args.action == "abort":
            abort_run(args)
        elif args.action == "advance":
            advance(args)
        else:
            contract, _, state = load_run(root)
            if args.action == "next":
                if not state["current_case"]:
                    print(json.dumps({"allowed_action": "run_complete"}, indent=2))
                    return 0
                instruction = next_instruction(contract, state, root)
                print(json.dumps(instruction, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(state, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"checkpoint error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
