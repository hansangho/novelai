---
description: 특정 Gate 만 수동 실행. /run-gate G3 5
argument-hint: "<G1|G2|G3|G4|G5> <chapter-number>"
allowed-tools: Read, Write, Bash, Task, Glob
---

# /run-gate

입력: `$ARGUMENTS` — 두 토큰 (예: `G3 5`).

## 실행
1. 첫 토큰을 Gate id 로, 두 번째를 챕터 번호로 파싱. 형식 오류면 usage 출력.
2. 해당 Gate 의 담당 서브에이전트를 Task 로 호출:
   - G1 → `style-linter`
   - G2 → `character-consistency-guardian`
   - G3 → `continuity-reviewer`
   - G4 → `perplexity-analyzer`
   - G5 → `writing-director`
3. 리뷰 리포트(`.work/reviews/<name>.md`) 생성 후 `gate_runner.py record` 로 결과 기록.
4. 결과 요약 출력.

## 용도
- 특정 Gate 만 다시 돌려 개선 확인
- 디버깅 / 임계값 튜닝
