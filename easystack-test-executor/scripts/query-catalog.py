#!/usr/bin/env python3
"""Read only the requested OpenStack operation from compact catalogs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CATALOGS = {
    "compute": "compute.json",
    "storage": "storage.json",
    "network-image-security": "network-image-security.json",
    "baremetal": "baremetal.json",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, choices=sorted(CATALOGS))
    parser.add_argument("--operation")
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / "catalogs" / CATALOGS[args.domain]
    data = json.loads(path.read_text(encoding="utf-8"))
    if not args.operation:
        print(json.dumps(sorted(data["operations"]), ensure_ascii=False))
        return 0
    operation = data["operations"].get(args.operation)
    if not operation:
        print(f"query-catalog error: unknown operation {args.operation}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {"domain": args.domain, "operation": args.operation, **operation},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
