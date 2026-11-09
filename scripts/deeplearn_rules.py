#!/usr/bin/env python3
"""DeepLearn V2 canonical enums and shared structural helpers.

This module is the executable counterpart of core/data-schema.md.
All validators import from here so enums and required fields have one
source of truth. Standard library only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ID_RE = re.compile(r"NODE-\d{3,}")
PROJECT_RE = re.compile(r"PROJECT-\d{3,}")
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

ENUMS = {
    "node_type": {
        "concept", "mechanism", "principle", "axiom", "law", "model", "procedure",
        "tool", "component", "interface", "protocol", "skill",
        "project_deliverable", "question",
    },
    "learning_category": {
        "academic_subject", "individual_concept", "technical_domain",
        "software_tool", "specific_problem", "practical_project", "competency",
    },
    "dependency_type": {
        "conceptual_dependency", "mathematical_dependency", "physical_dependency",
        "operational_dependency", "implementation_dependency",
    },
    "necessity": {"required", "recommended"},
    "importance": {"essential", "optional", "extension"},
    "practical_value": {"high", "medium", "low"},
    "confidence": {"unassessed", "provisional", "supported", "strong"},
    "review_status": {"not_scheduled", "scheduled", "due", "completed", "postponed"},
    "project_status": {"active", "paused", "completed", "archived"},
    "learning_mode": {"Explore", "Deep Dive", "Learn", "Decompose", "Build", "Diagnose"},
    "learning_intent": {"understand", "use", "research", "build", "solve", "master", "exam"},
    "assessment_type": {
        "recall", "explanation", "application", "derivation", "debugging",
        "prediction", "counterexample", "reverse_teaching",
        "cross_domain_transfer", "changed_condition_transfer",
    },
    "atomic_gate_status": {"passed", "failed", "not_applicable"},
    "evidence_result": {"pass", "partial", "fail"},
    "project_event": {
        "project_created", "classification_confirmed", "map_generated",
        "graph_changed", "lesson_completed", "assessment_completed",
        "mastery_updated", "misconception_found", "roadmap_changed",
        "review_completed",
    },
}

MASTERY_LEVELS = set(range(6))
DIFFICULTY = set(range(1, 6))
DECOMPOSITION_LEVELS = set(range(0, 7))

NODE_REQUIRED = {
    "id", "name", "description", "node_type", "learning_category",
    "decomposition_level", "difficulty", "importance", "time_estimate",
    "practical_value", "version",
}
PROGRESS_REQUIRED = {
    "project_id", "node_id", "mastery_level", "confidence", "review_status",
}
EDGE_REQUIRED = {
    "source_node_id", "target_node_id", "dependency_type", "necessity", "explanation",
}
EVIDENCE_REQUIRED = {
    "node_id", "assessment_type", "result", "date", "mastery_decision", "confidence",
}
QUALITY_DIMENSIONS = (
    "completeness", "independence", "dependency_correctness",
    "explanatory_depth", "verifiability", "boundary_clarity",
)
CRITICAL_DIMENSIONS = {"dependency_correctness", "explanatory_depth", "verifiability"}
ATOMIC_GATE_KEYS = (
    "why_exists", "problem_solved", "depends_on",
    "why_valid", "derivable", "verifiable",
)


def load_json(path: str):
    """Return parsed JSON, raising ValueError with a readable message."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"读取失败：{exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析失败：{exc}") from exc


def is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def err(errors: list, code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def validate_node_structure(node: dict, errors: list, where: str = "node") -> None:
    """Field-level validation of a KnowledgeNode. Graph-level checks live in validate_map.py."""
    if not isinstance(node, dict):
        err(errors, "node_not_object", f"{where}: 节点必须是对象")
        return
    missing = sorted(NODE_REQUIRED - set(node))
    if missing:
        err(errors, "missing_fields", f"{where}: 缺少必填字段 {', '.join(missing)}")
    node_id = node.get("id")
    if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id or ""):
        err(errors, "invalid_id", f"{where}: id 必须形如 NODE-001，实际为 {node_id!r}")
    for field, allowed in (
        ("node_type", ENUMS["node_type"]),
        ("learning_category", ENUMS["learning_category"]),
        ("importance", ENUMS["importance"]),
        ("practical_value", ENUMS["practical_value"]),
    ):
        if field in node and node[field] not in allowed:
            err(errors, "invalid_enum", f"{where}: {field}={node[field]!r} 不在枚举内")
    for field, allowed in (
        ("difficulty", DIFFICULTY),
        ("decomposition_level", DECOMPOSITION_LEVELS),
    ):
        if field in node and (not is_int(node[field]) or node[field] not in allowed):
            err(errors, "invalid_range", f"{where}: {field} 取值非法 {node[field]!r}")
    if "version" in node and (not is_int(node["version"]) or node["version"] < 1):
        err(errors, "invalid_version", f"{where}: version 必须是 >=1 的整数")
    estimate = node.get("time_estimate")
    if not isinstance(estimate, dict):
        err(errors, "invalid_time_estimate", f"{where}: time_estimate 必须是对象")
    else:
        lo, hi = estimate.get("min_hours"), estimate.get("max_hours")
        if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)) or lo <= 0 or hi < lo:
            err(errors, "invalid_time_estimate", f"{where}: 需满足 0 < min_hours <= max_hours")
    for field in ("aliases", "children", "prerequisites", "related_nodes", "objectives",
                  "principles", "trace_chain", "applications", "limitations",
                  "verification_methods", "dependency_edges"):
        if field in node and not isinstance(node[field], list):
            err(errors, "invalid_type", f"{where}: {field} 必须是数组")
    gate = node.get("atomic_gate")
    if gate is not None:
        if not isinstance(gate, dict):
            err(errors, "invalid_gate", f"{where}: atomic_gate 必须是对象")
        else:
            for key, value in gate.items():
                if key not in ATOMIC_GATE_KEYS:
                    err(errors, "invalid_gate", f"{where}: 未知验收项 {key}")
                    continue
                status = value.get("status") if isinstance(value, dict) else None
                if status not in ENUMS["atomic_gate_status"]:
                    err(errors, "invalid_gate", f"{where}: {key}.status 非法")
                elif status in ("failed", "not_applicable"):
                    note = value.get("note", "") if isinstance(value, dict) else ""
                    if status == "failed":
                        err(errors, "gate_failed", f"{where}: 六问验收项 {key} 未通过")
                    elif not note:
                        err(errors, "gate_missing_note", f"{where}: {key} 标为不适用必须给理由")
    quality = node.get("decomposition_quality")
    if quality is not None:
        if not isinstance(quality, dict):
            err(errors, "invalid_quality", f"{where}: decomposition_quality 必须是对象")
        else:
            vals = []
            for dim in QUALITY_DIMENSIONS:
                v = quality.get(dim)
                if not is_int(v) or v < 0 or v > 2:
                    err(errors, "invalid_quality", f"{where}: {dim} 必须是 0–2 整数")
                else:
                    vals.append(v)
            if len(vals) == len(QUALITY_DIMENSIONS) and quality.get("total") != sum(vals):
                err(errors, "invalid_quality", f"{where}: total 与六维之和不一致")
            for dim in CRITICAL_DIMENSIONS:
                if is_int(quality.get(dim)) and quality[dim] < 2:
                    err(errors, "gate_failed", f"{where}: 关键维度 {dim} 低于 2，禁止进入路线图")


def validate_edge_structure(edge: dict, errors: list, where: str = "edge") -> None:
    if not isinstance(edge, dict):
        err(errors, "edge_not_object", f"{where}: 依赖边必须是对象")
        return
    missing = sorted(EDGE_REQUIRED - set(edge))
    if missing:
        err(errors, "missing_fields", f"{where}: 缺少必填字段 {', '.join(missing)}")
    for field, allowed in (
        ("dependency_type", ENUMS["dependency_type"]),
        ("necessity", ENUMS["necessity"]),
    ):
        if field in edge and edge[field] not in allowed:
            err(errors, "invalid_enum", f"{where}: {field}={edge[field]!r} 不在枚举内")
    if not edge.get("explanation"):
        err(errors, "missing_explanation", f"{where}: 必须说明为什么必须先掌握")
    if edge.get("source_node_id") == edge.get("target_node_id"):
        err(errors, "self_loop", f"{where}: 自环不允许")


def validate_progress_structure(progress: dict, errors: list, where: str = "progress") -> None:
    if not isinstance(progress, dict):
        err(errors, "progress_not_object", f"{where}: 进度必须是对象")
        return
    missing = sorted(PROGRESS_REQUIRED - set(progress))
    if missing:
        err(errors, "missing_fields", f"{where}: 缺少必填字段 {', '.join(missing)}")
    pid = progress.get("project_id")
    if not isinstance(pid, str) or not PROJECT_RE.fullmatch(pid or ""):
        err(errors, "invalid_id", f"{where}: project_id 必须形如 PROJECT-001")
    nid = progress.get("node_id")
    if not isinstance(nid, str) or not ID_RE.fullmatch(nid or ""):
        err(errors, "invalid_id", f"{where}: node_id 必须形如 NODE-001")
    level = progress.get("mastery_level")
    if not is_int(level) or level not in MASTERY_LEVELS:
        err(errors, "invalid_mastery", f"{where}: mastery_level 必须是 0–5")
    for field, allowed in (
        ("confidence", ENUMS["confidence"]),
        ("review_status", ENUMS["review_status"]),
    ):
        if field in progress and progress[field] not in allowed:
            err(errors, "invalid_enum", f"{where}: {field}={progress[field]!r} 不在枚举内")
    for field, pattern in (("last_assessed", ISO_DATE_RE), ("next_review", ISO_DATE_RE)):
        value = progress.get(field)
        if value is not None and (not isinstance(value, str) or not pattern.fullmatch(value)):
            err(errors, "invalid_date", f"{where}: {field} 必须是 YYYY-MM-DD 或 null")
    evidence = progress.get("evidence", [])
    if not isinstance(evidence, list):
        err(errors, "invalid_type", f"{where}: evidence 必须是数组")
    else:
        for i, item in enumerate(evidence):
            if not isinstance(item, dict):
                err(errors, "invalid_evidence", f"{where}: evidence[{i}] 必须是对象")
                continue
            miss = sorted(EVIDENCE_REQUIRED - set(item))
            if miss:
                err(errors, "invalid_evidence", f"{where}: evidence[{i}] 缺字段 {', '.join(miss)}")
            if item.get("assessment_type") not in ENUMS["assessment_type"]:
                err(errors, "invalid_enum", f"{where}: evidence[{i}].assessment_type 非法")
            if item.get("result") not in ENUMS["evidence_result"]:
                err(errors, "invalid_enum", f"{where}: evidence[{i}].result 非法")
            if item.get("confidence") not in ENUMS["confidence"]:
                err(errors, "invalid_enum", f"{where}: evidence[{i}].confidence 非法")
    for field in ("misconceptions", "learning_history"):
        if field in progress and not isinstance(progress[field], list):
            err(errors, "invalid_type", f"{where}: {field} 必须是数组")


def markdown_links(root: Path):
    """Yield (source_file, link_target) for relative markdown links."""
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig")
        for target in link_re.findall(text):
            clean = target.split("#", 1)[0].strip()
            if not clean or re.match(r"^(?:https?://|mailto:)", clean):
                continue
            yield path, clean


def emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    for issue in result.get("errors", []):
        print(f"错误 [{issue['code']}] {issue['message']}")
    for issue in result.get("warnings", []):
        print(f"警告 [{issue['code']}] {issue['message']}")
    for key, value in result.get("stats", {}).items():
        print(f"{key}: {value}")
    print(result.get("summary", "校验完成"))
