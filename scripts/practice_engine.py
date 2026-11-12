#!/usr/bin/env python3
"""Practice task type recommendation + structural validation.

Usage:
  python practice_engine.py recommend context.json [--json]
  python practice_engine.py validate task.json [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import err
from v3_rules import ENUMS, validate_practice_task

STATE_TO_PRACTICE = {
    "unexposed": ("concept", "intuition"),
    "exposed_not_able": ("derivation", "diagram"),
    "understands": ("calculation", "socratic"),
    "independent_application": ("experiment", "code"),
    "transfer_capable": ("cross_domain_transfer", "reverse_teaching"),
    "stable_long_term": ("project", "case"),
}
HINT_TEMPLATE = [
    "方向提示：先判断本题应使用哪一类原理或工具。",
    "关键机制提示：点明核心关系，但不给具体步骤。",
    "局部步骤提示：给出第一步或局部推导，仍不给完整解答。",
]


def recommend(ctx):
    state = ctx.get("knowledge_state")
    if state not in STATE_TO_PRACTICE:
        raise ValueError(f"knowledge_state 非法：{state}")
    practice, modality = STATE_TO_PRACTICE[state]
    if ctx.get("domain") in ("electronics", "control", "physics", "embedded"):
        practice = "simulation" if practice == "experiment" and not ctx.get("can_execute") else practice
    hint_policy = "after_attempt" if ctx.get("attempted") else "hidden"
    return {"practice_type": practice, "teaching_modality": modality,
            "hints": HINT_TEMPLATE, "solution_visibility": hint_policy,
            "target_node_ids": ctx.get("target_node_ids", []),
            "target_competencies": ctx.get("target_competencies", []),
            "reason": f"knowledge_state={state} 与 domain={ctx.get('domain')} 决定练习类型"}


def validate(task):
    errors = []
    validate_practice_task(task, errors, "task")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="V3 练习引擎")
    parser.add_argument("command", choices=("recommend", "validate"))
    parser.add_argument("path", help="JSON 文件，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
        doc = json.loads(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2
    if args.command == "recommend":
        try:
            result = recommend(doc)
        except ValueError as exc:
            print(f"推荐失败：{exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    errors = validate(doc)
    print(json.dumps({"errors": errors, "valid": not errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
