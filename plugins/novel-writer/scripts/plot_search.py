#!/usr/bin/env python3
"""
Plot Archetype Search — bible/plot-archetypes.md 또는 풀 카탈로그에서 검색·조회.

사용:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plot_search.py
      → 전체 30 종 한 줄 요약 출력 (한눈에 보기 표)

  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plot_search.py 추리
      → "추리" 가 포함된 항목 (이름·요약·결합·함정) 표시

  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plot_search.py --genre 역사
      → 결합 가이드에서 "역사 느와르" 행의 메인·보조 추천

  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plot_search.py --combine 추리 비밀
      → 두 아키타입 결합의 권고 (장르 매핑·빈출 함정 종합)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent).resolve()
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()

# 작가 프로젝트의 간소 카탈로그 우선, 없으면 플러그인 풀 카탈로그
LOCAL_CATALOG = PROJECT / "bible" / "plot-archetypes.md"
PLUGIN_CATALOG = PLUGIN_ROOT / "templates" / "bible" / "plot-archetypes.md"
FULL_CATALOG = PLUGIN_ROOT.parent.parent / "docs" / "PLOT-ARCHETYPES.md"


def find_catalog() -> Path:
    for p in (LOCAL_CATALOG, PLUGIN_CATALOG, FULL_CATALOG):
        if p.exists():
            return p
    return PLUGIN_CATALOG  # fallback


def read_catalog() -> str:
    return find_catalog().read_text(encoding="utf-8")


def cmd_overview() -> None:
    """한눈에 보기 표 출력."""
    text = read_catalog()
    m = re.search(r"## 한눈에 보기\s*\n+(\|.*?)(?=\n##\s|\Z)", text, re.S)
    if m:
        print(m.group(1).strip())
    else:
        print("[plot-search] '한눈에 보기' 표 못 찾음")


def cmd_search(query: str) -> None:
    """이름 또는 본문에 query 가 포함된 항목 출력."""
    text = read_catalog()
    sections = re.split(r"^## (\d+)\.\s+", text, flags=re.M)
    matches = []
    # split 결과: [intro, "1", body1, "2", body2, ...]
    if len(sections) < 3:
        # 풀 카탈로그가 아니라 간소 버전 — 표 형식. 다른 검색.
        for line in text.splitlines():
            if query in line and "|" in line:
                print(line)
        return
    for i in range(1, len(sections), 2):
        idx = sections[i]
        body = sections[i + 1]
        title_line = body.splitlines()[0] if body else ""
        if query in title_line or query in body:
            matches.append((idx, body))
    if not matches:
        print(f"[plot-search] '{query}' 매치 없음")
        return
    for idx, body in matches[:5]:
        # 첫 30 줄 정도만
        lines = body.splitlines()
        snippet = "\n".join(lines[:30])
        print(f"## {idx}. {snippet}")
        print()


def cmd_genre(genre: str) -> None:
    text = read_catalog()
    m = re.search(r"## 결합 가이드\s*\n+(.*?)(?=\n## |\Z)", text, re.S)
    if not m:
        print("[plot-search] 결합 가이드 표 못 찾음"); return
    table = m.group(1)
    found = False
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        if genre in line.split("|")[1]:
            print(line)
            found = True
    if not found:
        print(f"[plot-search] 장르 '{genre}' 매치 없음. 사용 가능 장르 (표 첫 컬럼) 확인.")


def cmd_combine(a: str, b: str) -> None:
    text = read_catalog()
    print(f"## 결합 권고: {a} + {b}")
    print()

    # 결합 가이드 표에서 두 키워드가 함께 등장하는 행
    m = re.search(r"## 결합 가이드\s*\n+(.*?)(?=\n## |\Z)", text, re.S)
    if m:
        print("### 결합 가이드 표에서 둘 다 등장하는 장르")
        for line in m.group(1).splitlines():
            if line.startswith("|") and a in line and b in line:
                print(f"  {line}")
        print()

    # 풀 카탈로그라면 각 항목의 결합 항목 읽기
    if "**결합**" in text:
        print(f"### {a} 의 권장 결합")
        sections = re.split(r"^## (\d+)\.\s+", text, flags=re.M)
        for i in range(1, len(sections), 2):
            body = sections[i + 1]
            title_line = body.splitlines()[0] if body else ""
            if a in title_line:
                m2 = re.search(r"\*\*결합\*\*[:：]\s*(.+)", body)
                if m2:
                    print(f"  {m2.group(1).strip()}")
                m3 = re.search(r"\*\*빈출 함정\*\*[:：]\s*(.+)", body)
                if m3:
                    print(f"  ⚠ {a} 빈출 함정: {m3.group(1).strip()[:200]}")
                break
        print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="검색어 (플롯 이름·키워드)")
    ap.add_argument("--genre", help="장르별 결합 가이드 조회")
    ap.add_argument("--combine", nargs=2, metavar=("A", "B"), help="두 아키타입 결합 권고")
    args = ap.parse_args()

    print(f"# 플롯 아키타입 카탈로그 ({find_catalog().relative_to(find_catalog().parent.parent if find_catalog().is_relative_to(PROJECT) else find_catalog().parent.parent.parent)})")
    print()

    if args.combine:
        cmd_combine(args.combine[0], args.combine[1])
    elif args.genre:
        cmd_genre(args.genre)
    elif args.query:
        cmd_search(args.query)
    else:
        cmd_overview()
    return 0


if __name__ == "__main__":
    sys.exit(main())
