# Anthropic 공식 카탈로그 등재 준비 체크리스트

현재 `novel-writer` 는 `hans-novel-tools` 라는 개인 마켓플레이스에 배포 중. Anthropic 공식 카탈로그(`@claude-plugins-official` 접미사)에 등재되면 Claude Code UI 의 `/plugin` 에서 바로 검색·설치 가능.

## 제출 방법

**GitHub PR 아님** — 공식 폼 기반:
- [Claude.ai 제출 폼](https://claude.ai/settings/plugins/submit)
- 또는 [Console 제출 폼](https://platform.claude.com/plugins/submit)

폼 제출 후 Anthropic 팀이 검토. 심사 기간·기준 세부는 공식 문서 기준으로 "Quality · Security · Reliability" 라는 것만 공개됨.

참고:
- [Discover and install prebuilt plugins](https://code.claude.com/docs/en/discover-plugins) — 공식 문서
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — 승인된 플러그인 샘플 모음

## 사전 체크리스트

| 항목 | 현재 상태 | 설명 |
|------|-----------|------|
| `plugin.json` | ✅ v1.4.1 | `name` / `version` / `description` / `author` / `license` 모두 채움 |
| 루트 `LICENSE` | ✅ MIT | 레포 최상위 |
| 플러그인별 `LICENSE` | ✅ (v1.4.2 추가) | `plugins/novel-writer/LICENSE` |
| `README.md` | ✅ | 루트 README 에 설치·사용법·예시 |
| 플러그인 자체 README | ❌ (선택) | `plugins/novel-writer/README.md` 를 별도로 두면 `/plugin` UI 에서 바로 표시됨 — 권장 |
| `commands/` 또는 `skills/` | ✅ commands 14개 | — |
| `agents/` | ✅ 21개 | — |
| `hooks/hooks.json` | ✅ | — |
| `.mcp.json` | ➖ 해당 없음 | novel-writer 는 MCP 서버 없음 |
| 스크린샷·데모 | ❌ 미작성 | 루트 README 에 추가 권장 — 심사에서 품질 평가 가점 가능성 |
| 스모크 테스트 | ✅ 회고 2편 | `docs/pilot-*-retrospective.md` 에 실제 작동 증거 |

## 제출 전 추가로 할 일

### A. 플러그인 전용 README 작성 (권장)
`plugins/novel-writer/README.md` 를 만들어 `/plugin` UI 에서 플러그인을 선택했을 때 바로 보이는 설명. 루트 README 와 역할 분리:
- 루트 = 개발 레포 / 기여자용
- 플러그인 README = 사용자가 설치 전 읽는 "이게 뭐하는 플러그인인지"

### B. 보안 관련 점검 (권장)
- 훅·스크립트가 임의 코드 실행을 하지 않는지 확인 → 본 플러그인의 `bible_guard.py` / `session_log.py` 는 **작가 데이터만** 처리, 외부 네트워크 호출 없음
- PostToolUse 훅이 민감 정보를 로깅하지 않는지 → `session_log.py` 는 file path 와 command preview (120자) 만 기록. API 키·비밀번호 자동 마스킹은 없으므로, 작가 프로젝트에 민감 파일이 있다면 `.session/logs/` 를 git에서 제외 (기본 `.gitignore` 로 처리됨).
- 템플릿 복사 시 덮어쓰기 없음 → `init_novel.py` 가 기존 파일 건너뜀

### C. 품질 관련 점검
- 모든 스크립트 Python 문법 OK (`python3 -m py_compile`)
- JSON 메타 유효 (`json.load`)
- YAML 검증기 (`validate_state.py`) 자체 제공
- 지표 수집기 (`pilot_metrics.py`) 로 사용자가 품질 self-monitor 가능
- 파일럿 2회 (ch1-2, ch3-8) 에서 의도 결함 탐지율 100%

### D. 신뢰성 관련 점검
- 경로 추상화: `$CLAUDE_PROJECT_DIR` · `$CLAUDE_PLUGIN_ROOT` 표준 준수
- Idempotent 동작 (`/init-novel` 재호출 시 0 신규)
- 실패 시 사용자에게 명확한 메시지 출력

## 제출 시 전달할 요약 (폼 입력용 초안)

**Plugin name:** `novel-writer`
**Marketplace:** `hans-novel-tools` (개인 소스, 이전할지 Anthropic 결정에 맡김)
**Description:**
한국어 장편 소설 집필을 위한 멀티 에이전트 시스템. Bible/State 이분법으로 불변 설정과 가변 상태를 분리, 5단계 Gate (Style · Character · Continuity · Perplexity · Integration) 로 일관성 붕괴를 구조적으로 방지, Timeline append-only 로 장편의 사건 순서 혼선을 차단한다. 훅 기반 Bible 쓰기 차단으로 집필 중 설정 변경 실수를 예방한다.

**Key features:**
- 21 subagents (planning → research → characters → structure → writing → revision)
- 14 slash commands
- 2 hooks (PreToolUse for Bible write blocking, PostToolUse for session log)
- Project scaffolding via `/init-novel` (idempotent)
- YAML state validator (`validate_state.py`)
- Success metrics collector (`pilot_metrics.py`)

**Target users:** 한국어 장편 소설을 쓰는 작가 (웹소설·문학·장르 모두 포함)

**Supported languages:** 한국어 집중 (영어 소설에도 응용 가능하나 `style-rules.json` 튜닝 필요)

**Repository:** https://github.com/hansangho/novelai
**License:** MIT
**Current install:** `/plugin marketplace add hansangho/novelai` → `/plugin install novel-writer@hans-novel-tools`

**Pilot evidence:**
- `docs/pilot-01-retrospective.md` — 2 챕터 파일럿, 의도 결함 6건 100% 탐지, iter 2 수렴
- `docs/pilot-02-long-form-retrospective.md` — 8 챕터 누적 비대 검증, state 스냅샷 비누적 구조 실증, SP 추적 정확도 3/3

## 불확실한 부분

- `plugin.json` 의 모든 권장 필드 목록 공개 안 됨 → 공식 예제 저장소 (`anthropics/claude-plugins-official`) 의 기존 승인된 플러그인을 참고해 필드 추가 검토
- 심사 기간·재제출 정책 미공개
- 폼 제출 후 진행 상황 추적 방법 미공개
