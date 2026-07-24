#!/usr/bin/env python3
"""Timeout-aware argv runner with redacted immutable output files."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import threading
from pathlib import Path
from typing import TextIO

from _harness import redact


REQUEST_ID = re.compile(r"\breq-[0-9a-f-]{16,}\b", re.IGNORECASE)
PREVIEW_LIMIT = 64 * 1024


def _pump(
    source: TextIO,
    destination: TextIO,
    preview: list[str],
    size: list[int],
    request_ids: set[str],
) -> None:
    for raw_line in source:
        line = redact(raw_line)
        destination.write(line)
        destination.flush()
        request_ids.update(REQUEST_ID.findall(line))
        remaining = PREVIEW_LIMIT - size[0]
        if remaining > 0:
            preview.append(line[:remaining])
            size[0] += min(len(line), remaining)


def _terminate(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    except ProcessLookupError:
        pass


def execute(
    command: list[str],
    cwd: Path | None,
    timeout: int,
    stdout_path: Path,
    stderr_path: Path,
) -> tuple[int, bool, str, str, set[str]]:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    request_ids: set[str] = set()
    previews = ([], [])
    sizes = ([0], [0])
    with stdout_path.open("x", encoding="utf-8") as stdout_file, stderr_path.open(
        "x", encoding="utf-8"
    ) as stderr_file:
        os.chmod(stdout_path, 0o600)
        os.chmod(stderr_path, 0o600)
        try:
            process = subprocess.Popen(
                command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, bufsize=1, start_new_session=True,
            )
        except OSError as error:
            stderr_file.write(redact(str(error)) + "\n")
            return 127, False, "", redact(str(error)), request_ids
        threads = [
            threading.Thread(
                target=_pump,
                args=(stream, destination, preview, size, request_ids),
            )
            for stream, destination, preview, size in (
                (process.stdout, stdout_file, previews[0], sizes[0]),
                (process.stderr, stderr_file, previews[1], sizes[1]),
            )
        ]
        for thread in threads:
            thread.start()
        timed_out = False
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate(process)
            return_code = 124
        for thread in threads:
            thread.join()
    return return_code, timed_out, "".join(previews[0]), "".join(previews[1]), request_ids
