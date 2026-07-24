#!/usr/bin/env python3
"""Contract action binding, resource capture, and declarative checks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


PLACEHOLDER = re.compile(r"\$\{([^}]+)\}")


def lookup(value: Any, path: str) -> Any:
    current = value
    for component in path.split("."):
        if isinstance(current, list):
            current = current[int(component)]
        elif isinstance(current, dict) and component in current:
            current = current[component]
        else:
            raise ValueError(f"binding not found: {path}")
    return current


def bind_text(text: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        value = lookup(context, match.group(1))
        if isinstance(value, (dict, list)):
            raise ValueError(f"binding is not scalar: {match.group(1)}")
        return str(value)

    return PLACEHOLDER.sub(replace, text)


def bind_action(
    contract: dict[str, Any], action: dict[str, Any], resources: list[dict[str, Any]]
) -> list[str]:
    resource_map = {
        item["key"]: item for item in resources if item.get("key")
    }
    context = {
        "profile": contract["environment_profile"],
        "resource": resource_map,
        "run": {"id": contract["run_id"]},
    }
    return [bind_text(item, context) for item in action["command"]]


def decoded_output(text: str, output_format: str) -> Any:
    if output_format == "json":
        return json.loads(text)
    if output_format == "value":
        return text.strip().splitlines()[0] if text.strip() else ""
    return text


def resolve_capture(spec: Any, stdout: str, stderr: str) -> str:
    if isinstance(spec, str):
        return spec
    if not isinstance(spec, dict):
        raise ValueError("capture selector must be a string or object")
    source = stdout if spec.get("source", "stdout") == "stdout" else stderr
    value = decoded_output(source, spec.get("format", "text"))
    if "path" in spec:
        value = lookup(value, str(spec["path"]))
    if "regex" in spec:
        match = re.search(str(spec["regex"]), str(value), re.MULTILINE)
        if not match:
            raise ValueError(f"capture regex did not match: {spec['regex']}")
        value = match.group(int(spec.get("group", 1)))
    result = str(value).strip()
    if not result:
        raise ValueError("captured value is empty")
    return result


def capture_resources(
    action: dict[str, Any], stdout: str, stderr: str
) -> list[dict[str, Any]]:
    output = []
    for spec in action.get("capture", {}).get("resources", []):
        output.append(
            {
                "key": spec["key"],
                "type": spec["type"],
                "id": resolve_capture(spec["id"], stdout, stderr),
                "name": resolve_capture(spec["name"], stdout, stderr),
                "dependencies": list(spec.get("dependencies", [])),
                "cleanup_policy": spec.get("cleanup_policy", "delete"),
            }
        )
    return output


def action_output(root: Path, record: dict[str, Any], source: str) -> str:
    return (root / record[f"{source}_path"]).read_text(encoding="utf-8")


def evaluate(
    root: Path, evaluator: dict[str, Any], records: dict[str, dict[str, Any]]
) -> tuple[str, str, str]:
    record = records.get(str(evaluator.get("action_id", "")))
    if evaluator["type"] == "manual" or not record:
        return "UNKNOWN", "未自动判定", "无"
    evidence = record["stdout_path"]
    if evaluator["type"] == "action_status":
        actual = record["status"]
        expected = evaluator.get("expected", "PASS")
        return ("PASS" if actual == expected else "FAIL"), actual, evidence
    source = evaluator.get("source", "stdout")
    raw = action_output(root, record, source)
    evidence = record[f"{source}_path"]
    if evaluator["type"] == "regex":
        matched = bool(re.search(str(evaluator["pattern"]), raw, re.MULTILINE))
        passed = matched != bool(evaluator.get("negate", False))
        return ("PASS" if passed else "FAIL"), f"regex_match={matched}", evidence
    try:
        actual = lookup(json.loads(raw), str(evaluator["path"]))
    except (ValueError, IndexError, KeyError, json.JSONDecodeError) as error:
        return "FAIL", f"evaluator_error={error}", evidence
    expected = evaluator.get("value")
    return ("PASS" if actual == expected else "FAIL"), str(actual), evidence
