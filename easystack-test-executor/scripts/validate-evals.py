#!/usr/bin/env python3
"""Validate model eval definitions and repeated output completeness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def load_object(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_definitions(root: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    model = load_object(root / "evals.json")
    static = load_object(root / "cases.json")
    if model.get("skill_name") != "easystack-test-executor":
        errors.append("evals.json skill_name mismatch")
    evals = model.get("evals")
    if not isinstance(evals, list) or not evals:
        errors.append("evals.json requires non-empty evals")
        evals = []
    ids = [item.get("id") for item in evals if isinstance(item, dict)]
    if len(ids) != len(set(ids)) or not all(isinstance(item, int) for item in ids):
        errors.append("eval IDs must be unique integers")
    for item in evals:
        if not isinstance(item, dict):
            errors.append("every eval must be an object")
            continue
        for field in ("prompt", "expected_output"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"eval {item.get('id')}: {field} is required")
        expectations = item.get("expectations")
        if not isinstance(expectations, list) or not expectations:
            errors.append(f"eval {item.get('id')}: expectations must be non-empty")
    if not isinstance(static, list) or any(
        not isinstance(item.get("must_include"), list) or not item["must_include"]
        for item in static if isinstance(item, dict)
    ):
        errors.append("cases.json must_include definitions are invalid")
    return model, errors


def validate_results(
    model: dict[str, Any], results: Path, repeats: int
) -> tuple[list[dict[str, Any]], list[str]]:
    manifest: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in model["evals"]:
        for run in range(1, repeats + 1):
            path = results / f"eval-{item['id']}" / f"run-{run}.md"
            if not path.is_file() or not path.read_text(encoding="utf-8").strip():
                errors.append(f"missing model output: {path}")
                continue
            payload = path.read_bytes()
            manifest.append(
                {
                    "eval_id": item["id"],
                    "run": run,
                    "path": str(path),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
    return manifest, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-root", type=Path, default=Path(__file__).parents[1] / "evals")
    parser.add_argument("--results", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    try:
        model, errors = validate_definitions(args.eval_root)
        manifest: list[dict[str, Any]] = []
        if args.results:
            manifest, result_errors = validate_results(model, args.results, args.repeats)
            errors.extend(result_errors)
        print(json.dumps({"valid": not errors, "runs": manifest}, ensure_ascii=False))
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1 if errors else 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"validate-evals error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
