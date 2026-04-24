# (작품명) — Project Memory (L4)

> 본 파일은 Claude Code 가 매 세션 시작 시 자동 로드하는 프로젝트 메모리.
> `novel-writer` 플러그인의 계약을 Claude 가 어기지 않도록 하는 것이 목적.

## 한줄 요약
(작품 한 줄 소개)

## 디렉토리 계약 (반드시 지킨다)
| 경로 | 쓰기 권한 | 언제 |
|------|-----------|------|
| `bible/` | **LOCKED 시 Read-only**. 플러그인 훅이 차단. | 기획 단계에만 Character Architect / Structure Architect 가 쓴다. |
| `state/` | State Updater 전용 | 챕터 확정 직후만. |
| `timeline/history.md` | **append-only**. 수정·삭제 금지. | State Updater. |
| `story/chapters/` | `/finalize` 이후만 생성 | 작가 승인 후 `gate_runner.py finalize`. |
| `.work/` | 모든 에이전트의 스크래치 | 항상. gitignored. |
| `research/` | Research Specialist / Advisor Dispatcher | 자료 수집 |
| `.session/` | Session Manager | 휘발성 (current.yaml) + 영속 (history/, decisions.md) |

**bible/LOCK_STATUS.md 가 LOCKED 이면 `bible/` 어디에도 쓰지 마라.**

## 5 Gate 계약
| # | Gate | 에이전트 | FAIL 조건 |
|---|------|----------|-----------|
| G1 | Style | style-linter | error ≥1 |
| G2 | Character | character-consistency-guardian | 정보 누수 ≥1 |
| G3 | Continuity | continuity-reviewer | 시공간 모순 or 규칙 위반 |
| G4 | Perplexity | perplexity-analyzer | **선택적** (FAIL 없음) |
| G5 | Integration | writing-director | 리뷰 충돌·arc 이탈 |

### 실행 모드: Batch Feedback
G1~G4 를 같은 iter 에 모두 실행 → G5 가 종합 → Writer 가 1회 재작성으로 다수 이슈 동시 해결.

### 불변 원칙
1. Bible 은 집필 단계에서 불변. 예외 수정은 `_changelog.md` 기록 의무.
2. Timeline 은 append-only. 과거 엔트리 수정 금지.
3. 드래프트는 모두 `.work/writer-draft-chNN-vN.md`. `story/chapters/` 직행 금지.
4. 리뷰어는 드래프트를 수정하지 않는다.
5. 재작성 한도 3회.
6. 정보 누수(캐릭터가 unaware_of 를 발화·추론) 는 G2 FAIL 최상위 사유.

## 슬래시 커맨드
`/write-chapter N` · `/continue-writing` · `/gate-status N` · `/run-gate G? N` · `/override-gate G? <사유>` · `/timeline [필터]` · `/bible-lock` · `/bible-unlock <사유>` · `/state [N]` · `/perplexity <N|파일>` · `/revise-loop N` · `/finalize N` · `/resume` · `/metrics`

## 한국어 작성 원칙
- 원고·Bible·State·Timeline 은 **한국어**.
- 스타일 규칙은 `bible/style.md` + `bible/style-rules.json`.

## 참고
- 플러그인: `novel-writer` (PRD v1.4)
- 원 설계: github.com/hans/novelai
