#!/usr/bin/env python3
"""Shared definitions for test-run validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any


H3 = ("执行结果", "测试目标", "测试步骤", "结果检查", "创建的资源", "关键日志输出")
REQUIRED_RESULT_FIELDS = (
    "case_id",
    "title",
    "objective",
    "functional_status",
    "timing_status",
    "evidence_status",
    "cleanup_status",
    "diagnostic_status",
    "log_requirement",
)


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def valid_local_time(value: Any) -> bool:
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return False
    return parsed.utcoffset() is not None
