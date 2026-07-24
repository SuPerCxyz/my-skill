#!/usr/bin/env python3
"""Validate a runtime environment profile and print its stable cache key."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _profile import profile_key, validate_profile


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--profile", required=True, type=Path)
    result.add_argument("--max-age-days", type=int, default=30)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        profile, errors, warnings = validate_profile(args.profile, args.max_age_days)
        print(f"profile_key={profile_key(profile)}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1 if errors else 0
    except (OSError, ValueError) as error:
        print(f"validate-profile error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
