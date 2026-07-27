#!/usr/bin/env python3
"""Compatibility stub for the removed V2 command recorder."""

from __future__ import annotations

import argparse
import sys


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Disabled V2 entry point; use run-action.py for V3."
    )
    return result


def main() -> int:
    parser().parse_known_args()
    print(
        "record-command is disabled; use run-action.py for V3. "
        "V2 runs are read-only.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
