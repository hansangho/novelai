#!/usr/bin/env python3
"""
Bible Guard — PreToolUse 훅.

PRD v1.4 §2.3. bible/ 가 LOCKED 상태일 때 Write/Edit 계열 도구 호출을 차단한다.
DRAFTING 이거나 UNLOCKED 상태면 통과시킨다.

표준 입력으로 Claude Code 훅 이벤트 JSON 을 받고, 차단해야 하면
exit code 2 + stderr 메시지, 허용하면 exit 0 을 반환한다.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# 작가 프로젝트 루트. hooks 는 Claude Code 가 $CLAUDE_PROJECT_DIR 를 주입.
# 수동 실행·테스트 시 cwd 로 fallback.
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
BIBLE = PROJECT / "bible"
LOCK_FILE = BIBLE / "LOCK_STATUS.md"

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


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
    try:
        p = Path(raw).resolve()
    except (OSError, ValueError):
        return False
    try:
        p.relative_to(BIBLE)
        return True
    except ValueError:
        return False


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # 훅 입력이 비어도 통과 (로컬 수동 실행 대비)

    tool = event.get("tool_name") or event.get("tool") or ""
    if tool not in WRITE_TOOLS:
        return 0

    tool_input = event.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("notebook_path")
    if not path_in_bible(target):
        return 0

    # LOCK_STATUS.md 자체 수정은 lock/unlock 커맨드만 허용하므로 여기서는 막지 않음
    if target and Path(target).resolve() == LOCK_FILE.resolve():
        return 0

    status = read_lock_status()
    if status != "LOCKED":
        return 0

    sys.stderr.write(
        f"[bible-guard] bible/ 는 LOCKED 상태입니다. {target} 쓰기 차단. "
        f"`/bible-unlock <사유>` 로 해제 후 시도하십시오.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
