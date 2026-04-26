#!/usr/bin/env python3
"""
문서·메타데이터 일관성 검사기.

이 도구는 플러그인 본체에 포함되지 **않는** 개발자 전용 검사 도구다 (tools/).
릴리스마다 다음 8 항목을 자동 검사해 누락·불일치를 잡는다:

1. 커맨드 동기화      — plugins/novel-writer/commands/*.md 의 모든 슬래시 커맨드가
                       README × 2 + TUTORIAL + templates/CLAUDE 4 곳에 언급되는지
2. 에이전트 동기화    — plugins/novel-writer/agents/*.md 의 에이전트가 README 2개에 언급되는지
3. 버전 일치         — marketplace.json 의 plugin version 과 plugin.json 의 version 일치
4. 스크립트 동기화    — plugins/novel-writer/scripts/*.{py,sh} 가 루트 README 트리에 등장하는지
5. 하드코딩 경로      — templates/ 안에 /Users/, /home/ 같은 절대 경로 없는지
6. JSON 유효성       — marketplace.json, plugin.json, hooks.json, style-rules.json 모두 파싱 OK
7. 죽은 링크         — docs/ 와 README 들의 상대 경로 markdown 링크가 실제 존재하는지
8. 카운트 표기       — README 의 "16 슬래시 커맨드", "21 서브에이전트" 가 실제 개수와 일치

사용:
  python3 tools/check_docs.py             — 사람이 읽는 리포트
  python3 tools/check_docs.py --strict    — WARN 도 exit 1 (CI 용)
  python3 tools/check_docs.py --json      — 기계 판독
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "novel-writer"
COMMANDS_DIR = PLUGIN / "commands"
AGENTS_DIR = PLUGIN / "agents"
SCRIPTS_DIR = PLUGIN / "scripts"
TEMPLATES_DIR = PLUGIN / "templates"

DOC_TARGETS = [
    REPO / "README.md",
    PLUGIN / "README.md",
    REPO / "docs" / "TUTORIAL.md",
    TEMPLATES_DIR / "CLAUDE.md",
]


def collect_commands() -> list[str]:
    """commands/*.md 파일명에서 / 접두사 붙여 커맨드명 리스트."""
    if not COMMANDS_DIR.exists():
        return []
    return sorted(f"/{p.stem}" for p in COMMANDS_DIR.glob("*.md"))


def collect_agents() -> list[str]:
    """agents/*.md frontmatter 에서 name 필드 추출."""
    if not AGENTS_DIR.exists():
        return []
    names = []
    for p in AGENTS_DIR.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)^---\n", text, re.S | re.M)
        if not m:
            continue
        name_m = re.search(r"^name:\s*(\S+)", m.group(1), re.M)
        if name_m:
            names.append(name_m.group(1))
    return sorted(names)


def collect_scripts() -> list[str]:
    if not SCRIPTS_DIR.exists():
        return []
    return sorted(p.name for p in SCRIPTS_DIR.iterdir() if p.is_file() and not p.name.startswith("."))


# ---------- 검사 ----------

def check_commands_in_docs() -> list[dict]:
    """각 커맨드가 모든 핵심 문서에 적어도 한 번 언급되는지."""
    issues = []
    commands = collect_commands()
    for doc in DOC_TARGETS:
        if not doc.exists():
            issues.append({"level": "ERROR", "category": "doc-missing",
                           "msg": f"{doc.relative_to(REPO)} 파일 없음"})
            continue
        text = doc.read_text(encoding="utf-8")
        for cmd in commands:
            # cmd 그대로 (예: /export) 등장하는지 — 인자·코드블럭에 들어가도 매치
            if cmd not in text:
                issues.append({
                    "level": "WARN",
                    "category": "command-missing-from-doc",
                    "msg": f"{doc.relative_to(REPO)} 에 {cmd} 언급 없음",
                })
    return issues


def check_agents_in_docs() -> list[dict]:
    """루트 README 와 plugin README 에 에이전트가 그룹/개별로 언급되는지."""
    issues = []
    agents = collect_agents()
    for doc in [REPO / "README.md", PLUGIN / "README.md"]:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        # 에이전트 카테고리 키워드 또는 개별 이름 적어도 절반 이상 나오면 OK
        # (모든 21명을 매번 명시할 필요 없음 — 그룹 단위면 충분)
        named = sum(1 for a in agents if a in text)
        if named < len(agents) * 0.4:
            issues.append({
                "level": "WARN",
                "category": "agents-underdocumented",
                "msg": f"{doc.relative_to(REPO)} 에 명시된 에이전트 {named}/{len(agents)} — "
                       f"40% 미만. 그룹 단위로라도 언급 필요.",
            })
    return issues


def check_version_alignment() -> list[dict]:
    issues = []
    mp = REPO / ".claude-plugin" / "marketplace.json"
    pp = PLUGIN / ".claude-plugin" / "plugin.json"
    if not mp.exists() or not pp.exists():
        issues.append({"level": "ERROR", "category": "json-missing",
                       "msg": "marketplace.json 또는 plugin.json 없음"})
        return issues
    try:
        mp_data = json.loads(mp.read_text(encoding="utf-8"))
        pp_data = json.loads(pp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        issues.append({"level": "ERROR", "category": "json-syntax", "msg": f"JSON 파싱: {e}"})
        return issues

    pp_version = pp_data.get("version")
    plugins = mp_data.get("plugins") or []
    for entry in plugins:
        if entry.get("name") == pp_data.get("name"):
            mp_version = entry.get("version")
            if mp_version != pp_version:
                issues.append({
                    "level": "ERROR",
                    "category": "version-mismatch",
                    "msg": f"marketplace.json 의 {entry['name']} version={mp_version} "
                           f"vs plugin.json version={pp_version}",
                })
    return issues


def check_scripts_in_readme() -> list[dict]:
    """루트 README 트리에 모든 스크립트가 등장하는지."""
    issues = []
    scripts = [s for s in collect_scripts()
               if s.endswith((".py", ".sh")) and not s.endswith(".pyc")]
    readme = REPO / "README.md"
    if not readme.exists():
        return issues
    text = readme.read_text(encoding="utf-8")
    for s in scripts:
        if s not in text:
            issues.append({
                "level": "WARN",
                "category": "script-missing-from-readme",
                "msg": f"README.md 의 레포 구조 트리에 {s} 등장 안 함",
            })
    return issues


def check_hardcoded_paths() -> list[dict]:
    issues = []
    if not TEMPLATES_DIR.exists():
        return issues
    bad_patterns = [
        (re.compile(r"/Users/[a-zA-Z]+"), "macOS 사용자 절대 경로"),
        (re.compile(r"/home/[a-zA-Z]+"), "Linux 사용자 절대 경로"),
        (re.compile(r"C:\\\\Users\\\\"), "Windows 사용자 절대 경로"),
    ]
    for p in TEMPLATES_DIR.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in (".md", ".json", ".yaml", ".sh", ".py", ".txt"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pat, desc in bad_patterns:
            for m in pat.finditer(text):
                issues.append({
                    "level": "ERROR",
                    "category": "hardcoded-path",
                    "msg": f"{p.relative_to(REPO)} 에 {desc}: {m.group()!r}",
                })
    return issues


def check_json_validity() -> list[dict]:
    issues = []
    targets = [
        REPO / ".claude-plugin" / "marketplace.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
        PLUGIN / "hooks" / "hooks.json",
        TEMPLATES_DIR / "bible" / "style-rules.json",
    ]
    # 장르 프리셋 style-rules.json 도 추가
    genres_dir = TEMPLATES_DIR / "genres"
    if genres_dir.exists():
        targets.extend(genres_dir.rglob("style-rules.json"))
    for p in targets:
        if not p.exists():
            issues.append({"level": "WARN", "category": "json-missing",
                           "msg": f"{p.relative_to(REPO) if REPO in p.parents else p} 없음"})
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append({
                "level": "ERROR",
                "category": "json-syntax",
                "msg": f"{p.relative_to(REPO)} JSON 파싱 실패: {e}",
            })
    return issues


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def check_dead_links() -> list[dict]:
    issues = []
    docs_to_scan = [
        REPO / "README.md",
        PLUGIN / "README.md",
        TEMPLATES_DIR / "CLAUDE.md",
        REPO / "CLAUDE.md",
    ]
    docs_to_scan.extend((REPO / "docs").glob("*.md"))
    for doc in docs_to_scan:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = m.group(2)
            # 외부·앵커·이메일 링크 제외
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # # 부분 (앵커) 떼어냄
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (doc.parent / target_path).resolve()
            if not resolved.exists():
                issues.append({
                    "level": "WARN",
                    "category": "dead-link",
                    "msg": f"{doc.relative_to(REPO)} → {target_path} (존재하지 않음)",
                })
    return issues


COUNT_PATTERNS = [
    (re.compile(r"(\d+)\s*슬래시\s*커맨드"), "commands"),
    (re.compile(r"슬래시\s*커맨드\s*(\d+)\s*종"), "commands"),
    (re.compile(r"커맨드\s*(\d+)종"), "commands"),
    (re.compile(r"(\d+)\s*서브에이전트"), "agents"),
    (re.compile(r"서브에이전트\s*(\d+)\s*종"), "agents"),
    (re.compile(r"에이전트\s*(\d+)종"), "agents"),
]


def check_counts() -> list[dict]:
    issues = []
    actual = {
        "commands": len(collect_commands()),
        "agents": len(collect_agents()),
    }
    for doc in DOC_TARGETS:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        for pat, kind in COUNT_PATTERNS:
            for m in pat.finditer(text):
                claimed = int(m.group(1))
                if claimed != actual[kind]:
                    issues.append({
                        "level": "ERROR",
                        "category": "count-mismatch",
                        "msg": f"{doc.relative_to(REPO)}: '{m.group()}' 라고 했는데 실제 {kind} = {actual[kind]}",
                    })
    return issues


# ---------- 메인 ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="WARN 도 exit 1 (CI 용)")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    all_issues: list[dict] = []
    sections = [
        ("커맨드 동기화 (commands × 4 docs)", check_commands_in_docs),
        ("에이전트 언급 (READMEs)",          check_agents_in_docs),
        ("버전 일치 (marketplace ↔ plugin)",  check_version_alignment),
        ("스크립트 트리 (README)",           check_scripts_in_readme),
        ("하드코딩 절대 경로 (templates)",   check_hardcoded_paths),
        ("JSON 유효성",                       check_json_validity),
        ("죽은 markdown 링크",                check_dead_links),
        ("카운트 표기 (16/21 등)",            check_counts),
    ]

    section_results = []
    for label, fn in sections:
        issues = fn()
        all_issues.extend(issues)
        section_results.append({"label": label, "issues": issues})

    errors = [i for i in all_issues if i["level"] == "ERROR"]
    warnings = [i for i in all_issues if i["level"] == "WARN"]

    if args.json:
        print(json.dumps({
            "errors": len(errors),
            "warnings": len(warnings),
            "issues": all_issues,
        }, ensure_ascii=False, indent=2))
    else:
        print("# 문서 일관성 검사")
        print()
        for sec in section_results:
            n = len(sec["issues"])
            mark = "✅" if n == 0 else ("⚠️" if all(i["level"] == "WARN" for i in sec["issues"]) else "❌")
            print(f"{mark} {sec['label']} — {n} 건")
            for i in sec["issues"]:
                print(f"   [{i['level']}] {i['msg']}")
            print()
        print(f"## 요약: ERROR {len(errors)} / WARN {len(warnings)}")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
