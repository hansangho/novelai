---
description: 파일럿 지표 — 원고/State/Timeline/Gate/SP/지식·투사·validator·비용
argument-hint: "[--json] [--chapter N] [--project N] [--cost] [--model opus|sonnet|haiku]"
allowed-tools: Bash, Read
---

# /metrics

## 실행
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py $ARGUMENTS`

## 옵션
- `--json` → 기계 판독 (`.session/history/metrics/` 저장용)
- `--chapter N` → 특정 챕터만
- `--project N` → N 챕터 시의 예상 크기 외삽
- `--cost` → 챕터당 비용 추정 표시
- `--model opus|sonnet|haiku` → 비용 추정 모델 (기본 sonnet)

## 활용 예
```
/metrics                                # 현재 상태
/metrics --project 40                   # 40 챕터 시 저장소 용량 추정
/metrics --chapter 7                    # 챕터 7 집중
/metrics --cost                         # 챕터당 비용 (sonnet)
/metrics --cost --model opus --project 40   # 40 챕터 opus 비용
/metrics --json > .session/history/metrics/$(date +%Y-%m-%d).json
```

## 비용 추정 주의
- 휴리스틱 (입력 ≈ Bible+State+Timeline / 출력 ≈ 챕터+Gate 리포트)
- 한국어 토큰 환산: 약 1.7 글자 = 1 토큰
- 재작성 평균 배수 자동 반영
- 실제 비용은 Anthropic 대시보드 기준 — 단가·환율 변동
