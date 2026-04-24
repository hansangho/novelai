---
description: 진행 중인 챕터를 이어서 쓴다. state/current/ 와 .session/current.yaml 기준.
allowed-tools: Read, Write, Edit, Bash, Task, Glob
---

# /continue-writing

## 실행 절차

1. `.session/current.yaml` 읽기 — `active_chapter`, `gate_cursor`, `rewrite_iteration` 확인.
2. `active_chapter` 가 null 이면: `state/current/` 심볼릭 링크 대상에서 다음 챕터 번호 유추.
3. 상황별 분기:
   - **draft 가 .work/ 에 없음** → `/write-chapter {next}` 와 동일 흐름
   - **draft 있지만 Gate 진행 중** → `gate_cursor` 부터 Gate 파이프라인 재개
   - **Gate 통과했지만 finalize 안 됨** → 작가 확인 후 finalize
   - **finalize 완료, state 갱신 안 됨** → `state-updater` 호출
4. 각 단계에서 "어디부터 이어서 하는지" 한 문장 보고.

## 의도
중단된 집필 세션을 안전하게 재개. `/resume` 과는 다르게 **즉시 작업 재개** 에 초점.
