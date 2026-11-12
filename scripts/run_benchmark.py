#!/usr/bin/env python3
"""Deterministic 12-domain benchmark runner.

Usage: python run_benchmark.py [benchmarks/cases.json] [--json] [--case B01]
Exit codes: 0 all passed, 1 failures, 2 parse error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import ENUMS as V2
from v3_rules import ENUMS as V3

DEFAULT = Path(__file__).resolve().parent.parent / "benchmarks" / "cases.json"
VALID_ASSESSMENT = set(V2["assessment_type"]) | set(V3["competency_evidence_type"])


def check_case(case):
    errors = []
    for field in ("benchmark_id", "domain", "input", "expected_classification",
                  "expected_knowledge_structure", "expected_prerequisites",
                  "expected_teaching_strategy", "expected_assessment",
                  "failure_conditions"):
        if field not in case or case[field] in (None, "", []):
            errors.append(f"缺字段 {field}")
    cls = case.get("expected_classification")
    if cls and cls not in V2["learning_category"]:
        errors.append(f"分类 {cls} 不在七类枚举内")
    for modality in case.get("expected_teaching_strategy", []) or []:
        if modality not in V3["teaching_modality"]:
            errors.append(f"教学策略 {modality} 非法")
    for assessment in case.get("expected_assessment", []) or []:
        if assessment not in VALID_ASSESSMENT:
            errors.append(f"评估方式 {assessment} 非法")
    prereqs = case.get("expected_prerequisites", []) or []
    structure = case.get("expected_knowledge_structure", []) or []
    for p in prereqs:
        if structure and p not in structure:
            errors.append(f"前置 {p} 未出现在知识结构中")
    if not case.get("failure_conditions"):
        errors.append("failure_conditions 不能为空")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 V3 Benchmark 回归集")
    parser.add_argument("path", nargs="?", default=str(DEFAULT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case", help="只运行指定 benchmark_id")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取失败：{exc}", file=sys.stderr)
        return 2
    cases = data["cases"] if isinstance(data, dict) else data
    results, passed, failed = [], 0, 0
    for case in cases:
        if args.case and case.get("benchmark_id") != args.case:
            continue
        errors = check_case(case)
        ok = not errors
        passed += ok
        failed += not ok
        results.append({"benchmark_id": case.get("benchmark_id"),
                        "domain": case.get("domain"),
                        "status": "PASS" if ok else "FAIL", "errors": errors})
    summary = {"total": len(results), "passed": passed, "failed": failed,
               "verdict": "全部通过" if failed == 0 else "存在失败"}
    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            line = f"[{r['status']}] {r['benchmark_id']} {r['domain']}"
            if r["errors"]:
                line += " | " + "; ".join(r["errors"])
            print(line)
        print(f"Benchmark 合计 {summary['total']} | 通过 {passed} | 失败 {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
