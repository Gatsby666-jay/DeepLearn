#!/usr/bin/env python3
"""V3 test-suite runner with JSON-path assertions.

Usage: python run_v3_tests.py [root] [--json] [--case V01]
Script steps support expect_json (exact equality on dotted paths) and
expect_json_ne (value must differ from the given constant).
Exit codes: 0 all executed cases passed, 1 failure, 2 parse error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def get_path(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def run_step(root, step):
    script = root / "scripts" / step["script"]
    cmd = [sys.executable, str(script)] + list(step.get("args", []))
    if step.get("stdin") is not None:
        cmd.append("-")
    if step.get("fixture"):
        cmd.append(str(root / step["fixture"]))
    proc = subprocess.run(cmd, input=step.get("stdin"), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=90)
    detail = {"exit": proc.returncode, "expected": step.get("expect_exit", 0)}
    ok = proc.returncode == step.get("expect_exit", 0)
    if ok and step.get("expect_json"):
        try:
            payload = json.loads(proc.stdout)
            for dotted, expected in step["expect_json"].items():
                actual = get_path(payload, dotted)
                if actual != expected:
                    ok = False
                    detail[f"expect {dotted}"] = f"expected {expected!r}, got {actual!r}"
        except (ValueError, AttributeError):
            ok = False
            detail["parse"] = "无法解析 --json 输出"
    if ok and step.get("expect_json_ne"):
        try:
            payload = json.loads(proc.stdout)
            for dotted, forbidden in step["expect_json_ne"].items():
                actual = get_path(payload, dotted)
                if actual == forbidden:
                    ok = False
                    detail[f"forbid {dotted}"] = f"must differ from {forbidden!r}, got {actual!r}"
        except (ValueError, AttributeError):
            ok = False
            detail["parse"] = "无法解析 --json 输出"
    if ok and step.get("expect_error_code"):
        try:
            payload = json.loads(proc.stdout)
            codes = {e.get("code") for e in payload.get("errors", [])}
            ok = step["expect_error_code"] in codes
            detail["codes"] = sorted(codes)
        except ValueError:
            ok = False
    if not ok:
        detail["stdout"] = (proc.stdout or "")[-300:]
        detail["stderr"] = (proc.stderr or "")[-200:]
    return ok, detail


def run_cases(root, only=None):
    data = json.loads((root / "tests" / "v3_cases.json").read_text(encoding="utf-8-sig"))
    results, passed, failed, skipped = [], 0, 0, 0
    for case in data["cases"]:
        if only and case["id"] != only:
            continue
        kind = case["kind"]
        if kind == "not_automated":
            status, detail = "SKIP_NOT_AUTOMATED", {"reason": case.get("note", "")}
            skipped += 1
        elif kind == "contract":
            path = root / case["file"]
            text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
            missing = [m for m in case.get("contains", []) if m not in text]
            status = "PASS" if not missing else "FAIL"
            detail = {"missing_markers": missing}
        elif kind == "pipeline":
            steps, ok = [], True
            for step in case.get("steps", []):
                step_ok, step_detail = run_step(root, step)
                steps.append({"script": step["script"], "ok": step_ok})
                if not step_ok:
                    ok, detail = False, {"failed_step": step["script"], "detail": step_detail,
                                        "steps": steps}
                    break
            status = "PASS" if ok else "FAIL"
            detail = detail if not ok else {"steps": steps}
        else:
            ok, detail = run_step(root, case)
            status = "PASS" if ok else "FAIL"
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        results.append({"id": case["id"], "title": case["title"],
                        "kind": kind, "status": status, "detail": detail})
    return {"summary": {"total": len(results), "passed": passed, "failed": failed,
                        "not_automated": skipped,
                        "verdict": "全部确定性用例通过" if failed == 0 else "存在失败"},
            "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 DeepLearn V3 测试套件")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case")
    args = parser.parse_args()
    try:
        report = run_cases(Path(args.root).resolve(), args.case)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"读取用例失败：{exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for r in report["results"]:
            line = f"[{r['status']}] {r['id']} {r['title']}"
            if r["status"] == "FAIL":
                line += " | " + json.dumps(r["detail"], ensure_ascii=False)[:220]
            print(line)
        s = report["summary"]
        print(f"V3 合计 {s['total']} | 通过 {s['passed']} | 失败 {s['failed']} | 未自动化 {s['not_automated']}")
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
