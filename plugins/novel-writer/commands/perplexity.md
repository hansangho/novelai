---
description: Perplexity Gate 단독 실행 또는 임계값 캘리브레이션. /perplexity [N | 파일 | --calibrate]
argument-hint: "<chapter-number | file-path | --calibrate [--write]>"
allowed-tools: Read, Write, Task, Bash
---

# /perplexity

## 모드

### A. 드래프트 분석 (기본)
- `/perplexity 5` — 챕터 5 의 최신 드래프트 단독 분석
- `/perplexity .work/writer-draft-ch05-v2.md` — 특정 파일 직접 분석

### B. 캘리브레이션 (작가 작품 기준 임계값 자동 튜닝)
- `/perplexity --calibrate` — 누적 perplexity-report.md 들을 분석해 권장 임계값 제시
- `/perplexity --calibrate --write` — 권장 임계값을 `bible/style-rules.json` 에 자동 반영
  (bible LOCKED 면 차단 — 먼저 `/bible-unlock`)

## 실행

**A. 드래프트 분석**
1. 숫자면 `.work/writer-draft-ch{NN}-v*.md` 중 가장 최근 버전 선택.
2. 파일 경로면 그대로 사용.
3. `perplexity-analyzer` 서브에이전트 호출.
4. 결과를 `.work/reviews/chNN-iterX/perplexity-report.md` 에 기록.
5. 요약 출력: 플래그 수, 상위 5 문장.
6. 작가 선택 대화: 각 플래그에 대해 `수용` / `재작성` / `이 문장 통과` / `이 챕터 통과`.
   수용 결정이 많으면 다음 `/write-chapter` 시 Chapter Writer 에게 해당 라인 재작성 플래그 전달.

**B. 캘리브레이션**
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perplexity_calibrate.py [--write] [--json]
```

PRD §13 목표 수용률 (20~50%) 대비 현재 분포를 평가:
- 플래그율 < 5% → 임계값 낮춤(점수 6~7) 권고
- 플래그율 > 30% → 임계값 올림(점수 8~9) 권고
- 5~30% → 적정, 현재 유지

## 옵션 A 외부 LLM 정량
환경변수 `NOVELWRITER_PERPLEXITY_API` 를 설정하면 외부 API 와 연동 (작가 직접 구현, 인터페이스만 제공).
