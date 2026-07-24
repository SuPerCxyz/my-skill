#!/usr/bin/env python3
"""Runtime profile validation shared by profile and contract tools."""

from __future__ import annotations

import hashlib
import json
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from _contract import load_structured
from _validation import valid_local_time


PROFILE_ROOT = Path("/tmp/easystack-test-executor-profiles")
SECRET_KEYS = {"password", "token", "secret", "application_credential_secret"}


def nested(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for component in path.split("."):
        if not isinstance(current, dict) or component not in current:
            raise ValueError(f"missing profile field: {path}")
        current = current[component]
    return current


def find_secrets(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in SECRET_KEYS and item not in {"", "<REDACTED>", None}:
                findings.append(path)
            findings.extend(find_secrets(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(find_secrets(item, f"{prefix}[{index}]"))
    return findings


def profile_key(profile: dict[str, Any]) -> str:
    identity = {
        "target": nested(profile, "environment.target"),
        "region": nested(profile, "environment.region"),
        "project_id": nested(profile, "authentication.project_id"),
        "namespace": nested(profile, "kubernetes.namespace"),
        "cluster_uid": nested(profile, "fingerprint.cluster_uid"),
    }
    encoded = json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()
    return "env-" + hashlib.sha256(encoded).hexdigest()[:16]


def validate_permissions(path: Path) -> list[str]:
    errors: list[str] = []
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        errors.append("profile permissions must be 0600 or stricter")
    if stat.S_IMODE(path.parent.stat().st_mode) & 0o077:
        errors.append("profile directory permissions must be 0700 or stricter")
    return errors


def validate_profile(
    path: Path, max_age_days: int, enforce_runtime: bool = True
) -> tuple[dict[str, Any], list[str], list[str]]:
    profile = load_structured(path)
    errors: list[str] = []
    warnings: list[str] = []
    required = (
        "profile_version", "captured_at_local", "last_verified_at_local",
        "environment.target", "environment.region", "environment.timezone",
        "authentication.project_id", "authentication.execution_location",
        "kubernetes.namespace", "nova.images", "nova.flavors", "nova.networks",
        "cinder.volume_types", "cinder.backends", "fingerprint.cluster_uid",
        "fingerprint.openstack_release", "fingerprint.openstackclient_version",
        "fingerprint.backend_fingerprint",
    )
    for field in required:
        try:
            value = nested(profile, field)
            if value is None or value == "":
                errors.append(f"empty profile field: {field}")
        except (ValueError, TypeError):
            errors.append(f"missing profile field: {field}")
    if profile.get("profile_version") != 2:
        errors.append("profile_version must be 2")
    for field in ("captured_at_local", "last_verified_at_local"):
        if not valid_local_time(profile.get(field)):
            errors.append(f"{field} must be offset-aware RFC3339")
    verified = profile.get("last_verified_at_local")
    if valid_local_time(verified):
        instant = datetime.fromisoformat(str(verified)).astimezone(timezone.utc)
        if datetime.now(timezone.utc) - instant > timedelta(days=max_age_days):
            warnings.append(f"profile is older than {max_age_days} days")
    secrets = find_secrets(profile)
    if secrets:
        errors.append(f"plaintext secrets found at: {','.join(secrets)}")
    if enforce_runtime:
        try:
            path.resolve().relative_to(PROFILE_ROOT)
        except ValueError:
            errors.append(f"profile must be stored under {PROFILE_ROOT}")
        if path.exists():
            errors.extend(validate_permissions(path))
    return profile, errors, warnings
