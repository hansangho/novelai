# Bible Changelog

> 집필 단계 진입 후에도 Bible을 수정해야 했을 때만 기록한다 (PRD v1.4 §10.3).
> 형식:
>
> ```
> ## YYYY-MM-DD
> ### 변경: <파일 경로>
> - 필드:
> - 이전:
> - 변경:
> - 사유:
> - 작업자:
> - 영향 챕터:
> - 재검증:
> ```

(비어 있음)

## 2026-04-24
### unlock 사유: Phase 9 파일럿 — 조연 캐릭터·상하이 장소 Bible 확장
- 변경된 파일:
  - `bible/characters/park-bujang.md` (신규)
  - `bible/characters/kim-sumin.md` (신규)
  - `bible/universe/locations/shanghai-concession.md` (신규)
  - `bible/characters/_index.md` (조연 엔트리 "미작성" → 파일 경로)
- 이전: _index 에 placeholder 만 존재, 인물·장소 파일 미작성
- 변경: 챕터 3~10 집필에 필요한 인물 2인 + 장소 1곳 Bible 추가
- 사유: 챕터 3 이후 본격 등장. 챕터 3 Continuity Reviewer 검증에 park-bujang Bible 필요
- 작업자: Structure Architect + 작가
- 영향 챕터: 1, 2 (박 부장·수민 기존 언급 재검증 필요)
- 재검증: 기존 ch1·ch2 본문은 park-bujang / kim-sumin Bible 신설 내용과 충돌 없음 (화법·관계·사건 날짜 전부 일치). 추가 Gate 재실행 불필요.
