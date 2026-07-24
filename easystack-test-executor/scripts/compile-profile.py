#!/usr/bin/env python3
"""Validate a captured profile and store it under its stable environment key."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from _harness import atomic_text
from _profile import PROFILE_ROOT, profile_key, validate_profile


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--input", required=True, type=Path)
    return result


def compile_profile(source: Path) -> Path:
    profile, errors, _ = validate_profile(
        source.resolve(), max_age_days=36500, enforce_runtime=False
    )
    if errors:
        raise ValueError("; ".join(errors))
    try:
        import yaml
    except ImportError as error:
        raise ValueError("PyYAML is required to write the runtime profile") from error
    PROFILE_ROOT.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(PROFILE_ROOT, 0o700)
    destination = PROFILE_ROOT / f"{profile_key(profile)}.yaml"
    content = yaml.safe_dump(
        profile,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    atomic_text(destination, content)
    os.chmod(destination, 0o600)
    _, runtime_errors, _ = validate_profile(destination, max_age_days=30)
    if runtime_errors:
        raise ValueError("; ".join(runtime_errors))
    return destination


def main() -> int:
    args = parser().parse_args()
    try:
        print(compile_profile(args.input))
    except (OSError, ValueError) as error:
        print(f"compile-profile error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
