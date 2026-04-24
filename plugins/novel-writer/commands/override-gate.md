---
description: 현재 챕터에 한해 Gate 강제 통과. 사유 필수. /override-gate G1 "서정 장면이라 예외"
argument-hint: "<G1..G5> <reason>"
allowed-tools: Read, Write, Bash
---

# /override-gate

입력: `$ARGUMENTS` — `<GID> <reason...>`

## 실행
1. 사유가 비면 거부 — "사유는 필수입니다 (PRD §3.5 A안)."
2. 현재 챕터 번호는 `.session/current.yaml` 의 `active_chapter`.
3. `.work/gate-decisions.md` 에 append:
   ```
   - OVERRIDE <GID> @ <iso-ts> — <reason>
   - 작가: (사용자 이름 또는 환경변수)
   ```
4. `gate_runner.py record --gate <GID> --result PASS --note "OVERRIDE: <reason>"` 실행.
5. 다음 Gate 로 자동 진행할지 작가에게 질문.

## 주의
- 남용 경고: 동일 챕터에서 override 가 2건 이상이면 "Bible 또는 plan.md 를 재검토하세요" 경고.
- `_changelog.md` 수정은 하지 않는다 (Bible 변경이 아니라 Gate 완화이므로).
