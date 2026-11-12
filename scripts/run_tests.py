#!/usr/bin/env python3
"""DeepLearn V2 test suite runner.

Reads tests/cases.json and executes three kinds of cases:
  script        deterministic Python validation with an expected exit code
                and optional expected error code
  contract      documentation contract check (a file must contain given markers)
  not_automated subjective teaching quality; reported, never faked as tested

Usage: python run_tests.py [root] [--json] [--case T1]
Exit codes: 0 all executed cases passed, 1 failure, 2 argument/parse error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def run_script(root: Path, case: dict):
    script = root / "scripts" / case["script"]
    cmd = [sys.executable, str(script)] + list(case.get("args", []))
    if case.get("stdin") is not None:
        cmd.append("-")
    if case.get("fixture"):
        cmd.append(str(root / case["fixture"]))
    proc = subprocess.run(cmd, input=case.get("stdin"), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)
    expected = case.get("expect_exit", 0)
    detail = {"exit": proc.returncode, "expected": expected,
              "stdout": (proc.stdout or "")[-400:], "stderr": (proc.stderr or "")[-300:]}
    ok = proc.returncode == expected
    if ok and case.get("expect_error_code"):
        try:
            payload = json.loads(proc.stdout)
            codes = {e.get("code") for e in payload.get("errors", []) + payload.get("warnings", [])}
            ok = case["expect_error_code"] in codes
            detail["error_codes"] = sorted(codes)
        except (ValueError, AttributeError):
            ok = False
            detail["stdout"] = "无法解析 --json 输出：" + detail["stdout"]
    return ok, detail


def run_pipeline(root: Path, case: dict):
    """Chain several validators over one scenario's data flow."""
    details = []
    for step in case.get("steps", []):
        ok, detail = run_script(root, step)
        details.append({"script": step.get("script"), "exit": detail.get("exit"), "ok": ok})
        if not ok:
            return False, {"failed_step": step.get("script"), "steps": details,
                           "detail": detail}
    return True, {"steps": details}


def run_contract(root: Path, case: dict):
    path = root / case["file"]
    if not path.is_file():
        return False, {"missing": str(path)}
    text = path.read_text(encoding="utf-8-sig")
    missing = [m for m in case.get("contains", []) if m not in text]
    return not missing, {"missing_markers": missing}


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 DeepLearn V2 测试套件")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--case", help="只运行指定用例 ID")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    cases_file = root / "tests" / "cases.json"
    try:
        data = json.loads(cases_file.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print(f"读取测试用例失败：{exc}", file=sys.stderr)
        return 2

    results, passed, failed, skipped = [], 0, 0, 0
    for case in data["cases"]:
        if args.case and case["id"] != args.case:
            continue
        kind = case["kind"]
        if kind == "script":
            ok, detail = run_script(root, case)
        elif kind == "contract":
            ok, detail = run_contract(root, case)
        elif kind == "pipeline":
            ok, detail = run_pipeline(root, case)
        elif kind == "not_automated":
            ok, detail = True, {"status": "not_automated", "reason": case.get("note", "")}
            skipped += 1
        else:
            ok, detail = False, {"unknown_kind": kind}
        status = "PASS" if ok and kind != "not_automated" else (
            "SKIP_NOT_AUTOMATED" if kind == "not_automated" else "FAIL")
        if status == "PASS":
            passed += 1
        elif status == "FAIL":
            failed += 1
        results.append({"id": case["id"], "title": case["title"], "kind": kind,
                        "status": status, "detail": detail})

    summary = {"total": len(results), "passed": passed, "failed": failed,
               "not_automated": skipped,
               "verdict": "全部确定性用例通过" if failed == 0 else "存在失败用例"}
    if args.json:
        print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            line = f"[{r['status']}] {r['id']} {r['title']}"
            if r["status"] == "FAIL":
                line += " | " + json.dumps(r["detail"], ensure_ascii=False)[:220]
            print(line)
        print(f"合计 {summary['total']} | 通过 {passed} | 失败 {failed} | 未自动化 {skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
