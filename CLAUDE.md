# novelai — 플러그인 개발 레포 메모리 (L4)

> 이 레포는 `novel-writer` Claude Code 플러그인의 **소스 레포** 입니다. 실제 작가 작업 공간은 별도.

## 레포 성격
- 최상위에 `.claude-plugin/marketplace.json` 이 있어 Claude Code 가 이 레포를 마켓플레이스로 인식
- 실제 플러그인 콘텐츠는 `plugins/novel-writer/` 하위
- `examples/shanghai-shadow/` 는 플러그인으로 집필한 **샘플 작품** (ch1~8 확정)

## 개발 시 지켜야 할 것

### 스크립트 경로 규약
- 모든 `scripts/*.py` 는 **두 개의 환경 변수** 를 기준으로 경로를 해석한다:
  - `$CLAUDE_PROJECT_DIR` — 작가의 작품 폴더 (bible/, state/, timeline/ 등이 있는 곳)
  - `$CLAUDE_PLUGIN_ROOT` — 플러그인 설치 폴더 (scripts/, templates/ 등이 있는 곳)
- 수동 실행 시 fallback 은 `Path.cwd()` (PROJECT) 와 스크립트 파일 기준 상위 2단계 (PLUGIN_ROOT)
- **절대 하드코딩된 `Path(__file__).resolve().parent.parent` 로 작가 데이터에 접근 금지** — 플러그인 자체 파일(templates, scripts)에만 허용

### 커맨드 경로 규약
- 모든 `commands/*.md` 에서 플러그인 스크립트 호출은 `${CLAUDE_PLUGIN_ROOT}/scripts/...` 형태
- 상대 경로 `python3 scripts/...` 는 금지 — 작가 프로젝트에 해당 디렉토리가 없음

### 훅 경로 규약
- `hooks/hooks.json` 에서 command 는 반드시 `${CLAUDE_PLUGIN_ROOT}/scripts/...`
- PreToolUse/PostToolUse 는 작가 프로젝트의 파일 이벤트에 반응하지만, 실행되는 스크립트는 플러그인에 살아야 함

### 템플릿 규약
- `templates/` 내부는 **제네릭** 이어야 함 — 특정 작품(예: 상하이의 그림자) 내용이 섞이면 안 됨
- `.gitkeep` 으로 빈 디렉토리 유지 (git 이 빈 폴더를 추적 안 하므로)
- `init_novel.py` 는 템플릿을 "이미 있는 파일은 건너뛰는" 방식으로 복사

### 샘플 작품 (`examples/shanghai-shadow/`)
- 플러그인의 실제 작동 예시. 문제 발생 시 여기서 재현
- 새 기능·에이전트 추가 시 여기서 파일럿 실행
- `docs/pilot-*-retrospective.md` 에서 각 파일럿 결과 참고

## 에이전트 21종 + 커맨드 14종
상세는 `plugins/novel-writer/agents/`, `plugins/novel-writer/commands/` 참조.

## 5 Gate 계약 (배포 문서에 반영됨)
| # | Gate | 에이전트 |
|---|------|----------|
| G1 | Style | style-linter |
| G2 | Character | character-consistency-guardian |
| G3 | Continuity | continuity-reviewer |
| G4 | Perplexity | perplexity-analyzer (선택적) |
| G5 | Integration | writing-director |

Batch Feedback 모드 — G1~G4 동시 수행 → G5 종합 → 재작성. 재작성 한도 3회.

## 배포 체크리스트
1. `scripts/` 수정 시 → 작가 데이터 경로가 `$CLAUDE_PROJECT_DIR` 로만 접근하는지 확인
2. `commands/*.md` 수정 시 → `${CLAUDE_PLUGIN_ROOT}` 로 스크립트 참조하는지 확인
3. `templates/` 수정 시 → 작품 특정 내용 없는지 확인 (상하이 글자 검색)
4. 파일럿: `examples/shanghai-shadow/` 에서 pilot_metrics 실행해 regression 없는지 확인
5. `plugins/novel-writer/.claude-plugin/plugin.json` 의 `version` bump
6. `.claude-plugin/marketplace.json` 의 `plugins[0].version` 도 함께 bump
7. git tag → push → 사용자에게 "plugin update" 안내

## 파일럿 히스토리
- `docs/pilot-01-retrospective.md` — 초기 2챕터 파일럿. YAML/경로 이슈 발견
- `docs/pilot-02-long-form-retrospective.md` — 8챕터 누적 비대 검증. SP tracking·validator 신설

## 참고
- PRD 원본: `docs/novel-writing-agent-prd-v1.4.docx`
- 원 아이디어 크레딧: Thomas Houssin *Claude Book* (MIT)
