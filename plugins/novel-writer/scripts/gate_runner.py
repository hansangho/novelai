#!/usr/bin/env python3
"""
Gate Runner — PRD v1.4 §3. G1~G5 게이트 오케스트레이션.

드래프트 버전 관리, gate-decisions.md 기록, 재작성 반복 (최대 3회) 을 책임진다.
실제 에이전트 호출은 Claude Code 의 Task 도구가 담당 — 본 스크립트는 글루 레이어.

사용법 (플러그인 컨텍스트에서 $CLAUDE_PLUGIN_ROOT 사용):
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py run      --chapter 5
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py next     --chapter 5
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py record   --chapter 5 --gate G2 --result PASS [--note ...]
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py status   --chapter 5
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gate_runner.py finalize --chapter 5
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import sys
from pathlib import Path

# 작가 프로젝트 루트. 플러그인 hooks 는 $CLAUDE_PROJECT_DIR 를 주입.
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
WORK = PROJECT / ".work"
STORY = PROJECT / "story" / "chapters"
GATE_LOG = WORK / "gate-decisions.md"

GATES = [
    ("G1", "Style Gate",       "style-linter"),
    ("G2", "Character Gate",   "character-consistency-guardian"),
    ("G3", "Continuity Gate",  "continuity-reviewer"),
    ("G4", "Perplexity Gate",  "perplexity-analyzer"),
    ("G5", "Integration Gate", "writing-director"),
]
GATE_IDS = [g[0] for g in GATES]

MAX_ITER = 3
TERMINAL_RESULTS = {"PASS", "FAIL", "WARN", "OVERRIDE"}

SECTION_HEADER_RE = re.compile(
    r"^## ch(?P<ch>\d{2}) — iter (?P<iter>\d+)/\d+ @ (?P<ts>\S+)\s*$"
)
GATE_RECORD_RE = re.compile(
    r"^- (?P<gid>G[1-5]) (?P<result>PASS|FAIL|WARN|OVERRIDE)\b"
)


def drafts(chapter: int) -> list[Path]:
    return sorted(WORK.glob(f"writer-draft-ch{chapter:02d}-v*.md"))


def latest_draft(chapter: int) -> Path | None:
    xs = drafts(chapter)
    return xs[-1] if xs else None


def current_iter(chapter: int) -> int:
    """드래프트 파일 수 기준. v1 이 있으면 1, v3 이 있으면 3."""
    return len(drafts(chapter))


def read_log() -> str:
    return GATE_LOG.read_text(encoding="utf-8") if GATE_LOG.exists() else ""


def append_log(entry: str) -> None:
    GATE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with GATE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(entry + "\n")


def parse_sections(log: str) -> list[dict]:
    """gate-decisions.md 를 섹션 리스트로 파싱.
    각 섹션: {chapter, iter, ts, gates: {gid: result}, finalized: bool}."""
    sections: list[dict] = []
    current: dict | None = None
    for line in log.splitlines():
        m = SECTION_HEADER_RE.match(line)
        if m:
            current = {
                "chapter": int(m.group("ch")),
                "iter": int(m.group("iter")),
                "ts": m.group("ts"),
                "gates": {},
                "finalized": False,
            }
            sections.append(current)
            continue
        if current is None:
            continue
        gm = GATE_RECORD_RE.match(line)
        if gm:
            current["gates"][gm.group("gid")] = gm.group("result")
        elif line.startswith("- FINALIZED") and f"ch{current['chapter']:02d}" in line:
            current["finalized"] = True
    return sections


def latest_section_for(chapter: int, sections: list[dict]) -> dict | None:
    for s in reversed(sections):
        if s["chapter"] == chapter:
            return s
    return None


def cmd_run(args: argparse.Namespace) -> int:
    ch = args.chapter
    draft = latest_draft(ch)
    if not draft:
        print(
            f"[gate-runner] 챕터 {ch} 의 드래프트가 없습니다. "
            f".work/writer-draft-ch{ch:02d}-v1.md 를 먼저 만드세요.",
            file=sys.stderr,
        )
        return 1
    iteration = current_iter(ch)
    if iteration > MAX_ITER:
        print(
            f"[gate-runner] 재작성 한도 {MAX_ITER} 회 초과 (현재 v{iteration}). 작가 에스컬레이션 필요.",
            file=sys.stderr,
        )
        return 2

    sections = parse_sections(read_log())
    latest = latest_section_for(ch, sections)
    if latest and latest["iter"] == iteration and not latest["finalized"]:
        # 같은 iter 섹션이 이미 열려 있음 — 새로 열지 않고 재개.
        print(
            f"[gate-runner] ch{ch:02d} iter {iteration}/{MAX_ITER} 섹션이 이미 열려 있음. "
            f"진행 상태는 `status` 로 확인."
        )
    else:
        now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        append_log(f"\n## ch{ch:02d} — iter {iteration}/{MAX_ITER} @ {now}\n- draft: {draft.name}")
        print(f"[gate-runner] 새 섹션: ch{ch:02d} iter {iteration}/{MAX_ITER}")

    print(f"[gate-runner] 드래프트: {draft.name}")
    print("[gate-runner] 다음 Gate 들을 순서대로 서브에이전트로 호출하십시오:")
    for gid, name, agent in GATES:
        print(f"  {gid} {name:<18} → subagent: {agent}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    ch = args.chapter
    iteration = current_iter(ch)
    sections = parse_sections(read_log())
    latest = latest_section_for(ch, sections)
    if latest is None or latest["iter"] != iteration:
        # 현재 iter 섹션이 아직 없음 → G1 부터
        print("G1")
        return 0
    for gid in GATE_IDS:
        if gid not in latest["gates"]:
            print(gid)
            return 0
        if latest["gates"][gid] == "FAIL":
            # FAIL 이면 재작성이 필요 — 같은 Gate 를 다시 할지는 상위에서 결정.
            print("FAIL_BLOCK")
            return 0
    print("done")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    ch = args.chapter
    iteration = current_iter(ch)
    sections = parse_sections(read_log())
    latest = latest_section_for(ch, sections)
    if latest is None or latest["iter"] != iteration or latest["finalized"]:
        print(
            f"[gate-runner] ch{ch:02d} 의 현재 iter {iteration} 섹션이 없습니다. "
            f"먼저 `run` 을 호출하세요.",
            file=sys.stderr,
        )
        return 1
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    note = f" — {args.note}" if args.note else ""
    append_log(f"- {args.gate} {args.result} @ {now}{note}")
    print(f"[gate-runner] recorded: ch{ch:02d} iter {iteration} {args.gate} = {args.result}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    ch = args.chapter
    iteration = current_iter(ch)
    sections = parse_sections(read_log())
    latest = latest_section_for(ch, sections)
    print(f"챕터 {ch:02d} — iter {iteration}/{MAX_ITER}" + ("  (FINALIZED)" if latest and latest["finalized"] else ""))
    print("┌──────┬────────────────────────────────┬────────┐")
    print("│ Gate │ 담당                            │ 결과   │")
    print("├──────┼────────────────────────────────┼────────┤")
    for gid, name, agent in GATES:
        result = "—"
        if latest and latest["iter"] == iteration:
            result = latest["gates"].get(gid, "—")
        print(f"│ {gid:<4} │ {agent:<30} │ {result:<6} │")
    print("└──────┴────────────────────────────────┴────────┘")

    if latest is None or latest["iter"] != iteration:
        print("다음: `run` 으로 현재 iter 섹션을 열고 G1 부터 시작")
        return 0
    for gid in GATE_IDS:
        if gid not in latest["gates"]:
            print(f"다음: {gid} 실행")
            return 0
        if latest["gates"][gid] == "FAIL":
            print(f"다음: {gid} FAIL — chapter-writer 로 v{iteration+1} 재작성 필요")
            return 0
    if not latest["finalized"]:
        print("다음: 작가 확인 후 `finalize`")
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    ch = args.chapter
    draft = latest_draft(ch)
    if not draft:
        print(f"[gate-runner] ch{ch:02d} 드래프트 없음.", file=sys.stderr)
        return 1
    iteration = current_iter(ch)
    sections = parse_sections(read_log())
    latest = latest_section_for(ch, sections)
    if latest is None or latest["iter"] != iteration:
        print(
            f"[gate-runner] 현재 iter 의 Gate 섹션이 없습니다. 먼저 `run` 실행.",
            file=sys.stderr,
        )
        return 1
    if latest["finalized"]:
        print(f"[gate-runner] 이미 finalize 된 챕터입니다.", file=sys.stderr)
        return 1
    missing = [g for g in GATE_IDS if g not in latest["gates"]]
    failed = [g for g, r in latest["gates"].items() if r == "FAIL"]
    if missing:
        print(
            f"[gate-runner] 미실행 Gate: {','.join(missing)}. "
            f"`run` / subagent 호출 후 `record` 로 결과를 넣으세요.",
            file=sys.stderr,
        )
        return 1
    if failed:
        print(f"[gate-runner] FAIL Gate: {','.join(failed)}. /revise-loop 필요.", file=sys.stderr)
        return 1

    STORY.mkdir(parents=True, exist_ok=True)
    target = STORY / f"chapter-{ch:02d}.md"
    shutil.copy2(draft, target)
    append_log(f"- FINALIZED ch{ch:02d} ← {draft.name} → {target.relative_to(PROJECT)}")
    print(f"[gate-runner] finalized → {target}")
    print(f"[gate-runner] 다음: `python3 ${{CLAUDE_PLUGIN_ROOT}}/scripts/state_snapshot.py create --chapter {ch}` 로 state/chapter-{ch:02d}/ 생성 후 state-updater 서브에이전트 호출.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="gate_runner", description="Gate G1~G5 orchestrator (PRD v1.4 §3)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="현재 드래프트를 Gate 파이프라인에 투입")
    p_run.add_argument("--chapter", type=int, required=True)

    p_next = sub.add_parser("next", help="다음 실행할 Gate 이름 출력 (G1|G2|..|done|FAIL_BLOCK)")
    p_next.add_argument("--chapter", type=int, required=True)

    p_rec = sub.add_parser("record", help="Gate 결과 기록 (현재 iter 섹션에 append)")
    p_rec.add_argument("--chapter", type=int, required=True)
    p_rec.add_argument("--gate", required=True, choices=GATE_IDS)
    p_rec.add_argument("--result", required=True, choices=["PASS", "FAIL", "WARN", "OVERRIDE"])
    p_rec.add_argument("--note", default="")

    p_stat = sub.add_parser("status", help="현재 Gate 진행 상태 테이블 출력")
    p_stat.add_argument("--chapter", type=int, required=True)

    p_fin = sub.add_parser("finalize", help="최신 드래프트를 story/chapters/ 로 확정 이동")
    p_fin.add_argument("--chapter", type=int, required=True)

    args = parser.parse_args()
    dispatch = {
        "run": cmd_run,
        "next": cmd_next,
        "record": cmd_record,
        "status": cmd_status,
        "finalize": cmd_finalize,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
