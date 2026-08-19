#!/usr/bin/env python3
"""Structural validator for a feature-parity Markdown matrix.

Exit codes:
  0: pass
  1: matrix consistency errors
  2: matrix file unavailable
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_STATUS = {
    "Missing", "Partial", "Implemented", "Blocked",
    "Out-of-scope", "Intentional divergence",
}
VALID_VERIFY = {"Pass", "Fail", "Blocked", "Not run", "Not applicable"}
OUT_SCOPE = {"out", "no", "excluded"}


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "PARITY_MATRIX.md")
    if not path.is_file():
        print(f"ERROR: matrix not found: {path}")
        return 2

    rows: list[tuple[int, list[str]]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.lstrip().startswith("|") or re.match(r"^\s*\|?\s*-+", line):
            continue
        row = cells(line)
        if row and row[0] == "ID":
            continue
        if row and re.fullmatch(r"F-[A-Za-z0-9._-]+", row[0]):
            rows.append((lineno, row))

    errors: list[str] = []
    seen: set[str] = set()
    for lineno, row in rows:
        if len(row) < 8:
            errors.append(f"L{lineno}: expected >=8 columns, got {len(row)}")
            continue

        fid, _, scope, ref_ev, tgt_ev, status, verify, notes = row[:8]
        if fid in seen:
            errors.append(f"L{lineno}: duplicate ID {fid}")
        seen.add(fid)

        if status not in VALID_STATUS:
            errors.append(f"L{lineno} {fid}: invalid status {status!r}")
        if verify not in VALID_VERIFY:
            errors.append(f"L{lineno} {fid}: invalid verification {verify!r}")

        in_scope = scope.lower() not in OUT_SCOPE
        if in_scope and not ref_ev.strip("` "):
            errors.append(f"L{lineno} {fid}: missing reference evidence")
        if status == "Implemented" and tgt_ev.strip("` ") in {"", "-"}:
            errors.append(f"L{lineno} {fid}: Implemented without target evidence")
        if status in {"Partial", "Blocked", "Out-of-scope", "Intentional divergence"} and not notes.strip():
            errors.append(f"L{lineno} {fid}: {status} requires explanatory notes")
        if status == "Blocked" and verify == "Pass":
            errors.append(f"L{lineno} {fid}: Blocked cannot have verification Pass")
        if status in {"Missing", "Partial"} and verify == "Pass":
            errors.append(f"L{lineno} {fid}: {status} cannot have verification Pass")
        if status == "Implemented" and verify == "Not applicable" and in_scope:
            errors.append(f"L{lineno} {fid}: in-scope Implemented must not use Not applicable verification")

    print(f"Rows: {len(rows)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Parity matrix structural audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
