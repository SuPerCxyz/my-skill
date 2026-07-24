#!/usr/bin/env python3
"""Snapshot workers and collect correlation-filtered Kubernetes logs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from _contract import case_by_id
from _harness import atomic_json, read_json, safe_component
from _log_tools import (
    collect_one,
    correlation_ids,
    instance_map,
    parse_target,
    related_evidence,
    run_json,
    target_name,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(dest="action", required=True)
    snapshot = commands.add_parser("snapshot")
    snapshot.add_argument("--result-root", required=True, type=Path)
    snapshot.add_argument("--case-id", required=True)
    snapshot.add_argument("--stage", required=True, choices=("before", "after"))
    snapshot.add_argument("--namespace", required=True)
    snapshot.add_argument("--target", action="append", required=True)
    snapshot.add_argument("--kubectl", default="kubectl")
    collect = commands.add_parser("collect")
    collect.add_argument("--result-root", required=True, type=Path)
    collect.add_argument("--case-id", required=True)
    collect.add_argument("--namespace", required=True)
    collect.add_argument("--start", required=True)
    collect.add_argument("--end", required=True)
    collect.add_argument("--kubectl", default="kubectl")
    collect.add_argument("--timeout-seconds", type=int, default=300)
    return result


def snapshot(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    case_id = safe_component(args.case_id, "case ID")
    case_by_id(contract, case_id)
    path = root / "cases" / case_id / "logs" / f"instances-{args.stage}.json"
    requested = [parse_target(value) for value in args.target]
    existing = read_json(path)
    if existing:
        recorded = [
            {key: item[key] for key in ("name", "selector", "container")}
            for item in existing.get("targets", [])
        ]
        if recorded != requested or existing.get("namespace") != args.namespace:
            raise ValueError("existing snapshot differs from requested targets")
        return
    targets = []
    for target in requested:
        payload = run_json(
            [
                args.kubectl,
                "-n",
                args.namespace,
                "get",
                "pods",
                "-l",
                target["selector"],
                "-o",
                "json",
            ]
        )
        instances = []
        for pod in payload.get("items", []):
            statuses = {
                item["name"]: item
                for item in pod.get("status", {}).get("containerStatuses", [])
            }
            container = statuses.get(target["container"], {})
            instances.append(
                {
                    "pod": pod["metadata"]["name"],
                    "pod_uid": pod["metadata"]["uid"],
                    "node": pod.get("spec", {}).get("nodeName", ""),
                    "container": target["container"],
                    "container_id": container.get("containerID", ""),
                    "restart_count": container.get("restartCount", 0),
                }
            )
        targets.append({**target, "instances": instances})
    output = {"stage": args.stage, "namespace": args.namespace, "targets": targets}
    atomic_json(path, output)


def log_command(
    args: argparse.Namespace,
    pod: str,
    container: str,
    previous: bool = False,
) -> list[str]:
    command = [
        args.kubectl,
        "-n",
        args.namespace,
        "logs",
        pod,
        "-c",
        container,
        "--timestamps",
        f"--since-time={args.start}",
    ]
    if previous:
        command.append("--previous")
    return command


def collect_stream(
    args: argparse.Namespace,
    root: Path,
    case_id: str,
    target: dict[str, Any],
    item: dict[str, Any],
    suffix: str,
    identifiers: set[str],
    timezone_name: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    logs_root = root / "cases" / case_id / "logs"
    service = target["name"]
    pod_uid = item["pod_uid"]
    basename = f"{service}.{item['pod']}.{pod_uid[:8]}.{suffix}"
    raw_path = logs_root / "raw" / f"{basename}.log"
    error_path = logs_root / "raw" / f"{basename}.stderr.log"
    retry = 1
    while raw_path.exists() or error_path.exists():
        raw_path = logs_root / "raw" / f"{basename}.retry-{retry}.log"
        error_path = logs_root / "raw" / f"{basename}.retry-{retry}.stderr.log"
        retry += 1
    return_code, timed_out = collect_one(
        log_command(args, item["pod"], item["container"], suffix == "previous"),
        raw_path,
        error_path,
        args.timeout_seconds,
    )
    relative = raw_path.relative_to(root / "cases" / case_id).as_posix()
    stream = {
        "pod": item["pod"],
        "pod_uid": pod_uid,
        "stream": suffix,
        "return_code": return_code,
        "timed_out": timed_out,
        "source_path": relative,
    }
    evidence = []
    if return_code == 0:
        evidence = related_evidence(
            raw_path,
            relative,
            target,
            item,
            identifiers,
            timezone_name,
            args.end,
        )
    return stream, evidence


def collect(args: argparse.Namespace) -> None:
    root = args.result_root.resolve()
    contract = read_json(root / "execution-contract.json")
    case_id = safe_component(args.case_id, "case ID")
    case = case_by_id(contract, case_id)
    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00"))
    if start.utcoffset() is None or end.utcoffset() is None or end < start:
        raise ValueError("log window must use ordered offset-aware timestamps")
    logs_root = root / "cases" / case_id / "logs"
    before_data = read_json(logs_root / "instances-before.json")
    after_data = read_json(logs_root / "instances-after.json")
    if not before_data or not after_data:
        raise ValueError("both before and after instance snapshots are required")
    before = instance_map(before_data)
    after = instance_map(after_data)
    instances = {**before, **after}
    identifiers = correlation_ids(root, case_id)
    target_results: dict[str, dict[str, Any]] = {}
    evidence = []
    for key, source in instances.items():
        item = dict(source)
        target = item.pop("target")
        service = target["name"]
        result = target_results.setdefault(
            service, {"name": service, "status": "FAILED", "instances": []}
        )
        stream, found = collect_stream(
            args, root, case_id, target, item, "current", identifiers, contract["timezone"]
        )
        result["instances"].append(stream)
        evidence.extend(found)
        if stream["return_code"] == 0:
            result["status"] = "COLLECTED"
        prior = before.get(key)
        later = after.get(key)
        restarted = (
            prior
            and later
            and later.get("restart_count", 0) > prior.get("restart_count", 0)
        )
        if restarted:
            previous, found = collect_stream(
                args,
                root,
                case_id,
                target,
                item,
                "previous",
                identifiers,
                contract["timezone"],
            )
            result["instances"].append(previous)
            evidence.extend(found)
            if previous["return_code"] != 0:
                result["status"] = "PARTIAL"
    for result in target_results.values():
        codes = [item["return_code"] for item in result["instances"]]
        if codes and all(code == 0 for code in codes):
            result["status"] = "COLLECTED"
        elif any(code == 0 for code in codes):
            result["status"] = "PARTIAL"
        else:
            result["status"] = "FAILED"
    expected = {
        target_name(item)
        for item in case["log_targets"]
        if not isinstance(item, dict) or item.get("required", True)
    }
    collected = {
        name for name, item in target_results.items() if item["status"] == "COLLECTED"
    }
    if expected and expected <= collected and evidence:
        status = "COMPLETE"
    elif collected:
        status = "PARTIAL"
    else:
        status = "MISSING"
    atomic_json(
        logs_root / "collection-status.json",
        {
            "window": {"start": args.start, "end": args.end},
            "correlation_ids": sorted(identifiers),
            "targets": list(target_results.values()),
            "evidence_status": status,
            "evidence": evidence,
        },
    )


def main() -> int:
    args = parser().parse_args()
    try:
        if args.action == "snapshot":
            snapshot(args)
        else:
            collect(args)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
        print(f"collect-logs error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
