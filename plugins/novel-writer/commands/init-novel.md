---
description: 새 소설 프로젝트에 novel-writer 스캐폴딩을 설치한다. Bible·State·Timeline·Story·Work·Session·CLAUDE.md 템플릿 복사.
allowed-tools: Bash, Read
---

# /init-novel

## 실행
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_novel.py
```

## 수행
- `${CLAUDE_PROJECT_DIR}` 에 `bible/`, `state/`, `timeline/`, `story/`, `research/`, `.work/`, `.session/`, `CLAUDE.md` 스캐폴딩 복사
- `.gitignore` 에 novel-writer 구역 추가 (이미 있으면 append 만)
- **기존 파일·디렉토리는 절대 덮어쓰지 않음** (중간 수정 후 재실행 안전)

## 이후 단계 안내
스크립트가 다음 단계를 출력합니다:
1. `bible/style.md`, `structure.md` 검토·수정
2. `bible/characters/` 에 인물 프로필 추가 (`_template.md` 복사해 사용)
3. `story/synopsis.md`, `plan.md` 채우기
4. 준비되면 `/bible-lock` 후 `/write-chapter 1`

## 용도
- 빈 git 저장소에서 처음 시작할 때
- 이미 집필 중인 프로젝트에 novel-writer 플러그인 적용 시 — 빠진 파일만 보충
