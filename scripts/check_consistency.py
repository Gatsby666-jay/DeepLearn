#!/usr/bin/env python3
"""Cross-module consistency checks for DeepLearn V2.

Usage: python check_consistency.py [root] [--json]
Exit codes: 0 consistent, 1 inconsistencies, 2 argument error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from deeplearn_rules import ENUMS, emit

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
ROUTE_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|json|py))`")


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 DeepLearn V2 跨模块一致性")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"不是目录：{root}", file=sys.stderr)
        return 2
    errors, warnings = [], []

    schema = root / "core" / "data-schema.md"
    if not schema.is_file():
        errors.append({"code": "missing_schema", "message": "缺少 core/data-schema.md"})
        text = ""
    else:
        text = schema.read_text(encoding="utf-8-sig")
        enum_section = text.split("## 5. Canonical enums", 1)[-1]
        doc_keys = set(re.findall(r"^\|\s*`([a-z_]+)`\s*\|", enum_section, re.M))
        missing_keys = sorted(set(ENUMS) - doc_keys)
        extra_keys = sorted(doc_keys - set(ENUMS) - {"mastery_level", "difficulty", "quality_dimension"})
        if missing_keys:
            errors.append({"code": "enum_undocumented",
                           "message": "枚举未在 data-schema.md §5 定义：" + ", ".join(missing_keys)})
        if extra_keys:
            warnings.append({"code": "extra_enum_doc",
                             "message": "文档多出的枚举小节：" + ", ".join(extra_keys)})
        missing_values = [v for values in ENUMS.values() for v in values if v not in text]
        if missing_values:
            errors.append({"code": "enum_value_undocumented",
                           "message": "代码枚举值未写进文档：" + ", ".join(sorted(set(missing_values)))})

    orchestrator = root / "core" / "orchestrator.md"
    if not orchestrator.is_file():
        errors.append({"code": "missing_orchestrator", "message": "缺少 core/orchestrator.md"})
    else:
        for rel in sorted(set(ROUTE_RE.findall(orchestrator.read_text(encoding="utf-8-sig")))):
            if "/" not in rel:
                continue
            candidate = root / rel
            if not candidate.is_file():
                errors.append({"code": "broken_route",
                               "message": f"orchestrator.md 路由表引用 {rel} 不存在"})
        for token in ("INTAKE", "CLASSIFY", "MAP", "VALIDATE", "PLAN", "DIAGNOSE",
                      "TEACH", "ASSESS", "REMEDIATE", "REPLAN", "PERSIST", "CONTINUE"):
            if token not in orchestrator.read_text(encoding="utf-8-sig"):
                errors.append({"code": "missing_stage", "message": f"生命周期缺少 {token}"})

    skill = root / "SKILL.md"
    if skill.is_file():
        skill_text = skill.read_text(encoding="utf-8-sig")
        for rel in ("core/orchestrator.md", "core/data-schema.md",
                    "references/quality-gates.md", "learning/misconception.md",
                    "learning/spaced-review.md", "memory/version-control.md",
                    "scripts/run_tests.py"):
            if rel not in skill_text:
                errors.append({"code": "missing_entry_link",
                               "message": f"SKILL.md 未引用核心模块 {rel}"})

    compiled = 0
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
            compiled += 1
        except SyntaxError as exc:
            errors.append({"code": "syntax_error", "message": f"{path.name}:{exc.lineno} {exc.msg}"})

    headings = Counter()
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for title in re.findall(r"^##\s+(.+)$", path.read_text(encoding="utf-8-sig"), re.M):
            headings[title.strip()] += 1
    repeated = [f"{k} ({v} 处)" for k, v in headings.items() if v >= 3]
    if repeated:
        warnings.append({"code": "possible_duplicate_rules",
                         "message": "重复标题需人工确认是否重复定义：" + "；".join(repeated)})

    result = {
        "errors": errors, "warnings": warnings,
        "stats": {"enums": len(ENUMS), "scripts_compiled": compiled,
                  "markdown_headings": sum(headings.values())},
        "summary": ("一致性校验失败：%d 个问题" % len(errors)) if errors else "一致性校验通过",
    }
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
