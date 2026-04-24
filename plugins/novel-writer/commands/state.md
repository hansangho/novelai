---
description: 특정 챕터 말 상태 조회. /state 5 (없으면 current)
argument-hint: "[chapter-number]"
allowed-tools: Read, Bash, Glob
---

# /state

입력: `$ARGUMENTS` (선택 — 챕터 번호)

## 실행
1. 인자 없으면 `state/current/` symlink 사용.
2. `state/chapter-{NN}/*.yaml` 4개 파일 읽어 구조화 출력.
3. 이전 챕터와의 diff 요약 (옵션) — 주요 변화 3~5개.

## 출력
```
# 챕터 5 상태 (2026-04-23 18:30)

## 인물
- kim-dohyun @ 종로 경찰서 / 피로 high / 왼손 타박상 유지
- lee-seah @ 같은 위치 / 의심 단계 2

## 관계
- kim↔lee 신뢰 3→4, 친밀 3

## 장소
- 종로 경찰서: 평시 운영

## 미해결 서브플롯
- SP-A: 박 부장의 목적 (5장까지 단서 2)
- SP-C: 딸 수민의 의심 (신규 open)
```
