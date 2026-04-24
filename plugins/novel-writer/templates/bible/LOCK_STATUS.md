# Bible Lock Status

**상태:** DRAFTING

집필 단계 진입 시 `/bible-lock` 커맨드로 이 파일을 `LOCKED` 로 변경한다.
플러그인 훅(`scripts/bible_guard.py`)이 이 플래그를 읽어 `bible/` 하위에 대한 Write/Edit 을 차단한다.

| 상태 | 의미 | Write 허용 에이전트 |
|------|------|----------------------|
| DRAFTING | 기획 단계 | Character Architect, Structure Architect, 작가 |
| LOCKED   | 집필 단계 | **없음** (Bible Curator = 작가가 unlock 해야 함) |
| UNLOCKED | 예외 수정 중 | 작가 + 지명된 Architect. `_changelog.md` 기록 의무 |

마지막 변경: 초기화
