#!/usr/bin/env python3
"""Validate V3 structures and all cross-module references.

Usage: python validate_v3_schema.py file.json [more.json ...] [--json]
Exit codes: 0 valid, 1 validation errors, 2 argument/parse error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import emit, err
from v3_rules import VALIDATORS, ENUMS, ID_PATTERNS, check_id

CONTAINER_KEYS = {
    "profile": "learner_profile", "learner_profile": "learner_profile",
    "competencies": "competency", "competency_progress": "competency_progress",
    "events": "learning_event", "learning_events": "learning_event",
    "practice_tasks": "practice_task", "practice_evidence": "practice_evidence",
    "learning_plan": "learning_plan", "graph_changes": "knowledge_graph_change",
    "resources": "resource", "assessment_results": "assessment_result",
    "knowledge_nodes": "v2_node", "progress": "v2_progress",
}


def detect(obj):
    if not isinstance(obj, dict):
        return None
    keys = set(obj)
    if "competency_id" in keys and "proficiency_level" in keys:
        return "competency_progress"
    if "competency_id" in keys:
        return "competency"
    if "profile_id" in keys:
        return "learner_profile"
    if "event_id" in keys:
        return "learning_event"
    if "exercise_id" in keys and "scores" not in keys:
        return "practice_task"
    if "evidence_id" in keys:
        return "practice_evidence"
    if "plan_id" in keys:
        return "learning_plan"
    if "change_id" in keys:
        return "knowledge_graph_change"
    if "resource_id" in keys:
        return "resource"
    if "assessment_id" in keys:
        return "assessment_result"
    if "node_id" in keys and "mastery_level" in keys:
        return "v2_progress"
    if "id" in keys and "node_type" in keys:
        return "v2_node"
    return None


def collect(doc, errors):
    found = {}
    if isinstance(doc, list):
        items = [("item", x) for x in doc]
    elif isinstance(doc, dict):
        single = detect(doc)
        if single:
            found.setdefault(single, []).append(doc)
            return found
        items = list(doc.items())
    else:
        err(errors, "invalid_document", "顶层必须是对象或数组")
        return found
    for key, value in items:
        values = value if isinstance(value, list) else [value]
        for item in values:
            if not isinstance(item, dict):
                continue
            kind = CONTAINER_KEYS.get(key) or detect(item)
            if kind is None:
                if key not in ("stages", "decision", "versions", "classification",
                               "objective", "goal", "source"):
                    err(errors, "unknown_structure", f"无法识别结构：{key}")
                continue
            found.setdefault(kind, []).append(item)
    return found


def cross_checks(found, errors, warnings):
    node_ids = {n.get("id") for n in found.get("v2_node", []) if isinstance(n, dict)}
    comp_ids = {c.get("competency_id") for c in found.get("competency", []) if isinstance(c, dict)}
    task_ids = {t.get("exercise_id") for t in found.get("practice_task", []) if isinstance(t, dict)}
    if not node_ids:
        warnings.append({"code": "no_nodes", "message": "未声明 KnowledgeNode，跳过节点引用检查"})
    if not comp_ids:
        warnings.append({"code": "no_competencies", "message": "未声明 Competency，跳过能力引用检查"})
    for i, c in enumerate(found.get("competency", [])):
        for nid in c.get("required_knowledge", []) or []:
            if node_ids and nid not in node_ids:
                err(errors, "missing_reference", f"competency#{i}: required_knowledge {nid} 不存在")
    for i, t in enumerate(found.get("practice_task", [])):
        for nid in t.get("target_node_ids", []) or []:
            if node_ids and nid not in node_ids:
                err(errors, "missing_reference", f"task#{i}: target_node_ids {nid} 不存在")
        for cid in t.get("target_competencies", []) or []:
            if comp_ids and cid not in comp_ids:
                err(errors, "missing_reference", f"task#{i}: target_competencies {cid} 不存在")
    for i, e in enumerate(found.get("practice_evidence", [])):
        if task_ids and e.get("exercise_id") not in task_ids:
            err(errors, "missing_reference", f"evidence#{i}: exercise_id 不存在")
        if e.get("execution_status") != "executed" and e.get("evidence_source") == "objective_assessment":
            warnings.append({"code": "unexecuted_objective",
                             "message": f"evidence#{i}: 未实际执行却标为客观测评，需人工复核"})
    for i, c in enumerate(found.get("competency_progress", [])):
        if comp_ids and c.get("competency_id") not in comp_ids:
            err(errors, "missing_reference", f"competency_progress#{i}: competency_id 不存在")
    for i, ch in enumerate(found.get("knowledge_graph_change", [])):
        for nid in ch.get("affected_node_ids", []) or []:
            if node_ids and nid not in node_ids:
                err(errors, "missing_reference", f"change#{i}: affected_node_ids {nid} 不存在")
    for i, r in enumerate(found.get("resource", [])):
        for nid in r.get("relevant_node_ids", []) or []:
            if node_ids and nid not in node_ids:
                err(errors, "missing_reference", f"resource#{i}: relevant_node_ids {nid} 不存在")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 DeepLearn V3 结构与跨模块引用")
    parser.add_argument("paths", nargs="+", help="JSON 文件，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, warnings, found_all, files = [], [], {}, 0
    for path in args.paths:
        try:
            raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
            doc = json.loads(raw)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"读取或解析失败：{exc}", file=sys.stderr)
            return 2
        found = collect(doc, errors)
        for kind, items in found.items():
            validator = VALIDATORS.get(kind)
            for i, item in enumerate(items):
                if validator:
                    validator(item, errors, f"{path}:{kind}#{i}")
            found_all.setdefault(kind, []).extend(items)
        files += 1
    cross_checks(found_all, errors, warnings)
    result = {"errors": errors, "warnings": warnings,
              "stats": {"files": files, "structures": sum(len(v) for v in found_all.values()),
                        "kinds": {k: len(v) for k, v in found_all.items()},
                        "enums": len(ENUMS)},
              "summary": ("校验失败：%d 个错误" % len(errors)) if errors
                         else "校验通过：V3 结构与跨模块引用一致"}
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
