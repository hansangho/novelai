#!/usr/bin/env bash
# bible_lock.sh — bible/LOCK_STATUS.md 의 상태 플래그를 갱신한다.
#
# 사용법:
#   bible_lock.sh lock   "사유"
#   bible_lock.sh unlock "사유"
#   bible_lock.sh status

set -euo pipefail

# 작가 프로젝트 루트. Claude Code 가 $CLAUDE_PROJECT_DIR 를 주입.
# 수동 실행 시 cwd 로 fallback.
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
LOCK_FILE="${PROJECT_ROOT}/bible/LOCK_STATUS.md"

action="${1:-status}"
reason="${2:-}"

case "${action}" in
  status)
    grep -E '^\*\*상태:\*\*' "${LOCK_FILE}" || echo "**상태:** DRAFTING"
    ;;

  lock)
    python3 - "$LOCK_FILE" "LOCKED" "$reason" <<'PY'
import sys, datetime, pathlib
path, state, reason = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(path)
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
stamped = False
for line in lines:
    if line.startswith("**상태:**"):
        out.append(f"**상태:** {state}")
    elif line.startswith("마지막 변경:"):
        ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        out.append(f"마지막 변경: {ts} — {state} ({reason or '(사유 없음)'})")
        stamped = True
    else:
        out.append(line)
if not stamped:
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    out.append(f"마지막 변경: {ts} — {state} ({reason or '(사유 없음)'})")
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"bible/ -> {state}")
PY
    ;;

  unlock)
    python3 - "$LOCK_FILE" "UNLOCKED" "$reason" <<'PY'
import sys, datetime, pathlib
path, state, reason = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(path)
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
stamped = False
for line in lines:
    if line.startswith("**상태:**"):
        out.append(f"**상태:** {state}")
    elif line.startswith("마지막 변경:"):
        ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        out.append(f"마지막 변경: {ts} — {state} ({reason or '(사유 없음)'})")
        stamped = True
    else:
        out.append(line)
if not stamped:
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    out.append(f"마지막 변경: {ts} — {state} ({reason or '(사유 없음)'})")
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"bible/ -> {state}")
PY
    if [ -z "${reason}" ]; then
      echo "경고: /bible-unlock 은 사유를 기록해야 합니다. _changelog.md 에 직접 입력하거나 커맨드 인자로 전달하세요." >&2
    else
      # _changelog.md 에 플레이스홀더 엔트리 추가
      ts="$(date +%Y-%m-%d)"
      changelog="${PROJECT_ROOT}/bible/_changelog.md"
      {
        echo
        echo "## ${ts}"
        echo "### unlock 사유: ${reason}"
        echo "- 변경된 파일: (수정 후 채워 넣을 것)"
        echo "- 필드:"
        echo "- 이전:"
        echo "- 변경:"
        echo "- 작업자:"
        echo "- 영향 챕터:"
        echo "- 재검증:"
      } >> "${changelog}"
    fi
    ;;

  *)
    echo "usage: $0 {lock|unlock|status} [reason]" >&2
    exit 64
    ;;
esac
