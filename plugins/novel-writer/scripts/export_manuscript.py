#!/usr/bin/env python3
"""
Export Manuscript — 확정 챕터들을 단일 원고로 통합.

기본: story/chapters/chapter-NN.md 들을 하나의 markdown 으로 합쳐
  ${CLAUDE_PROJECT_DIR}/build/manuscript-YYYY-MM-DD.md 로 출력.

옵션:
  --format {markdown|epub|pdf|docx}  (epub/pdf/docx 는 pandoc 필요)
  --range CH1-CH2                    특정 챕터 범위만
  --include-meta                     synopsis·plan 도 통합 (편집자 공유용)
  --strip-comments                   <!-- ... --> HTML 주석 제거 (출판용)

사용:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/export_manuscript.py
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/export_manuscript.py --format epub
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/export_manuscript.py --range 1-3 --strip-comments
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STORY = PROJECT / "story"
CHAPTERS = STORY / "chapters"
BUILD = PROJECT / "build"

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def parse_range(spec: str) -> range:
    if "-" in spec:
        a, b = spec.split("-", 1)
        return range(int(a), int(b) + 1)
    n = int(spec)
    return range(n, n + 1)


def collect_chapters(rng: range | None) -> list[Path]:
    paths: list[Path] = []
    for p in sorted(CHAPTERS.glob("chapter-*.md")):
        try:
            n = int(p.stem.split("-")[-1])
        except ValueError:
            continue
        if rng is None or n in rng:
            paths.append(p)
    return paths


def build_markdown(chapters: list[Path], include_meta: bool, strip_comments: bool) -> str:
    parts: list[str] = []

    # 메타 (선택)
    if include_meta:
        synopsis = STORY / "synopsis.md"
        plan = STORY / "plan.md"
        if synopsis.exists():
            parts.append("# 시놉시스\n\n" + synopsis.read_text(encoding="utf-8") + "\n")
        if plan.exists():
            parts.append("# 전체 아웃라인\n\n" + plan.read_text(encoding="utf-8") + "\n")
        parts.append("\n---\n\n# 본편\n")

    # 챕터들
    for p in chapters:
        text = p.read_text(encoding="utf-8")
        if strip_comments:
            text = HTML_COMMENT_RE.sub("", text)
        parts.append(text.rstrip() + "\n\n")

    return "".join(parts)


def write_output(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def convert_with_pandoc(md_path: Path, out_path: Path, fmt: str) -> int:
    if not shutil.which("pandoc"):
        print(f"[export] pandoc 가 설치돼 있지 않습니다. brew install pandoc 후 다시 시도하세요.", file=sys.stderr)
        return 2
    cmd = ["pandoc", str(md_path), "-o", str(out_path)]
    if fmt == "pdf":
        # PDF 는 한국어 폰트가 시스템에 있어야 함. 보통 LaTeX 엔진 필요.
        cmd += ["--pdf-engine=xelatex", "-V", "mainfont=AppleMyungjo"]
    print(f"[export] pandoc 실행: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="원고 통합·내보내기")
    ap.add_argument("--format", "-f", default="markdown",
                    choices=["markdown", "md", "epub", "pdf", "docx"])
    ap.add_argument("--range", "-r", help="챕터 범위 (예: 1-5 또는 3)")
    ap.add_argument("--include-meta", action="store_true", help="synopsis·plan 포함")
    ap.add_argument("--strip-comments", action="store_true", help="HTML 주석 제거 (출판용)")
    ap.add_argument("--out", help="출력 파일 경로 (기본: build/manuscript-YYYY-MM-DD.<ext>)")
    args = ap.parse_args()

    if not CHAPTERS.exists():
        print(f"[export] story/chapters/ 가 없습니다.", file=sys.stderr)
        return 1

    rng = parse_range(args.range) if args.range else None
    chapters = collect_chapters(rng)
    if not chapters:
        print(f"[export] 대상 챕터가 없습니다.", file=sys.stderr)
        return 1

    fmt = "markdown" if args.format in ("markdown", "md") else args.format
    today = datetime.date.today().isoformat()
    range_tag = f"-ch{rng.start:02d}-ch{rng.stop-1:02d}" if rng else ""
    ext = {"markdown": "md", "epub": "epub", "pdf": "pdf", "docx": "docx"}[fmt]

    out_path = Path(args.out) if args.out else (BUILD / f"manuscript-{today}{range_tag}.{ext}")

    md_content = build_markdown(chapters, args.include_meta, args.strip_comments)

    if fmt == "markdown":
        write_output(md_content, out_path)
        print(f"[export] {out_path.relative_to(PROJECT)}")
        print(f"  포함: {len(chapters)} 챕터, {len(md_content):,} 자")
        return 0

    # pandoc 변환은 중간 markdown 파일을 거쳐
    tmp_md = BUILD / f".tmp-export-{today}.md"
    write_output(md_content, tmp_md)
    rc = convert_with_pandoc(tmp_md, out_path, fmt)
    try:
        tmp_md.unlink()
    except OSError:
        pass
    if rc != 0:
        return rc
    print(f"[export] {out_path.relative_to(PROJECT)} 생성")
    return 0


if __name__ == "__main__":
    sys.exit(main())
