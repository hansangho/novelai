#!/usr/bin/env python3
"""
State / Timeline Validator.

State Updater 가 챕터 확정 후, 또는 /gate-status 가 호출될 때 실행한다.
검사 항목:

기본 (v1):
  - YAML 문법
  - 필수 키
  - SP payoff_chapter 단조성 (뒤로 이동 = ERROR, 앞으로 이동 = WARN)

확장 (v1.6):
  - 시간 흐름: completed_at 이 챕터 번호와 단조 증가
  - 인물 등장 누적: 후속 챕터의 character 가 갑자기 사라지면 WARN
  - 관계 비대칭: 양방향 trust 차이가 큰 경우 의도 확인
  - last_hinted ≤ 현재 챕터, payoff > 현재 챕터 또는 status=closed

사용:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_state.py [--chapter N]
"""

from __future__ import annotations

import argparse
import datetime
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

ASYMMETRY_THRESHOLD = 4  # trust 양방향 차이 임계


def parse_dt(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(str(s))
    except (TypeError, ValueError):
        return None


def validate_yaml(path: Path) -> tuple[list[str], dict | None]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"YAML 문법: {e.__class__.__name__}: {e}")
        return errors, None
    if data is None:
        errors.append("빈 문서")
        return errors, None
    required = REQUIRED_TOP_KEYS.get(path.name, set())
    missing = required - set(data.keys())
    if missing:
        errors.append(f"필수 키 누락: {sorted(missing)}")
    return errors, data


def load_chapter(ch_dir: Path) -> tuple[list[str], dict]:
    """챕터 디렉토리의 모든 YAML 로드. (errors, {filename: data})"""
    errors: list[str] = []
    loaded: dict = {}
    for fname in REQUIRED_TOP_KEYS:
        fp = ch_dir / fname
        if not fp.exists():
            errors.append(f"{ch_dir.name}/{fname}: 파일 없음")
            continue
        e, data = validate_yaml(fp)
        for msg in e:
            errors.append(f"{ch_dir.name}/{fname}: {msg}")
        if data is not None:
            loaded[fname] = data
    return errors, loaded


def validate_temporal(chapters: list[dict]) -> tuple[list[str], list[str]]:
    """챕터들의 completed_at 시각이 챕터 번호와 단조 증가인지."""
    errors: list[str] = []
    warnings: list[str] = []
    prev_ch = None
    prev_dt = None
    for ch_data in chapters:
        ch_num = ch_data.get("ch_num")
        completed = ch_data.get("loaded", {}).get("character-states.yaml", {}).get("completed_at")
        dt = parse_dt(completed)
        if dt is None and completed not in (None, "null", ""):
            warnings.append(f"ch{ch_num:02d}: completed_at 파싱 실패 ({completed!r})")
        if prev_dt and dt and dt < prev_dt:
            warnings.append(
                f"ch{ch_num:02d} completed_at ({dt.isoformat()}) < ch{prev_ch:02d} ({prev_dt.isoformat()}). "
                f"State Updater 시각 vs 서사 시간이 혼동된 듯."
            )
        if dt:
            prev_ch, prev_dt = ch_num, dt
    return errors, warnings


def validate_character_continuity(chapters: list[dict]) -> tuple[list[str], list[str]]:
    """후속 챕터에서 등장하던 캐릭터가 사라지면 WARN."""
    errors: list[str] = []
    warnings: list[str] = []
    seen_so_far: set[str] = set()
    for ch_data in chapters:
        ch_num = ch_data.get("ch_num")
        char_data = ch_data.get("loaded", {}).get("character-states.yaml", {}).get("characters") or {}
        current = set(char_data.keys())
        if seen_so_far and not seen_so_far.issubset(current):
            missing = seen_so_far - current
            # 누락된 인물이 단순히 "이번 챕터 등장 안 함" 일 수 있으므로 WARN
            warnings.append(
                f"ch{ch_num:02d}: 이전 챕터까지 등장했던 캐릭터 {sorted(missing)} 가 본 state 에 없음. "
                f"등장 없으면 명시적으로 'physical.location: 불명 (배경)' 식으로 둘 것 권장."
            )
        seen_so_far |= current
    return errors, warnings


def validate_relationship_asymmetry(chapters: list[dict]) -> tuple[list[str], list[str]]:
    """trust 양방향 차이가 임계 초과면 WARN (의도된 비대칭일 수도, 단순 오류일 수도)."""
    errors: list[str] = []
    warnings: list[str] = []
    for ch_data in chapters:
        ch_num = ch_data.get("ch_num")
        rel = ch_data.get("loaded", {}).get("relationships.yaml", {}).get("relationships") or []
        # (a→b) trust 와 (b→a) trust 비교
        index = {(r.get("from"), r.get("to")): r.get("trust") for r in rel if r.get("trust") is not None}
        seen_pairs = set()
        for (a, b), t1 in index.items():
            if not a or not b:
                continue
            if (a, b) in seen_pairs:
                continue
            seen_pairs.add((a, b))
            t2 = index.get((b, a))
            if t2 is not None and abs(t1 - t2) >= ASYMMETRY_THRESHOLD:
                warnings.append(
                    f"ch{ch_num:02d}: {a}↔{b} trust 비대칭 큼 ({a}→{b}={t1}, {b}→{a}={t2}). "
                    f"의도된 것이면 relationships.yaml 의 note 필드에 '비대칭 의도' 기록 권장."
                )
    return errors, warnings


def validate_sp_constraints(chapters: list[dict]) -> tuple[list[str], list[str]]:
    """SP 의 last_hinted, payoff 범위 검증.
    - last_hinted_at_chapter ≤ 현재 챕터
    - status='open' 또는 'partial' 인 SP 는 payoff > 현재 챕터
    - status='closed' 면 payoff 가 현재 챕터 ≤
    """
    errors: list[str] = []
    warnings: list[str] = []
    for ch_data in chapters:
        ch_num = ch_data.get("ch_num")
        threads = ch_data.get("loaded", {}).get("open-threads.yaml", {}).get("threads") or []
        for t in threads:
            sp = t.get("id", "?")
            last_hint = t.get("last_hinted_at_chapter")
            payoff = t.get("planned_payoff_chapter")
            status = t.get("status")
            if last_hint is not None and last_hint > ch_num:
                errors.append(f"ch{ch_num:02d} SP {sp}: last_hinted_at_chapter ({last_hint}) > 현재 챕터")
            if status in ("open", "partial") and payoff is not None and payoff <= ch_num:
                warnings.append(
                    f"ch{ch_num:02d} SP {sp}: status={status} 인데 payoff={payoff} ≤ 현재. "
                    f"이미 회수돼야 할 시점인데 미해결로 표기 — status 갱신 필요."
                )
            if status == "closed" and payoff is not None and payoff > ch_num:
                warnings.append(
                    f"ch{ch_num:02d} SP {sp}: status=closed 인데 payoff={payoff} > 현재. 모순."
                )
    return errors, warnings


def validate_sp_payoff_history(chapters: list[dict]) -> tuple[list[str], list[str]]:
    """payoff 가 뒤로 이동하면 ERROR (이미 지난 챕터보다 작은 값). 앞으로만 이동하면 WARN."""
    errors: list[str] = []
    warnings: list[str] = []
    payoff_history: dict[str, list[tuple[int, int]]] = {}
    for ch_data in chapters:
        ch_num = ch_data.get("ch_num")
        threads = ch_data.get("loaded", {}).get("open-threads.yaml", {}).get("threads") or []
        for t in threads:
            sp = t.get("id")
            payoff = t.get("planned_payoff_chapter")
            if sp and payoff is not None:
                payoff_history.setdefault(sp, []).append((ch_num, payoff))
    for sp, hist in payoff_history.items():
        hist.sort()
        prev_payoff = None
        direction_changes: list[tuple[int, int, int]] = []
        for ch, p in hist:
            if prev_payoff is not None and p != prev_payoff:
                direction_changes.append((ch, prev_payoff, p))
                if p < prev_payoff and p <= ch:
                    errors.append(
                        f"SP {sp}: ch{ch} 에서 payoff 가 {prev_payoff} → {p} 로 뒤이동하며 ch{ch} 이하 — 비논리"
                    )
            prev_payoff = p
        if direction_changes and not [e for e in errors if sp in e]:
            changes_str = ", ".join(f"ch{c}: {pp}→{np}" for c, pp, np in direction_changes)
            warnings.append(f"SP {sp} payoff 계획 재조정: {changes_str} (정상 — 서사 진화)")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, help="특정 챕터만 검증")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    chapters: list[dict] = []
    if args.chapter is not None:
        d = STATE / f"chapter-{args.chapter:02d}"
        if not d.exists():
            print(f"[validate_state] {d} 없음", file=sys.stderr)
            return 2
        e, loaded = load_chapter(d)
        errors.extend(e)
        chapters.append({"ch_num": args.chapter, "loaded": loaded})
    else:
        for d in sorted(STATE.glob("chapter-*")):
            try:
                ch_num = int(d.name.split("-")[-1])
            except ValueError:
                continue
            e, loaded = load_chapter(d)
            errors.extend(e)
            chapters.append({"ch_num": ch_num, "loaded": loaded})

    # 의미적 검증 (전 챕터 대상)
    if not args.chapter:
        for fn in (validate_temporal, validate_character_continuity,
                   validate_relationship_asymmetry, validate_sp_constraints,
                   validate_sp_payoff_history):
            e, w = fn(chapters)
            errors.extend(e)
            warnings.extend(w)
    else:
        # 단일 챕터 검증 시는 SP 제약만
        e, w = validate_sp_constraints(chapters)
        errors.extend(e)
        warnings.extend(w)

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
