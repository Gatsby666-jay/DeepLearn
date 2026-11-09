#!/usr/bin/env python3
"""Check every internal Markdown link, script and template reference in the skill.

Usage: python validate_references.py [root] [--json]
Exit codes: 0 valid, 1 broken references, 2 argument error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from deeplearn_rules import emit, markdown_links

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|json|py))`")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 DeepLearn V2 内部引用")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"不是目录：{root}", file=sys.stderr)
        return 2

    errors, warnings, checked = [], [], 0
    for source, target in markdown_links(root):
        resolved = (source.parent / target).resolve()
        checked += 1
        if not resolved.exists():
            errors.append({"code": "broken_link",
                           "message": f"{source.relative_to(root)} -> {target}（目标不存在）"})

    # Paths mentioned inside the Orchestrator routing table and other core docs.
    for doc in sorted((root / "core").glob("*.md")) if (root / "core").is_dir() else []:
        text = doc.read_text(encoding="utf-8-sig")
        for path_str in set(BACKTICK_PATH_RE.findall(text)):
            if "/" not in path_str:
                continue
            candidate = root / path_str
            checked += 1
            if not candidate.is_file():
                errors.append({"code": "broken_route",
                               "message": f"{doc.relative_to(root)} 路由表引用 {path_str} 不存在"})

    required = ["SKILL.md", "core/orchestrator.md", "core/data-schema.md",
                "references/quality-gates.md", "scripts/validate_map.py",
                "scripts/validate_schema.py", "scripts/run_tests.py",
                "templates/knowledge-node.json", "templates/learner-progress.json"]
    for rel in required:
        checked += 1
        if not (root / rel).is_file():
            errors.append({"code": "missing_required", "message": f"缺少必需文件 {rel}"})

    result = {
        "errors": errors,
        "warnings": warnings,
        "stats": {"checked": checked, "root": str(root)},
        "summary": ("校验失败：%d 个断链/缺失" % len(errors)) if errors else "校验通过：内部引用全部有效",
    }
    emit(result, args.json)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
