#!/usr/bin/env python3
"""
State Snapshot Helper.

State Updater 서브에이전트가 챕터 확정 직후 호출한다:
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state_snapshot.py create --chapter 5

수행:
1. state/template/ → state/chapter-05/ 복사 (이미 있으면 실패)
2. state/current → chapter-05 심볼릭 링크 갱신
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STATE = PROJECT / "state"
TEMPLATE = STATE / "template"


def cmd_create(ch: int) -> int:
    target = STATE / f"chapter-{ch:02d}"
    if target.exists():
        print(f"[state-snapshot] {target} 이미 존재합니다.", file=sys.stderr)
        return 1
    shutil.copytree(TEMPLATE, target)
    current = STATE / "current"
    if current.is_symlink() or current.exists():
        current.unlink()
    current.symlink_to(target.name)
    print(f"[state-snapshot] 생성: {target}")
    print(f"[state-snapshot] current → {target.name}")
    print("[state-snapshot] YAML 값은 State Updater 에이전트가 채웁니다.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create")
    c.add_argument("--chapter", type=int, required=True)
    args = ap.parse_args()
    if args.cmd == "create":
        return cmd_create(args.chapter)
    return 0


if __name__ == "__main__":
    sys.exit(main())
