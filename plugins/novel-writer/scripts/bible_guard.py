#!/usr/bin/env python3
"""
Bible Guard — PreToolUse 훅.

PRD v1.4 §2.3. bible/ 가 LOCKED 상태일 때 다음 도구 호출을 차단한다:
- Write / Edit / MultiEdit / NotebookEdit (직접 파일 쓰기)
- Bash (echo > / sed -i / cat > / tee 등 우회 시도)

DRAFTING 이거나 UNLOCKED 상태면 통과.

표준 입력으로 Claude Code 훅 이벤트 JSON 을 받고, 차단 시 exit code 2 + stderr,
허용 시 exit 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
BIBLE = PROJECT / "bible"
LOCK_FILE = BIBLE / "LOCK_STATUS.md"

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Bash 명령에서 'bible/' 경로에 쓰기를 시도하는 패턴.
# 대상이 bible/ 안의 파일일 때만 차단.
BASH_WRITE_PATTERNS = [
    re.compile(r">\s*[\"']?(?P<path>[^\s>&|;\"']+)"),                   # echo ... > file
    re.compile(r">>\s*[\"']?(?P<path>[^\s>&|;\"']+)"),                  # echo ... >> file
    re.compile(r"\btee\b\s+(?:-\w+\s+)*[\"']?(?P<path>[^\s>&|;\"']+)"),   # tee file / tee -a file
    re.compile(r"\bcp\b\s+\S+\s+[\"']?(?P<path>[^\s>&|;\"']+)"),         # cp src dst
    re.compile(r"\bmv\b\s+\S+\s+[\"']?(?P<path>[^\s>&|;\"']+)"),         # mv src dst
    re.compile(r"\bsed\b\s+(?:-\w+\s+)*-i(?:\s+''|\.\w+)?\s+(?:-\w+\s+)*[\"']?(?P<path>[^\s>&|;\"']+)"),  # sed -i file
    re.compile(r"\b(?:rm|unlink)\b\s+(?:-\w+\s+)*[\"']?(?P<path>[^\s>&|;\"']+)"),                       # rm file
    re.compile(r"\btruncate\b\s+(?:-\w+\s+)*[\"']?(?P<path>[^\s>&|;\"']+)"),
]


def read_lock_status() -> str:
    if not LOCK_FILE.exists():
        return "DRAFTING"
    for line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("**상태:**"):
            return line.split("**상태:**", 1)[1].strip()
    return "DRAFTING"


def path_in_bible(raw: str | None) -> bool:
    if not raw:
        return False
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = PROJECT / candidate
    try:
        p = candidate.resolve()
    except (OSError, ValueError):
        return False
    try:
        p.relative_to(BIBLE)
        return True
    except ValueError:
        return False


def is_lock_file(raw: str | None) -> bool:
    if not raw:
        return False
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = PROJECT / candidate
    try:
        return candidate.resolve() == LOCK_FILE.resolve()
    except (OSError, ValueError):
        return False


def bash_targets_bible(command: str) -> list[str]:
    """Bash 명령 문자열에서 bible/ 안을 가리키는 쓰기 대상을 추출."""
    targets: list[str] = []
    for pat in BASH_WRITE_PATTERNS:
        for m in pat.finditer(command):
            target = m.group("path")
            # bible/ 키워드가 명령 어디에든 등장하지 않으면 빠른 패스
            if "bible" not in command:
                continue
            if path_in_bible(target) and not is_lock_file(target):
                targets.append(target)
    return targets


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # 훅 입력이 비어도 통과 (로컬 수동 실행 대비)

    tool = event.get("tool_name") or event.get("tool") or ""
    tool_input = event.get("tool_input") or {}
    status = read_lock_status()

    if status != "LOCKED":
        return 0

    if tool in WRITE_TOOLS:
        target = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("notebook_path")
        if not path_in_bible(target):
            return 0
        if is_lock_file(target):
            return 0
        sys.stderr.write(
            f"[bible-guard] bible/ 는 LOCKED 상태입니다. {target} 쓰기 차단 ({tool}). "
            f"`/bible-unlock <사유>` 로 해제 후 시도하십시오.\n"
        )
        return 2

    if tool == "Bash":
        command = tool_input.get("command") or ""
        targets = bash_targets_bible(command)
        if targets:
            sys.stderr.write(
                f"[bible-guard] bible/ 는 LOCKED 상태입니다. Bash 명령이 다음 파일을 쓰려 합니다: {targets}. "
                f"`/bible-unlock <사유>` 로 해제 후 시도하십시오.\n"
            )
            return 2
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
