#!/usr/bin/env python3
"""
Visualize — relationships → mermaid 그래프, timeline → HTML, SP 추적도.

각 챕터의 state YAML 을 읽어 다음 산출물을 build/visualizations/ 에 생성:
- relationships-chNN.md  (mermaid graph)
- relationships-current.md (state/current 기준)
- timeline.html          (인터랙티브 — 단순 정적 HTML)
- sp-tracking.md         (각 SP 의 챕터별 진행 상태)
- characters.md          (인물별 등장·지식 누적 그래프)

사용:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/visualize.py [--chapter N] [--all]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[visualize] PyYAML 필요: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STATE = PROJECT / "state"
TIMELINE = PROJECT / "timeline" / "history.md"
BUILD = PROJECT / "build" / "visualizations"


def load_yaml(p: Path):
    if not p.exists():
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None


def chapter_dirs() -> list[tuple[int, Path]]:
    out: list[tuple[int, Path]] = []
    for d in sorted(STATE.glob("chapter-*")):
        try:
            n = int(d.name.split("-")[-1])
        except ValueError:
            continue
        out.append((n, d))
    return out


def relationships_to_mermaid(ch_num: int, ch_dir: Path) -> str:
    rel_data = load_yaml(ch_dir / "relationships.yaml") or {}
    char_data = load_yaml(ch_dir / "character-states.yaml") or {}
    rels = rel_data.get("relationships") or []
    chars = char_data.get("characters") or {}

    lines = [f"# 인물 관계도 — 챕터 {ch_num}", ""]
    lines.append("```mermaid")
    lines.append("graph LR")
    # 노드
    for cid, info in chars.items():
        info = info or {}
        version = info.get("version", "?")
        location = (info.get("physical") or {}).get("location") or "?"
        label = f"{cid}<br/>{version}<br/>{location}"
        lines.append(f"  {cid}[\"{label}\"]")
    # 엣지
    for r in rels:
        a, b = r.get("from"), r.get("to")
        if not a or not b:
            continue
        trust = r.get("trust", "?")
        intimacy = r.get("intimacy", "?")
        label = r.get("label", "")
        edge_label = f"trust {trust}/int {intimacy}"
        if label:
            edge_label += f"<br/>{label}"
        lines.append(f"  {a} -- \"{edge_label}\" --> {b}")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def sp_tracking_md() -> str:
    """모든 챕터를 횡단해 SP 별 진행 상태 표 작성."""
    sp_history: dict[str, list[dict]] = {}
    for ch_num, d in chapter_dirs():
        ot = load_yaml(d / "open-threads.yaml") or {}
        for t in (ot.get("threads") or []):
            sp = t.get("id")
            if not sp:
                continue
            sp_history.setdefault(sp, []).append({
                "ch": ch_num,
                "label": t.get("label", "?"),
                "status": t.get("status", "?"),
                "last_hinted": t.get("last_hinted_at_chapter", "?"),
                "payoff": t.get("planned_payoff_chapter", "?"),
            })

    lines = ["# 서브플롯 (SP) 추적도", ""]
    for sp, hist in sorted(sp_history.items()):
        latest = hist[-1]
        lines.append(f"## {sp} — {latest['label']}")
        lines.append("")
        lines.append(f"| 챕터 | status | last_hinted | payoff |")
        lines.append(f"|------|--------|-------------|--------|")
        for h in hist:
            lines.append(f"| ch{h['ch']:02d} | {h['status']} | ch{h['last_hinted']} | ch{h['payoff']} |")
        lines.append("")
        # mermaid timeline
        lines.append("```mermaid")
        lines.append("gantt")
        lines.append(f"    title {sp}: {latest['label']}")
        lines.append("    dateFormat X")
        lines.append("    axisFormat ch%s")
        seen_status = set()
        for h in hist:
            section = h["status"]
            seen_status.add(section)
            lines.append(f"    section {section}")
            lines.append(f"    ch{h['ch']:02d} 진행 :{h['ch']}, 1")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def characters_md() -> str:
    """인물별 등장·지식 누적 그래프."""
    char_history: dict[str, list[dict]] = {}
    for ch_num, d in chapter_dirs():
        cs = load_yaml(d / "character-states.yaml") or {}
        for cid, info in (cs.get("characters") or {}).items():
            info = info or {}
            knowledge = info.get("knowledge") or {}
            char_history.setdefault(cid, []).append({
                "ch": ch_num,
                "version": info.get("version", "?"),
                "aware": len(knowledge.get("aware_of") or []),
                "unaware": len(knowledge.get("unaware_of") or []),
                "location": (info.get("physical") or {}).get("location", "?"),
            })

    lines = ["# 인물별 등장·지식 추이", ""]
    for cid, hist in sorted(char_history.items()):
        lines.append(f"## {cid}")
        lines.append("")
        lines.append(f"| ch | version | aware_of | unaware_of | 위치 |")
        lines.append(f"|----|---------|----------|------------|------|")
        for h in hist:
            loc = (h["location"] or "?")[:40]
            lines.append(f"| {h['ch']:02d} | {h['version']} | {h['aware']} | {h['unaware']} | {loc} |")
        lines.append("")
    return "\n".join(lines)


TIMELINE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>Timeline — novel-writer</title>
<style>
body { font-family: -apple-system, system-ui, sans-serif; max-width: 800px; margin: 2em auto; padding: 1em; color: #222; }
h1 { border-bottom: 2px solid #333; padding-bottom: .3em; }
.chapter { margin: 2em 0; padding: 1em 1.5em; background: #f7f7f7; border-left: 4px solid #555; }
.chapter h2 { margin-top: 0; }
.events { list-style: none; padding-left: 0; }
.events li { padding: .3em 0; border-bottom: 1px dashed #ddd; }
.events li:last-child { border-bottom: none; }
.time { color: #666; font-family: ui-monospace, monospace; font-size: .9em; }
</style></head>
<body>
<h1>Timeline — 사건 연대기</h1>
__CONTENT__
</body></html>"""


def timeline_to_html() -> str:
    if not TIMELINE.exists():
        return TIMELINE_HTML_TEMPLATE.replace("__CONTENT__", "<p>timeline/history.md 없음.</p>")
    text = TIMELINE.read_text(encoding="utf-8")
    chapters_html: list[str] = []

    for m in re.finditer(r"^## 챕터 (\d+) — (.+?)$\n([\s\S]+?)(?=^## 챕터 |\Z)", text, re.MULTILINE):
        ch = m.group(1)
        title = m.group(2).strip()
        body = m.group(3)
        events = re.findall(r"^- \[([^\]]+)\] (.+?)$", body, re.MULTILINE)
        evs_html = "\n".join(
            f'<li><span class="time">[{t}]</span> {e}</li>' for t, e in events
        )
        chapters_html.append(
            f'<div class="chapter"><h2>챕터 {ch} — {title}</h2><ul class="events">\n{evs_html}\n</ul></div>'
        )
    return TIMELINE_HTML_TEMPLATE.replace("__CONTENT__", "\n".join(chapters_html))


def main() -> int:
    ap = argparse.ArgumentParser(description="state·timeline 시각화 산출물 생성")
    ap.add_argument("--chapter", type=int, help="특정 챕터 관계도만")
    ap.add_argument("--all", action="store_true", help="전 산출물 생성 (기본)")
    args = ap.parse_args()

    if not STATE.exists():
        print(f"[visualize] state/ 없음", file=sys.stderr)
        return 1

    BUILD.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if args.chapter is not None:
        d = STATE / f"chapter-{args.chapter:02d}"
        if not d.exists():
            print(f"[visualize] {d} 없음", file=sys.stderr)
            return 1
        out = BUILD / f"relationships-ch{args.chapter:02d}.md"
        out.write_text(relationships_to_mermaid(args.chapter, d), encoding="utf-8")
        written.append(out)
    else:
        # 전체
        for ch_num, d in chapter_dirs():
            out = BUILD / f"relationships-ch{ch_num:02d}.md"
            out.write_text(relationships_to_mermaid(ch_num, d), encoding="utf-8")
            written.append(out)

        # 통합
        sp_path = BUILD / "sp-tracking.md"
        sp_path.write_text(sp_tracking_md(), encoding="utf-8")
        written.append(sp_path)

        chars_path = BUILD / "characters.md"
        chars_path.write_text(characters_md(), encoding="utf-8")
        written.append(chars_path)

        html_path = BUILD / "timeline.html"
        html_path.write_text(timeline_to_html(), encoding="utf-8")
        written.append(html_path)

    print(f"[visualize] {len(written)} 파일 생성:")
    for p in written:
        print(f"  {p.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
