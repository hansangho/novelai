---
description: 지정 챕터의 모든 Gate 를 재실행하고 실패 시 최대 3회까지 재작성 루프. /revise-loop 5
argument-hint: "<chapter-number>"
allowed-tools: Read, Write, Bash, Task, Glob
---

# /revise-loop

입력: `$ARGUMENTS` — 챕터 번호

## 실행 (PRD §3.4)
1. 현재 드래프트 iter 확인. 없으면 "`.work/writer-draft-ch{NN}-v1.md` 가 필요합니다" 안내 후 종료.
2. 반복 (최대 3회 or PASS 까지):
   - G1~G4 를 Batch Feedback 모드로 병렬 호출 (결과 `.work/reviews/*.md`).
   - G5 `writing-director` 가 전 리뷰를 종합 → `.work/reviews/chNN-iterX/integration.md`.
   - 모든 핵심 Gate(G1~G3, G5) PASS → 루프 탈출 (G4 는 선택적, WARN 허용).
   - 하나라도 FAIL → `chapter-writer` 를 Task 로 호출해 v{iter+1} 생성.
3. 3회 초과 FAIL → **작가 에스컬레이션**:
   - `.work/gate-decisions.md` 에 전체 이력 블록 append
   - 세 가지 선택지 출력:
     - **A. Gate 완화** — `/override-gate <GID> <사유>`
     - **B. Bible 수정** — `/bible-unlock <사유>` 후 근본 원인 수정
     - **C. 작가 직접 작성** — 작가가 손으로 드래프트, 이후 Gate 재검증만
4. PASS 로 종료 시: 작가 확인 → `gate_runner.py finalize` → `state-updater` 호출.

## 주의
- 같은 피드백이 v1→v2→v3 에서 반복되면 Writer 가 같은 문제를 반복하는 것 — G5 Integration 이 피드백 우선순위 조정 필요.
