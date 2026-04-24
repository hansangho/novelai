#!/usr/bin/env python3
"""
State / Timeline Validator.

State Updater 가 챕터 확정 후, 또는 /gate-status 가 호출될 때 실행한다.
YAML 문법·필수 키·누적 SP 일관성을 빠르게 검사.

사용법:
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_state.py [--chapter N]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    print("[validate_state] PyYAML 가 필요합니다: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
STATE = PROJECT / "state"
TIMELINE = PROJECT / "timeline" / "history.md"

REQUIRED_TOP_KEYS = {
    "character-states.yaml": {"chapter", "completed_at", "characters"},
    "locations-state.yaml":  {"chapter", "completed_at", "locations"},
    "relationships.yaml":    {"chapter", "completed_at", "relationships"},
    "open-threads.yaml":     {"chapter", "completed_at", "threads"},
}


def validate_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"YAML 문법: {e.__class__.__name__}: {e}")
        return errors
    if data is None:
        errors.append("빈 문서")
        return errors
    required = REQUIRED_TOP_KEYS.get(path.name, set())
    missing = required - set(data.keys())
    if missing:
        errors.append(f"필수 키 누락: {sorted(missing)}")
    return errors


def validate_chapter(ch_dir: Path) -> list[str]:
    errors: list[str] = []
    for fname in REQUIRED_TOP_KEYS:
        fp = ch_dir / fname
        if not fp.exists():
            errors.append(f"{ch_dir.name}/{fname}: 파일 없음")
            continue
        for e in validate_yaml(fp):
            errors.append(f"{ch_dir.name}/{fname}: {e}")
    return errors


def validate_sp_consistency() -> tuple[list[str], list[str]]:
    """SP 누적 스캔.
    - ERROR: payoff 가 **뒤로 이동** (이미 지난 챕터보다 작은 값) — 비논리
    - WARN: payoff 가 앞으로만 이동 — 계획 재조정, 정상
    """
    errors: list[str] = []
    warnings: list[str] = []
    payoff_history: dict[str, list[tuple[int, int]]] = {}  # sp -> [(ch, payoff)]
    for ch_dir in sorted(STATE.glob("chapter-*")):
        try:
            ch_num = int(ch_dir.name.split("-")[-1])
        except ValueError:
            continue
        fp = ch_dir / "open-threads.yaml"
        if not fp.exists():
            continue
        try:
            data = yaml.safe_load(fp.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        for t in (data.get("threads") or []):
            sp = t.get("id")
            payoff = t.get("planned_payoff_chapter")
            if sp and payoff is not None:
                payoff_history.setdefault(sp, []).append((ch_num, payoff))
    for sp, hist in payoff_history.items():
        hist.sort()
        prev_payoff = None
        direction_changes: list[tuple[int, int, int]] = []  # (ch, prev, new)
        for ch, p in hist:
            if prev_payoff is not None and p != prev_payoff:
                direction_changes.append((ch, prev_payoff, p))
                if p < prev_payoff and p <= ch:
                    errors.append(
                        f"SP {sp}: ch{ch} 에서 payoff 가 {prev_payoff} → {p} 로 뒤이동하며 이미 지나간 ch{ch} 이하 — 비논리"
                    )
            prev_payoff = p
        if direction_changes and not errors:
            changes_str = ", ".join(f"ch{c}: {pp}→{np}" for c, pp, np in direction_changes)
            warnings.append(f"SP {sp} payoff 계획 재조정: {changes_str} (정상 — 서사 진화)")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, help="특정 챕터만 검증")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    if args.chapter is not None:
        d = STATE / f"chapter-{args.chapter:02d}"
        if not d.exists():
            print(f"[validate_state] {d} 없음", file=sys.stderr)
            return 2
        errors.extend(validate_chapter(d))
    else:
        for d in sorted(STATE.glob("chapter-*")):
            errors.extend(validate_chapter(d))
        e2, w2 = validate_sp_consistency()
        errors.extend(e2)
        warnings.extend(w2)

    for w in warnings:
        print(f"[validate_state] WARN: {w}")
    if errors:
        print(f"[validate_state] {len(errors)} 개 오류:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"[validate_state] 전부 정상 (warnings: {len(warnings)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
