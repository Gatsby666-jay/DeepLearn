---
name: deeplearn
description: 当用户提出学习目标、要求搞懂某个概念或原理、拆解一门学科或技术、上手某个工具、追问「为什么／怎么工作」、做一个项目或练成一项能力时触发；由 Orchestrator 驱动完整学习闭环，先分类并生成知识结构图、知识依赖图、学习路线图，按统一 schema 递归拆解到知识原子，通过自适应教学、误解诊断、证据化评估与动态重排验证真实理解。不适用于只要一句话解释、索要习题答案、生成课件或资料清单、制定纯时间表。
---

# DeepLearn V2

## 核心目标

把任意学习目标转成可迁移的理解与实际能力。核心原则：**递归拆解 → 统一数据 → 三图校验 → 闭环教学 → 证据验证 → 动态重排**。本 Skill 与具体学科、工具、项目无关，所有策略均为通用方法。

**拆解深度不等于目录长度。** 真正的深度是能回答：为什么这个知识存在、解决什么问题、依赖什么基础、为何成立、能否从原理推出、如何证明真的懂了。

V2 最重要的不是功能数量，而是**完整闭环**：理解目标 → 构建知识网络 → 规划路线 → 自适应教学 → 检测掌握 → 纠错 / 调整路线 / 保存进度 → 继续学习（循环）。

## 工作原则（硬约束）

1. 先建立全局认知，再局部深挖；先理解底层原理，再掌握上层应用；先验证理解，再进入下一节点。
2. 首次响应只给：分类 + 三图全局概览 + 下一步选择。禁止一次性长篇教学（首轮 ≤40 行 / ≤800 字）。
3. 渐进披露：全局图 → 选分支 → 递归拆解 → 选知识点 → 单节点教学 → 练习验证 → 更新状态 → 下一节点。
4. **知识树 ≠ 学习序列**；**知识深度 ≠ 掌握度**；**父子关系 ≠ 前置关系**。
5. 不以「已讲解」判定掌握；升级必须有练习、推理或实践证据。
6. 每个原子单元过「六问验收门」并满足五道质量门禁（[references/quality-gates.md](references/quality-gates.md)）；任一门未过不得推进。
7. 闭环不得线性结束：`REMEDIATE → REPLAN → PERSIST → CONTINUE` 必须回流到 `TEACH` / `MAP` / `PLAN`；`VALIDATE` 失败停在 `VALIDATE`。

## V2 架构与入口（单一事实来源）

| 职责 | 权威文件 |
|---|---|
| 生命周期、5 工作流、闭环、状态转换 | [core/orchestrator.md](core/orchestrator.md) |
| KnowledgeNode / LearnerProgress / 边 / 枚举 | [core/data-schema.md](core/data-schema.md) |
| 分类 + 学习意图 + 置信度 | [references/classification.md](references/classification.md) |
| 递归拆解（自适应深度、去重、质量分） | [references/decomposition.md](references/decomposition.md) |
| 三图与边类型 | [references/three-graphs.md](references/three-graphs.md) |
| 质量门禁与六问验收 | [references/quality-gates.md](references/quality-gates.md) |
| 第一性原理与正确性检查 | [references/first-principles.md](references/first-principles.md) |
| Atomic / Integration Lesson | [references/teaching.md](references/teaching.md) |
| 评估、证据、冲突证据 | [references/assessment.md](references/assessment.md) |
| 误解诊断 | [learning/misconception.md](learning/misconception.md) |
| 间隔复习 | [learning/spaced-review.md](learning/spaced-review.md) |
| 反向教学与迁移 | [references/transfer-reverse.md](references/transfer-reverse.md) |
| A/B/C + 目标导向路径 | [references/learning-paths.md](references/learning-paths.md) |
| 事件驱动状态 | [references/state-management.md](references/state-management.md) |
| 版本与快照 | [memory/version-control.md](memory/version-control.md) |
| 资源发现 | [references/resources.md](references/resources.md) |
| 结构化模板 | `templates/`（JSON）、`assets/`（Markdown） |
| 确定性校验 | `scripts/`（`scripts/run_tests.py` 为测试入口） |
| 测试样本与用例 | `tests/` |

规则只在权威文件里定义一次；V1 路径全部保留，未移动任何既有文件。

## 激活与交互模式

| Mode | 用户意图 | 首轮产物 |
|---|---|---|
| Explore | 想知道某领域包含什么 | 分类 + 意图 + 三图概览 + 推荐序列 |
| Decompose | 要尽可能深地拆开 | 层级树 + 六问验收 + 依赖边 + 原理追溯链 + 基础边界 |
| Deep Dive | 彻底搞懂一个概念 | 概念分解 + 按需第一性原理项 + 推导 + 一节聚焦课 + 验证与迁移 |
| Learn | 要被带着一步步学 | 路线图 + 当前一课（单节点）+ 讲解 + 练习 + 反馈 |
| Build | 要做实际项目 | 交付物 + 子系统 + 技术依赖 + 目标导向路线 + 测试 |
| Diagnose | 想找知识缺口 | 诊断题 → 误解定位 → 定向补救 → 重测 → 重排路线 |

Mode 随时可切换；切换保留 state，不重建图。默认 Explore。由 Orchestrator 选择工作流 A–E，不把宽泛学科流程强加给简单问题。

## 输入规范

- 必需：目标文本。可选：起点、可用时间、用途、约束、偏好深度。
- 缺失采用默认（零基础 / 每周 3–5h / 能应用并讲清 / 中文资料），首行标「假设：…」后继续。
- 仅目标完全不明且无法合理假设时提 **1 个**澄清问题，同时给出降级产物。

## 分类引擎

保留七类 A–G（academic_subject / individual_concept / technical_domain / software_tool / specific_problem / practical_project / competency）。新增**独立的学习意图层**：understand / use / research / build / solve / master / exam。分类与意图互不替代；输出主类、辅类、意图、置信度与依据。详见 [references/classification.md](references/classification.md)。

## 三图引擎

| 图 | 边语义 | 回答 | 结构 |
|---|---|---|---|
| 知识结构图 | A **包含** B | 有哪些部分 | 树，父唯一 |
| 知识依赖图 | B **必须先于** A | 学会前要会什么 | DAG，跨分支、带边类型 |
| 学习路线图 | 阶段 N 先于 N+1 | 按什么顺序学 | 阶段序列 + 属性 |

依赖边字段：`source_node_id → target_node_id`（方向恒定）、`dependency_type`（conceptual / mathematical / physical / operational / implementation）、`necessity`（required / recommended）、`explanation`。仅 required 边进入 `prerequisites`。

生成顺序：结构图 → 补依赖边（主动找跨分支边）→ 运行 `scripts/validate_map.py --strict` → 拓扑排序 → 叠加目标/状态生成 A/B/C 或目标导向路线 → 状态变化时动态重排。**root、terminal、声明用途的独立可选节点合法**；环必须阻断路线图。详见 [references/three-graphs.md](references/three-graphs.md)。

三图骨架：[assets/knowledge-map.md](assets/knowledge-map.md)、[assets/prerequisite-graph.md](assets/prerequisite-graph.md)、[assets/learning-roadmap.md](assets/learning-roadmap.md)。

## 递归拆解引擎

层级 L0–L6 为概念性刻度，按类别选分解链与深度，不对所有知识用同一套。对每个节点问八问（是什么 / 解决什么 / 含哪些组件 / 依赖什么 / 如何工作 / 为何成立 / 能否独立解释应用 / 还缺什么）。

六问原子验收改为**类别感知**：每问 `passed` / `failed` / `not_applicable`，不适用给理由；缺适用项即继续下钻。分解质量分六维各 0–2（总 12），`dependency_correctness` / `explanatory_depth` / `verifiability` 任一低于 2 即门禁失败。

节点 ID 稳定 `NODE-\d{3,}`，`aliases` 别名映射，跨分支同一概念用 `canonical_id` 指向规范节点；不得仅因名称相近合并。基础深度按目标相对确定，到达真实边界时显式声明理由，不无限下钻。禁止目录式拆解（只列名词无机制/原理/依赖）。详见 [references/decomposition.md](references/decomposition.md) 与 [core/data-schema.md](core/data-schema.md)。

## 第一性原理分析

13 项框架按需选取；每个重要节点写 `trace_chain`：节点 → 机制 → 支撑原理 → 基础边界，并明确回答「为什么成立」。做假设检查、推导条件检查、量纲/单位一致性（适用时）、反例与边界检查；区分定理 / 经验观测 / 模型 / 近似 / 假设 / 类比，不把类比当机制。详见 [references/first-principles.md](references/first-principles.md)、[assets/concept-analysis.md](assets/concept-analysis.md)。

## 教学、诊断与评估

- **Atomic Lesson**：一次一个新机制，九段结构（目标 → 前置 → 直觉 → 定义 → 机制 → 原理连接 → 示例 → 验证 → 独立推理）。
- **Integration Lesson**：把已学多个节点串成完整系统，不引入新基础材料、不重复讲单点。
- 表征按知识类型选（图 / 推导 / 可跑代码 / 实验 / 类比+反例 / 时序图 / 状态表）；不理解时换表征、简化、回退前置、给新题，不重复原文。25 行是可读性指导，不是硬上限。
- 误解诊断十类错误 + 证据门槛，见 [learning/misconception.md](learning/misconception.md)。
- 评估十类、`evidence` 八字段、`confidence` 与 `mastery_level` 分轴；冲突证据并存、不得判 L4/L5；掌握度 0–5 定义见 [core/data-schema.md](core/data-schema.md)。
- 复习按掌握度、近期表现、错误频率、难度、时间间隔、重要性差异化排程，见 [learning/spaced-review.md](learning/spaced-review.md)。

单课骨架：[assets/lesson.md](assets/lesson.md)。评估细则：[references/assessment.md](references/assessment.md)。

## 反向教学与迁移

从 L5/L6 原理出发逐层重建上层，七步不泄露结论。迁移任务写全 `target_node_id / required_prerequisites / transfer_distance / expected_reasoning / evaluation_criteria`；四类模板（跨域同构、对象变化、远域连接、反事实）不变。Level 5 必须有反向教学重建 + 两类以上迁移证据。不得把「缺前置」误判为「迁移能力不足」。详见 [references/transfer-reverse.md](references/transfer-reverse.md)。

## 学习路径与闭环

A 入门 / B 高效（默认）/ C 深研 + 目标导向路径；排序前置优先，关键路径按工期而非节点数计算。重排触发：掌握度变化、缺失前置、图变化、目标变化、时间约束、重复错误；保留已完成进度，不整表重建。

闭环由 [core/orchestrator.md](core/orchestrator.md) 控制：`INTAKE → CLASSIFY → MAP → VALIDATE → PLAN → DIAGNOSE → TEACH → ASSESS → REMEDIATE → REPLAN → PERSIST → CONTINUE`。每阶段有入口条件、成功判据、失败处理与事件写回；验证失败不得前进，中断可按 `current_stage` 恢复。

## 状态、版本与资源

- 每个重要事件立即写回，不等会话结束；项目目录独立，状态字段由 `scripts/validate_state.py` 校验。
- 版本化三图与节点，图变更不得清空已证明掌握度，仅必要时定向重评；快照与 changelog 见 [memory/version-control.md](memory/version-control.md)。
- 资源必须绑定 `NODE-*`，记录 title/source/url/type/difficulty/language/relevant_node_ids/prerequisites/intended_use/last_verified；不编造 URL，未验证标 `last_verified: null`。资源不是掌握度证据。

模板：[assets/progress-tracker.md](assets/progress-tracker.md)、`templates/knowledge-node.json`、`templates/learner-progress.json`。

## 确定性校验（不靠模型判断）

```bash
python scripts/validate_schema.py templates/knowledge-node.json --json
python scripts/validate_map.py graph.json --strict --json
python scripts/validate_roadmap.py roadmap.json --json
python scripts/validate_references.py --json
python scripts/validate_state.py state.json --json
python scripts/check_consistency.py --json
python scripts/run_tests.py --json
```

脚本分工：`validate_schema.py` 管字段、枚举、父子引用与门禁条件必填；`validate_map.py` 管图结构（重复 ID、缺失引用、自环、环、重复边、边类型、断连分量、孤立节点）；`validate_roadmap.py` 管阶段拓扑序、缺失前置、阶段引用、关键路径工期与非法时长；`validate_state.py` 管证据、掌握度、历史与阶段事件一致性；`validate_references.py` 管内部链接；`check_consistency.py` 管跨模块枚举与脚本可编译性。退出码 `0` 通过 / `1` 校验失败 / `2` 参数或解析错误；`--strict` 阻断孤立节点，但**合法多连通分量只作警告**。**脚本不判定教学质量、解释正确性或迁移题质量**，这些由质量门禁自检清单约束。

## 输出格式

按 Mode 输出对应字段（模板见 `assets/`）；通用首行「假设：…」、末行「下一步：…（2–3 个动作）」。禁止鼓励语、空泛形容词、无判据的「已掌握」。Learn 一次只教一个节点。格式锚点：[examples/academic-subject.md](examples/academic-subject.md)、[examples/individual-concept.md](examples/individual-concept.md)、[examples/technical-domain.md](examples/technical-domain.md)、[examples/practical-project.md](examples/practical-project.md)。每轮按 [references/quality-gates.md](references/quality-gates.md) 自检清单过一遍。

## 边界与禁止项

- 不做通用辅导闲聊、不堆资料清单、不出习题答案、不做纯时间表、不生成课件。
- 不做目录式拆解；不靠层级数冒充深度；L3 以下无机制或原理不计入成果。
- 不一次性倾倒几万字教学；不在前置未达标时教进阶。
- 不混淆知识树与依赖顺序、知识深度与掌握度、父子与前置、置信度与掌握度。
- 不在依赖图里留环；不因节点无入边就一律拒绝；不把定义当解释，不把类比当机制。
- 不无证据升级掌握度、不覆盖历史证据、不因图变化重置全部进度、不重建未变化的图。
- 不虚构章节、版本、API、论文或 URL；不确定标「待核实」。
- 不把具体学科、工具或项目写进规则本身；不把复杂流程强加给简单问题。

## 失败处理

| 情形 | 动作 |
|---|---|
| 目标含糊 | 1 个澄清 + 基于假设的降级概览 |
| 目标与时间冲突 | 保留目标，给最小可达子集 + 未覆盖范围 |
| 复合 / 跨类 | 主 + 辅策略，三图只出一套 |
| `VALIDATE` 失败（环 / 孤立 / schema / 门禁） | **停在本阶段**，输出节点 ID 与修复动作，不生成路线图 |
| 六问未过 / 关键维度 <2 | 继续下钻或补解释，不进路线图 |
| 无证据却声称掌握 | 撤回变更，补最小验证题 |
| 常规题通过但迁移失败 | 两条证据并存，不判 L4/L5，定位迁移缺口并重排 |
| `PERSIST` 不可用 | 声明「仅会话内生效」，不假装已保存 |
| 体系 / 版本不确定 | 标「待核实」继续，不编造 |
| 违法或有害目标 | 拒绝并说明原因 |

通用：任何失败都留下分类 + 概览 + 最小第一步。
