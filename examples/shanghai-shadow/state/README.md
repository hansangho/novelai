# state/ — 챕터별 상태 스냅샷

PRD v1.4 §2 의 **State** 영역. 각 챕터가 모든 Gate 를 통과하면 State Updater 에이전트가 `state/chapter-NN/` 디렉토리를 생성하고 `current/` 심볼릭 링크를 갱신한다.

## 파일 목록
- `character-states.yaml` — 캐릭터 물리/감정/지식 상태
- `locations-state.yaml`  — 장소 상태
- `relationships.yaml`    — 인물 간 관계 스냅샷
- `open-threads.yaml`     — 미해결 서브플롯

## 규칙
- State 는 **불변이 아니다.** 챕터가 끝날 때마다 새 디렉토리가 쌓인다.
- `current/` 는 가장 최근 챕터 디렉토리로 향하는 symlink.
- 다음 챕터의 Writer·Reviewer 는 `current/` 만 기본 참조한다.
- 과거 챕터 상태를 보려면 `state/chapter-N/` 를 직접 지정한다.

## 생성 방법
1. 챕터가 Gate G5 를 통과하고 작가 승인까지 끝난다.
2. State Updater 가 `state/template/` 을 복사해 `state/chapter-NN/` 을 만든다.
3. 확정 원고를 읽어 변동 사항을 채운다.
4. `ln -sfn chapter-NN state/current` 로 심볼릭 링크 갱신.
5. `timeline/history.md` 에 append.
