---
description: 지정한 챕터의 초고를 작성하고 Gate G1~G5 파이프라인을 자동 실행한다. 사용: /write-chapter 5
argument-hint: "<chapter-number>"
allowed-tools: Read, Write, Edit, Bash, Task, TodoWrite, Glob, Grep
---

# /write-chapter

입력: `$ARGUMENTS` (챕터 번호, 예: `5`)

## 실행 절차

당신은 **Writing Director** 역할이다. 다음을 순서대로 수행한다:

1. `story/plan.md` 에서 챕터 $ARGUMENTS 의 아웃라인 추출.
2. `bible/LOCK_STATUS.md` 확인 — `DRAFTING` 이면 "집필 단계가 아닙니다. `/bible-lock` 으로 Lock 후 진행하세요." 경고만 출력하고 종료.
3. `.work/scenes-ch{$ARGUMENTS:02d}.md` 존재 여부 확인. 없으면 `scene-planner` 서브에이전트를 Task 로 호출해 생성.
4. `chapter-writer` 서브에이전트를 Task 로 호출:
   - 입력 요약: bible/, state/current/*.yaml, timeline/history.md (해당 챕터 범위), plan.md#ch$ARGUMENTS, .work/scenes-ch*.md
   - 출력: `.work/writer-draft-ch{NN}-v1.md`
5. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py run --chapter $ARGUMENTS` 실행.
6. Gate 파이프라인 수행 — **Batch Feedback 모드** (기본):
   - G1~G4 를 한 iter 에 모두 실행해 전체 피드백을 수집한 뒤, G5 Integration 이 종합해 Writer 에게 한 번에 돌려준다.
   - PRD §3.3 의 strict fail-fast 와의 차이: 재작성 전에 모든 관점의 피드백이 쌓여 1회 재작성 안에서 더 많은 이슈를 동시 해결 (파일럿 결과로 채택).
   - 병렬 호출 가능 — G1~G4 는 서로 독립. Task 도구를 한 턴에 4개 발행해도 안전.
   - G1 `style-linter` → `.work/reviews/chNN-iterX/style-lint.md`
   - G2 `character-consistency-guardian` → `.work/reviews/chNN-iterX/character-review.md`
   - G3 `continuity-reviewer` → `.work/reviews/chNN-iterX/continuity-review.md`
   - G4 `perplexity-analyzer` → `.work/reviews/chNN-iterX/perplexity-report.md` (선택적 통과)
   - G5 `writing-director` (본인이 Integration) → `.work/reviews/chNN-iterX/integration.md`
   - 각 Gate 결과는 `gate_runner.py record` 로 기록
7. 모든 Gate PASS 시 작가에게 확인 요청 → 승인 후 `gate_runner.py finalize --chapter $ARGUMENTS` 실행.
8. `state-updater` 서브에이전트 호출 → state/chapter-NN/ + timeline/history.md 갱신.
9. 최종 요약 보고 (소요 iter 수, WARN 목록, 다음 챕터 훅).

## Gate FAIL 처리
- iter < 3 이면: FAIL 리포트 + `chapter-writer` 에 재작성 지시 (v2, v3).
- iter == 3 에도 FAIL: `.work/gate-decisions.md` 에 전체 이력 기록, 작가에게 A/B/C 선택지 제시 (PRD §3.5).

## 주의
- 이 커맨드는 시간이 오래 걸린다. 각 단계 시작 시 한 줄로 진행 상황 보고.
- 중간에 사용자가 중단하면 `.session/current.yaml` 에 `rewrite_iteration` 과 `gate_cursor` 를 저장.
