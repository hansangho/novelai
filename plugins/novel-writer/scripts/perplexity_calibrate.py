#!/usr/bin/env python3
"""
Perplexity Calibrator — 작가 작품 기준 임계값 자동 튜닝.

Perplexity Analyzer 의 임계값(기본: 하위 20% 플래그) 을 작가 작품의 실제 분포에
맞춰 조정한다. 이미 finalize 된 챕터들의 문장을 분석해, 작가 본인의 평균
복잡도(=독창성) 분포를 산출하고 권장 임계값을 제시.

옵션 A — 외부 LLM 정량: 환경변수 NOVELWRITER_PERPLEXITY_API 가 있으면
                        해당 API 호출 (구현은 작가가 직접 — 인터페이스만 제공).
옵션 B — Claude 자체 판정 (기본): 본 스크립트는 통계 메타분석만 수행. 실제 점수
                                  는 perplexity-analyzer 에이전트가 매긴 .work/reviews
                                  /chNN-iterX/perplexity-report.md 의 누적 데이터를 사용.

사용:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perplexity_calibrate.py [--write]
    --write 옵션이면 권장 임계값을 bible/style-rules.json 에 직접 반영
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STYLE_RULES = PROJECT / "bible" / "style-rules.json"
REVIEWS = PROJECT / ".work" / "reviews"

PERPLEXITY_FLAG_RE = re.compile(r"점수\s*(\d+)")  # "점수 8" 형식
TOTAL_SENT_RE = re.compile(r"총\s*문장:\s*(\d+)")
FLAGGED_RE = re.compile(r"플래그:\s*(\d+)")


def collect_reports() -> list[dict]:
    """모든 perplexity 리포트 를 모아 통계용 데이터 추출."""
    if not REVIEWS.exists():
        return []
    reports: list[dict] = []
    for ch_iter_dir in sorted(REVIEWS.glob("ch*-iter*")):
        rp = ch_iter_dir / "perplexity-report.md"
        if not rp.exists():
            continue
        text = rp.read_text(encoding="utf-8")
        total_m = TOTAL_SENT_RE.search(text)
        flag_m = FLAGGED_RE.search(text)
        scores = [int(m.group(1)) for m in PERPLEXITY_FLAG_RE.finditer(text)]
        reports.append({
            "path": str(rp.relative_to(PROJECT)),
            "total_sentences": int(total_m.group(1)) if total_m else 0,
            "flagged_count": int(flag_m.group(1)) if flag_m else len(scores),
            "scores": scores,
        })
    return reports


def compute_distribution(reports: list[dict]) -> dict:
    total_sent = sum(r["total_sentences"] for r in reports)
    total_flagged = sum(r["flagged_count"] for r in reports)
    all_scores = [s for r in reports for s in r["scores"]]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    flag_rate = (total_flagged / total_sent * 100) if total_sent else 0
    return {
        "report_count": len(reports),
        "total_sentences": total_sent,
        "total_flagged": total_flagged,
        "flag_rate_pct": round(flag_rate, 2),
        "average_flagged_score": round(avg_score, 2),
        "score_distribution": {s: all_scores.count(s) for s in sorted(set(all_scores))} if all_scores else {},
    }


def recommend_threshold(dist: dict) -> dict:
    """PRD §13 목표: 수용률 20~50%. 현재 플래그율을 보고 임계값 제안."""
    rate = dist["flag_rate_pct"]
    avg_score = dist["average_flagged_score"]
    rec = {"current_flag_rate_pct": rate, "current_threshold_score": avg_score}

    if rate < 5:
        rec["verdict"] = "너무 느슨 — 플래그가 너무 적게 나옴"
        rec["suggested_threshold"] = max(6, int(avg_score) - 1) if avg_score else 6
        rec["reason"] = "임계값을 낮춰(점수 6~7) 더 많은 문장을 검토"
    elif rate > 30:
        rec["verdict"] = "너무 엄격 — 플래그가 너무 많이 나옴"
        rec["suggested_threshold"] = min(9, int(avg_score) + 1) if avg_score else 9
        rec["reason"] = "임계값을 올려(점수 8~9) 정말 뻔한 문장만 잡기"
    else:
        rec["verdict"] = "적정 — PRD 목표 범위 내 (5~30%)"
        rec["suggested_threshold"] = int(avg_score) if avg_score else 8
        rec["reason"] = "현재 임계값 유지"

    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="권장 임계값을 bible/style-rules.json 의 perplexity_threshold 필드에 반영")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    reports = collect_reports()
    if not reports:
        print("[perplexity-calibrate] perplexity-report.md 가 없습니다. "
              "먼저 챕터를 집필하고 G4 Gate 를 실행하세요.", file=sys.stderr)
        return 1

    dist = compute_distribution(reports)
    rec = recommend_threshold(dist)

    if args.json:
        print(json.dumps({"distribution": dist, "recommendation": rec}, ensure_ascii=False, indent=2))
    else:
        print(f"## Perplexity 캘리브레이션 — 작가 작품 기준")
        print(f"")
        print(f"리포트 분석: {dist['report_count']} 개")
        print(f"총 문장: {dist['total_sentences']}, 플래그: {dist['total_flagged']} ({dist['flag_rate_pct']}%)")
        print(f"플래그된 문장 평균 점수: {dist['average_flagged_score']}")
        if dist["score_distribution"]:
            print(f"점수 분포: {dist['score_distribution']}")
        print(f"")
        print(f"### 권장")
        print(f"  판정:    {rec['verdict']}")
        print(f"  현재 비율: {rec['current_flag_rate_pct']}%")
        print(f"  권장 임계값 점수: {rec['suggested_threshold']}")
        print(f"  이유: {rec['reason']}")

    if args.write:
        if not STYLE_RULES.exists():
            print(f"[perplexity-calibrate] style-rules.json 없음 — --write 무시", file=sys.stderr)
            return 0
        rules = json.loads(STYLE_RULES.read_text(encoding="utf-8"))
        rules.setdefault("perplexity_threshold", {})["score"] = rec["suggested_threshold"]
        rules["perplexity_threshold"]["calibrated_from"] = f"{dist['report_count']} reports, {dist['total_sentences']} sentences"
        STYLE_RULES.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\n[perplexity-calibrate] style-rules.json 갱신: perplexity_threshold.score = {rec['suggested_threshold']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
