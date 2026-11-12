#!/usr/bin/env python3
"""Validate a DeepLearn V2 learning roadmap against its dependency graph.

Input JSON:
{
  "project_id": "PROJECT-001",
  "nodes": [{"id": "NODE-001", "prerequisites": []}, ...],
  "stages": [{"id": "S1", "nodes": ["NODE-001"], "depends_on": [],
              "duration": {"min_hours": 2, "max_hours": 4}}, ...],
  "critical_path": ["S1", "S2"]        # optional
}

Checks: duplicate stage IDs, invalid stage references, missing node coverage,
duplicate node placement, missing prerequisites, prerequisite ordering,
stage dependency consistency, illegal durations, stage cycles, and whether a
declared critical path is actually the longest-duration path (not the chain
with the most nodes).

Usage: python validate_roadmap.py roadmap.json [--json]
Exit codes: 0 valid, 1 validation errors, 2 argument/parse errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import ID_RE, PROJECT_RE, emit, err, load_json


def topo_order(ids, deps, errors):
    indeg = {s: 0 for s in ids}
    adj = {s: [] for s in ids}
    for stage, parents in deps.items():
        for parent in parents:
            if parent in adj:
                adj[parent].append(stage)
                indeg[stage] += 1
    queue = [s for s in ids if indeg[s] == 0]
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    if len(order) != len(ids):
        err(errors, "stage_cycle", "阶段依赖存在环，无法生成学习路线")
    return order, adj


def validate(doc, errors, warnings):
    if not isinstance(doc, dict):
        err(errors, "roadmap_not_object", "roadmap 必须是对象")
        return
    for key in ("project_id", "nodes", "stages"):
        if key not in doc:
            err(errors, "missing_fields", f"缺少必填字段 {key}")
    pid = doc.get("project_id")
    if pid is not None and (not isinstance(pid, str) or not PROJECT_RE.fullmatch(pid)):
        err(errors, "invalid_id", "project_id 必须形如 PROJECT-001")

    raw_nodes = doc.get("nodes", [])
    raw_stages = doc.get("stages", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_stages, list):
        err(errors, "invalid_type", "nodes 与 stages 必须是数组")
        return

    node_prereq = {}
    for i, item in enumerate(raw_nodes):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            err(errors, "invalid_node", f"nodes[{i}] 缺少合法 id")
            continue
        nid = item["id"]
        if not ID_RE.fullmatch(nid):
            err(errors, "invalid_id", f"nodes[{i}].id={nid} 不符合 NODE-001 格式")
        if nid in node_prereq:
            err(errors, "duplicate_node_ids", f"重复节点 ID {nid}")
        node_prereq[nid] = item.get("prerequisites", []) or []

    stage_ids, deps, stage_of = [], {}, {}
    for i, item in enumerate(raw_stages):
        if not isinstance(item, dict):
            err(errors, "invalid_stage", f"stages[{i}] 必须是对象")
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not sid:
            err(errors, "invalid_stage", f"stages[{i}].id 非法")
            continue
        if sid in deps:
            err(errors, "duplicate_stage_ids", f"重复阶段 ID {sid}")
            continue
        stage_ids.append(sid)
        parents = item.get("depends_on", []) or []
        deps[sid] = parents
        if sid in parents:
            err(errors, "stage_cycle", f"阶段 {sid} 自依赖")
        duration = item.get("duration")
        if not isinstance(duration, dict):
            err(errors, "invalid_duration", f"{sid}: 缺少 duration")
        else:
            lo, hi = duration.get("min_hours"), duration.get("max_hours")
            if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)) \
                    or lo <= 0 or hi < lo:
                err(errors, "invalid_duration", f"{sid}: 需满足 0 < min_hours <= max_hours")
        members = item.get("nodes", []) or []
        for nid in members:
            if nid not in node_prereq:
                err(errors, "invalid_stage_reference", f"{sid}: 引用不存在的节点 {nid}")
            if nid in stage_of:
                err(errors, "duplicate_node_placement",
                    f"节点 {nid} 同时出现在 {stage_of[nid]} 与 {sid}")
            else:
                stage_of[nid] = sid

    for parent_list in deps.values():
        for parent in parent_list:
            if parent not in deps and parent not in stage_ids:
                err(errors, "invalid_stage_reference", f"depends_on 引用不存在的阶段 {parent}")

    for nid in node_prereq:
        if nid not in stage_of:
            err(errors, "missing_stage_coverage", f"节点 {nid} 未被任何阶段覆盖")

    order, adj = topo_order(stage_ids, deps, errors)
    rank = {sid: i for i, sid in enumerate(order)}

    for nid, prereqs in node_prereq.items():
        if nid not in stage_of:
            continue
        for pre in prereqs:
            if pre not in node_prereq:
                err(errors, "missing_prerequisite", f"{nid} 的前置 {pre} 不存在")
                continue
            if pre not in stage_of:
                err(errors, "missing_prerequisite", f"{nid} 的前置 {pre} 未排入任何阶段")
                continue
            if rank.get(stage_of[pre], -1) >= rank.get(stage_of[nid], -1):
                err(errors, "invalid_prerequisite_order",
                    f"{nid}({stage_of[nid]}) 排在前置 {pre}({stage_of[pre]}) 之前或同阶段")
            elif stage_of[pre] not in transitive_parents(stage_of[nid], deps):
                err(errors, "missing_stage_dependency",
                    f"阶段 {stage_of[nid]} 缺少对 {stage_of[pre]} 的 depends_on 声明")

    # Longest-duration path (DP over the stage DAG), not the longest node chain.
    best = {}
    for sid in order:
        parents = [p for p in deps.get(sid, []) if p in best]
        base = max((best[p] for p in parents), default=0)
        d = next((s.get("duration", {}) for s in raw_stages
                  if isinstance(s, dict) and s.get("id") == sid), {})
        best[sid] = base + (d.get("max_hours") if isinstance(d.get("max_hours"), (int, float)) else 0)
    max_duration = max(best.values(), default=0)

    declared = doc.get("critical_path")
    if declared is not None:
        if not isinstance(declared, list) or not declared:
            err(errors, "invalid_critical_path", "critical_path 必须是非空数组")
        else:
            for sid in declared:
                if sid not in deps:
                    err(errors, "invalid_critical_path", f"critical_path 引用不存在阶段 {sid}")
            for a, b in zip(declared, declared[1:]):
                if a in deps and b in deps and a not in deps[b]:
                    err(errors, "invalid_critical_path", f"{a} -> {b} 之间没有阶段依赖边")
            total = 0
            for sid in declared:
                d = next((s.get("duration", {}) for s in raw_stages
                          if isinstance(s, dict) and s.get("id") == sid), {})
                if isinstance(d.get("max_hours"), (int, float)):
                    total += d["max_hours"]
            if total < max_duration:
                err(errors, "invalid_critical_path",
                    f"声明的关键路径工期 {total}h 小于最长工期路径 {max_duration}h")
    stats = {
        "node_count": len(node_prereq), "stage_count": len(stage_ids),
        "topological_order": order, "longest_duration_hours": max_duration,
    }
    return stats


def transitive_parents(sid, deps):
    seen, stack = set(), list(deps.get(sid, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack += deps.get(cur, [])
    return seen


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 DeepLearn V2 学习路线图")
    parser.add_argument("path", help="roadmap JSON 文件，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        doc = json.loads(sys.stdin.read()) if args.path == "-" else load_json(args.path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取或解析失败：{exc}", file=sys.stderr)
        return 2
    errors, warnings = [], []
    stats = validate(doc, errors, warnings) or {}
    result = {"errors": errors, "warnings": warnings, "stats": stats,
              "summary": ("校验失败：%d 个错误" % len(errors)) if errors
                         else "校验通过：阶段顺序、前置、工期与关键路径一致"}
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
