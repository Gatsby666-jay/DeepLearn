# V3 Baseline — V2 审计记录（2026-11-12）

## 1. 审计范围与方法

读取 V2 全部 **64 个文件**（含 8 个 Python 脚本、24 个测试样本、29 份 Markdown、10 个模板/示例），运行全部校验器与 47 个测试用例；逐目录核对职责、被引用关系与调用关系。**依据实际文件与执行输出，不依据文档自述。**

## 2. 目录与职责

| 目录 | 职责 | 被引用方 |
|---|---|---|
| `SKILL.md` | V2 入口、模块路由表、确定性校验命令 | 平台加载器 |
| `core/` | Orchestrator 12 阶段、统一数据 schema | SKILL.md、全部模块 |
| `references/` | 11 份方法论（分类/拆解/三图/门禁/原理/教学/评估/迁移/路径/状态/资源） | Orchestrator 路由表 |
| `learning/` | 误解诊断、间隔复习 | Orchestrator、teaching、state |
| `memory/` | 版本与快照 | state-management |
| `scripts/` | 8 个 Python：7 校验/共享库 + 1 测试入口 | SKILL.md、tests |
| `templates/` | KnowledgeNode / LearnerProgress JSON | validate_schema、tests |
| `assets/` | 6 个输出骨架 | 各 Mode |
| `tests/` | cases.json(47) + 24 fixtures | run_tests.py |
| `examples/` | 4 个首轮响应锚点 | SKILL.md |

## 3. 数据结构与调用关系

V2 单一事实来源 = `core/data-schema.md` + 可执行的 `scripts/deeplearn_rules.py`（15 组枚举、`NODE_REQUIRED`、`PROGRESS_REQUIRED`）。三轴严格分离：`parent_id`（组织结构）/ `prerequisites`（学习依赖）/ `mastery_level`（学习者水平），`decomposition_level` 永不表示掌握度。

调用链：`SKILL.md` → `core/orchestrator.md` → `references/*`；确定性层由 `deeplearn_rules.py` 提供共享校验函数，`validate_schema.py` / `validate_map.py` / `validate_state.py` / `validate_references.py` / `check_consistency.py` / `validate_roadmap.py` 各自 import；`run_tests.py` 通过 subprocess 串联全部脚本。

## 4. V2 基准测试结果（实际执行）

| 命令 | 结果 |
|---|---|
| `quick_validate.py` | 通过 |
| `run_tests.py` | **47 用例：44 通过 / 0 失败 / 3 未自动化**（29 script + 12 contract + 3 pipeline + 3 not_automated） |
| `validate_references.py` | checked 93，内部引用全部有效 |
| `check_consistency.py` | enums 15、scripts_compiled 8、markdown_headings 181，通过 |
| `package_skill.py` | Skill is valid |
| git | `142f913 fix(v2.1): audit-driven gate, state and roadmap validation` |

## 5. V3 兼容性分析

| 项 | 结论 |
|---|---|
| V2 schema | **不修改**；V3 新增结构放在 `core/v3-schema.md` 与 `scripts/v3_rules.py` |
| V2 测试 | **不删除、不改写断言**；V3 新增独立 `tests/v3_cases.json` 与 `benchmarks/` |
| V2 状态文件 | 旧 `state.json` 缺 V3 字段时按默认值补，不改已有值、不覆盖 evidence/history |
| V2 模块 | `learning/`、`references/`、`memory/` 全部保留，V3 只新增目录 |
| 迁移 | `scripts/migrate_v2_v3.py` 提供备份、迁移、校验、回滚与报告 |
| 风险 | 见 §6 |

## 6. 风险清单

| ID | 风险 | 缓解 |
|---|---|---|
| R1 | 扩展 schema 破坏 V2 校验 | V2 校验器零改动；V3 用独立 `validate_v3_schema.py` |
| R2 | 迁移覆盖学习历史 | 迁移前强制备份；只增字段不删字段；提供 `rollback` |
| R3 | 能力等级与知识掌握度混淆 | 两套独立 ID 空间（`NODE-*` / `COMP-*`）与独立进度结构 |
| R4 | 多模态能力假设过强 | `multimodal/capability-fallback.md` 强制能力探测与降级 |
| R5 | 自评被当作掌握证据 | `evidence_source` 枚举区分 self_report / model_inference / objective_assessment |
| R6 | 单次错误触发图谱重构 | 变更提案需 `evidence_count >= 2` 且 `confidence >= supported` |
| R7 | Benchmark 只做字符串匹配 | `run_benchmark.py` 对结构/分类/前置/策略做确定性断言 |
| R8 | 实验未运行却声称成功 | `execution_status` 枚举：executed / theoretical / simulated / not_run |

## 7. Phase 0 结论

V2 基线稳定，可原地扩展。V3 采用「**保留 + 新增 + 迁移**」策略，不重构、不移动、不删除。
