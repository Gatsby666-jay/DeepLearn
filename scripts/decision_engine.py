#!/usr/bin/env python3
"""Unified adaptive decision engine (deterministic, testable).

Input:  a decision context JSON (goal, nodes, competencies, errors, review,
        preferences, time constraint).
Output: nine decision fields plus a short reason and a priority trace.

Usage: python decision_engine.py context.json [--json] [--output plan.json]
Exit codes: 0 decision produced, 1 blocking validation, 2 argument/parse error.

Time constraint is an actual decision input, not a pass-through field:
when time_constraint_hours is a positive number <= TIGHT_BUDGET_HOURS,
optional expansion (P6) is suppressed to a minimal viable subset and the
reason records the constraint. Mandatory prerequisite repair (P1) and
recurring-misconception remediation (P2) are never skipped for time reasons.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from v3_rules import ENUMS, SCHEMA_VERSION

PRIORITY = [
    "P1_blocking_prerequisite_gap", "P2_recurring_misconception",
    "P3_important_review_due", "P4_key_knowledge_for_goal",
    "P5_practice_for_competency", "P6_optional_expansion",
]

TIGHT_BUDGET_HOURS = 2


class BlockingValidation(ValueError):
    """Business-level validation failure, reported with exit code 1."""


def decide(ctx):
    if not isinstance(ctx, dict):
        raise BlockingValidation("决策上下文必须是对象")

    nodes = ctx.get("nodes", []) or []
    comps = ctx.get("competency_progress", []) or []
    errors = ctx.get("common_errors", []) or []
    prefs = ctx.get("preferences", {}) or {}
    if not isinstance(prefs, dict):
        raise BlockingValidation("preferences 必须是对象：键为教学表征，数值为权重")

    time_raw = ctx.get("time_constraint_hours")
    if time_raw is not None:
        if isinstance(time_raw, bool) or not isinstance(time_raw, (int, float)) or time_raw <= 0:
            raise BlockingValidation("time_constraint_hours 必须是正数（小时）")
    tight = isinstance(time_raw, (int, float)) and 0 < time_raw <= TIGHT_BUDGET_HOURS

    gaps = [n for n in nodes if (n.get("prerequisite_gaps") or [])
            and any(g.get("necessity", "required") == "required"
                    for g in n["prerequisite_gaps"] if isinstance(g, dict))]
    recurring = [e for e in errors if (e.get("count", 0) or 0) >= 2]
    review_due = [n for n in nodes if n.get("review_status") == "due"
                  and n.get("importance") == "essential"]
    weak = [n for n in nodes if (n.get("mastery_level", 0) or 0) < 3
            and n.get("importance") == "essential"]
    low_comp = [c for c in comps if c.get("proficiency_level") in ("C0", "C1", "C2")]

    if gaps:
        priority, problem = PRIORITY[0], "存在阻塞性前置缺口"
        next_node = gaps[0].get("prerequisite_gaps", [{}])[0].get("node_id") or gaps[0].get("node_id")
        repair, review, project, advance = True, False, False, False
        modality, practice = "intuition", "concept"
    elif recurring:
        priority, problem = PRIORITY[1], "同一核心误解反复出现"
        next_node = recurring[0].get("node_id") or (nodes[0].get("node_id") if nodes else None)
        repair, review, project, advance = True, False, False, False
        modality, practice = "socratic", "debug"
    elif review_due:
        priority, problem = PRIORITY[2], "重要知识到期且有遗忘风险"
        next_node = review_due[0].get("node_id")
        repair, review, project, advance = False, True, False, False
        modality, practice = "reverse_teaching", "concept"
    elif weak:
        priority, problem = PRIORITY[3], "推进当前目标所需的关键知识"
        next_node = weak[0].get("node_id")
        repair, review, project, advance = False, False, False, True
        modality, practice = "derivation", "calculation"
    elif low_comp:
        priority, problem = PRIORITY[4], "知识已达标但能力不足，需通过实践建立能力"
        next_node = nodes[0].get("node_id") if nodes else None
        repair, review, project, advance = False, False, True, True
        modality, practice = "code", "project"
    else:
        priority, problem = PRIORITY[5], "主干达标，可扩展选修与探索"
        next_node = nodes[0].get("node_id") if nodes else None
        repair, review, project, advance = False, False, False, True
        modality, practice = "case", "cross_domain_transfer"

    if prefs:
        best = max(prefs.items(), key=lambda kv: kv[1] if isinstance(kv[1], (int, float)) else 0)[0]
        if best in ENUMS["teaching_modality"] and priority in (PRIORITY[3], PRIORITY[5]):
            modality = best

    evidence_signals = {
        "node_count": len(nodes), "competency_count": len(comps),
        "recurring_errors": len(recurring), "review_due": len(review_due),
        "weak_nodes": len(weak), "low_competencies": len(low_comp),
    }
    if sum(evidence_signals.values()) < 1:
        raise BlockingValidation("决策上下文无任何可用信号，禁止输出决策")

    reason = f"{problem}；依据 {evidence_signals} 与六类信号，按优先级 {priority} 决定。"
    decision = {
        "current_problem": problem, "next_node_id": next_node,
        "needs_review": "yes" if review else "no",
        "needs_prerequisite_repair": "yes" if repair else "no",
        "teaching_modality": modality, "practice_type": practice,
        "enter_project_practice": "yes" if project else "no",
        "allow_advance": "yes" if advance and not repair else "no",
        "reason": reason,
    }

    if tight:
        if priority == PRIORITY[5]:
            decision["allow_advance"] = "no"
            decision["enter_project_practice"] = "no"
            decision["practice_type"] = "concept"
            decision["reason"] = reason + (
                f"；时间约束 {time_raw}h ≤ {TIGHT_BUDGET_HOURS}h，仅安排最小可达子集，跳过选修与延展")
        else:
            decision["reason"] = reason + (
                f"；时间约束 {time_raw}h ≤ {TIGHT_BUDGET_HOURS}h，优先必修节点，不跳过 P1/P2 补救")

    trace = {"priority": priority, "trace": PRIORITY[:PRIORITY.index(priority) + 1],
             "signals": evidence_signals, "time_constraint_hours": time_raw,
             "time_constraint_applied": bool(tight)}
    return decision, trace


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepLearn V3 统一自适应决策引擎")
    parser.add_argument("path", help="决策上下文 JSON，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="可选：写出 LearningPlan JSON")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2
    try:
        ctx = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"JSON 解析失败：{exc}", file=sys.stderr)
        return 2
    try:
        decision, trace = decide(ctx)
    except BlockingValidation as exc:
        print(f"阻塞性校验未通过：{exc}", file=sys.stderr)
        return 1
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        print(f"上下文结构错误：{exc}", file=sys.stderr)
        return 2
    plan = {"plan_id": "PLAN-001", "project_id": ctx.get("project_id", "PROJECT-001"),
            "version": 1, "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "goal": ctx.get("goal", ""),
            "decision": decision, "stages": [], "next_action": decision["next_node_id"],
            "reason": decision["reason"], "schema_version": SCHEMA_VERSION,
            "source": "decision_engine", "priority_trace": trace}
    if args.output:
        Path(args.output).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps({"decision": decision, "trace": trace, "plan": plan},
                         ensure_ascii=False, indent=2))
    else:
        for key, value in decision.items():
            print(f"{key}: {value}")
        print("priority:", trace["priority"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
