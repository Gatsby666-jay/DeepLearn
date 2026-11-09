#!/usr/bin/env python3
"""DeepLearn 知识依赖图校验器（零第三方依赖）。

边语义：A -> B 表示「掌握 A 是学习 B 的前置」。
检查：环检测、拓扑序、起点、分层建议、孤立节点、孤立终点。

用法：
  python validate_map.py graph.mmd
  python validate_map.py graph.mmd --strict   # G2 零孤立节点门禁
  python validate_map.py graph.json --json
  cat graph.mmd | python validate_map.py -

输入格式：
  Mermaid: flowchart LR / graph TD 中的 `A[标签] --> B[标签]` 行
  JSON:    {"nodes": ["A", "B"], "edges": [["A", "B"]]}
           其中 nodes 可省略；labels 可选，形如 {"A": "数字逻辑"}

退出码：
  0  无环，图可用
  1  检测到环、图为空，或 --strict 下存在孤立节点
  2  参数错误 / 解析失败
"""
from __future__ import annotations

import argparse
import heapq
import json
import re
import sys
from pathlib import Path

EDGE_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?\s*-->\s*"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]]*\])?"
)
LABEL_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[([^\]]*)\]")


def try_reconfigure_stdout() -> None:
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def parse_mermaid(text: str) -> tuple[set[str], list[tuple[str, str]], dict[str, str]]:
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    labels: dict[str, str] = {}
    for line in text.splitlines():
        for node_id, label in LABEL_RE.findall(line):
            nodes.add(node_id)
            labels.setdefault(node_id, label.strip())
        for src, dst in EDGE_RE.findall(line):
            edges.append((src, dst))
            nodes.add(src)
            nodes.add(dst)
    return nodes, edges, labels


def parse_json(text: str) -> tuple[set[str], list[tuple[str, str]], dict[str, str]]:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON 顶层必须是对象")
    raw_edges = data.get("edges", [])
    edges: list[tuple[str, str]] = []
    for item in raw_edges:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            edges.append((str(item[0]), str(item[1])))
        elif isinstance(item, dict) and "from" in item and "to" in item:
            edges.append((str(item["from"]), str(item["to"])))
        else:
            raise ValueError(f"无法识别的边：{item!r}")
    nodes = {str(n) for n in data.get("nodes", [])}
    for src, dst in edges:
        nodes.add(src)
        nodes.add(dst)
    labels = {str(k): str(v) for k, v in data.get("labels", {}).items()}
    return nodes, edges, labels


def find_cycle(nodes: set[str], adj: dict[str, list[str]]) -> list[str]:
    """DFS 找一条具体环路径，用于报告，而不只是说「有环」。"""
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in adj.get(node, []):
            if state.get(nxt) == 1:
                start = stack.index(nxt)
                return stack[start:] + [nxt]
            if state.get(nxt, 0) == 0:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(nodes):
        if state.get(node, 0) == 0:
            found = visit(node)
            if found:
                return found
    return []


def analyze(nodes: set[str], edges: list[tuple[str, str]]) -> dict:
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    indeg: dict[str, int] = {n: 0 for n in nodes}
    for src, dst in edges:
        if src == dst:
            continue
        if (src, dst) in adj[src]:
            continue
        adj[src].append(dst)
        indeg[dst] += 1

    indeg0 = dict(indeg)
    work = dict(indeg)
    heap = [n for n, d in work.items() if d == 0]
    heapq.heapify(heap)
    order: list[str] = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for nxt in sorted(adj.get(node, [])):
            work[nxt] -= 1
            if work[nxt] == 0:
                heapq.heappush(heap, nxt)

    has_cycle = len(order) != len(nodes)
    cycle = find_cycle(nodes, adj) if has_cycle else []

    levels: dict[str, int] = {n: 0 for n in nodes}
    for node in order:
        for nxt in adj.get(node, []):
            levels[nxt] = max(levels[nxt], levels[node] + 1)
    grouped: dict[int, list[str]] = {}
    for node, level in levels.items():
        grouped.setdefault(level, []).append(node)
    stages = [sorted(grouped[k]) for k in sorted(grouped)]

    isolated = sorted(n for n in nodes if not adj[n] and indeg0[n] == 0)
    terminals = sorted(n for n in nodes if not adj[n] and indeg0[n] > 0)
    roots = sorted(n for n in nodes if indeg0[n] == 0 and adj[n])

    return {
        "node_count": len(nodes),
        "edge_count": sum(len(v) for v in adj.values()),
        "starts": roots,
        "order": order,
        "stages": stages,
        "has_cycle": has_cycle,
        "cycle": cycle,
        "isolated": isolated,
        "terminals": terminals,
    }


def main() -> int:
    try_reconfigure_stdout()
    parser = argparse.ArgumentParser(description="校验 DeepLearn 知识依赖图")
    parser.add_argument("path", help="Mermaid/JSON 文件路径，'-' 表示从 stdin 读取")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    parser.add_argument("--strict", action="store_true", help="G2 门禁：存在孤立节点即失败")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2

    try:
        if raw.lstrip().startswith("{"):
            nodes, edges, labels = parse_json(raw)
        else:
            nodes, edges, labels = parse_mermaid(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"解析失败：{exc}", file=sys.stderr)
        return 2

    if not nodes:
        print("图中没有节点，无法生成路线图", file=sys.stderr)
        return 1

    result = analyze(nodes, edges)
    if args.json:
        result["labels"] = labels
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"节点 {result['node_count']} / 边 {result['edge_count']}")
        print(f"起点：{', '.join(result['starts']) or '（无）'}")
        print(f"拓扑序：{' -> '.join(result['order']) or '（无）'}")
        print("建议阶段：" + " | ".join("S{}: {}".format(i + 1, ", ".join(s))
                                       for i, s in enumerate(result["stages"])))
        if result["isolated"]:
            label = "错误" if args.strict else "警告"
            print(f"{label}：孤立节点 {', '.join(result['isolated'])}（无前置、无后继，需补依赖边或声明为基础边界）")
        if result["terminals"]:
            print(f"终点节点：{', '.join(result['terminals'])}")
        if result["has_cycle"]:
            print("错误：检测到循环依赖 " + " -> ".join(result["cycle"]))
            print("处理：把环上某节点拆为「先会用 → 后懂原理」两步后重新校验")
        elif args.strict and result["isolated"]:
            print("校验失败（strict）：存在孤立节点，按 G2 门禁不得生成路线图")
        else:
            print("校验通过：依赖图无环，可用于生成学习路线图")

    if result["has_cycle"]:
        return 1
    if args.strict and result["isolated"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
