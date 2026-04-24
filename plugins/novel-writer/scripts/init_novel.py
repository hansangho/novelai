#!/usr/bin/env python3
"""
novel-writer 프로젝트 초기화.

새 소설 프로젝트에서 다음 한 번 실행:
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_novel.py

수행:
1. $CLAUDE_PROJECT_DIR 에 bible/, state/, timeline/, story/, research/, .work/, .session/ 스캐폴딩
2. CLAUDE.md (없으면) 복사
3. .gitignore 에 novel-writer 구역 추가 (이미 있으면 건너뜀)
4. 기존 디렉토리·파일은 보존 (덮어쓰기 안 함)
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent).resolve()
TEMPLATES = PLUGIN_ROOT / "templates"
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()

GITIGNORE_MARKER = "# --- novel-writer 플러그인 ---"


def copy_if_absent(src: Path, dst: Path) -> tuple[int, int]:
    """재귀 복사 — 이미 존재하는 파일은 건너뜀. (created, skipped) 반환."""
    created = skipped = 0
    if src.is_file():
        if dst.exists():
            return (0, 1)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return (1, 0)
    for entry in src.iterdir():
        sub_dst = dst / entry.name
        c, s = copy_if_absent(entry, sub_dst)
        created += c
        skipped += s
    return (created, skipped)


def ensure_gitignore() -> str:
    gitignore = PROJECT / ".gitignore"
    template = (TEMPLATES / "gitignore.template").read_text(encoding="utf-8")
    if not gitignore.exists():
        gitignore.write_text(template, encoding="utf-8")
        return "gitignore 생성"
    existing = gitignore.read_text(encoding="utf-8")
    if GITIGNORE_MARKER in existing:
        return "gitignore 이미 설정됨"
    gitignore.write_text(existing.rstrip() + "\n\n" + template, encoding="utf-8")
    return "gitignore 에 novel-writer 구역 append"


def main() -> int:
    if not TEMPLATES.exists():
        print(f"[init-novel] 템플릿 디렉토리 없음: {TEMPLATES}", file=sys.stderr)
        return 1
    if not PROJECT.exists():
        print(f"[init-novel] 프로젝트 디렉토리 없음: {PROJECT}", file=sys.stderr)
        return 1

    print(f"[init-novel] 플러그인: {PLUGIN_ROOT}")
    print(f"[init-novel] 대상:   {PROJECT}")

    total_created = total_skipped = 0
    for entry in sorted(TEMPLATES.iterdir()):
        if entry.name == "gitignore.template":
            continue
        target = PROJECT / entry.name
        c, s = copy_if_absent(entry, target)
        total_created += c
        total_skipped += s
        note = f"신규 {c}" if c else "유지"
        if s:
            note += f", 기존 유지 {s}"
        print(f"  {entry.name}: {note}")

    # state/template/ 은 필수 (state_snapshot.py 가 읽음)
    state_template = PROJECT / "state" / "template"
    if not state_template.exists():
        print(f"  ⚠ state/template/ 없음 — 복사 실패 확인 필요", file=sys.stderr)

    gi = ensure_gitignore()
    print(f"  .gitignore: {gi}")

    print()
    print(f"[init-novel] 완료. 신규 {total_created} / 유지 {total_skipped}")
    print(f"[init-novel] 다음 단계:")
    print(f"  1. bible/style.md, structure.md 등 기본 파일 검토·수정")
    print(f"  2. bible/characters/ 에 인물 프로필 추가 (template 복사)")
    print(f"  3. story/synopsis.md, plan.md 채우기")
    print(f"  4. 준비되면 `/bible-lock` 후 `/write-chapter 1`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
