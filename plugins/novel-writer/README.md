# novel-writer

한국어 장편 소설 집필을 위한 Claude Code 멀티 에이전트 시스템. **소크라테스식 대화**로 결정을 이끌어내고, **5-Gate 검증**으로 일관성을 지킨다.

## 설치

```
/plugin marketplace add hansangho/novelai
/plugin install novel-writer@hans-novel-tools
```

빈 폴더(또는 기존 git 레포)에서:

```
/init-novel
```

`bible/`, `state/`, `timeline/`, `story/`, `.work/`, `.session/`, `CLAUDE.md`, `.gitignore` 스캐폴딩 설치. 기존 파일은 덮어쓰지 않음.

## 핵심 특징

**소크라테스식 대화 (v1.5.0 신규)** — 캐릭터·플롯·장면·주제 결정 시 에이전트가 후보를 제시하기 전에 **작가에게 먼저 질문**한다. 산파술(maieutics) — 작가 내면의 답을 끌어낸다. 빠른 답을 원하면 "빠른 드래프트" 같은 키워드로 우회. 적용: theme-scout / character-architect / structure-architect / scene-planner / cliche-detector / plot-originality-critic / material-finder. 상세: [`docs/SOCRATIC-MODE.md`](../../docs/SOCRATIC-MODE.md).

**Bible / State 이분법** — 불변 설정(bible/)과 가변 상태(state/chapter-NN/)를 디렉토리 수준에서 엄격히 분리. 집필 단계에서 훅이 bible/ 쓰기를 차단.

**5-Gate 일관성 파이프라인** — 각 챕터 드래프트는 다음을 순차 통과:
| Gate | 책임 | FAIL 조건 |
|------|------|-----------|
| G1 Style | style-linter | error ≥1 (금지어·AI 시작구·과부사·대사 태그 위반) |
| G2 Character | character-consistency-guardian | 정보 누수 ≥1 |
| G3 Continuity | continuity-reviewer | 시공간 모순·세계관 규칙 위반 |
| G4 Perplexity | perplexity-analyzer | 선택적 (FAIL 없음, 독창성 플래그만) |
| G5 Integration | writing-director | 리뷰 충돌·plan.md 이탈 |

재작성 루프 최대 3회. 초과 시 작가 에스컬레이션 (Gate 완화 / Bible 수정 / 수동 작성).

**Timeline append-only** — 확정 사건을 시간순 누적. 장편에서 "언제 누가 뭘 했더라" 검색 가능 (`/timeline kim-dohyun`, `/timeline --unresolved` 등).

## 17 슬래시 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/init-novel [장르]` | 빈 프로젝트 스캐폴딩. 장르: `historic-noir` / `urban-fantasy` / `web-novel` / `sf` |
| `/write-chapter N` | 초고 작성 + G1~G5 파이프라인 자동 실행 |
| `/continue-writing` | 중단된 지점부터 재개 |
| `/gate-status N` | 현재 Gate 진행 상태 |
| `/run-gate G? N` | 특정 Gate 단독 실행 |
| `/override-gate G? <사유>` | Gate 강제 통과 |
| `/revise-loop N` | 전 Gate 재실행 + 재작성 루프 |
| `/finalize N` | 확정 이동 → state/timeline 갱신 |
| `/timeline [필터]` | 사건 연대기 조회 |
| `/bible-lock` / `/bible-unlock <사유>` | Bible 쓰기 토글 |
| `/state [N]` | 챕터 말 상태 조회 |
| `/perplexity <N\|파일\|--calibrate>` | 독창성 분석 / 임계값 자동 튜닝 |
| `/resume` | 세션 복원 |
| `/metrics [--cost \| --project N \| --json]` | 지표 리포트 + 비용 추정 |
| `/export [--format md\|epub\|pdf\|docx]` | 챕터 통합·내보내기 |
| `/visualize` | 인물 관계 mermaid·SP 추적·timeline HTML |

## 21 서브에이전트

**기획** (`theme-scout`, `genre-expert`, `cliche-detector`, `material-finder`)
**자료 조사** (`research-specialist`, `advisor-dispatcher` + 동적 Advisors)
**캐릭터** (`character-architect`, `dynamic-character-agent`)
**구조** (`structure-architect`, `scene-planner`, `plot-originality-critic`)
**집필** (`chapter-writer`)
**Gate** (`style-linter`, `character-consistency-guardian`, `continuity-reviewer`, `perplexity-analyzer`, `writing-director`)
**챕터 종료** (`state-updater`)
**퇴고** (`revision-editor`, `proofreader`)
**세션 관리** (`session-manager`)

## 불변 원칙 (플러그인이 강제)

1. `bible/` LOCKED 상태에서 쓰기 금지 — PreToolUse 훅 차단
2. `timeline/history.md` append-only — 이전 엔트리 수정 금지
3. 드래프트는 `.work/writer-draft-chNN-vN.md` — `story/chapters/` 직행 금지
4. 리뷰어는 리포트만 쓴다 — 수정은 Chapter Writer 몫
5. 재작성 한도 3회
6. 정보 누수 (unaware_of 발화·추론) 는 G2 FAIL 최상위 사유

## 상세 가이드

- [TUTORIAL.md](../../docs/TUTORIAL.md) — **터미널·git 처음이어도 따라할 수 있는** 작가용 사용 안내
- [SOCRATIC-MODE.md](../../docs/SOCRATIC-MODE.md) — 소크라테스식 대화 방법론
- [PRD v1.4](../../docs/novel-writing-agent-prd-v1.4.docx) — 원본 설계 명세
- [파일럿 01 회고](../../docs/pilot-01-retrospective.md) — 2 챕터 스모크
- [파일럿 02 회고](../../docs/pilot-02-long-form-retrospective.md) — 8 챕터 누적 비대 검증

## 라이선스

MIT. 개념 차용: Thomas Houssin *Claude Book* (MIT).
