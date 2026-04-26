#!/usr/bin/env python3
"""
novel-writer 프로젝트 초기화.

사용:
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_novel.py [장르]

지원 장르 (선택, 미지정시 generic 템플릿만):
    historic-noir   — 1900~1950 시대극 + 누아르
    urban-fantasy   — 현대 한국 + 초자연
    web-novel       — 웹소설 (회귀·헌터·로판)
    sf              — 하드 SF·스페이스 오페라

수행:
1. $CLAUDE_PROJECT_DIR 에 generic 스캐폴딩 복사 (templates/ 하위, genres/ 제외)
2. 장르가 지정되면 templates/genres/<장르>/ 의 파일을 generic 위에 덮어쓰기
3. CLAUDE.md, .gitignore 등 추가
4. 기존 파일은 보존 — 단, 장르 파일은 generic 을 덮어쓸 수 있음 (장르 우선)
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent).resolve()
TEMPLATES = PLUGIN_ROOT / "templates"
GENRES = TEMPLATES / "genres"
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()

GITIGNORE_MARKER = "# --- novel-writer 플러그인 ---"


def copy_if_absent(src: Path, dst: Path) -> tuple[int, int]:
    """재귀 복사 — 이미 존재하는 파일은 건너뜀."""
    created = skipped = 0
    if src.is_file():
        if dst.exists():
            return (0, 1)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return (1, 0)
    for entry in src.iterdir():
        c, s = copy_if_absent(entry, dst / entry.name)
        created += c
        skipped += s
    return (created, skipped)


def copy_overwrite(src: Path, dst: Path) -> int:
    """장르 프리셋용 — generic 을 덮어쓰기 (단 README 같은 메타는 건너뜀)."""
    overwritten = 0
    if src.is_file():
        if src.name == "README.md":
            return 0
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return 1
    for entry in src.iterdir():
        if entry.name == "README.md":
            continue
        # 장르 디렉토리 내 파일은 bible/ 아래로 매핑
        # genres/historic-noir/style-rules.json → bible/style-rules.json
        # genres/historic-noir/structure.md     → bible/structure.md
        # genres/historic-noir/characters/_template.md → bible/characters/_template.md
        target = dst / entry.name
        overwritten += copy_overwrite(entry, target)
    return overwritten


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


def list_genres() -> list[str]:
    if not GENRES.exists():
        return []
    return sorted(p.name for p in GENRES.iterdir() if p.is_dir())


def main() -> int:
    ap = argparse.ArgumentParser(description="novel-writer 프로젝트 초기화")
    ap.add_argument("genre", nargs="?", help=f"장르 (선택). 가능: {', '.join(list_genres())}")
    args = ap.parse_args()

    if not TEMPLATES.exists():
        print(f"[init-novel] 템플릿 디렉토리 없음: {TEMPLATES}", file=sys.stderr)
        return 1
    if not PROJECT.exists():
        print(f"[init-novel] 프로젝트 디렉토리 없음: {PROJECT}", file=sys.stderr)
        return 1

    print(f"[init-novel] 플러그인: {PLUGIN_ROOT}")
    print(f"[init-novel] 대상:   {PROJECT}")
    if args.genre:
        if args.genre not in list_genres():
            print(f"[init-novel] 알 수 없는 장르: {args.genre}", file=sys.stderr)
            print(f"  사용 가능: {', '.join(list_genres())}", file=sys.stderr)
            return 1
        print(f"[init-novel] 장르 프리셋: {args.genre}")

    # 1. Generic 스캐폴딩 (templates/ 하위, genres/ 제외)
    total_created = total_skipped = 0
    for entry in sorted(TEMPLATES.iterdir()):
        if entry.name in ("gitignore.template", "genres"):
            continue
        target = PROJECT / entry.name
        c, s = copy_if_absent(entry, target)
        total_created += c
        total_skipped += s
        note = f"신규 {c}" if c else "유지"
        if s:
            note += f", 기존 유지 {s}"
        print(f"  {entry.name}: {note}")

    # 2. 장르 프리셋 (옵션) — bible/ 위에 덮어쓰기
    overwritten = 0
    if args.genre:
        genre_dir = GENRES / args.genre
        bible_dir = PROJECT / "bible"
        # 장르 디렉토리의 파일들을 bible/ 로 매핑하며 복사 (덮어쓰기)
        for entry in genre_dir.iterdir():
            if entry.name == "README.md":
                continue
            target = bible_dir / entry.name
            n = copy_overwrite(entry, target)
            overwritten += n
            print(f"  bible/{entry.name}: 장르 적용 ({n})")

    # 3. state/template/ 검증
    state_template = PROJECT / "state" / "template"
    if not state_template.exists():
        print(f"  ⚠ state/template/ 없음 — 복사 실패 확인 필요", file=sys.stderr)

    # 4. .gitignore
    gi = ensure_gitignore()
    print(f"  .gitignore: {gi}")

    print()
    print(f"[init-novel] 완료. 신규 {total_created} / 유지 {total_skipped} / 장르 덮어쓰기 {overwritten}")
    print(f"[init-novel] 다음 단계:")
    print(f"  1. bible/style.md, structure.md 등 기본 파일 검토·수정")
    print(f"  2. bible/characters/ 에 인물 프로필 추가 (template 복사)")
    print(f"  3. story/synopsis.md, plan.md 채우기")
    print(f"  4. 준비되면 `/bible-lock` 후 `/write-chapter 1`")
    if args.genre:
        print()
        print(f"[init-novel] 장르 가이드: {GENRES / args.genre / 'README.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
