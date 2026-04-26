---
description: 확정 챕터들을 단일 원고로 통합·내보내기. /export [--format markdown|epub|pdf|docx] [--range 1-5] [--include-meta] [--strip-comments]
argument-hint: "[--format markdown|epub|pdf|docx] [--range A-B] [--include-meta] [--strip-comments]"
allowed-tools: Bash, Read
---

# /export

확정된 `story/chapters/chapter-NN.md` 들을 단일 원고로 합칩니다.

## 실행
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/export_manuscript.py $ARGUMENTS
```

## 옵션
| 옵션 | 용도 |
|------|------|
| `--format markdown` (기본) | 단일 .md 파일 |
| `--format epub` | 전자책 — pandoc 필요 (`brew install pandoc`) |
| `--format pdf` | PDF — pandoc + xelatex (한국어 폰트 mainfont 옵션 자동) |
| `--format docx` | Word 문서 |
| `--range 1-5` | 특정 챕터 범위만 |
| `--include-meta` | synopsis·plan 도 첫 페이지에 포함 (편집자 공유용) |
| `--strip-comments` | `<!-- scene: ... -->` 같은 HTML 주석 제거 (출판용) |
| `--out 경로` | 출력 파일 경로 직접 지정 |

## 출력 위치
`${CLAUDE_PROJECT_DIR}/build/manuscript-YYYY-MM-DD.<확장자>` (기본).

## 활용
- **편집자 공유**: `/export --format docx --include-meta`
- **공모전 제출**: `/export --format pdf --strip-comments`
- **백업**: `/export --range 1-10 --strip-comments`
- **부분 공유**: `/export --range 5 --format epub`

## 주의
- pandoc 미설치 시 markdown 만 가능. epub/pdf/docx 는 pandoc 설치 후.
- PDF 한국어는 시스템에 한국어 지원 LaTeX 엔진 필요 (macOS: `brew install --cask mactex`).
