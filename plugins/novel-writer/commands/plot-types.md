---
description: 30종 플롯 아키타입 카탈로그 조회 — 전체 / 검색 / 장르별 / 결합. /plot-types [검색어] [--genre 장르] [--combine A B]
argument-hint: "[검색어 | --genre 장르 | --combine A B]"
allowed-tools: Bash, Read
---

# /plot-types

## 사용

```
/plot-types                            # 전체 30 종 한눈에
/plot-types 추리                        # "추리" 포함 아키타입 검색
/plot-types --genre 역사                # 역사 느와르의 결합 권고
/plot-types --combine 추리 비밀         # 두 아키타입 결합의 장르·함정
```

## 실행
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plot_search.py $ARGUMENTS
```

## 출력
- 작가 프로젝트의 `bible/plot-archetypes.md` 가 있으면 우선 참조 (작가 본인 보강 반영)
- 없으면 플러그인 템플릿의 카탈로그
- 풀 카탈로그(30 종 + 빈출 함정 포함) 는 플러그인 저장소의 `docs/PLOT-ARCHETYPES.md`

## 활용 예
- 구조 설계 시작 시: `/plot-types` 로 30 종 훑기
- 작가 묘사한 작품의 후보 찾기: `/plot-types 잃었다` (복수 매칭)
- 장르 튜닝: `/plot-types --genre 미스터리` (메인·보조 추천)
- 메인+보조 비교: `/plot-types --combine 추리 비밀` (결합 권고 + 빈출 함정)

## 30 종 목록
어른-어린아이 / 변모 / 라이벌 / 체인지 / 추리 / 유혹 / 동물 / 추구 / 희생자 / 성장 / 촉매 / 복수 / 발견 / 추적 / 플랫폼 / 아이러니 1·2 / 비밀 / 괴물 극복 / 거지에서 부자로 / 여정과 귀환 / 비극 / 재생 / 로맨스 / 사기 / 생존 / 광기·붕괴 / 통과의례 / 가족 비밀 / 운명 거역
