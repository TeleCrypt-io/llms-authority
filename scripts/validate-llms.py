#!/usr/bin/env python3
"""Validate the narrow public-content contract for the Pages llms.txt file.

This validator intentionally does not try to judge architecture claims. It catches the conditions
that make a missing, malformed, private, or operational document unsafe to publish. It has no
network or repository-state dependency so it can run both locally and in the release workflow.
"""

from __future__ import annotations

import re
import stat
import sys
from pathlib import Path


MAX_BYTES = 512 * 1024
MAX_LINES = 4096
VERSION = re.compile(r"^# TeleCrypt(?:\s|$)", re.IGNORECASE)

# These patterns identify concrete operational material, not broad vocabulary. Public principles
# may discuss passwords, credentials, webhooks, or payment boundaries without exposing a value or
# endpoint. A future document may also name a component without describing its private mechanics.
FORBIDDEN_PATTERNS = (
    re.compile(r"\b(?:test\.)?(?:checkout|customer)\.dodopayments\.com\b", re.I),
    re.compile(r"\b(?:backend|storage)(?:\.stage)?\.telecrypt\.io\b", re.I),
    re.compile(
        r"\b(?:api[_ -]?key|access[_ -]?token|password|credential)\s*[:=]\s*"
        r"(?:[A-Za-z0-9_-]{24,}|[A-Za-z0-9+/]{24,}={0,2})\b",
        re.I,
    ),
    re.compile(r"\b(?:sk_(?:live|test)_|gh[pousr]_)[A-Za-z0-9_-]{16,}\b", re.I),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b", re.I),
    re.compile(
        r"\b(?:card(?:\s+number)?\s*[:=]\s*\d[\d -]{11,18}|cvv\s*[:=]\s*\d{3,4})\b",
        re.I,
    ),
)


class ValidationError(ValueError):
    """Raised when a candidate public authority is not safe to publish."""


def validate(path: Path) -> None:
    """Validate *path* without following symlinks or consulting external state."""

    try:
        metadata = path.lstat()
    except OSError as error:
        raise ValidationError(f"cannot read {path}: {error}") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ValidationError("llms.txt must be a regular file")
    if metadata.st_size <= 0 or metadata.st_size > MAX_BYTES:
        raise ValidationError("llms.txt size is outside the permitted range")

    try:
        content = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ValidationError(f"llms.txt is not valid UTF-8: {error}") from error
    if content.startswith("\ufeff"):
        raise ValidationError("llms.txt must not start with a UTF-8 BOM")
    if "\x00" in content:
        raise ValidationError("llms.txt contains a NUL byte")
    if not content.endswith("\n"):
        raise ValidationError("llms.txt must end with a newline")
    if any((ord(char) < 0x09 or 0x0B <= ord(char) < 0x20 or ord(char) == 0x7F) for char in content):
        raise ValidationError("llms.txt contains a disallowed control character")

    lines = content.splitlines()
    if len(lines) > MAX_LINES:
        raise ValidationError("llms.txt contains too many lines")
    if not lines or not any(line.strip() for line in lines):
        raise ValidationError("llms.txt must contain public content")
    if not VERSION.match(lines[0]):
        raise ValidationError("llms.txt must begin with a TeleCrypt Markdown heading")
    if any(pattern.search(content) for pattern in FORBIDDEN_PATTERNS):
        raise ValidationError("llms.txt contains private or operational-only material")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} PATH", file=sys.stderr)
        return 2
    try:
        validate(Path(argv[1]))
    except ValidationError as error:
        print(f"invalid llms.txt: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
