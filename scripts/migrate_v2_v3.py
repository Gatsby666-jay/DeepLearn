#!/usr/bin/env python3
"""V2 -> V3 state migration with backup, verification and rollback.

Commands: backup | migrate | verify | rollback
No V2 field is changed or removed; V3 fields are added with empty defaults.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

from v3_rules import SCHEMA_VERSION


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def cmd_backup(args) -> int:
    source, backup_dir = Path(args.source), Path(args.backup_dir)
    if not source.is_file():
        print(f"源文件不存在：{source}", file=sys.stderr)
        return 2
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"v2_backup_{utc_stamp()}.json"
    shutil.copy2(source, target)
    (target.with_suffix(".json.sha256")).write_text(sha256(target), encoding="utf-8")
    print(json.dumps({"backup": str(target), "sha256": sha256(target),
                      "source": str(source)}, ensure_ascii=False, indent=2))
    return 0


def v3_defaults(doc):
    """Add-only migration; never infer mastery, competency or preference values."""
    out = copy.deepcopy(doc)
    out.setdefault("schema_version", SCHEMA_VERSION)
    out.setdefault("learner_profile", {
        "profile_id": "PROFILE-001",
        "project_id": doc.get("project_id", "PROJECT-001"),
        "schema_version": SCHEMA_VERSION,
        "created_at": dt.date.today().isoformat(),
        "source": "migration",
        "prior_knowledge": [], "learning_preferences": {},
        "knowledge_states": [], "requires_assessment": True,
    })
    out.setdefault("competency_progress", [])
    out.setdefault("practice_evidence", [])
    out.setdefault("learning_plan", None)
    mapping = {
        "project_created": "project_created", "classification_confirmed": "classification_confirmed",
        "map_generated": "map_generated", "graph_changed": "graph_changed",
        "lesson_completed": "lesson_completed", "assessment_completed": "assessment_completed",
        "mastery_updated": "mastery_updated", "misconception_found": "misconception_found",
        "roadmap_changed": "roadmap_changed", "review_completed": "review_completed",
    }
    events = []
    for i, event in enumerate(doc.get("events", []) or [], start=1):
        if not isinstance(event, dict):
            continue
        events.append({
            "event_id": f"EVENT-{i:03d}", "project_id": doc.get("project_id", "PROJECT-001"),
            "event_type": mapping.get(event.get("event"), "project_created"),
            "occurred_at": event.get("date", dt.date.today().isoformat()),
            "payload": {"detail": event.get("detail", "")},
            "evidence_refs": [], "source": "migration",
            "schema_version": SCHEMA_VERSION,
        })
    out.setdefault("learning_events", events)
    return out


def cmd_migrate(args) -> int:
    source, output = Path(args.source), Path(args.output)
    if not source.is_file():
        print(f"源文件不存在：{source}", file=sys.stderr)
        return 2
    backup = Path(args.backup) if args.backup else None
    if not backup or not backup.is_file():
        print("拒绝迁移：必须先提供有效备份（backup 子命令生成）", file=sys.stderr)
        return 1
    expected = backup.with_suffix(".json.sha256")
    if expected.is_file() and expected.read_text(encoding="utf-8").strip() != sha256(backup):
        print("拒绝迁移：备份 sha256 校验失败", file=sys.stderr)
        return 1
    migrated = v3_defaults(read_json(source))
    write_json(output, migrated)
    print(json.dumps({"source": str(source), "output": str(output),
                      "backup": str(backup), "added_fields": [
                          "schema_version", "learner_profile", "competency_progress",
                          "practice_evidence", "learning_plan", "learning_events"],
                      "note": "V2 原字段全部保留；未推断任何掌握度或能力等级"},
                     ensure_ascii=False, indent=2))
    return 0


def flatten(doc, prefix=""):
    out = {}
    for key, value in doc.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        elif isinstance(value, list):
            out[path] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            out[path] = value
    return out


def cmd_verify(args) -> int:
    before, after = read_json(Path(args.source)), read_json(Path(args.migrated))
    flat_before, flat_after = flatten(before), flatten(after)
    changed = {k: (v, flat_after.get(k)) for k, v in flat_before.items()
               if k in flat_after and flat_after[k] != v}
    missing = sorted(set(flat_before) - set(flat_after))
    added = sorted(set(flat_after) - set(flat_before))
    report = {
        "source": args.source, "migrated": args.migrated,
        "preserved_fields": len(flat_before) - len(missing) - len(changed),
        "changed_v2_fields": changed, "missing_v2_fields": missing,
        "added_v3_fields": added,
        "evidence_count_before": sum(len(p.get("evidence", [])) for p in before.get("progress", [])),
        "evidence_count_after": sum(len(p.get("evidence", [])) for p in after.get("progress", [])),
        "history_count_before": len(before.get("history", []) or []),
        "history_count_after": len(after.get("history", []) or []),
        "verdict": "pass" if not changed and not missing else "fail",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "pass" else 1


def cmd_rollback(args) -> int:
    backup, target = Path(args.backup), Path(args.target)
    if not backup.is_file():
        print(f"备份不存在：{backup}", file=sys.stderr)
        return 2
    expected = backup.with_suffix(".json.sha256")
    if expected.is_file() and expected.read_text(encoding="utf-8").strip() != sha256(backup):
        print("拒绝回滚：备份 sha256 校验失败", file=sys.stderr)
        return 1
    shutil.copy2(backup, target)
    print(json.dumps({"rolled_back_to": str(backup), "target": str(target),
                      "sha256": sha256(target), "status": "ok"},
                     ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="V2→V3 状态迁移、备份、校验与回滚")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("backup"); b.add_argument("--source", required=True); b.add_argument("--backup-dir", required=True)
    m = sub.add_parser("migrate"); m.add_argument("--source", required=True); m.add_argument("--output", required=True); m.add_argument("--backup")
    v = sub.add_parser("verify"); v.add_argument("--source", required=True); v.add_argument("--migrated", required=True)
    r = sub.add_parser("rollback"); r.add_argument("--backup", required=True); r.add_argument("--target", required=True)
    args = parser.parse_args()
    return {"backup": cmd_backup, "migrate": cmd_migrate,
            "verify": cmd_verify, "rollback": cmd_rollback}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
