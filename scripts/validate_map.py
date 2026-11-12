#!/usr/bin/env python3
"""DeepLearn V2 knowledge/dependency graph validator (standard library only).

Input shapes
------------
1. Mermaid text:   flowchart LR / graph TD lines with `A[label] --> B[label]`
2. V1 simple JSON: {"nodes": ["A", "B"], "edges": [["A", "B"]]}
3. V2 node JSON:   {"nodes": [{KnowledgeNode}, ...],
                    "edges": [{source_node_id, target_node_id, dependency_type,
                               necessity, explanation}, ...]}

Edge direction is always prerequisite_node -> dependent_node.
Root nodes, terminal nodes and declared independent optional concepts are valid.

Checks: duplicate IDs, missing references, invalid direction fields, self loops,
cycles, duplicate edges, invalid edge enums, missing mandatory node fields,
invalid node enums, inconsistent parent/child references, invalid mastery
references (when progress is supplied), disconnected components,
prerequisite/required-edge consistency, and quality-gate failures.

Usage:
  python validate_map.py graph.mmd [--strict] [--json]
  python validate_map.py graph.json [--strict] [--json]
  cat graph.mmd | python validate_map.py - [--strict] [--json]

Exit codes: 0 valid, 1 validation failure, 2 argument/parse error.
"""
from __future__ import annotations

import argparse
import heapq
import json
import re
import sys
from pathlib import Path

from deeplearn_rules import (
    emit, err, validate_edge_structure, validate_node_structure,
    validate_progress_structure,
)

EDGE_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?\s*-->\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?"
)
LABEL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[([^\]]*)\]")


def reconfigure_stdout() -> None:
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def parse_text(raw: str):
    """Return (mode, node_ids, node_objects, edges, labels, progress)."""
    if raw.lstrip().startswith("{"):
        data = json.loads(raw)
        raw_nodes = data.get("nodes", [])
        raw_edges = []
        for key in ("edges", "dependency_edges"):
            raw_edges += data.get(key, []) or []
        raw_progress = data.get("progress", [])
        if isinstance(raw_progress, dict):
            raw_progress = [raw_progress]
        if raw_nodes and all(isinstance(n, dict) for n in raw_nodes):
            edges = []
            for edge in raw_edges:
                if isinstance(edge, dict):
                    norm = dict(edge)
                    if "source_node_id" not in norm and "from" in norm:
                        norm["source_node_id"] = norm["from"]
                    if "target_node_id" not in norm and "to" in norm:
                        norm["target_node_id"] = norm["to"]
                    edges.append((norm.get("source_node_id"), norm.get("target_node_id"),
                                  norm.get("necessity", "required"), norm))
                elif isinstance(edge, (list, tuple)) and len(edge) == 2:
                    edges.append((edge[0], edge[1], "required", None))
            return "v2", [n.get("id") for n in raw_nodes], raw_nodes, edges, {}, raw_progress
        ids = [str(n) for n in raw_nodes]
        edges = []
        for edge in raw_edges:
            if isinstance(edge, (list, tuple)) and len(edge) == 2:
                edges.append((str(edge[0]), str(edge[1]), "required", None))
            elif isinstance(edge, dict):
                edges.append((edge.get("source_node_id") or edge.get("from"),
                              edge.get("target_node_id") or edge.get("to"),
                              edge.get("necessity", "required"), edge))
        for src, dst, _, _ in edges:
            if src:
                ids.append(str(src))
            if dst:
                ids.append(str(dst))
        return "v1", list(dict.fromkeys(ids)), [], edges, {}, []

    ids, edges, labels = [], [], {}
    for line in raw.splitlines():
        for node_id, label in LABEL_RE.findall(line):
            labels.setdefault(node_id, label.strip())
        for src, dst in EDGE_RE.findall(line):
            edges.append((src, dst, "required", None))
            ids += [src, dst]
    return "v1", list(dict.fromkeys(ids)), [], edges, labels, []


def find_cycle(adj):
    state, stack = {}, []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for nxt in adj.get(node, []):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if state.get(nxt, 0) == 0:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(adj):
        if state.get(node, 0) == 0:
            found = visit(node)
            if found:
                return found
    return []


def analyze(ids, edges, strict):
    errors, warnings = [], []
    ids = [str(i) for i in ids if i is not None]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        err(errors, "duplicate_node_ids", "重复节点 ID：" + ", ".join(duplicates))
    id_set = set(ids)

    adj = {n: [] for n in ids}
    indeg = {n: 0 for n in ids}
    seen_pairs = set()
    for src, dst, necessity, _ in edges:
        if src is None or dst is None:
            err(errors, "invalid_edge_direction",
                "边缺少 source_node_id / target_node_id，方向必须为前置→后继")
            continue
        if src == dst:
            err(errors, "self_loop", f"自环：{src} -> {dst}")
            continue
        if src not in id_set or dst not in id_set:
            err(errors, "missing_reference", f"边引用不存在节点：{src} -> {dst}")
            continue
        pair = (src, dst)
        if pair in seen_pairs:
            warnings.append({"code": "duplicate_edge", "message": f"重复边：{src} -> {dst}"})
            continue
        seen_pairs.add(pair)
        adj[src].append(dst)
        indeg[dst] += 1

    indeg0 = dict(indeg)
    work = dict(indeg)
    heap = [n for n, d in work.items() if d == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for nxt in sorted(adj[node]):
            work[nxt] -= 1
            if work[nxt] == 0:
                heapq.heappush(heap, nxt)

    has_cycle = len(order) != len(ids)
    cycle = find_cycle(adj) if has_cycle else []
    if has_cycle:
        err(errors, "dependency_cycle", "循环依赖 " + " -> ".join(cycle)
            + "；阻断路线图生成，需拆为「先会用 → 后懂原理」两步")

    levels = {n: 0 for n in ids}
    for node in order:
        for nxt in adj[node]:
            levels[nxt] = max(levels[nxt], levels[node] + 1)
    grouped = {}
    for node, level in levels.items():
        grouped.setdefault(level, []).append(node)
    stages = [sorted(grouped[k]) for k in sorted(grouped)]

    isolated = sorted(n for n in ids if not adj[n] and indeg0[n] == 0)
    terminals = sorted(n for n in ids if not adj[n] and indeg0[n] > 0)
    roots = sorted(n for n in ids if indeg0[n] == 0 and adj[n])
    if isolated:
        warnings.append({"code": "isolated_nodes",
                         "message": "孤立节点 " + ", ".join(isolated)
                                    + "（根节点/终点节点合法，孤立项需声明范围与用途）"})

    undirected = {n: set() for n in ids}
    for src, dst, _, _ in edges:
        if src in undirected and dst in undirected:
            undirected[src].add(dst)
            undirected[dst].add(src)
    unseen, components = set(ids), []
    while unseen:
        start = min(unseen)
        queue, comp = [start], []
        unseen.discard(start)
        while queue:
            node = queue.pop()
            comp.append(node)
            for nxt in sorted(undirected[node] & unseen):
                unseen.discard(nxt)
                queue.append(nxt)
        components.append(sorted(comp))
    if len(components) > 1:
        warnings.append({"code": "disconnected_components",
                         "message": f"存在 {len(components)} 个连通分量：" +
                                    " | ".join(", ".join(c) for c in components)})

    result = {
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "node_count": len(ids), "edge_count": len(seen_pairs),
            "starts": roots, "terminals": terminals, "isolated": isolated,
            "components": len(components),
        },
        "order": order,
        "stages": stages,
        "cycle": cycle,
        "has_cycle": has_cycle,
    }
    strict_blocking = [w for w in warnings if w["code"] != "disconnected_components"]
    blocking = errors or (strict_blocking if strict else [])
    result["passed"] = not blocking
    result["summary"] = ("校验失败：%d 错误 / %d 警告（strict）" %
                         (len(errors), len(warnings)) if blocking
                         else "校验通过：依赖图可生成学习路线图")
    return result


def main() -> int:
    reconfigure_stdout()
    parser = argparse.ArgumentParser(description="校验 DeepLearn V2 知识依赖图")
    parser.add_argument("path", help="Mermaid/JSON 文件路径，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true", help="机器可读输出")
    parser.add_argument("--strict", action="store_true", help="警告也视为失败（G2 门禁）")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
        mode, ids, node_objects, edges, labels, progress = parse_text(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取或解析失败：{exc}", file=sys.stderr)
        return 2
    if not ids:
        print("图中没有节点，无法生成路线图", file=sys.stderr)
        return 1

    result = analyze(ids, edges, args.strict)

    if mode == "v2":
        for i, node in enumerate(node_objects):
            validate_node_structure(node, result["errors"], f"node#{i}")
        for i, (_, _, _, edge_obj) in enumerate(edges):
            if edge_obj is not None:
                validate_edge_structure(edge_obj, result["errors"], f"edge#{i}")
        for i, item in enumerate(progress):
            validate_progress_structure(item, result["errors"], f"progress#{i}")
        id_set = set(str(i) for i in ids)
        for i, item in enumerate(progress):
            if isinstance(item, dict) and item.get("node_id") not in id_set:
                err(result["errors"], "invalid_mastery_reference",
                    f"progress#{i}: node_id {item.get('node_id')} 不存在")
        for node in node_objects:
            declared = set(node.get("prerequisites", []) or [])
            derived = {src for src, dst, necessity, _ in edges
                       if dst == node.get("id") and necessity == "required"}
            if declared != derived:
                err(result["errors"], "prerequisite_mismatch",
                    f"{node.get('id')}: prerequisites 与 required 边不一致 "
                    f"({sorted(declared)} vs {sorted(derived)})")
        strict_blocking = [w for w in result["warnings"] if w["code"] != "disconnected_components"]
        blocking = result["errors"] or (strict_blocking if args.strict else [])
        result["passed"] = not blocking
        result["summary"] = ("校验失败：%d 错误 / %d 警告（strict）" %
                             (len(result["errors"]), len(result["warnings"])) if blocking
                             else "校验通过：结构、门禁与依赖图均通过")

    result["mode"] = mode
    result["labels"] = labels
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        emit(result, False)
        print("起点：" + (", ".join(result["stats"]["starts"]) or "（无）"))
        print("拓扑序：" + (" -> ".join(result["order"]) or "（无）"))
        print("建议阶段：" + " | ".join("S{}: {}".format(i + 1, ", ".join(s))
                                       for i, s in enumerate(result["stages"])))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
