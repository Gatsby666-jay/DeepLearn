#!/usr/bin/env python3
"""Validate DeepLearn V2 learner state files (state.json / progress.json).

Usage: python validate_state.py state.json [more.json ...] [--json]
Exit codes: 0 valid, 1 validation errors, 2 argument/parse errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deeplearn_rules import (
    ENUMS, ISO_DATE_RE, PROJECT_RE, ID_RE, emit, err, is_int,
    load_json, validate_progress_structure,
)

STAGES = {"INTAKE", "CLASSIFY", "MAP", "VALIDATE", "PLAN", "DIAGNOSE",
          "TEACH", "ASSESS", "REMEDIATE", "REPLAN", "PERSIST", "CONTINUE"}
REQUIRED = {"project_id", "status", "current_stage", "versions", "progress", "events"}


def check_state(doc, errors, warnings, where):
    if not isinstance(doc, dict):
        err(errors, "state_not_object", f"{where}: state 必须是对象")
        return
    missing = sorted(REQUIRED - set(doc))
    if missing:
        err(errors, "missing_fields", f"{where}: 缺少必填字段 {', '.join(missing)}")
    pid = doc.get("project_id")
    if not isinstance(pid, str) or not PROJECT_RE.fullmatch(pid or ""):
        err(errors, "invalid_id", f"{where}: project_id 必须形如 PROJECT-001")
    if doc.get("status") not in ENUMS["project_status"]:
        err(errors, "invalid_enum", f"{where}: status 非法 {doc.get('status')!r}")
    if doc.get("current_stage") not in STAGES:
        err(errors, "invalid_stage", f"{where}: current_stage 不在 12 阶段内")
    versions = doc.get("versions")
    if not isinstance(versions, dict):
        err(errors, "invalid_version", f"{where}: versions 必须是对象")
    else:
        for key, value in versions.items():
            if not is_int(value) or value < 1:
                err(errors, "invalid_version", f"{where}: versions.{key} 必须是 >=1 整数")
    for field in ("current_node",):
        value = doc.get(field)
        if value is not None and (not isinstance(value, str) or not ID_RE.fullmatch(value)):
            err(errors, "invalid_id", f"{where}: {field} 必须是 NODE-001 形式或 null")
    for field in ("weak_nodes", "history", "events", "progress"):
        if field in doc and not isinstance(doc[field], list):
            err(errors, "invalid_type", f"{where}: {field} 必须是数组")

    progress = doc.get("progress", [])
    if isinstance(progress, list):
        known_ids = {p.get("node_id") for p in progress if isinstance(p, dict)}
        for i, item in enumerate(progress):
            validate_progress_structure(item, errors, f"{where}:progress#{i}")
            if not isinstance(item, dict):
                continue
            level = item.get("mastery_level")
            evidence = item.get("evidence", []) or []
            if is_int(level) and level > 0 and not evidence:
                warnings.append({"code": "no_evidence",
                                 "message": f"{where}: {item.get('node_id')} mastery={level} 但无证据"})
            if is_int(level) and level >= 4:
                types = {e.get("assessment_type") for e in evidence if isinstance(e, dict)}
                if not (types & {"cross_domain_transfer", "changed_condition_transfer",
                                 "reverse_teaching", "derivation"}):
                    err(errors, "unsupported_mastery",
                        f"{where}: {item.get('node_id')} mastery>=4 缺少迁移/推导/反向教学证据")
            # Conflicting evidence must coexist and must not justify deep mastery.
            normal_pass = any(isinstance(e, dict) and e.get("assessment_type") == "application"
                              and e.get("result") == "pass" for e in evidence)
            transfer_fail = any(isinstance(e, dict) and
                                e.get("assessment_type") in {"cross_domain_transfer", "changed_condition_transfer"}
                                and e.get("result") == "fail" for e in evidence)
            if normal_pass and transfer_fail and is_int(level) and level >= 4:
                err(errors, "conflicting_evidence",
                    f"{where}: {item.get('node_id')} 常规题通过但迁移失败，不得判 L4/L5")
        for field in ("current_node",):
            value = doc.get(field)
            if isinstance(value, str) and value not in known_ids and progress:
                warnings.append({"code": "current_node_not_in_progress",
                                 "message": f"{where}: current_node {value} 没有进度记录"})

    events = doc.get("events", [])
    if isinstance(events, list):
        for i, event in enumerate(events):
            if not isinstance(event, dict):
                err(errors, "invalid_event", f"{where}: events[{i}] 必须是对象")
                continue
            name = event.get("event")
            if name not in ENUMS["project_event"]:
                err(errors, "invalid_enum", f"{where}: events[{i}].event 非法 {name!r}")
            date = event.get("date")
            if not isinstance(date, str) or not ISO_DATE_RE.fullmatch(date):
                err(errors, "invalid_date", f"{where}: events[{i}].date 必须是 YYYY-MM-DD")
    history = doc.get("history", [])
    if isinstance(history, list):
        for i, item in enumerate(history):
            if not item or not isinstance(item, (str, dict)):
                err(errors, "invalid_history", f"{where}: history[{i}] 为空或类型非法")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 DeepLearn V2 学习状态")
    parser.add_argument("paths", nargs="+", help="state/progress JSON 文件，'-' 表示 stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, warnings, count = [], [], 0
    for path in args.paths:
        try:
            doc = json.loads(sys.stdin.read()) if path == "-" else load_json(path)
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"解析失败：{exc}", file=sys.stderr)
            return 2
        items = doc if isinstance(doc, list) else [doc]
        for item in items:
            if isinstance(item, dict) and "mastery_level" in item and "project_id" in item and "events" not in item:
                validate_progress_structure(item, errors, path)
            else:
                check_state(item, errors, warnings, path)
            count += 1
    result = {
        "errors": errors, "warnings": warnings,
        "stats": {"documents": count},
        "summary": ("校验失败：%d 个错误" % len(errors)) if errors else "校验通过：状态与证据结构一致",
    }
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
