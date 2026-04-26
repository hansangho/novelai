---
description: state·timeline 시각화 — 인물 관계 mermaid, SP 추적, timeline HTML, 인물 지식 추이
argument-hint: "[--chapter N]"
allowed-tools: Bash, Read
---

# /visualize

## 실행
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/visualize.py $ARGUMENTS
```

## 산출물 (`${CLAUDE_PROJECT_DIR}/build/visualizations/`)

| 파일 | 내용 |
|------|------|
| `relationships-chNN.md` | 챕터별 인물 관계 mermaid 그래프 (trust/intimacy 라벨) |
| `sp-tracking.md` | 서브플롯별 챕터간 status 추이 (mermaid gantt 포함) |
| `characters.md` | 인물별 등장·지식 누적 표 (aware_of / unaware_of 카운트) |
| `timeline.html` | 사건 연대기 정적 HTML (브라우저로 열어 확인) |

## 옵션
- 인자 없음 → 전 챕터 + 통합 산출물
- `--chapter N` → 특정 챕터의 관계도만

## 보기
- mermaid `.md` 파일은 GitHub 에서 자동 렌더링.
- VS Code 의 mermaid 미리보기 확장 사용.
- `timeline.html` 은 `open build/visualizations/timeline.html` (macOS) 으로 브라우저에서.

## 활용
- 작가 본인 — 작품 구조 한눈에 점검
- 편집자·스튜디오 공유 — 인물 관계·서브플롯 진척 시각화
