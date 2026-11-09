#!/usr/bin/env python3
"""Validate KnowledgeNode / LearnerProgress JSON against core/data-schema.md.

Usage:
  python validate_schema.py file.json [more.json ...] [--json]
  cat file.json | python validate_schema.py - [--json]

Exit codes: 0 valid, 1 validation errors, 2 argument/parse errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import (
    emit, err, load_json,
    validate_edge_structure, validate_node_structure, validate_progress_structure,
)


def classify(doc):
    """Return (nodes, progress, edges) from the accepted document shapes."""
    nodes, progress, edges = [], [], []
    if isinstance(doc, list):
        for item in doc:
            n, p, e = classify(item)
            nodes += n
            progress += p
            edges += e
        return nodes, progress, edges
    if not isinstance(doc, dict):
        raise ValueError("JSON 顶层必须是对象或数组")
    if "id" in doc and ("node_type" in doc or "decomposition_level" in doc or "time_estimate" in doc):
        return [doc], [], []
    if "nodes" in doc or "progress" in doc or "edges" in doc or "dependency_edges" in doc:
        raw_nodes = doc.get("nodes", [])
        if isinstance(raw_nodes, dict):
            raw_nodes = [raw_nodes]
        if isinstance(raw_nodes, list):
            nodes = [x for x in raw_nodes if isinstance(x, dict)]
        for key in ("edges", "dependency_edges"):
            for edge in doc.get(key, []) or []:
                edges.append(edge)
        raw_progress = doc.get("progress", [])
        if isinstance(raw_progress, dict):
            raw_progress = [raw_progress]
        progress = [x for x in raw_progress if isinstance(x, dict)]
        return nodes, progress, edges
    keys = set(doc)
    if "mastery_level" in keys or "review_status" in keys:
        return [], [doc], []
    if "source_node_id" in keys:
        return [], [], [doc]
    return [doc], [], []


def cross_checks(nodes, progress, edges, errors, warnings):
    ids = [n.get("id") for n in nodes if isinstance(n.get("id"), str)]
    id_set = set(ids)
    if len(ids) != len(id_set):
        dup = sorted({x for x in ids if ids.count(x) > 1})
        err(errors, "duplicate_node_ids", f"重复节点 ID：{', '.join(dup)}")
    if not id_set:
        warnings.append({"code": "no_nodes", "message": "未提供节点，跳过引用一致性检查"})
        return
    for i, node in enumerate(nodes):
        where = f"{node.get('id', 'node#' + str(i))}"
        for field in ("parent_id", "canonical_id"):
            value = node.get(field)
            if value is not None and value not in id_set:
                err(errors, "missing_reference", f"{where}: {field} 指向不存在的节点 {value}")
        for field in ("children", "prerequisites", "related_nodes"):
            for ref in node.get(field, []) or []:
                if ref not in id_set:
                    err(errors, "missing_reference", f"{where}: {field} 指向不存在的节点 {ref}")
        parent = node.get("parent_id")
        for child in node.get("children", []) or []:
            target = next((n for n in nodes if n.get("id") == child), None)
            if target and target.get("parent_id") != node.get("id"):
                err(errors, "invalid_parent_child", f"{where}: 子节点 {child} 的 parent_id 不互逆")
    required_by_target = {}
    for j, edge in enumerate(edges):
        validate_edge_structure(edge, errors, f"edge#{j}")
        src, dst = edge.get("source_node_id"), edge.get("target_node_id")
        for label, value in (("source", src), ("target", dst)):
            if isinstance(value, str) and value not in id_set:
                err(errors, "missing_reference", f"edge#{j}: {label} 指向不存在的节点 {value}")
        if edge.get("necessity") == "required" and isinstance(dst, str):
            required_by_target.setdefault(dst, set()).add(src)
    for node in nodes:
        declared = set(node.get("prerequisites", []) or [])
        derived = required_by_target.get(node.get("id"), set())
        if declared != derived:
            err(errors, "prerequisite_mismatch",
                f"{node.get('id')}: prerequisites={sorted(declared)} 与 required 边推导的 {sorted(derived)} 不一致")
    for i, item in enumerate(progress):
        nid = item.get("node_id")
        if isinstance(nid, str) and nid not in id_set:
            err(errors, "invalid_mastery_reference", f"progress#{i}: node_id {nid} 不存在")
        if item.get("mastery_level", 0) >= 4 and not item.get("evidence"):
            warnings.append({"code": "weak_evidence",
                             "message": f"progress#{i}: mastery>=4 但无证据记录"})


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 DeepLearn V2 结构化数据")
    parser.add_argument("paths", nargs="+", help="JSON 文件路径，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true", help="机器可读输出")
    args = parser.parse_args()

    errors, warnings, counts = [], [], {"nodes": 0, "progress": 0, "edges": 0, "files": 0}
    for path in args.paths:
        try:
            if path == "-":
                doc = json.loads(sys.stdin.read())
            else:
                doc = load_json(path)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"解析失败：{exc}", file=sys.stderr)
            return 2
        try:
            nodes, progress, edges = classify(doc)
        except ValueError as exc:
            print(f"结构识别失败：{exc}", file=sys.stderr)
            return 2
        for i, node in enumerate(nodes):
            validate_node_structure(node, errors, f"{path}:node#{i}")
        for i, item in enumerate(progress):
            validate_progress_structure(item, errors, f"{path}:progress#{i}")
        cross_checks(nodes, progress, edges, errors, warnings)
        counts["nodes"] += len(nodes)
        counts["progress"] += len(progress)
        counts["edges"] += len(edges)
        counts["files"] += 1

    result = {
        "errors": errors,
        "warnings": warnings,
        "stats": counts,
        "summary": ("校验失败：%d 个错误" % len(errors)) if errors else "校验通过：结构与引用一致",
    }
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
