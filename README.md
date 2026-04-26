# novel-writer — Claude Code 플러그인

한국어 장편 소설 집필을 위한 멀티 에이전트 시스템을 Claude Code 플러그인으로 배포하는 레포.

- **19개 서브에이전트** + **14개 슬래시 커맨드** + **5단계 Gate 검증 파이프라인**
- **Bible / State 이분법** — 불변 설정과 가변 상태를 엄격히 분리
- **Timeline append-only** — 장편에서 사건 순서 혼선 방지
- **Batch Feedback Gate** — 재작성 1~2회 안에 모든 일관성 이슈 수렴
- **훅 기반 Bible 쓰기 차단** — 집필 중 설정 변경 실수 방지

원본 PRD: [`docs/novel-writing-agent-prd-v1.4.docx`](docs/novel-writing-agent-prd-v1.4.docx) · 차용 참고: Thomas Houssin *Claude Book* (MIT).

---

## 설치 (사용자용)

```
# Claude Code 세션에서:
/plugin marketplace add hansangho/novelai
/plugin install novel-writer@hans-novel-tools
```

그리고 작업할 소설 프로젝트(빈 폴더 또는 기존 git 레포)에서:

```
/init-novel
```

`bible/`, `state/`, `timeline/`, `story/`, `.work/`, `.session/`, `CLAUDE.md`, `.gitignore` 스캐폴딩이 들어갑니다. 기존 파일은 덮어쓰지 않습니다.

### 튜토리얼

- 🌱 **개발 지식이 없는 작가용**: [`docs/작가용-사용법.md`](docs/작가용-사용법.md) — 터미널이 처음이어도 따라할 수 있는 안내. 비유와 단계별 설명 위주.
- 🛠️ **개발자·익숙한 사용자용**: [`docs/TUTORIAL.md`](docs/TUTORIAL.md) — 빈 폴더 → 챕터 1 확정까지 30~60분 walkthrough.

### 스크린샷 · 데모

> 스크린샷·데모 GIF 는 실사용 세션에서 캡처 필요. 아래 장면을 제안:

1. **`/plugin` 상태** — `novel-writer Plugin · hans-novel-tools` 성공 로드 표시
2. **`/init-novel` 실행** — 빈 폴더에 28 파일 스캐폴딩이 한 번에 생성되는 로그
3. **`/write-chapter 1` Gate 파이프라인** — G1~G5 리포트가 순차 생성되고 재작성 루프가 도는 시퀀스
4. **`bible_guard` 훅 차단** — LOCKED 상태에서 bible/ 수정 시도 시 훅이 `exit 2` 로 막는 메시지
5. **`/metrics` 출력** — 8챕터 기준 지표 표 전체

캡처 방법:
- macOS: `⇧⌘5` 로 터미널 영역 녹화 → `.mov` → `ffmpeg` 로 `.gif` 변환 (`ffmpeg -i in.mov -vf "fps=10,scale=900:-1" out.gif`)
- 또는 [asciinema](https://asciinema.org) 로 터미널 세션 녹화 → SVG/GIF export
- 캡처물은 `docs/screenshots/` 에 두고 이 섹션에서 상대 경로로 참조

---

## 빠른 시작 (작가 워크플로우)

```bash
# 1. 기획
#    theme-scout, genre-expert, cliche-detector, material-finder 가 브레인스토밍을 돕는다

# 2. 자료 조사
#    research-specialist, advisor-dispatcher 가 팩트·자문

# 3. Bible 구축 (기획 단계에만 쓰기 가능)
#    bible/characters/*.md, bible/universe/*.md, bible/structure.md, bible/style.md

# 4. 집필 단계 진입
/bible-lock

# 5. 챕터 집필 + 자동 Gate 검증
/write-chapter 1

# 6. Gate 통과 시 확정
/finalize 1

# 7. 중단 후 재개
/resume
```

---

## 주요 슬래시 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/init-novel` | 스캐폴딩 설치 |
| `/write-chapter N` | 초고 작성 + G1~G5 파이프라인 |
| `/continue-writing` | 중단된 지점부터 재개 |
| `/gate-status N` | 현재 Gate 진행 상태 |
| `/run-gate G? N` | 특정 Gate 단독 실행 |
| `/override-gate G? <사유>` | Gate 강제 통과 |
| `/revise-loop N` | 전 Gate 재실행 + 재작성 루프 |
| `/finalize N` | 확정 이동 → state/timeline 갱신 |
| `/timeline [필터]` | 사건 연대기 조회 |
| `/bible-lock` / `/bible-unlock <사유>` | Bible 쓰기 토글 |
| `/state [N]` | 챕터 말 상태 조회 |
| `/perplexity <N\|파일>` | 독창성 분석 |
| `/resume` | 세션 복원 |
| `/metrics [--json\|--project N]` | 지표 리포트 |

---

## 5-Gate 파이프라인

```
Chapter Writer → .work/writer-draft-chNN-v1.md
     │
     ├─ G1 Style Gate        (style-linter)
     ├─ G2 Character Gate    (character-consistency-guardian)
     ├─ G3 Continuity Gate   (continuity-reviewer)
     ├─ G4 Perplexity Gate   (perplexity-analyzer, 선택적)
     └─ G5 Integration Gate  (writing-director)
         │
         PASS → 작가 확인 → /finalize → state-updater
         FAIL → Chapter Writer 재작성 (v2, v3 — 최대 3회)
                 3회 초과 → A: override / B: bible-unlock / C: 수동 작성
```

---

## 레포 구조

```
novelai/                                  (이 레포 = 플러그인 소스)
├── .claude-plugin/
│   └── marketplace.json                  # 마켓플레이스 선언
├── plugins/
│   └── novel-writer/                     # 실제 플러그인
│       ├── .claude-plugin/plugin.json
│       ├── agents/                       # 서브에이전트 21종
│       ├── commands/                     # 슬래시 커맨드 14종
│       ├── hooks/hooks.json              # PreToolUse·PostToolUse 훅
│       ├── scripts/                      # python·bash 도우미
│       │   ├── bible_guard.py            # LOCKED 쓰기 차단
│       │   ├── bible_lock.sh             # lock/unlock
│       │   ├── gate_runner.py            # G1~G5 오케스트레이션
│       │   ├── state_snapshot.py         # state/chapter-NN 생성
│       │   ├── session_log.py            # PostToolUse 로그
│       │   ├── validate_state.py         # YAML 문법 검증
│       │   ├── pilot_metrics.py          # /metrics 백엔드
│       │   └── init_novel.py             # /init-novel 백엔드
│       └── templates/                    # /init-novel 이 복사할 빈 스캐폴딩
│           ├── bible/, state/, timeline/, story/, research/
│           ├── .work/, .session/
│           ├── CLAUDE.md                 # 작가용 프로젝트 메모리
│           └── gitignore.template
├── examples/
│   └── shanghai-shadow/                  # 샘플 작품 (상하이의 그림자, ch1~8 집필 완료)
├── docs/
│   ├── novel-writing-agent-prd-v1.4.docx # 원본 스펙
│   ├── pilot-01-retrospective.md
│   └── pilot-02-long-form-retrospective.md
├── CLAUDE.md                             # 이 레포 (플러그인 개발용) 프로젝트 메모리
└── README.md
```

---

## 불변 원칙 (플러그인이 강제)

1. `bible/` 은 LOCKED 상태에서 **절대 쓰기 금지** — 훅이 차단
2. `timeline/history.md` 는 **append-only** — 이전 엔트리 수정 금지
3. 드래프트는 모두 `.work/writer-draft-chNN-vN.md` — `story/chapters/` 직행 금지
4. 리뷰어는 **리포트만** 쓴다 — 수정은 Chapter Writer 몫
5. 재작성 한도 **3회**
6. 정보 누수(캐릭터가 `unaware_of` 발화·추론)는 G2 FAIL 최상위 사유

---

## 개발 (플러그인 본체 수정)

이 레포를 직접 clone 한 개발자는:

```bash
git clone https://github.com/hansangho/novelai
cd novelai

# 샘플 작품 (examples/shanghai-shadow/) 에서 플러그인 동작 검증
cd examples/shanghai-shadow
CLAUDE_PROJECT_DIR=$(pwd) CLAUDE_PLUGIN_ROOT=../../plugins/novel-writer \
  python3 ../../plugins/novel-writer/scripts/pilot_metrics.py
```

`docs/pilot-01-retrospective.md`, `docs/pilot-02-long-form-retrospective.md` 가 2회의 파일럿 결과·발견된 이슈·해결 과정을 기록.

---

## 라이선스
- 플러그인: [MIT](LICENSE)
- Bible/State/Gate/Perplexity/Timeline 개념 차용: Thomas Houssin *Claude Book* (MIT)

## 문의
hansanghoo@gmail.com
