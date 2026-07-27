#!/usr/bin/env python3
"""Reject operation examples that report success before a terminal state."""

from __future__ import annotations

import re
import sys
from pathlib import Path


INTERMEDIATE = {
    "confirm_needed",
    "dialog_opened",
    "menu_opened",
    "selected",
    "submitted_or_confirm_needed",
    "wizard_progressing",
}
TERMINAL_RESULT = re.compile(
    r'\bok\s*:\s*(?:true|false)\b|"ok"\s*:\s*(?:true|false)'
)


def result_block(lines: list[str], start: int) -> str:
    """Return the local object containing an ok=true example."""
    output: list[str] = []
    for line in lines[start : start + 30]:
        output.append(line)
        if "}" in line:
            break
    return "\n".join(output)


def findings(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            structured = "{" in line or line.lstrip().startswith(('"ok"', "ok:"))
            if not structured or not TERMINAL_RESULT.search(line):
                continue
            number = index + 1
            block = result_block(lines, index)
            if re.search(r'\bok\s*:\s*true\b|"ok"\s*:\s*true', line) and any(
                status in block for status in INTERMEDIATE
            ):
                errors.append(
                    f"{path.relative_to(root)}:{number}: intermediate state uses ok=true"
                )
            if not re.search(r'\bterminal\s*:\s*true\b|"terminal"\s*:\s*true', block):
                errors.append(
                    f"{path.relative_to(root)}:{number}: terminal result marker missing"
                )
            if not re.search(r'\bsubmitted\s*:\s*(?:true|false)\b|'
                             r'"submitted"\s*:\s*(?:true|false)', block):
                errors.append(
                    f"{path.relative_to(root)}:{number}: submitted marker missing"
                )
    template = root / "patterns" / "operation-template.md"
    text = template.read_text(encoding="utf-8")
    if "`ok` 只表示 terminal" not in text or '"terminal": true' not in text:
        errors.append("operation-template.md: terminal result contract missing")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = findings(root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: operation examples preserve terminal result semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
