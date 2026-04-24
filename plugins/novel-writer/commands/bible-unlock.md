---
description: bible/ 를 일시적으로 편집 가능 상태로 전환. 사유 기록 자동.
argument-hint: "<reason>"
allowed-tools: Read, Write, Bash, Task
---

# /bible-unlock

입력: `$ARGUMENTS` — 사유 (필수)

## 실행
1. 사유가 비면 거부: "사유는 필수입니다. `/bible-unlock \"캐릭터 이름 충돌 해소\"` 형식."
2. `bash ${CLAUDE_PLUGIN_ROOT}/scripts/bible_lock.sh unlock "$ARGUMENTS"` 실행.
3. 스크립트가 `_changelog.md` 에 placeholder 엔트리를 append 하므로, 작가에게 "어떤 파일의 어떤 필드를 수정할 예정이신가요?" 질문.
4. `continuity-reviewer` 서브에이전트를 Task 로 호출 — **영향 분석** 수행 (PRD §10.2):
   - 수정 예정 필드를 이미 언급한 챕터·라인 나열
   - timeline/history.md 내 관련 엔트리
   - 선택지 A/B/C 제시
5. 작가가 수정 완료 후에는 `/bible-lock` 재실행을 권고.

## 주의
- Unlock 상태는 위험하다. 훅이 `bible/` 쓰기를 허용하므로 실수로 다른 에이전트가 Bible 에 쓸 수 있다.
- 가능한 한 짧게 — 수정 후 즉시 lock.
