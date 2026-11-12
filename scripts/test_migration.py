#!/usr/bin/env python3
"""End-to-end V2->V3 migration test: backup, migrate, verify, rollback.

Uses a temporary workspace; never touches real learner state files.
Usage: python test_migration.py [--json]
Exit codes: 0 all assertions passed, 1 assertion failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATE = ROOT / "scripts" / "migrate_v2_v3.py"
SOURCE = ROOT / "tests" / "fixtures" / "v3_migration_source.json"


def run(*args):
    return subprocess.run([sys.executable, str(MIGRATE)] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=60)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> int:
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        backup_dir = tmpdir / "backups"
        migrated = tmpdir / "v3_state.json"
        target = tmpdir / "state.json"
        target.write_bytes(SOURCE.read_bytes())
        original_sha = sha(target)

        r0 = run("migrate", "--source", target, "--output", migrated)
        checks.append({"name": "无备份时拒绝迁移", "pass": r0.returncode == 1})

        r1 = run("backup", "--source", target, "--backup-dir", backup_dir)
        backups = sorted(backup_dir.glob("v2_backup_*.json"))
        checks.append({"name": "备份生成", "pass": r1.returncode == 0 and len(backups) == 1})
        backup = backups[0] if backups else None

        r2 = run("migrate", "--source", target, "--output", migrated, "--backup", backup)
        checks.append({"name": "带备份迁移成功", "pass": r2.returncode == 0})

        r3 = run("verify", "--source", target, "--migrated", migrated)
        report = json.loads(r3.stdout) if r3.returncode in (0, 1) else {}
        checks.append({"name": "V2 字段零改动", "pass": r3.returncode == 0 and report.get("verdict") == "pass"})
        checks.append({"name": "证据与历史数量不变",
                       "pass": report.get("evidence_count_before") == report.get("evidence_count_after")
                               and report.get("history_count_before") == report.get("history_count_after")})
        v3 = json.loads(migrated.read_text(encoding="utf-8")) if migrated.is_file() else {}
        checks.append({"name": "V3 字段只增不推断",
                       "pass": v3.get("schema_version") == 3
                               and v3.get("learner_profile", {}).get("requires_assessment") is True
                               and v3.get("competency_progress") == []})

        r4 = run("rollback", "--backup", backup, "--target", target)
        checks.append({"name": "回滚恢复原始字节",
                       "pass": r4.returncode == 0 and sha(target) == original_sha})
        checks.append({"name": "回滚后 V2 schema 无 V3 字段",
                       "pass": "schema_version" not in json.loads(target.read_text(encoding="utf-8"))})

    verdict = all(c["pass"] for c in checks)
    out = {"verdict": "pass" if verdict else "fail", "checks": checks,
           "passed": sum(c["pass"] for c in checks), "total": len(checks)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
