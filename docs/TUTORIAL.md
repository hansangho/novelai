# 튜토리얼 — 첫 소설 쓰기 (novel-writer 플러그인)

이 가이드는 `novel-writer` 를 처음 쓰는 작가가 **빈 폴더에서 챕터 1 확정본**까지 가는 전체 경로를 다룹니다. 분량: 30~60 분.

전제:
- Claude Code CLI 가 설치되어 있고 로그인되어 있다 (`claude --version` 확인).
- `novel-writer@hans-novel-tools` 플러그인이 설치·활성화되어 있다 (`/plugin` 확인).

---

## 1. 빈 프로젝트 준비 (1 분)

터미널에서:

```bash
mkdir ~/Writing/my-first-novel
cd ~/Writing/my-first-novel
git init
claude
```

Claude Code 세션이 열리면:

```
/init-novel
```

아래 구조가 들어옵니다 (기존 파일은 덮어쓰지 않음):

```
my-first-novel/
├── CLAUDE.md                 ← 작가용 프로젝트 메모리
├── .gitignore                ← .work/·휘발성 세션 제외
├── bible/
│   ├── style.md              ← 문체 규칙
│   ├── style-rules.json      ← 기계 판독 규칙
│   ├── structure.md          ← 서사 구조
│   ├── universe/
│   │   ├── _overview.md
│   │   ├── rules.md          ← 세계의 법칙
│   │   └── historical-facts.md
│   ├── characters/
│   │   ├── _index.md
│   │   └── _template.md      ← 새 인물마다 복사
│   ├── _changelog.md
│   └── LOCK_STATUS.md        ← 현재 DRAFTING
├── state/template/           ← state_snapshot.py 가 쓰는 원본
├── timeline/
│   ├── history.md            ← append-only
│   └── current-chapter.md
├── story/
│   ├── synopsis.md
│   ├── plan.md
│   └── chapters/             (비어 있음)
├── research/
├── .work/
└── .session/
```

---

## 2. 기획 — 주제와 장르 탐색 (10~15 분)

### 2.1 주제 브레인스토밍

```
1900년대 초 경성에서 은퇴한 형사의 마지막 사건을 다루고 싶어.
주제 후보 몇 개 제안해줘.
```

Writing Director 가 **Theme Scout** 서브에이전트를 호출해 `research/subjects/themes-*.md` 에 3~5개 주제 후보를 저장합니다. 각 후보마다 "왜 지금 이 이야기인가" 논거 포함.

### 2.2 장르 검토

```
역사 느와르로 가려고 해. 장르 관습과 최근 트렌드 확인해줘.
```

**Genre Expert** 가 필수 요소·하위 장르·2023~ 트렌드·위험한 관습을 정리해 `research/subjects/genre-*.md` 에 저장.

### 2.3 클리셰 점검

```
지금까지 나온 설정이 장르 클리셰에 빠져 있는지 봐줘.
```

**Cliché Detector** 가 🟢/🟡/🔴 판정 + 변주 제안.

---

## 3. 자료 조사 (15~30 분)

```
1900년대 초 경성 경찰 조직·사건·장소 고증이 필요해. research-specialist 호출.
```

**Research Specialist** 가 `research/subjects/deep-*.md` 를 작성 — 1차·2차 자료, 시간선, 인물 지도, 장면 소재, 주의점, 출처 모두 포함.

추가로 전문성이 필요하면:

```
1923년 경성 순사의 일상 루틴을 자문위원으로 소집해줘.
```

**Advisor Dispatcher** 가 맞춤 자문위원 페르소나 카드를 만들고 그 시점의 인물로 답변. 결과는 `research/advisors/*.md` 에 영속 저장.

---

## 4. Bible 구축 (20~40 분)

`bible/` 은 집필 단계 진입 전까지만 쓸 수 있습니다. 이후엔 훅이 차단해요.

### 4.1 문체 규칙 (`bible/style.md`)

템플릿이 이미 있으니 그대로 써도 되고, 작품에 맞게 조정. 예:
- 평균 문장 길이 목표
- 금지 어휘 (`그러나`, `~의 것이다` 등)
- AI 시작구 패턴 (`그날 아침,`, `운명의` …) 차단
- 대사 태그 규칙

`bible/style-rules.json` 은 Style Linter 가 **기계 판독** 하는 규칙입니다 — 정규식·임계값 단위로 조정.

### 4.2 세계관 (`bible/universe/*.md`)

- `_overview.md` — 시공간, 분위기, 주요 세력
- `rules.md` — 물리·마법·사회 규칙 (통신 수단이 중요 — 시대 오류 방지)
- `historical-facts.md` — 실제 역사 고증 (Continuity Reviewer 가 참조)
- `locations/` — 주요 장소별 개별 파일

### 4.3 인물 (`bible/characters/`)

주요 인물마다 `_template.md` 를 복사해 작성:

```bash
cp bible/characters/_template.md bible/characters/kim-dohyun.md
```

또는 Claude 에게:

```
주인공 '김도현' 프로필 만들어줘. 34세 전직 형사, 1921년 부패 목격 후 은퇴…
```

**Character Architect** 가 체계적으로:
- 물리·외모
- 배경
- 성격 강점/약점/결함
- 화법 습관
- **지식 경계** (알 수 있는 것 / 알 수 없는 것 / 챕터별 자각 시점)
- 관계 수치
- Arc (v1, v2 범위)
- 금기

> **가장 중요한 필드는 "지식 경계"입니다.** Character Consistency Guardian 이 Gate G2 에서 정보 누수를 차단할 때 이걸 기준으로 삼아요.

### 4.4 구조 설계 (`bible/structure.md`)

**Structure Architect** 가 `bible/structure.md` + `story/plan.md` 작성 — 전체 챕터 블록, 서브플롯 id (SP-A, SP-B …), 회수 챕터, 금지선.

### 4.5 시놉시스 (`story/synopsis.md`)

작가 본인이 작성. 로그라인 + 주인공/적대/반전/결말 방향/톤.

---

## 5. 집필 단계 진입 (1 분)

```
/bible-lock
```

이 순간부터 `bible/` 은 **Read-only**. 실수로 쓰려고 하면 훅이 차단합니다:

```
[bible-guard] bible/ 는 LOCKED 상태입니다. .../style.md 쓰기 차단.
`/bible-unlock <사유>` 로 해제 후 시도하십시오.
```

집필 중에도 Bible 수정이 꼭 필요하면:

```
/bible-unlock "김도현의 딸 이름을 수민에서 지영으로 변경"
```

→ `_changelog.md` 에 자동 기록 + Continuity Reviewer 가 영향받는 챕터 경고.

---

## 6. 챕터 1 집필 (20~40 분)

```
/write-chapter 1
```

자동 흐름:
1. `story/plan.md` 에서 챕터 1 아웃라인 추출
2. **Scene Planner** 호출 → `.work/scenes-ch01.md` 생성 (장면 beat sheet)
3. **Chapter Writer** 호출 → `.work/writer-draft-ch01-v1.md` 생성
4. **Gate G1~G4 병렬 실행** (Batch Feedback 모드):
   - G1 Style Linter → `.work/reviews/style-lint.md`
   - G2 Character Consistency Guardian → `.work/reviews/character-review.md`
   - G3 Continuity Reviewer → `.work/reviews/continuity-review.md`
   - G4 Perplexity Analyzer → `.work/reviews/perplexity-report.md` (선택적)
5. **G5 Writing Director** 종합 → `.work/reviews/integration.md`
6. 모든 Gate PASS → 작가 확인 요청
7. 승인 → `/finalize 1` → `story/chapters/chapter-01.md` 확정
8. **State Updater** 자동 호출 → `state/chapter-01/*.yaml` + `timeline/history.md` append

### Gate FAIL 시

iter v2 재작성이 자동으로 시작됩니다. 최대 3회. 3회 초과 시 작가 에스컬레이션:
- **A. `/override-gate G? <사유>`** — 특정 Gate 강제 통과
- **B. `/bible-unlock <사유>`** — Bible 자체 수정 (근본 원인)
- **C. 직접 작성** — Writer 무시하고 작가 본인 집필

### 중간 상태 확인

```
/gate-status 1
```

각 Gate 현황 표로 출력.

### 특정 Gate만 재실행

```
/run-gate G3 1
```

---

## 7. 일상 워크플로우

| 상황 | 커맨드 |
|------|-------|
| 이어서 쓰기 | `/continue-writing` |
| 다음 챕터 집필 | `/write-chapter 2` |
| 중단 후 재개 | `/resume` |
| 특정 챕터 상태 조회 | `/state 5` |
| 사건 연대기 조회 | `/timeline` / `/timeline kim-dohyun` / `/timeline --unresolved` |
| 독창성만 단독 체크 | `/perplexity 5` |
| 전체 Gate 재주행 | `/revise-loop 5` |
| 지표 대시보드 | `/metrics` / `/metrics --project 40` |
| Bible 수정 사이클 | `/bible-unlock <사유>` → 수정 → `/bible-lock` |

---

## 8. 퇴고 (챕터 전체 확정 후)

```
챕터 1~10 전체 퇴고해줘.
```

- **Revision Editor**: 구조·페이싱·감정 곡선·정보 분배
- **Proofreader**: 한국어 어문규정·맞춤법·띄어쓰기

각각 `.work/reviews/revision-*.md`, `proofread-chNN.md` 에 리포트.

---

## 9. 자주 막히는 지점

### "정보 누수" FAIL 이 자꾸 납니다
가장 흔한 원인: 캐릭터가 본인이 모를 시점에 무언가를 안 것처럼 암시함. `bible/characters/<id>.md` 의 **"알 수 없는 것"** 목록을 다시 보세요. 그 목록이 없다면 먼저 채워야 합니다.

### Style Linter 가 너무 엄격해요
`bible/style-rules.json` 의 임계값 조정. 또는 해당 장면에 `<!-- scene: lyrical -->` / `<!-- scene: action -->` 태그 부여 → `scene_overrides` 임계값 적용.

### Perplexity 플래그가 너무 많아요 / 적어요
선택적 Gate 이므로 FAIL 은 안 납니다. 단, PRD §13 목표 수용률 20~50% 를 벗어나면 `perplexity-analyzer.md` 의 임계값 조정.

### state YAML 문법 오류
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_state.py` 직접 실행해 위치 확인. 자주 발생하는 함정:
- 값이 `**` 로 시작 → 따옴표로 감싸기 (YAML alias 로 오인)
- 값 안에 `"` 포함 → 전체를 `'` 로 감싸기

### Bible 을 이미 LOCK 했는데 중대 수정이 필요
`/bible-unlock <사유>` — Continuity Reviewer 가 영향 챕터 자동 분석. 수정 후 `/bible-lock` 재호출.

---

## 10. 참고 샘플 작품

실제 8 챕터 파일럿이 `examples/shanghai-shadow/` 에 있습니다. 구조 의문이 생기면 거기서 확인하세요:
- `bible/characters/kim-dohyun.md` 의 "지식 경계" 섹션
- `state/chapter-03/character-states.yaml` 에서 turning point 이후 상태 변화 기록 방식
- `timeline/history.md` 의 챕터 블록 포맷
- `.work/gate-decisions.md` 의 실제 Gate 결정 이력

---

## 11. 지표 추적 (선택)

주간 retro 시 `.session/history/metrics/YYYY-MM-DD.json` 에 스냅샷 저장:

```bash
claude
> /metrics --json > .session/history/metrics/$(date +%Y-%m-%d).json
```

시간 경과에 따른 평균 재작성 횟수·Gate 통과율·Bible 수정 빈도 추이 추적 가능.

---

이상입니다. 막히는 지점이 생기면 회고 문서(`docs/pilot-01-retrospective.md`, `docs/pilot-02-long-form-retrospective.md`) 에 비슷한 시나리오가 있을 수 있어요.
