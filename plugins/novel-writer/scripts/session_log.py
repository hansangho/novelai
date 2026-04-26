#!/usr/bin/env python3
"""
Session Log — PostToolUse 훅.

Claude Code 가 호출한 각 도구 이벤트를 .session/logs/YYYY-MM-DD.jsonl 에 append.
Session Manager 와 /resume 커맨드가 이 로그를 활용.

민감 정보 마스킹:
- API key 패턴 (sk-..., ghp_..., aws_..., 일반 hex 토큰 등)
- 비밀번호·토큰 환경변수 값
- 마스킹된 위치는 [REDACTED:타입] 으로 치환
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
LOG_DIR = PROJECT / ".session" / "logs"

# 민감 패턴들. 매치하면 [REDACTED:타입] 으로 치환.
SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("anthropic-key", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}")),
    ("openai-key",    re.compile(r"sk-(?!ant)[a-zA-Z0-9]{20,}")),
    ("github-pat",    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("github-fine-grained", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws-secret",     re.compile(r"aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{20,}", re.I)),
    ("slack-token",    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("ssh-private",    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----")),
    ("password-arg",   re.compile(r"(--?password[= ]|-p\s+|PASSWORD=|TOKEN=|SECRET=)\S+", re.I)),
    ("authorization",  re.compile(r"(Authorization:\s*Bearer\s+)\S+", re.I)),
    ("env-var-secret", re.compile(r"\b(?:API_KEY|SECRET_KEY|ACCESS_TOKEN|REFRESH_TOKEN)\s*=\s*[\"']?[A-Za-z0-9_\-]{12,}", re.I)),
]


def mask(text: str) -> str:
    """문자열 안의 민감 패턴을 [REDACTED:타입] 으로 치환."""
    if not text:
        return text
    for kind, pat in SECRET_PATTERNS:
        text = pat.sub(f"[REDACTED:{kind}]", text)
    return text


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
        # 명령 미리보기 + 민감 정보 마스킹
        record["command_preview"] = mask(str(tool_input["command"])[:200])

    # 추가 안전장치 — 직렬화 직후 한 번 더 마스킹 (혹시 다른 필드에 들어가 있을 경우)
    line = json.dumps(record, ensure_ascii=False)
    line = mask(line)

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
