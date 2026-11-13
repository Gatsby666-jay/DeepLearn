# Changelog


## v3.0.1 — 工程卫生与决策引擎修复（2026-11-13）

依据 2026-11-13 外部评审《DeepLearn 项目问题与改进措施》落地，**V3 数据结构与学习闭环零改动**。

| 项 | 内容 |
|---|---|
| 许可证 | 新增 `LICENSE`（MIT，Copyright (c) 2026 Gatsby666-jay）；README 快速开始注明协议，解除 fork / 集成的法律阻塞 |
| 持续集成 | 新增 `.github/workflows/test.yml`：push / PR 自动跑 compileall、引用、一致性、V2、V3、Benchmark、迁移、图与路线图校验共 8 组命令；README 挂状态徽章 |
| 文档事实订正 | README 验证表头日期改为实际执行日、证据强度拆成「脚本 81 / 契约 20 / 串联 5 / **端到端 0** / 未自动化 6」、引用数 126→127；`docs/V3_TEST_REPORT.md` 修正把 SA–SH 误述为「非空字符串检查」（实际为 `trace.priority` 精确值断言）与迁移「7 项」→ 8 项；CHANGELOG 同步 |
| 普适性边界 | README 删除「演奏」等无边界主张，限定为陈述性 / 可形式化程序性知识；已知限制新增默会知识与运动技能条目 |
| `decision_engine.py` | ① 新增 `BlockingValidation`，业务阻塞返回退出码 1、参数与解析错误返回 2（原 docstring 声明的 1 永不发生）；② `preferences` 非 dict 受控拒绝，不再 traceback；③ `time_constraint_hours` 真正参与分支（≤2h 时 P6 收缩为最小可达子集，P1/P2 补救不被跳过）；④ `created_at` 改运行时 UTC，去掉硬编码日期；⑤ 修正空信号错误文案 |
| 测试 | `run_v3_tests.py` 支持 `expect_json_ne`；新增 V27–V32 六条回归与 5 个 fixture；V13 期望退出码 2→1（语义归位，非放宽） |
| 首轮自检 | `SKILL.md` 新增 8 条首轮响应自检清单，把 G1–G5 前置到 Agent 必然加载的内容；明确「脚本不能宿主强制拦截」 |
| 发布方式 | `publish_v2.py` 从 Contents API 逐文件 PUT 改为 Git Data API 单提交（tree → commit → ref），一次发布只产生 1 条 commit；**不重写历史** |

### 测试

V2 47（44 通过 / 0 失败 / 3 未自动化）+ V3 53（50 通过 / 0 失败 / 3 未自动化）+ Benchmark 12 = **112 用例，106 通过 / 0 失败 / 6 未自动化**；`validate_references.py` 127 处引用有效；`check_consistency.py` 18 个脚本可编译；`package_skill.py` 报 Skill is valid；GitHub Actions 首次运行绿。

### 历史提交说明

2026-11-12 的 v3.0 推送产生 30+ 条同名 commit，成因是旧发布脚本按文件调用 Contents API，每个文件生成一条 commit，并非逐文件测试后的独立提交。自 v3.0.1 起改为单提交；已有历史保留，不做 rebase / force push。


## v3.0 — Adaptive Learning Intelligence System（2026-11-12）

从 Knowledge-Centered Learning 升级为 **Learner-Centered Competency Development**。**V2 零删除、零移动、零 schema 改动**：64 个原文件、47 个测试、8 个脚本行为、12 阶段 Orchestrator 全部保留。

### 六大引擎与新增目录

`intelligence/`（学习者画像/自适应/决策）、`knowledge/`（图谱进化/关系/来源可信度）、`competency/`（能力模型/映射/评估/评分标准）、`practice/`（练习/实验/项目/实践评价）、`multimodal/`（输入适配/图片/代码/能力降级）、`evaluation/`（学习效果/教学质量/Benchmark）、`benchmarks/`（12 领域）、`docs/`（V3_BASELINE / V3_ARCHITECTURE / V3_MIGRATION / V3_TEST_REPORT / V3_ROADMAP）、`core/v3-schema.md`、`core/v3-integration.md`、`memory/learner-history.md`。

### 统一数据模型

新增 10 类 V3 结构（LearnerProfile / Competency / CompetencyProgress / LearningEvent / PracticeTask / PracticeEvidence / LearningPlan / KnowledgeGraphChange / Resource / AssessmentResult），全部带唯一 ID、`schema_version=3`、时间字段、来源/证据引用、明确枚举与空值规则；`scripts/v3_rules.py` 为可执行单一事实来源，`scripts/validate_v3_schema.py` 校验跨模块引用。V2 的 KnowledgeNode / LearnerProgress / 15 组枚举**原样保留**。

### 工程实现（可执行、已测试）

`v3_rules.py`、`validate_v3_schema.py`、`migrate_v2_v3.py`（backup/migrate/verify/rollback）、`decision_engine.py`（九项输出 + 六级优先级 + 理由）、`competency_engine.py`（七维评分 → C0–C5）、`practice_engine.py`（类型推荐 + 三级提示校验）、`knowledge_evolution.py`（提案证据门槛）、`run_benchmark.py`、`run_v3_tests.py`、`test_migration.py`。

### 测试结果

- V2 回归 `run_tests.py`：47 用例 44 通过 / 0 失败 / 3 未自动化（**未退化**）
- V3 套件 `run_v3_tests.py`：47 用例 44 通过 / 0 失败 / 3 未自动化；含场景 A–H 决策优先级断言、10 模板校验、能力/练习/图谱引擎、迁移全流程、V2 回归
- `run_benchmark.py`：12 领域 12 通过 / 0 失败
- `quick_validate.py` 通过；`validate_references.py` 126 处引用有效；`check_consistency.py` 18 个脚本可编译；`package_skill.py` Skill is valid

### 迁移与回滚

`docs/V3_MIGRATION.md` 定义只增不改的字段映射；`migrate_v2_v3.py` 无备份拒绝迁移、迁移前校验 sha256、verify 逐字段比对 V2 原值、rollback 恢复原始字节。`test_migration.py` 端到端断言 8 项全部通过。

### 已知限制

Orchestrator / state 读写快照 / replan / 复习调度 / 资源验证器仍为规则级设计；图片识别、代码执行、仿真为宿主可选能力，本包只提供适配与降级；教学质量主观评价与真迁移题质量未自动化（N01–N03）。详见 `docs/V3_ROADMAP.md`。


## v2.1 — 工程验收缺陷修复（2026-11-12）

依据 2026-11-12 工程验收报告（CONDITIONAL PASS）G 节逐项修复，**未移动或删除任何文件**。

| 缺陷 | 修复 |
|---|---|
| 六问验收门 / G1 可绕过（`atomic_gate`、`decomposition_quality`、`mechanism` 全可选） | `deeplearn_rules.py` 增加条件必填与 `gate_incomplete`；缺字段报 `gate_missing` / `quality_missing` / `missing_mechanism` |
| `evidence.mastery_decision` 与 `mastery_level` 不一致不报 | `validate_state.py` 新增 `mastery_evidence_mismatch` |
| `history` 清空、阶段与事件矛盾均通过 | 新增 `history_missing`、`stage_event_mismatch` |
| `--strict` 误判合法多分支 | 仅孤立节点阻断；`disconnected_components` 保留警告 |
| 字段缺失误报 `self_loop`、v2 不支持 `from`/`to` 别名 | 自环判断要求两端非 None；v2 边字段归一化 |
| roadmap 校验器完全缺失 | 新增 `scripts/validate_roadmap.py`（阶段拓扑序、缺失前置、阶段引用、关键路径工期、非法时长、阶段环） |
| 12 个场景用例只是字符串包含检查 | T 用例改名「契约检查」；新增 3 个 `pipeline` 用例串联多校验器验证真实数据流 |
| SKILL.md 脚本职责表述笼统 | 改为逐脚本分工表，并把 `validate_roadmap.py` 加入校验命令 |

### 测试

`run_tests.py` → **47 用例：44 通过 / 0 失败 / 3 未自动化**（29 script + 12 contract + 3 pipeline + 3 not_automated）。新增 R1–R4（路线图）、G1–G6（缺陷回归）、E1–E3（多校验器串联场景）。

独立探针复核：P1 由 `exit=0 errors=[]` 变为 `exit=1` 含 `gate_missing/quality_missing/missing_mechanism`；P3b/P7/P8 分别命中 `mastery_evidence_mismatch` / `history_missing` / `stage_event_mismatch`；P4 strict 由 1 变 0；P6 不再误报自环。

### 仍未改变

Orchestrator、state 读写/快照、replan、复习调度、资源验证器、Lesson 生成仍是**规则级设计**，本次未实现运行时执行层；真实 Agent 端到端回归仍未建立。

## v2.0 — 完整闭环架构升级（2026-11-09）

### 架构审计发现（修改前）

审计对象：V1 全部 23 个文件（SKILL.md、README.md、references/ 11、assets/ 6、scripts/ 1、examples/ 3），逐个核对职责、被引用关系与实际使用情况。基线 `quick_validate.py` 通过，无断链。

| 类别 | 发现 |
|---|---|
| 缺失文件 | Orchestrator、统一数据 schema、误解诊断、间隔复习、版本管理、结构化 JSON 模板、测试套件、CHANGELOG |
| 缺失 schema | KnowledgeNode / LearnerProgress / DependencyEdge 只在散文中描述，字段命名不统一（`mastery` vs `mastery_level`），无机器可读定义 |
| 重复规则 | 六问验收与门禁细则同时写在 SKILL.md、quality-gates.md、decomposition.md；三图与严格模式说明在两处重复 |
| 冲突规则 | 「讲解 ≤25 行」被写成硬上限，与「不得牺牲概念完整性」冲突；`--strict` 的「零孤立节点」与「根节点合法」冲突 |
| 不完整工作流 | 阶段按 Mode 描述，但无统一生命周期、无状态转换表、无失败阻塞与中断恢复；诊断后没有强制回流到路线重排 |
| 未实现功能 | 学习意图层、类别感知六问、分解质量分、节点去重、目标相对基础、Integration Lesson、动态关键路径、事件驱动持久化、间隔复习 |
| 无效假设 | 假设所有节点都应有一条入边；V2 明确 root / terminal / 声明用途的独立可选概念合法 |
| 缺失测试 | 只有人工 dry-run 记录，没有可执行用例与确定性断言 |

### 关键设计决策

1. **不移动任何 V1 文件**。`references/`、`assets/`、`scripts/`、`examples/` 路径与内部链接全部保留；新增内容放进 `core/`、`learning/`、`memory/`、`templates/`、`tests/`。`core/orchestrator.md` 的模块路由表是职责归属的单一事实来源，规则只在权威文件定义一次。
2. **确定性验证交给 Python**。新增 `scripts/deeplearn_rules.py` 作为枚举与必填字段的可执行单一事实来源；6 个校验脚本 + 1 个测试入口。**未单独创建 `validate_dependencies.py`**：依赖边校验已由增强后的 `validate_map.py` 完整覆盖，拆成两个脚本只会重复规则。
3. **闭环优先于功能数量**。实现 12 阶段生命周期、5 种工作流、状态转换表；硬性规定 `VALIDATE` 失败阻塞、无证据不得前进、`REMEDIATE → REPLAN → PERSIST → CONTINUE` 必须回流、中断按 `current_stage` 恢复。
4. **V1 兼容修正**：`≤25 行` 从硬上限改为可读性指导；`--strict` 不再拒绝所有无入边节点，孤立项与断连组件作为警告，仅 strict 下阻断。Mermaid 与 V1 简单 JSON 输入格式保持可用（S13/S14 回归通过）。
5. **版本线厘清**：上一轮「六问验收 + 五道门禁」原在 README 中标为 V2，本次更正为 **v1.1**；本次完整架构升级为 **v2.0**。

### 新增文件

`core/orchestrator.md`、`core/data-schema.md`、`learning/misconception.md`、`learning/spaced-review.md`、`memory/version-control.md`、`templates/knowledge-node.json`、`templates/learner-progress.json`、`scripts/deeplearn_rules.py`、`scripts/validate_schema.py`、`scripts/validate_references.py`、`scripts/validate_state.py`、`scripts/check_consistency.py`、`scripts/run_tests.py`、`tests/cases.json`、`tests/fixtures/`（14 个 JSON 样本）、`examples/technical-domain.md`、`CHANGELOG.md`。

### 修改文件

`SKILL.md`（重写为 V2 入口）、`README.md`、`scripts/validate_map.py`（重写增强，保持 V1 输入兼容）、11 份 `references/`、2 个 `assets/` 模板（均以追加 V2 增补章节方式修改，未删 V1 内容）。

### 移除 / 替换文件

无文件被移除。`validate_map.py` 被重写但保留全部 V1 命令行行为（`-`、`--json`、`--strict`、退出码语义）。

### 实现状态分级

| 能力 | 状态 |
|---|---|
| 统一 schema、枚举、ID 规则 | 已实现并测试（S1–S3、S8–S12） |
| 图校验（环/自环/重复 ID/缺失引用/枚举/重复边/断连/门禁） | 已实现并测试（S4–S14） |
| 状态与证据校验（含冲突证据） | 已实现并测试（S15–S17） |
| 内部引用与跨模块一致性 | 已实现并测试（S18–S19） |
| 12 阶段生命周期、5 工作流、闭环与中断恢复 | 已实现；契约级测试（T1–T12），未在真实 Agent 会话中端到端执行 |
| 统一 schema 在真实运行时被 Agent 完整遵守 | 已实现但**未充分测试**：脚本能校验提交给它的数据，不能保证 Agent 每次都生成合规 JSON |
| Atomic / Integration Lesson、误解诊断、间隔复习、版本快照 | 已实现为可执行规则文档；契约级测试通过，教学质量未自动化验证 |
| 自适应教学质量、误解根因准确度、真迁移判定 | **未自动化**（N1–N3），依赖执行 Agent 判断与质量门禁自检 |
| 资源引擎联网验证 | 仅文档实现；不编造 URL，未验证即标注 |

### 测试结果

`python scripts/run_tests.py` → 合计 34：通过 31、失败 0、未自动化 3。
`quick_validate.py` 通过；`validate_references.py` 检查 92 处引用全部有效；`check_consistency.py` 通过（1 条警告：`使用说明` 标题在 3 个 assets 模板中重复，属模板通用标题，非重复规则）。

### 已知限制

- 门禁是规则级检查，依赖执行 Agent 运行自检清单；宿主层不强制拦截。
- 脚本只做结构化确定性验证，不判定解释正确性、类比恰当性或迁移题质量。
- 12 个生命周期用例是文档契约检查 + 确定性脚本断言，不是真实 Agent 端到端回归。
- state 需要可写 workspace；不可写时声明「仅会话内生效」。
- Mermaid 渲染取决于宿主客户端。

## v1.1 — 质量门禁与六问原子验收（2026-11-09）

依据外部评审的五个问题（只生成目录、知识点孤立、解释停在概念层、文字墙教学、无法判断掌握），新增 `references/quality-gates.md`，把「拆解深度 ≠ 目录长度」固化为六问验收门与 G1–G5 五道门禁；`scripts/validate_map.py` 增加 `--strict`；同步修正 SKILL.md、7 份 references、模板与示例。文件数 22 → 23。

## v1.0 — 通用学习拆解引擎（2026-11-09）

初始版本：七类分类、L0–L6 递归拆解、三图引擎、13 项第一性原理、0–5 掌握度、反向教学与四类迁移、A/B/C 路径、六种 Mode、状态管理、资源引擎、`validate_map.py`。发布至 GitHub 并安装到 WorkBuddy 用户级 skills 目录。
