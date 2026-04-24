---
description: 파일럿 지표 수집 — 원고/State/Timeline/Gate/SP/지식 성장·투사·validator 종합 리포트
argument-hint: "[--json] [--chapter N] [--project N]"
allowed-tools: Bash, Read
---

# /metrics

입력: `$ARGUMENTS` (선택 — 하위 옵션)

## 실행
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py $ARGUMENTS` 실행 후 출력을 그대로 사용자에게 전달.

## 주요 옵션
- 인자 없음 → 텍스트 전체 리포트
- `--json` → CI/트렌드 저장용 JSON
- `--chapter N` → 특정 챕터만 (filter 일부 섹션)
- `--project N` → N 챕터 시의 예상 크기 외삽

## 용도
- 집필 중간 점검 (챕터 완료 직후)
- PRD §13 성공 지표 추적
- 장편 누적 비대 조기 경보 (현재 대비 40/60 챕터 추정)
- `.session/history/` 에 스냅샷 저장 시 `--json` 로

## 활용 예
```
/metrics                   # 지금 현재 상태
/metrics --project 40      # 40 챕터 시 저장소 용량 추정
/metrics --chapter 7       # 챕터 7 만 집중
```

## 자동화 힌트
주간 retro 시 `--json` 출력을 `.session/history/metrics-YYYY-MM-DD.json` 로 저장하면 추세 추적 가능.
