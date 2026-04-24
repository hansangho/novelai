---
description: bible/ 를 LOCKED 상태로 설정. 집필 단계 진입 시 호출.
allowed-tools: Read, Write, Bash
---

# /bible-lock

## 실행
1. 현재 상태 확인: `bash ${CLAUDE_PLUGIN_ROOT}/scripts/bible_lock.sh status`.
2. 이미 LOCKED 면 "이미 잠겨 있습니다" 출력 후 종료.
3. 아닌 경우:
   - Bible 완성도 경고 체크 — 다음 파일이 비어 있거나 기본 템플릿과 동일하면 경고:
     - `bible/style.md`
     - `bible/structure.md`
     - `bible/universe/_overview.md`, `rules.md`
     - `bible/characters/_index.md` 에 최소 1개 인물 등록
   - 경고가 있으면 작가에게 "정말 lock 할까요?" 확인.
4. `bash ${CLAUDE_PLUGIN_ROOT}/scripts/bible_lock.sh lock "집필 단계 진입"` 실행.
5. `.session/current.yaml` 의 `phase` 를 `drafting` 으로 변경.
6. 결과 출력: "bible/ → LOCKED. 이후 Write/Edit 훅이 차단합니다. `/bible-unlock <사유>` 로 해제."

## 원칙
- Lock 은 가벼운 상태 변경이 아니다. 집필 내내 참조 기반이 바뀌지 않도록 보장하는 장치.
