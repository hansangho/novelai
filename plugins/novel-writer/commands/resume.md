---
description: 중단된 세션을 복원한다. Session Manager 가 current.yaml, logs, history, decisions 를 종합해 현재 위치를 재구성.
allowed-tools: Read, Bash, Task, Glob
---

# /resume

## 실행
1. `session-manager` 서브에이전트 호출.
2. Session Manager 는 다음을 읽고 한 단락 요약:
   - `.session/current.yaml`
   - `.session/logs/YYYY-MM-DD.jsonl` (최근 2일)
   - `.session/history/` 최신
   - `.session/decisions.md` 최근 5개 엔트리
   - `.work/gate-decisions.md` 최근 엔트리
   - `state/current/*.yaml`
3. 요약 출력:
   - 현재 phase, active_chapter, gate_cursor
   - 마지막 서사 판단
   - 바로 이어서 할 수 있는 작업 1~3 제안 (예: `/continue-writing`, `/revise-loop 5`, `/bible-unlock "..."`).
4. 작가가 선택하면 해당 커맨드 실행.
