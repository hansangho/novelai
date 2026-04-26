#!/usr/bin/env python3
"""
Pilot Metrics — 파일럿 종합 지표 수집.

PRD v1.4 §13 성공 지표 + Phase 9 비대 측정을 한 번에 출력한다.
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py` — 사람이 읽는 리포트
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py --json` — 기계 판독 (CI·트렌드 저장용)
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py --chapter 7` — 특정 챕터만
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pilot_metrics.py --project 40` — 40 챕터 추정
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STORY = PROJECT / "story" / "chapters"
STATE = PROJECT / "state"
BIBLE = PROJECT / "bible"
TIMELINE = PROJECT / "timeline" / "history.md"
GATE_LOG = PROJECT / ".work" / "gate-decisions.md"
REVIEWS = PROJECT / ".work" / "reviews"
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parent.parent)).resolve()

CH_RE = re.compile(r"chapter-(\d+)")
TIMELINE_SECTION_RE = re.compile(r"^## 챕터 (\d+)", re.M)
GATE_SECTION_RE = re.compile(r"## ch(\d{2}) — iter (\d+)/3 @ (\S+)")
GATE_RECORD_RE = re.compile(r"^- (G[1-5]) (PASS|FAIL|WARN|OVERRIDE)", re.M)
FINALIZED_RE = re.compile(r"- FINALIZED ch(\d{2})")


# ---------- 수집 ----------

def collect_artifacts() -> dict:
    return {
        "chapters_finalized": sorted(int(p.stem.split("-")[-1]) for p in STORY.glob("chapter-*.md")),
        "state_snapshots":    sorted(int(m.group(1)) for m in (CH_RE.search(str(p)) for p in STATE.glob("chapter-*")) if m),
        "bible_files":        sorted(str(p.relative_to(PROJECT)) for p in BIBLE.rglob("*") if p.is_file()),
        "review_files":       sorted(p.name for p in REVIEWS.glob("*.md")) if REVIEWS.exists() else [],
        "current_symlink":    STATE.joinpath("current").resolve().name if STATE.joinpath("current").exists() else None,
    }


def collect_story_volume() -> dict:
    chapters: list[dict] = []
    total_chars = 0
    total_lines = 0
    for p in sorted(STORY.glob("chapter-*.md")):
        text = p.read_text(encoding="utf-8")
        chars = len(text)
        lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        ch_num = int(p.stem.split("-")[-1])
        chapters.append({"chapter": ch_num, "bytes": len(text.encode("utf-8")), "chars": chars, "lines": lines})
        total_chars += chars
        total_lines += lines
    return {"per_chapter": chapters, "total_chars": total_chars, "total_lines": total_lines, "count": len(chapters)}


def collect_timeline() -> dict:
    if not TIMELINE.exists():
        return {"exists": False}
    text = TIMELINE.read_text(encoding="utf-8")
    per_chapter: list[dict] = []
    matches = list(TIMELINE_SECTION_RE.finditer(text))
    for i, m in enumerate(matches):
        ch = int(m.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[m.start():end]
        per_chapter.append({"chapter": ch, "lines": block.count("\n"), "chars": len(block)})
    return {
        "exists": True,
        "total_bytes": len(text.encode("utf-8")),
        "total_lines": text.count("\n"),
        "total_chars": len(text),
        "per_chapter": per_chapter,
    }


def collect_state_sizes() -> list[dict]:
    out: list[dict] = []
    for d in sorted(STATE.glob("chapter-*")):
        if not d.is_dir():
            continue
        ch = int(d.name.split("-")[-1])
        files = {}
        total = 0
        for f in d.glob("*.yaml"):
            b = f.stat().st_size
            files[f.name] = b
            total += b
        out.append({"chapter": ch, "total_bytes": total, "files": files})
    return out


def collect_bible_stats() -> dict:
    if not BIBLE.exists():
        return {"exists": False}
    files: list[dict] = []
    total = 0
    for p in BIBLE.rglob("*"):
        if not p.is_file():
            continue
        b = p.stat().st_size
        files.append({"path": str(p.relative_to(PROJECT)), "bytes": b})
        total += b
    return {"exists": True, "total_bytes": total, "file_count": len(files), "files": files}


def collect_sp_tracking() -> dict:
    """챕터 순회하며 SP id 별 (last_hinted, status, payoff) 변화를 수집."""
    if yaml is None:
        return {"available": False, "reason": "PyYAML 미설치"}
    history: dict[str, list[dict]] = {}
    for d in sorted(STATE.glob("chapter-*")):
        ch = int(d.name.split("-")[-1])
        fp = d / "open-threads.yaml"
        if not fp.exists():
            continue
        try:
            data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            return {"available": False, "reason": f"YAML 에러 {fp}: {e}"}
        for t in (data.get("threads") or []):
            sp = t.get("id")
            if not sp:
                continue
            history.setdefault(sp, []).append({
                "at_chapter": ch,
                "status": t.get("status"),
                "last_hinted": t.get("last_hinted_at_chapter"),
                "payoff": t.get("planned_payoff_chapter"),
                "label": t.get("label"),
            })
    return {"available": True, "threads": history}


def collect_knowledge_growth() -> dict:
    """각 인물의 aware_of item 수가 챕터마다 어떻게 변하는지."""
    if yaml is None:
        return {"available": False, "reason": "PyYAML 미설치"}
    growth: dict[str, list[dict]] = {}
    for d in sorted(STATE.glob("chapter-*")):
        ch = int(d.name.split("-")[-1])
        fp = d / "character-states.yaml"
        if not fp.exists():
            continue
        try:
            data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        for name, info in (data.get("characters") or {}).items():
            k = (info or {}).get("knowledge") or {}
            aware = len(k.get("aware_of") or [])
            unaware = len(k.get("unaware_of") or [])
            growth.setdefault(name, []).append({"chapter": ch, "aware_of": aware, "unaware_of": unaware})
    return {"available": True, "characters": growth}


def collect_gate_stats() -> dict:
    if not GATE_LOG.exists():
        return {"exists": False}
    log = GATE_LOG.read_text(encoding="utf-8")

    iters_by_ch: dict[str, list[int]] = {}
    for m in GATE_SECTION_RE.finditer(log):
        ch, it = m.group(1), int(m.group(2))
        iters_by_ch.setdefault(ch, []).append(it)

    gate_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "OVERRIDE": 0}
    for _gid, result in GATE_RECORD_RE.findall(log):
        gate_counts[result] = gate_counts.get(result, 0) + 1

    finalized = sorted(set(int(m) for m in FINALIZED_RE.findall(log)))

    final_iters: dict[str, int] = {ch: max(its) for ch, its in iters_by_ch.items()}
    total_rewrites = sum((it - 1) for it in final_iters.values())
    avg_rewrites = total_rewrites / len(final_iters) if final_iters else 0.0

    return {
        "exists": True,
        "chapters_tracked": sorted(int(ch) for ch in iters_by_ch.keys()),
        "final_iter_per_chapter": {int(ch): it for ch, it in final_iters.items()},
        "gate_counts": gate_counts,
        "finalized_chapters": finalized,
        "avg_rewrites_per_chapter": round(avg_rewrites, 2),
        "max_rewrites": max(final_iters.values()) - 1 if final_iters else 0,
    }


def run_validator() -> dict:
    """validate_state.py 를 호출해 YAML 무결성을 검사."""
    validator = PLUGIN_ROOT / "scripts" / "validate_state.py"
    if not validator.exists():
        return {"available": False, "reason": "validate_state.py 없음"}
    try:
        r = subprocess.run(
            ["python3", str(validator)],
            capture_output=True, text=True, timeout=30,
            cwd=PROJECT,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"available": False, "reason": str(e)}
    return {
        "available": True,
        "exit_code": r.returncode,
        "stdout": r.stdout.strip(),
        "stderr": r.stderr.strip(),
    }


# ---------- 투사 ----------

def project_to(chapters: int, current: dict) -> dict:
    """선형 외삽으로 N 챕터 시의 예상치."""
    if current["story"]["count"] < 1:
        return {"available": False, "reason": "원고 없음"}
    ch_count = current["story"]["count"]
    avg_chapter_chars = current["story"]["total_chars"] / ch_count
    timeline_bytes_per_ch = (current["timeline"]["total_bytes"] / ch_count) if current["timeline"].get("exists") else 0
    avg_state_bytes = (
        sum(s["total_bytes"] for s in current["state_sizes"]) / len(current["state_sizes"])
        if current["state_sizes"] else 0
    )
    return {
        "target_chapters": chapters,
        "story_total_chars": int(avg_chapter_chars * chapters),
        "story_total_kb":    round(avg_chapter_chars * chapters / 1024, 1),
        "timeline_bytes":    int(timeline_bytes_per_ch * chapters),
        "timeline_kb":       round(timeline_bytes_per_ch * chapters / 1024, 1),
        "state_total_bytes": int(avg_state_bytes * chapters),
        "state_total_kb":    round(avg_state_bytes * chapters / 1024, 1),
        "assumption":        "챕터 크기가 현재 평균 유지 — 실작가 작업은 더 길 수 있음",
    }


# ---------- 렌더 ----------

def render_text(m: dict, projection: dict | None) -> str:
    L: list[str] = []
    L.append("## 파일럿 지표 — novelai")
    L.append("")
    art = m["artifacts"]
    L.append(f"### 아티팩트")
    L.append(f"- 확정 챕터: {len(art['chapters_finalized'])} 개 {art['chapters_finalized']}")
    L.append(f"- State 스냅샷: {len(art['state_snapshots'])} 개 (current → {art['current_symlink']})")
    L.append(f"- Bible 파일: {len(art['bible_files'])} 개")
    L.append(f"- Review 파일: {len(art['review_files'])} 개")
    L.append("")

    story = m["story"]
    L.append(f"### 원고 (story/chapters/)")
    L.append(f"- 총 {story['count']} 챕터, {story['total_chars']:,} 자, {story['total_lines']:,} 줄")
    if story['count']:
        avg = story['total_chars'] / story['count']
        L.append(f"- 평균 챕터 분량: {avg:.0f} 자 ({avg/1024:.1f} KB)")
        sizes = sorted(c['chars'] for c in story['per_chapter'])
        L.append(f"- 범위: 최소 {sizes[0]:,} / 최대 {sizes[-1]:,} 자")
    L.append("")

    tl = m["timeline"]
    L.append(f"### Timeline (append-only)")
    if tl.get("exists"):
        L.append(f"- 전체: {tl['total_lines']:,} 줄 / {tl['total_bytes']:,} bytes ({tl['total_bytes']/1024:.1f} KB)")
        if tl["per_chapter"]:
            avg_l = sum(c['lines'] for c in tl['per_chapter']) / len(tl['per_chapter'])
            avg_c = sum(c['chars'] for c in tl['per_chapter']) / len(tl['per_chapter'])
            L.append(f"- 챕터당 평균: {avg_l:.0f} 줄 / {avg_c:.0f} 자")
    else:
        L.append(f"- 없음")
    L.append("")

    state = m["state_sizes"]
    L.append(f"### State 스냅샷")
    if state:
        L.append(f"- 챕터별 크기 (bytes):")
        for s in state:
            L.append(f"    ch{s['chapter']:02d}: {s['total_bytes']:,}")
        avg_s = sum(s['total_bytes'] for s in state) / len(state)
        sizes = sorted(s['total_bytes'] for s in state)
        L.append(f"- 평균 {avg_s:.0f} bytes / 최소 {sizes[0]:,} / 최대 {sizes[-1]:,}")
        L.append(f"- 누적 성장 없음 확인: (max − min) / avg = {(sizes[-1]-sizes[0])/avg_s*100:.1f}% 변동")
    L.append("")

    bib = m["bible"]
    L.append(f"### Bible (정적 참조)")
    if bib.get("exists"):
        L.append(f"- {bib['file_count']} 파일 / {bib['total_bytes']:,} bytes ({bib['total_bytes']/1024:.1f} KB)")
    L.append("")

    gate = m["gate_stats"]
    L.append(f"### Gate 통계")
    if gate.get("exists"):
        L.append(f"- 확정 챕터: {gate['finalized_chapters']}")
        L.append(f"- 챕터별 최종 iter: {gate['final_iter_per_chapter']}")
        L.append(f"- Gate 결과 합계: PASS {gate['gate_counts']['PASS']} / FAIL {gate['gate_counts']['FAIL']} / WARN {gate['gate_counts']['WARN']} / OVERRIDE {gate['gate_counts']['OVERRIDE']}")
        L.append(f"- 평균 재작성 횟수: {gate['avg_rewrites_per_chapter']} (PRD §13 목표: 1~2)")
        L.append(f"- 최대 재작성: {gate['max_rewrites']} (한도: 3)")
    else:
        L.append("- gate-decisions.md 없음")
    L.append("")

    sp = m["sp_tracking"]
    L.append(f"### 서브플롯 (SP) 누적 추적")
    if sp.get("available"):
        for sp_id, hist in sorted(sp["threads"].items()):
            latest = hist[-1]
            L.append(f"- {sp_id}: {latest['label']}")
            L.append(f"    최신 ch{latest['at_chapter']} | status={latest['status']} | last_hinted=ch{latest['last_hinted']} | payoff=ch{latest['payoff']}")
    else:
        L.append(f"- 불가: {sp.get('reason')}")
    L.append("")

    kg = m["knowledge_growth"]
    L.append(f"### 지식(aware_of) 성장")
    if kg.get("available"):
        for name, series in sorted(kg["characters"].items()):
            points = [(s["chapter"], s["aware_of"]) for s in series]
            compact = " / ".join(f"ch{c}:{n}" for c, n in points)
            L.append(f"- {name:<15} {compact}")
    else:
        L.append(f"- 불가: {kg.get('reason')}")
    L.append("")

    val = m["validator"]
    L.append(f"### validate_state.py")
    if val.get("available"):
        L.append(f"- exit_code: {val['exit_code']}")
        for line in (val.get("stdout") or "").splitlines():
            L.append(f"    {line}")
        if val.get("stderr"):
            for line in val["stderr"].splitlines():
                L.append(f"    ! {line}")
    else:
        L.append(f"- 불가: {val.get('reason')}")
    L.append("")

    if projection:
        L.append(f"### 투사 — {projection['target_chapters']} 챕터 추정 (현재 평균 기준)")
        L.append(f"- 원고 총량: {projection['story_total_kb']} KB")
        L.append(f"- Timeline: {projection['timeline_kb']} KB")
        L.append(f"- State 총합: {projection['state_total_kb']} KB (*누적 아님 — 각 챕터 독립 스냅샷 합계*)")
        L.append(f"- 주의: {projection['assumption']}")
        L.append("")

    return "\n".join(L)


# ---------- 메인 ----------

def estimate_cost(metrics: dict, model: str = "sonnet") -> dict:
    """챕터당 평균 토큰 사용량과 모델별 단가로 비용 추정.

    Claude API 단가 (2026 기준 추정 — 변동 가능):
    - opus:    $15 / 1M input, $75 / 1M output
    - sonnet:  $3  / 1M input, $15 / 1M output
    - haiku:   $0.25/ 1M input, $1.25/ 1M output

    가정 (실제 측정 아닌 휴리스틱):
    - 챕터당 토큰: input ≈ (Bible + State + Timeline + 입력 컨텍스트) / 3 (대략 3 글자 = 1 토큰)
    - output ≈ (챕터 본문 + Gate 5 리포트) / 3
    - Gate 5 회 호출 + 재작성 평균 0.5 회 → 토큰 ×1.5
    """
    pricing = {
        "opus":   {"input_per_1m": 15.00, "output_per_1m": 75.00},
        "sonnet": {"input_per_1m":  3.00, "output_per_1m": 15.00},
        "haiku":  {"input_per_1m":  0.25, "output_per_1m":  1.25},
    }
    if model not in pricing:
        return {"available": False, "reason": f"unknown model: {model}"}

    bible_chars   = metrics["bible"].get("total_bytes", 0) if metrics["bible"].get("exists") else 0
    timeline_chars = metrics["timeline"].get("total_bytes", 0) if metrics["timeline"].get("exists") else 0
    avg_state = (
        sum(s["total_bytes"] for s in metrics["state_sizes"]) / len(metrics["state_sizes"])
        if metrics["state_sizes"] else 0
    )
    story_count = metrics["story"]["count"]
    avg_chapter_chars = (metrics["story"]["total_chars"] / story_count) if story_count else 3000

    # 1 챕터 입력 토큰 추정 (대략적)
    input_chars = bible_chars + timeline_chars + avg_state + avg_chapter_chars  # 컨텍스트 + 직전 챕터
    output_chars = avg_chapter_chars + 5 * 800  # 본문 + Gate 5 리포트 (각 ~800자)

    # 한국어 → 토큰 환산: 약 1.5 ~ 2 글자 / 1 토큰 (영어 4:1 보다 빡빡)
    input_tokens = input_chars / 1.7
    output_tokens = output_chars / 1.7

    # 재작성 가중치 (현재 평균)
    avg_rewrites = metrics["gate_stats"].get("avg_rewrites_per_chapter", 0.5) if metrics["gate_stats"].get("exists") else 0.5
    multiplier = 1 + avg_rewrites * 0.5  # 재작성 1회당 +50%

    input_tokens *= multiplier
    output_tokens *= multiplier

    p = pricing[model]
    cost_per_chapter = (input_tokens / 1_000_000) * p["input_per_1m"] + (output_tokens / 1_000_000) * p["output_per_1m"]

    return {
        "available": True,
        "model": model,
        "pricing": p,
        "estimated_input_tokens_per_chapter": int(input_tokens),
        "estimated_output_tokens_per_chapter": int(output_tokens),
        "rewrite_multiplier": round(multiplier, 2),
        "cost_per_chapter_usd": round(cost_per_chapter, 3),
        "cost_per_chapter_krw": round(cost_per_chapter * 1380, 0),  # 환율 ~1380 (가정)
        "warning": "휴리스틱 추정. 실제 비용은 Anthropic API 대시보드 기준. 환율·단가는 변동 가능.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="기계 판독 출력")
    ap.add_argument("--chapter", type=int, help="단일 챕터만 (일부 섹션 필터)")
    ap.add_argument("--project", type=int, help="N 챕터 시의 추정 크기 계산")
    ap.add_argument("--cost", action="store_true", help="챕터당 비용 추정 표시")
    ap.add_argument("--model", default="sonnet", choices=["opus", "sonnet", "haiku"],
                    help="비용 추정 모델 (기본: sonnet)")
    args = ap.parse_args()

    metrics = {
        "artifacts":       collect_artifacts(),
        "story":           collect_story_volume(),
        "timeline":        collect_timeline(),
        "state_sizes":     collect_state_sizes(),
        "bible":           collect_bible_stats(),
        "gate_stats":      collect_gate_stats(),
        "sp_tracking":     collect_sp_tracking(),
        "knowledge_growth": collect_knowledge_growth(),
        "validator":       run_validator(),
    }

    if args.chapter is not None:
        ch = args.chapter
        # 필터: per-chapter 섹션만 해당 챕터 남기기
        metrics["story"]["per_chapter"] = [c for c in metrics["story"]["per_chapter"] if c["chapter"] == ch]
        metrics["state_sizes"] = [s for s in metrics["state_sizes"] if s["chapter"] == ch]
        if metrics["timeline"].get("exists"):
            metrics["timeline"]["per_chapter"] = [c for c in metrics["timeline"]["per_chapter"] if c["chapter"] == ch]

    projection = project_to(args.project, metrics) if args.project else None
    cost = estimate_cost(metrics, args.model) if args.cost else None

    if args.json:
        out = {"metrics": metrics, "projection": projection, "cost": cost}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(render_text(metrics, projection))
        if cost and cost.get("available"):
            print(f"### 비용 추정 — 모델 {cost['model']} (휴리스틱)")
            print(f"- 챕터당 입력 토큰: ~{cost['estimated_input_tokens_per_chapter']:,}")
            print(f"- 챕터당 출력 토큰: ~{cost['estimated_output_tokens_per_chapter']:,}")
            print(f"- 재작성 배수: ×{cost['rewrite_multiplier']}")
            print(f"- 챕터당 비용: 약 ${cost['cost_per_chapter_usd']} / ₩{cost['cost_per_chapter_krw']:,.0f}")
            if args.project:
                total_usd = cost['cost_per_chapter_usd'] * args.project
                print(f"- {args.project} 챕터 총 추정: 약 ${total_usd:.2f} / ₩{total_usd*1380:,.0f}")
            print(f"- ⚠ {cost['warning']}")
            print()

    gate = metrics["gate_stats"]
    if gate.get("exists") and gate["max_rewrites"] > 3:
        return 1
    if metrics["validator"].get("available") and metrics["validator"].get("exit_code", 0) not in (0,):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
