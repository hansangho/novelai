# 파일럿 01 회고 — *상하이의 그림자* 챕터 1

**일시:** 2026-04-24
**대상:** PRD v1.4 스캐폴딩 End-to-End 검증
**결과:** ✅ 성공 (iter 2 에서 G1~G5 통과, finalize + state/timeline 갱신 완료)

## 파일럿 설계
- 샘플 작품: 1923년 경성·상하이 역사 느와르 *상하이의 그림자*
- Bible: 김도현·이세아 캐릭터, 종로 경찰서 장소, 세계관/규칙/고증/문체/구조
- 목표: 챕터 1 초고 → Gate G1~G5 → finalize → state snapshot → timeline append
- 의도적 결함 6개를 v1 에 심어 탐지 여부를 검증

## 의도 결함과 탐지 결과 (100% 탐지)
| # | 결함 | 심은 위치 | 탐지 Gate | 수정 (v2) |
|---|------|-----------|-----------|-----------|
| 1 | AI 시작구 `^그날 아침` | L.5 | G1 error | "쇠 난간의 냉기가 먼저였다." |
| 2 | 금지어 "그러나" 2회 | L.5, L.30 | G1 warn | 두 곳 모두 제거 |
| 3 | 과부사 "매우 정말" | L.7 | G1 error / G4 플래그 | "목례" 로 전환 |
| 4 | 대사 태그 비문 "박 부장이 라고 말했다" 2회 | L.24 | G1 error | 삭제 + 짧은 침묵 |
| 5 | 정보 누수 — 도현이 딸의 의심을 이미 앎 | L.9 | **G2 FAIL (최상위)** | 모호한 "어긋난 감각" |
| 6 | 시대 오류 — 가방에서 꺼낸 전화기 | L.28 | **G3 FAIL** | 내부 유선 수화기 |

+ 부가 탐지: G5 가 plan.md 의 "예감 잠듦" 끝 상태 누락을 포착 — 마지막 문단 추가

## 정량 지표 (PRD §13 대비)
| 지표 | 파일럿 | PRD 목표 |
|------|--------|----------|
| 재작성 반복 횟수 | 1회 (iter 1 → iter 2 에 PASS) | 1~2회 |
| 일관성 오류 발견율 (의도 결함 탐지율) | 6/6 (100%) | 놓침 < 10% |
| Bible 수정 빈도 | 0 | 집필 전체에서 평균 ≤ 2 |
| Perplexity 수용률 | 0/3 (작가 재량 거절) | 20~50% |
| Gate G4 플래그 수 | v1 4건 → v2 3건 | — |

Perplexity 수용률은 목표 하한 미만이지만 파일럿 규모(48문장) 에서 유의미하지 않다. 장편 파일럿에서 재측정 필요.

## 발견한 이슈와 조치
### 블로커급 (조치 완료)
1. **`gate_runner.py next` 로직 오류** — 과거 iter 의 PASS 기록이 새 iter 를 차단.
   → 섹션 파싱 + 현재 iter 범위로 스코프 제한 + `FAIL_BLOCK` 신호 추가. `status` 서브커맨드 신설.
2. **`Write` 도구의 Read-before-write 제약** — state/chapter-NN/*.yaml 에 1차 쓰기 실패.
   → state-updater 에이전트 스펙에 "Read → Write 순서" 명시. 재시도 후 성공.

### 품질 개선 (조치 완료)
3. **Style Linter 의 HTML 주석 오탐** — Writer 의 `<!-- rewrite notes v2 -->` 블록에서 금지어 "그러나" 오탐.
   → style-linter 에이전트 스펙에 주석 블록 제외 규칙 + Python 스니펫 명시.
4. **PRD 의 strict fail-fast vs batch-feedback 효율** — 한 번에 G2/G3 도 탐지해야 1회 재작성에 모든 이슈 해결 가능.
   → CLAUDE.md / `/write-chapter` / `/revise-loop` / writing-director 모두 **Batch Feedback 모드**를 공식 채택으로 전환. PRD 의 strict 모드도 보존되며, 재작성 루프는 여전히 최대 3회.
5. **state/template/*.yaml 의 예시 데이터** — 템플릿에 김도현 예시가 남아 있어 State Updater 가 전 작품에 걸쳐 이를 상속할 위험.
   → 템플릿을 빈 매핑 (`{}` / `[]`) 으로 정리, 주석으로 스키마만 남김.

### 미결 (차후)
6. **로컬 Perplexity(옵션 A)** — 현재 옵션 B (Claude 자체 판정) 기본. GPU 사용자용 확장 경로는 마련 안 함. Phase 9 후반 검토.
7. **기계 판독 Style Linter 보조 스크립트** — 현재 Linter 는 에이전트 전용. Python 헬퍼로 빠른 pre-commit 체크를 만들면 피드백 속도 향상 가능. 우선순위 낮음.

## 아티팩트 경로
- 드래프트: `.work/writer-draft-ch01-v1.md`, `.work/writer-draft-ch01-v2.md`
- 리뷰: `.work/reviews/{style-lint, character-review, continuity-review, perplexity-report, integration}.md`
- Gate 기록: `.work/gate-decisions.md`
- 확정본: `story/chapters/chapter-01.md`
- State: `state/chapter-01/*.yaml` + `state/current → chapter-01`
- Timeline: `timeline/history.md` 챕터 1 블록
- 세션: `.session/current.yaml`, `.session/decisions.md`

## 결론
- PRD v1.4 의 Bible/State/Gate/Timeline/Work 5대 구조가 실제 작업 흐름에서 **함께 작동**한다.
- 의도 결함 탐지율 100% — Gate 설계가 과소도 과대도 아닌 적정 수준.
- 1회 재작성 만에 수렴 — PRD 목표 범위 내.
- 장편 파일럿(다수 챕터 누적 시 state 비대·timeline 비대) 은 Phase 9 후반에 별도 필요.

## 다음 단계 제안
1. ✅ **2회차 축약 파일럿 완료** — 아래 섹션 참조.
2. 정량 지표 수집 자동화 — `scripts/pilot_metrics.py` (선택).
3. 실제 작가의 장편 착수 전에 Phase 9 완료 (장편 특유의 state·timeline 비대 이슈 확인).

## 2회차 축약 파일럿 — 챕터 2 (이세아 도입)

**목적:** 1회차에서 발견한 6개 이슈 조치사항이 실제 워크플로에서 작동하는지 검증.

**드래프트:** `.work/writer-draft-ch02-v1.md` — 25 문장, 1 장면, 의도적 결함 없음.

**결과:**
- G1 PASS (기계검사 전부 통과, HTML 주석 배제 규칙 적용 — `그런데도` 는 허용으로 정확히 분류)
- G2 PASS (이세아 내면 0 공개, 도현 unaware_of 3종 준수)
- G3 PASS (state/chapter-01 의 상태 승계 정확 — 왼손 흉터·피로·감정 모티프)
- G4 WARN (플래그 2, 선택적 통과)
- G5 PASS (plan.md 모티프 승계 "예감→얼굴")
- **iter 1 수렴, 재작성 0회**

**검증된 개선 사항:**
| 조치 | 검증 |
|------|------|
| `gate_runner` next 재설계 | 챕터 1 iter 2 에서 완료된 섹션이 챕터 2 새 섹션 열기에 영향 주지 않음 ✓ |
| state/template/*.yaml 정리 | 챕터 2 state 가 빈 `{}` `[]` 로 시작, 이전 작품 예시 상속 없음 ✓ |
| State Updater Read→Write | 4개 YAML 모두 Read 후 Write 로 충돌 없이 갱신 ✓ |
| Batch Feedback 모드 | G1~G4 동시 수집 + G5 종합 → 단일 재작성으로 수렴하는 패턴 공식화 ✓ |
| Style Linter HTML 주석 배제 | `<!-- scene: ... -->` `<!-- end -->` 등이 본문 검사에 영향 없음 ✓ |

**누적 정량 지표 (2 챕터 기준):**
| 지표 | 값 | PRD §13 목표 |
|------|----|--------------|
| 평균 재작성 횟수 | 0.5회 (ch1: 1, ch2: 0) | 1~2 |
| 의도 결함 탐지율 | 6/6 (100%) | 놓침 < 10% |
| Bible 수정 빈도 | 0 | ≤ 2 |
| Gate 통과율 (iter 당) | 8/10 PASS, 2/10 WARN, 0 FAIL (iter 2 기준) | — |

**결론:** PRD v1.4 의 전 구조가 2개 챕터 연속으로 안정 작동. 장편 파일럿(10+ 챕터) 에서의 스트레스 테스트만 남김.
