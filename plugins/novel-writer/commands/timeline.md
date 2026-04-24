---
description: "Timeline 조회. 옵션: (없음) 전체 / <인물> / <장소> / @chN-chM / --unresolved"
argument-hint: "[filter]"
allowed-tools: Read, Grep, Glob, Bash
---

# /timeline

입력: `$ARGUMENTS` (선택 — 필터)

## 실행 매핑 (PRD §5.4)
- **빈 인자** → `timeline/history.md` 전체를 챕터별 요약으로 출력.
- **단어 시작이 `@`** → 챕터 범위 (`@ch3-ch7`) → 해당 범위 섹션만.
- **`--unresolved`** → `state/chapter-*/open-threads.yaml` 를 aggregate 하여 아직 `closed` 가 아닌 서브플롯 목록.
- **그 외** → 검색어로 간주. `grep -n <term>` 으로 `history.md` 매칭 라인 추출 + 주변 3줄 컨텍스트. `bible/characters/_index.md` 의 id 매칭되면 해당 id 중심으로도 필터링.

## 출력
구조화된 bullet 요약. 너무 길면 "더 보기는 `/timeline @chX-chY`" 힌트.
