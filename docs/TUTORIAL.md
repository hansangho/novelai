# 튜토리얼 — 처음 쓰는 작가를 위한 안내

이 도구를 처음 쓰는 작가가 **빈 폴더에서 챕터 1 확정본**까지 가는 전체 경로를 다룹니다. **개발 지식이 없어도 따라할 수 있도록** 기본 개념부터 안내합니다.

소요 시간: 설치·기획 포함 30~90분 (장편 한 챕터 분량 집필 시간은 별도).

---

## 0. 시작하기 전에 — 이게 뭐예요?

### Claude(클로드)
사람과 한국어로 대화하는 AI 입니다. "주인공의 어린 시절 상처는 어떤 모양일까?" 같은 질문에 같이 생각해 줍니다.

### Claude Code
Claude 를 **컴퓨터의 글자 화면(터미널)** 에서 쓰는 프로그램. 채팅과 다른 점은 **파일을 직접 만들고 수정**합니다 — 우리가 시킨 대로 원고를 폴더에 진짜 저장해 줍니다.

### novel-writer 플러그인
Claude Code 에 끼우는 **소설 작가용 부속품**. 두 가지를 자동으로 합니다.

1. **결정의 동반자** — 캐릭터·플롯·장면을 정할 때 Claude 가 답을 던지지 않고 **질문을 던져서 작가의 답을 끌어냅니다** (소크라테스식 대화).
2. **일관성 감시인 5명** — 챕터를 쓸 때마다 5명의 검수원이 자동으로 원고를 본 뒤 OK/재작성 판정. 이름이 챕터 1에서 "수민" 챕터 5에서 "수영" 으로 변하는 식의 실수를 미리 잡습니다.

### 폴더 구조 (한눈에 비유)

| 폴더 | 비유 |
|------|------|
| `bible/`     | **작품 사전·설정집** — 캐릭터·세계관·문체·금지선. 한 번 정하면 잘 안 바뀜 |
| `state/`     | **챕터별 노트** — 챕터 1 끝났을 때 누가 어디 있었지? 같은 메모 (자동) |
| `timeline/`  | **사건 일지** — 1923-01-15에 무슨 일이 있었나 시간순 (자동) |
| `story/`     | **실제 원고** — 챕터 1, 2, ... 의 본문 |
| `.work/`     | **임시 작업장** — 검수 통과 안 한 초고 (자동 정리, 무시 가능) |
| `.session/`  | **세션 메모** — 어디까지 작업했는지 (자동) |

---

## 1. 설치 — 한 번만 (15~30분)

### 1.1. 터미널 열기
"터미널" 은 Mac 의 기본 프로그램. **글자로 컴퓨터에 명령**하는 까만 창입니다.

1. 키보드 `⌘ + Space` (커맨드 + 스페이스) → 화면 중앙에 검색창 (스포트라이트).
2. **"터미널"** 입력 → 엔터.
3. 까만 창이 열립니다.

### 1.2. Claude Code 설치
터미널에 아래를 **그대로 복사 붙여넣기** 후 엔터:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

(또는 Homebrew 가 있다면 `brew install --cask claude-code`)

### 1.3. Claude 에 로그인
같은 터미널에서:

```bash
claude
```

처음 실행이면 로그인 안내가 뜹니다. 따라가면 브라우저가 열려 로그인 페이지가 나옵니다. **claude.ai 계정**(무료/Pro/Max/Team/Enterprise) 로 로그인.

> 장편 한 편을 쓰기에 무료 한도는 부족할 수 있습니다 — Pro 이상 권장.

### 1.4. 설치 확인
```bash
claude --version
```

버전 번호가 출력되면 OK.

### 1.5. novel-writer 플러그인 설치
Claude 가 켜진 상태에서:

```
/plugin marketplace add hansangho/novelai
```

이어서:

```
/plugin install novel-writer@hans-novel-tools
```

"설치되었습니다" 메시지가 나오면 완료.

> **에러가 보여도 당황 금지.** 메시지 전체를 복사해 Claude 에게 붙여넣고 "이거 어떻게 해결해?" 라고 물어보면 알려줍니다.

### 1.6. Claude 종료·재시작
- 종료: 터미널에 `exit` + 엔터, 또는 `Ctrl + C` 두 번
- 재시작: 터미널에서 `claude` 입력

---

## 2. 빈 프로젝트 준비 (5분)

소설 한 편마다 **별도 폴더**를 씁니다 (다른 작품과 섞이지 않도록).

### 2.1. 폴더 만들고 들어가기
터미널에서:

```bash
mkdir -p ~/Documents/내소설들/내첫소설
cd ~/Documents/내소설들/내첫소설
```

설명:
- `mkdir -p ...` → "내 문서 안에 '내소설들/내첫소설' 폴더를 만들어라"
- `cd ...` → "그 폴더 안으로 들어가라"

원하는 이름·위치로 바꿔도 됩니다 (예: `~/Desktop/소설/광주의겨울`).

### 2.2. Claude 시작 + 스캐폴딩
같은 터미널에서:

```bash
claude
```

Claude 가 켜진 뒤:

```
/init-novel
```

→ 0절의 표에 있던 폴더들과 빈 템플릿 파일이 자동으로 들어옵니다. 이미 파일이 있으면 덮어쓰지 않습니다.

### 장르 프리셋 (선택)
장르가 이미 정해졌다면 미리 채워진 시작점을 받을 수 있습니다:

```
/init-novel historic-noir     # 1900~1950 시대극 + 누아르
/init-novel urban-fantasy     # 현대 한국 + 초자연
/init-novel web-novel         # 웹소설 (회귀·헌터·로판) — 짧은 호흡·후킹 강조
/init-novel sf                # 하드 SF·스페이스 오페라
```

→ 일반 템플릿 위에 장르별 `style-rules.json`·`structure.md`·`characters/_template.md` 가 덮어 씌워집니다. 장르 클리셰 차단 규칙이 자동 추가돼요.

---

## 3. 기획 — 주제와 장르 탐색 (10~20분)

이 도구의 가장 특별한 점: **Claude 가 답을 던지지 않고 질문을 던집니다**. 답을 듣고 다음 질문을 쌓아 갑니다 (소크라테스식 대화).

> 🐢 **느린 게 답답하면**: 어느 단계에서든 `빠른 드래프트 모드로 옵션 3개만 줘` 라고 말하면 질문 없이 바로 후보 제시.

### 3.1. 주제 브레인스토밍
Claude 에게 한국어로 그냥 말하세요:

```
1900년대 초 경성에서 은퇴한 형사의 마지막 사건을 다루고 싶어.
주제 같이 찾아줘.
```

**theme-scout** 가 호출되어 질문을 던집니다:
- "최근 며칠 안에 반복해서 떠오르는 이미지·감정이 있나요?"
- "당신이 쓰기 두려운 이야기는 무엇입니까? 왜 두렵습니까?"
- "이 이야기에서 절대 들어가면 안 되는 것은?"

답하다 보면 본인도 몰랐던 진짜 주제가 드러납니다. 결과는 `research/subjects/themes-*.md` 에 저장.

### 3.2. 장르 검토
```
역사 느와르로 가려고 해. 장르 관습과 최근 트렌드 확인해줘.
```

**Genre Expert** 가 필수 요소·하위 장르·2023~ 트렌드·위험한 관습을 정리.

### 3.3. 클리셰 점검
```
지금까지 나온 설정이 장르 클리셰에 빠져 있는지 봐줘.
```

**Cliché Detector** 가 🟢/🟡/🔴 판정. 단순히 "뻔하니 빼라" 가 아니라 "이게 의식적 선택인가?" 를 묻습니다.

---

## 4. 자료 조사 (15~30분)

```
1900년대 초 경성 경찰 조직·사건·장소 고증이 필요해.
```

**Research Specialist** 가 `research/subjects/deep-*.md` 작성 — 1차·2차 자료, 시간선, 인물 지도, 장면 소재, 주의점, 출처 모두 포함.

전문성이 더 필요하면:

```
1923년 경성 순사의 일상 루틴을 자문위원으로 소집해줘.
```

**Advisor Dispatcher** 가 맞춤 자문위원 페르소나를 만들고 답변. 결과는 `research/advisors/*.md` 에 영속 저장.

---

## 5. Bible 구축 (20~60분) — 가장 중요

`bible/` 은 작품의 **사전**입니다. 집필 단계 진입 전까지만 쓸 수 있고 (그 후엔 훅이 차단), 모든 검수가 이걸 기준으로 합니다.

### 5.1. 문체 규칙 (`bible/style.md`)
템플릿이 이미 있으니 그대로 쓰거나 작품에 맞게 조정:
- 평균 문장 길이 목표
- 금지 어휘 (`그러나`, `~의 것이다` 등)
- AI 시작구 패턴 (`그날 아침,`, `운명의` …) 차단
- 대사 태그 규칙

`bible/style-rules.json` 은 Style Linter 가 **기계 판독**하는 규칙입니다.

### 5.2. 세계관 (`bible/universe/*.md`)
- `_overview.md` — 시공간·분위기·주요 세력
- `rules.md` — **물리·마법·사회 규칙** (통신 수단이 중요 — 시대 오류 방지!)
- `historical-facts.md` — 실제 역사 고증 (Continuity Reviewer 가 참조)
- `locations/` — 주요 장소별 개별 파일

### 5.3. 인물 (`bible/characters/`) — 핵심
주요 인물마다 `_template.md` 를 복사해 작성하거나, 그냥 Claude 에게 부탁:

```
주인공 '김도현' 프로필 만들어줘. 34세 전직 형사, 1921년 부패 목격 후 은퇴…
```

**Character Architect** 가 7단계 질문으로 인물을 끌어냅니다:
1. 가장 오래된 상처
2. 스스로에게 인정 못하는 욕망 (결함)
3. 강점이 약점으로 바뀌는 지점
4. 절대 하지 않을 행동
5. 타인의 오해
6. **지식 경계 — 알 수 있는 / 알 수 없는 / 시간이 지나야 아는** ← 가장 중요
7. 신뢰하는 한 사람과 그 배신 방식

> 💡 **"지식 경계" 가 왜 중요한가요?**
> 챕터 7에서 주인공이 알게 되는 비밀을 챕터 3에서 모르게 해야 합니다. **챕터 7 이후 자각** 이라고 명시해 두면, 챕터 3 검수 때 "이 인물 이걸 아직 모를 텐데?" 하고 자동으로 잡습니다 (Gate G2).

### 5.4. 구조 설계 (`bible/structure.md` + `story/plan.md`)

```
전체 플롯 같이 잡아보자.
```

**Structure Architect** 가 결말 이미지부터 거꾸로 묻습니다:
- "마지막 장면에서 카메라가 마지막까지 머무는 지점은?"
- "중간 지점(약 절반) 에서 되돌아갈 수 없는 사건은?"
- "오프닝의 약속 중 의도적으로 배신할 약속은?"

답하다 보면 챕터 1, 2, 3, … 의 윤곽이 잡힙니다.

### 5.5. 시놉시스 (`story/synopsis.md`)
작가 본인이 작성. 로그라인 + 주인공/적대/반전/결말 방향/톤.

---

## 6. 집필 단계 진입 (1분)

```
/bible-lock
```

이 순간부터 `bible/` 은 **Read-only**. 실수로 쓰려고 하면 훅이 차단:

```
[bible-guard] bible/ 는 LOCKED 상태입니다. .../style.md 쓰기 차단.
`/bible-unlock <사유>` 로 해제 후 시도하십시오.
```

집필 중 Bible 수정이 꼭 필요하면:

```
/bible-unlock "김도현의 딸 이름을 수민에서 지영으로 변경"
```

→ `_changelog.md` 에 자동 기록 + Continuity Reviewer 가 영향받는 챕터 경고.

---

## 7. 챕터 1 집필 (20~60분)

```
/write-chapter 1
```

자동 흐름:
1. `story/plan.md` 에서 챕터 1 아웃라인 추출
2. **Scene Planner** 호출 → `.work/scenes-ch01.md` (장면 beat sheet)
3. **Chapter Writer** 호출 → `.work/writer-draft-ch01-v1.md` (초고)
4. **Gate G1~G4 동시 실행** (Batch Feedback):
   - **G1 Style** — 금지어·과부사·AI 시작구 등
   - **G2 Character** — 정보 누수 (알 수 없는 사실 누설)
   - **G3 Continuity** — 시간·공간·세계관 위반
   - **G4 Perplexity** — 문장 독창성 (선택적)
5. **G5 Writing Director** 종합
6. 모든 Gate PASS → 작가 확인 요청
7. 승인 → `/finalize 1` → `story/chapters/chapter-01.md` 확정
8. **State Updater** 자동 호출 → `state/chapter-01/*.yaml` + `timeline/history.md` append

### Gate FAIL 시
iter v2 재작성이 자동 시작 (최대 3회). 3회 초과 시 작가 에스컬레이션:
- **A. `/override-gate G? <사유>`** — 특정 Gate 강제 통과
- **B. `/bible-unlock <사유>`** — Bible 자체 수정 (근본 원인)
- **C. 직접 작성** — 작가가 손으로 고친 뒤 검수만 다시

### 중간 상태 확인
```
/gate-status 1
```

각 Gate 현황을 표로 출력.

### 특정 Gate만 재실행
```
/run-gate G3 1
```

---

## 8. 일상 워크플로우

### 작업 시작 매번
터미널에서:
```bash
cd ~/Documents/내소설들/내첫소설
claude
```

작업 이어쓰기:
```
/resume
```

→ 어디까지 했는지 정리.

### 자주 쓰는 커맨드

| 상황 | 커맨드 |
|------|-------|
| 다음 챕터 집필 | `/write-chapter 2` |
| 이어서 쓰기 | `/continue-writing` |
| 중단 후 재개 | `/resume` |
| 챕터 N 끝 상태 조회 | `/state 5` |
| 사건 검색 | `/timeline` / `/timeline 김도현` |
| 미회수 떡밥 | `/timeline --unresolved` |
| 독창성 단독 체크 | `/perplexity 5` |
| 독창성 임계값 자동 튜닝 | `/perplexity --calibrate` (—write 로 적용) |
| 전체 Gate 재주행 | `/revise-loop 5` |
| 지표 대시보드 | `/metrics` / `/metrics --project 40` |
| 비용 추정 | `/metrics --cost --model sonnet` |
| **원고 통합·내보내기** | `/export` (md) / `/export --format epub` |
| **편집자에 전달** | `/export --format docx --include-meta` |
| **공모전 제출용 PDF** | `/export --format pdf --strip-comments` |
| **시각화 산출물** | `/visualize` (mermaid 관계도·SP 추적·timeline HTML) |
| Bible 수정 | `/bible-unlock <사유>` → 수정 → `/bible-lock` |
| 사용 가능 명령 보기 | `/help` |

---

## 9. 퇴고 (챕터 전체 확정 후)

```
챕터 1~10 전체 퇴고해줘.
```

- **Revision Editor** — 구조·페이싱·감정 곡선·정보 분배
- **Proofreader** — 한국어 어문규정·맞춤법·띄어쓰기

각각 `.work/reviews/chNN-iterX/revision.md`, `proofread.md` 에 리포트.

---

## 9.1 출판·공유 (퇴고 후)

```
/export
```

→ `build/manuscript-YYYY-MM-DD.md` 에 챕터 1~N 통합본 생성. 옵션:

```
/export --format epub                       # 전자책 (pandoc 필요)
/export --format pdf --strip-comments       # PDF 출판용 (HTML 주석 제거)
/export --format docx --include-meta        # 편집자 제출 (시놉시스·plan 포함)
/export --range 1-5                         # 1~5장만
```

`pandoc` 설치: `brew install pandoc`. PDF 한국어는 추가로 `brew install --cask mactex` 필요.

## 9.2 시각화

```
/visualize
```

→ `build/visualizations/` 에 다음 생성:
- `relationships-chNN.md` — 챕터별 인물 관계 mermaid 그래프
- `sp-tracking.md` — 서브플롯 진행 추적
- `characters.md` — 인물별 등장·지식 누적 표
- `timeline.html` — 사건 연대기 정적 HTML

mermaid 파일은 GitHub 에서 자동 렌더링됩니다. HTML 은 브라우저로 열기:
```bash
open build/visualizations/timeline.html
```

---

## 10. 자주 막히는 지점

### "Claude 가 영어로 답해요"
한 줄 추가:
```
한국어로 답해줘.
```

### "정보 누수 (G2) FAIL 이 자꾸 나요"
가장 흔한 원인: 캐릭터가 본인이 모를 시점에 무언가를 안 것처럼 암시. `bible/characters/<id>.md` 의 **"알 수 없는 것"** 목록을 다시 보세요. 그 목록이 없다면 먼저 채워야 합니다.

### "Style Linter (G1) 가 너무 엄격해요"
`bible/style-rules.json` 의 임계값 조정. 또는 해당 장면에 `<!-- scene: lyrical -->` / `<!-- scene: action -->` 태그 부여 → `scene_overrides` 임계값 적용.

### "세계관 위반 (G3) FAIL"
챕터에 시대 오류·공간 모순. `bible/universe/historical-facts.md` 와 충돌하는 부분 수정. 또는 `rules.md` 가 너무 엄격하면 완화.

### "Perplexity (G4) 플래그가 너무 많아요/적어요"
**자동 캘리브레이션**:
```
/perplexity --calibrate
```
누적 리포트를 분석해 작가 작품에 맞는 권장 임계값을 제시. `--write` 추가하면 `bible/style-rules.json` 에 자동 반영 (Bible LOCKED 면 먼저 unlock).

수동 조정:
선택적 Gate 라 FAIL 은 안 납니다. 단, 수용률 20~50% 를 벗어나면 `perplexity-analyzer.md` 의 임계값 조정.

### "Claude 가 너무 많이 물어봐요"
```
빠른 드래프트 모드로.
```
또는:
```
소크라테스 건너뛰어. 그냥 옵션 3개 줘.
```

### "지금 어떤 상태인지 모르겠어요"
```
/resume
```
또는:
```
지금까지 우리 뭐 했지? 정리해줘.
```

### "캐릭터 이름을 바꾸고 싶어요"
이미 챕터를 몇 개 썼다면 Bible 이 잠겨 있습니다.
```
/bible-unlock "주인공 이름을 김도현에서 박진우로 변경"
```
→ Continuity Reviewer 가 자동으로 모든 챕터·timeline·state 에서 영향받는 부분을 찾아 보여줍니다. 수정 끝나면:
```
/bible-lock
```

### "이전에 쓴 챕터를 다시 보려면?"
폴더에서 직접 `~/Documents/내소설들/내첫소설/story/chapters/chapter-01.md` 를 텍스트 편집기로 열거나, Claude 에게:
```
챕터 3 본문 보여줘.
```

### "Claude 를 끄면 작업이 사라지나요?"
**아니요.** 모든 파일이 폴더에 저장됩니다. 다음에 같은 폴더에서 `claude` 다시 실행 → `/resume` 하면 계속됩니다.

### "다른 컴퓨터에서도 작업하려면?"
폴더 자체를 클라우드 (iCloud Drive·Dropbox·Google Drive) 에 두거나, GitHub 같은 곳에 올려두면 됩니다. 필요하면 Claude 에게:
```
이 폴더 GitHub 에 올려줘.
```

### "state YAML 문법 오류"
직접 검증:
```
검증 스크립트 실행해줘.
```
또는 터미널에서:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_state.py
```

자주 발생하는 함정:
- 값이 `**` 로 시작 → 따옴표로 감싸기 (YAML alias 로 오인됨)
- 값 안에 `"` 포함 → 전체를 `'` 로 감싸기

---

## 11. 안전 장치 — 실수해도 돌이킬 수 있어요

### 자동 보호
1. **모든 파일은 디스크에 저장** — Claude 가 갑자기 종료돼도 사라지지 않음
2. **Bible 잠금** — 집필 중 실수로 설정 변경 차단
3. **Timeline 추가만 가능** — 과거 사건을 실수로 지우지 않음
4. **드래프트 / 확정본 분리** — 검수 실패한 글은 `.work/` 에. 확정본 (`story/chapters/`) 은 안전

### Time Machine 권장
Mac 의 **Time Machine** 백업을 켜두시면 더 안전합니다. (시스템 환경설정 → 일반 → Time Machine)

### 중요 시점에 폴더 복사
챕터 5 끝났을 때처럼 중간 마일스톤마다 폴더 전체를 복사해 두면 더 안전:
```bash
cp -r ~/Documents/내소설들/내첫소설 ~/Documents/내소설들/내첫소설_백업_챕터5까지
```

---

## 12. 도움 받는 법

### Claude 에게 직접
무엇이든 한국어로 말하세요. 안 되면:
```
이게 안 돼. 어떻게 해야 해?
```
오류 메시지가 보이면 **메시지 전체를 복사해서 그냥 붙여넣고** "이거 뭐야?" 라고 물어보면 풀어 줍니다.

### 사용 가능 명령 보기
```
/help
```

### 플러그인 업데이트 받기
```
/plugin marketplace update hans-novel-tools
```

### 이 튜토리얼이 부족하면
Claude 에게:
```
사용법 가이드 더 자세히 설명해줘.
```

### 버그·개선 제안
hansanghoo@gmail.com

### 플러그인 GitHub
https://github.com/hansangho/novelai

---

## 13. 참고 — 샘플 작품

실제 8 챕터 파일럿이 `examples/shanghai-shadow/` (저장소 안) 에 있습니다. 구조 의문이 생기면 거기서 확인:
- `bible/characters/kim-dohyun.md` 의 "지식 경계" 섹션 작성 예시
- `state/chapter-03/character-states.yaml` 의 turning point 이후 상태 변화 기록
- `timeline/history.md` 의 챕터 블록 포맷
- `.work/gate-decisions.md` 의 실제 Gate 결정 이력

또한 회고 문서:
- `docs/pilot-01-retrospective.md` — 2 챕터 스모크
- `docs/pilot-02-long-form-retrospective.md` — 8 챕터 누적 검증

---

## 14. 지표 추적 (선택)

주간 retro 시 스냅샷 저장:
```
/metrics --json > .session/history/metrics/$(date +%Y-%m-%d).json
```

시간 경과에 따른 평균 재작성 횟수·Gate 통과율·Bible 수정 빈도 추이 추적 가능.

---

## 한 마디

이 도구는 **글을 대신 써주는 게 아닙니다.** 작가의 결정을 더 명확하게 만들고, 일관성 실수를 잡고, 자료 정리를 돕습니다. **이야기 자체는 작가의 것**이고, Claude 는 그 옆의 동료입니다.

처음이라 막막해도 한 챕터만 끝까지 따라 해보시면 흐름이 잡힙니다. 막힌 부분이 있으면 망설이지 말고 Claude 에게 한국어로 물어보세요.
