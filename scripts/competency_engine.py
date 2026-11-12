#!/usr/bin/env python3
"""Deterministic competency proficiency judgement (C0-C5).

Usage: python competency_engine.py evidence.json [--json]
Exit codes: 0 judged, 1 invalid input, 2 argument/parse error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from v3_rules import ENUMS, SCORE_DIMENSIONS, validate_practice_evidence
from deeplearn_rules import err


def judge(evidence, current="C0"):
    errors = []
    validate_practice_evidence(evidence, errors, "evidence")
    if errors:
        return None, errors
    scores = evidence["scores"]
    independence = scores["independence"]
    anomaly = scores["anomaly_handling"]
    reasoning = scores["reasoning"]
    executed = evidence["execution_status"] == "executed"
    objective = evidence["evidence_source"] == "objective_assessment"
    hints = evidence["hint_level_used"]
    etypes = set(evidence.get("evidence_types", []) or [])
    result = evidence.get("result", "fail")

    if result != "pass" or not objective:
        level, why = "C0", "未通过或非客观测评证据"
    elif hints == 3 or independence == 0:
        level, why = "C2", "提示依赖为 3 或独立完成度为 0，最高 C2"
    elif reasoning == 0:
        level, why = "C1", "推理过程不可复核"
    elif not executed:
        level, why = "C3", "未实际执行，最高 C3，且不得支撑 C4/C5"
    elif anomaly == 0:
        level, why = "C3", "缺少异常处理证据"
    elif anomaly >= 1 and (etypes & {"anomaly_resolution", "constrained_task_completion"}):
        level, why = "C4", "已执行且独立处理异常/约束"
    elif etypes & {"cross_scenario_transfer", "independent_project"}:
        level, why = "C5", "已执行、可迁移并给出优化/方案比较证据"
    else:
        level, why = "C3", "独立完成标准任务"

    order = ["C0", "C1", "C2", "C3", "C4", "C5"]
    downgraded = order.index(level) < order.index(current) if current in order else False
    return {"suggested_level": level, "current_level": current,
            "downgraded": downgraded, "reason": why,
            "blocking_for_c4_c5": not (executed and independence > 0 and anomaly > 0),
            "scores_used": {d: scores[d] for d in SCORE_DIMENSIONS}}, []


def main() -> int:
    parser = argparse.ArgumentParser(description="V3 能力等级判定")
    parser.add_argument("path", help="PracticeEvidence JSON，'-' 表示 stdin")
    parser.add_argument("--current", default="C0")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
        doc = json.loads(raw)
        result, errors = judge(doc, args.current)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2
    if errors:
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
