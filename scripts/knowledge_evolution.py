#!/usr/bin/env python3
"""Validate knowledge-graph change proposals (deterministic gate).

Usage: python knowledge_evolution.py proposal.json [--json]
Exit codes: 0 valid proposal, 1 rejected, 2 argument/parse error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import err
from v3_rules import ENUMS, validate_change

MIN_EVIDENCE = 2
MIN_CONFIDENCE = {"unassessed": 0, "provisional": 1, "supported": 2, "strong": 3}


def check(doc, known_nodes=None):
    errors = []
    validate_change(doc, errors, "proposal")
    evidence = doc.get("evidence", []) or []
    if len(evidence) < MIN_EVIDENCE:
        err(errors, "insufficient_evidence",
            f"至少需 {MIN_EVIDENCE} 条独立证据，实际 {len(evidence)} 条；不得因一次错误重构图谱")
    if MIN_CONFIDENCE.get(doc.get("confidence"), 0) < MIN_CONFIDENCE["supported"]:
        err(errors, "low_confidence", "提案置信度必须 >= supported")
    if doc.get("status") == "applied" and not doc.get("requires_reassessment"):
        warnings = ["已应用变更但未要求重评，需人工复核"]
    else:
        warnings = []
    if known_nodes:
        for nid in doc.get("affected_node_ids", []) or []:
            if nid not in known_nodes:
                err(errors, "missing_reference", f"affected_node_ids {nid} 不存在")
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "evidence_count": len(evidence), "impact_scope": doc.get("impact_scope", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description="V3 知识图谱变更提案校验")
    parser.add_argument("path", help="提案 JSON，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
        result = check(json.loads(raw))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
