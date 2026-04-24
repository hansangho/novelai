#!/usr/bin/env python3
"""
Session Log — PostToolUse 훅.

Claude Code 가 호출한 각 도구 이벤트를 .session/logs/YYYY-MM-DD.jsonl 에 1 줄씩 append 한다.
Session Manager 와 /resume 커맨드가 이 로그를 활용한다.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
LOG_DIR = PROJECT / ".session" / "logs"


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    log_path = LOG_DIR / f"{today}.jsonl"

    record = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "tool": event.get("tool_name") or event.get("tool"),
        "subagent": event.get("agent") or event.get("subagent_type"),
        "hook": event.get("hook_event_name"),
    }
    tool_input = event.get("tool_input") or {}
    if "file_path" in tool_input:
        record["path"] = tool_input["file_path"]
    if "command" in tool_input:
        record["command_preview"] = str(tool_input["command"])[:120]

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
