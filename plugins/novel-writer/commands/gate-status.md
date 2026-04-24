---
description: 특정 챕터의 Gate 통과 상태 조회. /gate-status 5
argument-hint: "<chapter-number>"
allowed-tools: Read, Bash
---

# /gate-status

입력: `$ARGUMENTS` (챕터 번호)

## 실행
1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py status --chapter $ARGUMENTS` 실행.
2. 스크립트 출력에 덧붙여 `.work/reviews/*.md` 존재 여부 요약 (Read + Glob).
3. 다음 해야 할 일 1문장 권고 (스크립트 출력 하단 "다음:" 라인을 그대로 활용).
