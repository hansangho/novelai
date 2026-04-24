---
description: Gate 를 통과한 .work/ 드래프트를 story/chapters/ 로 확정 이동하고 State / Timeline 을 갱신한다.
argument-hint: "<chapter-number>"
allowed-tools: Read, Write, Bash, Task, Glob
---

# /finalize

입력: `$ARGUMENTS` — 챕터 번호

## 실행
1. `.work/gate-decisions.md` 에서 해당 챕터 최신 iter 의 모든 Gate 가 PASS(or WARN 수용)인지 확인.
2. 하나라도 FAIL 이면 거부: "/revise-loop 를 먼저 완료하세요".
3. 작가 확인 대화:
   - 최신 드래프트 첫 500자 미리보기
   - 변경될 파일 목록 (story/chapters/chapter-NN.md, state/chapter-NN/, timeline/history.md)
4. 승인 시:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py finalize --chapter $ARGUMENTS`
   - `state-updater` 서브에이전트 Task 로 호출 → YAML + timeline append
5. `.session/current.yaml` 의 `active_chapter` 를 다음으로, `gate_cursor`/`rewrite_iteration` 초기화.
6. 완료 보고 — 다음 챕터 아웃라인 미리보기 (`story/plan.md`).
