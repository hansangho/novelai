---
description: Perplexity Gate 단독 실행. /perplexity 5 또는 /perplexity .work/writer-draft-ch05-v2.md
argument-hint: "<chapter-number | file-path>"
allowed-tools: Read, Write, Task, Bash
---

# /perplexity

입력: `$ARGUMENTS`

## 실행
1. 숫자면 `.work/writer-draft-ch{NN}-v*.md` 중 가장 최근 버전 선택.
2. 파일 경로면 그대로 사용.
3. `perplexity-analyzer` 서브에이전트 호출.
4. 결과를 `.work/reviews/chNN-iterX/perplexity-report.md` 에 기록.
5. 요약 출력: 플래그 수, 상위 5문장.
6. 작가 선택 대화:
   - 각 플래그에 대해 `수용` / `재작성` / `이 문장 통과` / `이 챕터 통과`.
   - 수용 결정이 많으면 다음 `/write-chapter` 시 Chapter Writer 에게 해당 라인 재작성 플래그 전달.

## 옵션
- 임계값 조정이 필요하면 대화형으로 작가에게 묻는다 (기본 하위 20%).
