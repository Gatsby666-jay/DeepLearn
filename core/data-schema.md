# 统一数据架构（单一事实来源）

本文件定义 DeepLearn V2 全部结构化数据的权威结构。任何模块不得自行发明知识节点或学习进度的字段表示；新增字段必须同步修改本文件、`templates/` 与 `scripts/validate_schema.py`。规范文本与可机读校验保持一致，由 `validate_schema.py` 做确定性判定。

## 1. 三条不可混淆的轴

| 轴 | 字段 | 语义 | 禁止 |
|---|---|---|---|
| 知识组织 | `parent_id` / `children` | 包含关系，构成知识结构树 | 不得把父子关系自动解释为前置关系 |
| 学习依赖 | `prerequisites` / `dependency_edges` | 学会某节点前必须掌握什么 | 不得由树结构推导，不得与 `related_nodes` 混用 |
| 学习者状态 | `LearnerProgress.mastery_level` | 某个学习者对某节点的掌握程度 | 不得用 `decomposition_level` 表示 |

`decomposition_level` 描述**知识深度**（L0–L6），`mastery_level` 描述**人的水平**（0–5）。两者永远不同轴。

## 2. KnowledgeNode

| 字段 | 类型 | 必填 | 约束 / 默认 | 说明 |
|---|---|---|---|---|
| `id` | string | 是 | `NODE-\d{3,}` | 稳定唯一 ID，不复用、不因改名而改变 |
| `name` | string | 是 | 非空 | 规范名称 |
| `description` | string | 是 | 非空 | 一句不含循环定义的表述 |
| `aliases` | array[string] | 否 | `[]` | 别名，用于去重与检索 |
| `canonical_id` | string \| null | 否 | `null` | 若为跨分支引用，指向规范节点 ID |
| `parent_id` | string \| null | 否 | `null` | 结构树父节点，根节点为 null |
| `children` | array[string] | 否 | `[]` | 结构树子节点 ID |
| `node_type` | enum | 是 | 见 §5 | 节点性质 |
| `learning_category` | enum | 是 | 七类之一 | 所属学习目标类别 |
| `decomposition_level` | int | 是 | 0–6 | 知识深度，非掌握度 |
| `prerequisites` | array[string] | 否 | `[]` | 必需前置节点 ID 列表 |
| `dependency_edges` | array[DependencyEdge] | 否 | `[]` | 完整依赖边，含类型与必要性 |
| `difficulty` | int | 是 | 1–5 | 难度 |
| `importance` | enum | 是 | essential / optional / extension | 必修 / 选学 / 拓展 |
| `time_estimate` | object | 是 | `{min_hours, max_hours}`，`0 < min <= max` | 估算区间，非精确承诺 |
| `practical_value` | enum | 是 | high / medium / low | 实践价值 |
| `objectives` | array[string] | 否 | `[]` | 学完能做什么（可观察） |
| `mechanism` | string | 否 | `""` | 它如何工作；L3 以下节点原则上不得为空 |
| `principles` | array[string] | 否 | `[]` | 支撑原理 |
| `trace_chain` | array[string] | 否 | `[]` | 节点 → 机制 → 支撑原理 → 基础边界 |
| `related_nodes` | array[string] | 否 | `[]` | 关联但**不必然是前置**的节点 |
| `applications` | array[string] | 否 | `[]` | 实际应用 |
| `limitations` | array[string] | 否 | `[]` | 失效条件与边界 |
| `verification_methods` | array[string] | 否 | `[]` | 可执行的验证方式 |
| `atomic_gate` | object | 否 | 见 §5 | 六问验收，按类别适用性判定 |
| `decomposition_quality` | object | 否 | 见 §5 | 六维 0–2 分，总分 0–12 |
| `version` | int | 是 | `>= 1`，默认 1 | 节点数据版本 |

### atomic_gate 结构

```json
{"why_exists": {"status": "passed", "note": "..."},
 "problem_solved": {"status": "passed", "note": "..."},
 "depends_on": {"status": "passed", "note": "..."},
 "why_valid": {"status": "passed", "note": "..."},
 "derivable": {"status": "not_applicable", "note": "本节点为经验性事实"},
 "verifiable": {"status": "passed", "note": "..."}}
```

`status` 只能是 `passed` / `failed` / `not_applicable`；`not_applicable` 必须给 `note` 说明不适用理由。任一适用项 `failed` 不得进入路线图。

### decomposition_quality 结构

六个维度各 0–2 分：`completeness`, `independence`, `dependency_correctness`, `explanatory_depth`, `verifiability`, `boundary_clarity`；另含 `total`(0–12) 与 `critical_pass`(bool)。**总分不是唯一判据**：`dependency_correctness`、`explanatory_depth`、`verifiability` 为关键维度，任一低于 2 即 `critical_pass=false`，继续拆解或补解释。

## 3. LearnerProgress

| 字段 | 类型 | 必填 | 约束 / 默认 | 说明 |
|---|---|---|---|---|
| `project_id` | string | 是 | `PROJECT-\d{3,}` | 学习项目 ID |
| `node_id` | string | 是 | 必须指向存在的 KnowledgeNode | 进度所属节点 |
| `mastery_level` | int | 是 | 0–5，见 §5 | 掌握度 |
| `evidence` | array[Evidence] | 否 | `[]` | 证据记录，只追加不覆盖 |
| `confidence` | enum | 是 | unassessed / provisional / supported / strong | 证据置信度，**不等于掌握度** |
| `misconceptions` | array[object] | 否 | `[]` | 已诊断的误解及根因 |
| `last_assessed` | string \| null | 否 | `null` | ISO 日期 |
| `review_status` | enum | 是 | 见 §5 | 复习状态 |
| `next_review` | string \| null | 否 | `null` | ISO 日期 |
| `learning_history` | array[object] | 否 | `[]` | 事件历史，只追加 |

### Evidence 结构（每次掌握度变更必须写入一条）

```json
{"node_id": "NODE-001", "assessment_type": "application",
 "result": "pass", "reasoning_quality": "supported",
 "error_type": null, "date": "2026-11-09",
 "mastery_decision": 3, "confidence": "provisional"}
```

`assessment_type` 取 §5 的十类枚举。冲突证据（常规题通过、迁移题失败）**两条都保留**，不得用后者覆盖前者，也不得据此判定 L5。

## 4. DependencyEdge

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `source_node_id` | string | 是 | 前置节点 ID |
| `target_node_id` | string | 是 | 后继节点 ID，不得等于 source |
| `dependency_type` | enum | 是 | 见 §5 |
| `necessity` | enum | 是 | required / recommended |
| `explanation` | string | 是 | 为什么必须先掌握 |

**方向恒为 `prerequisite_node → dependent_node`**，全项目一致，校验器据此判环与拓扑序。

一致性约束：`node.prerequisites` 必须等于「所有以该节点为 target 且 `necessity=required` 的边的 source 集合」，`recommended` 边不进 `prerequisites`。由 `validate_schema.py` 与 `validate_map.py` 双重检查。

## 5. Canonical enums（唯一定义）

| 枚举 | 取值 |
|---|---|
| `node_type` | concept, mechanism, principle, axiom, law, model, procedure, tool, component, interface, protocol, skill, project_deliverable, question |
| `learning_category` | academic_subject, individual_concept, technical_domain, software_tool, specific_problem, practical_project, competency |
| `dependency_type` | conceptual_dependency, mathematical_dependency, physical_dependency, operational_dependency, implementation_dependency |
| `necessity` | required, recommended |
| `difficulty` | 1, 2, 3, 4, 5 |
| `importance` | essential, optional, extension |
| `practical_value` | high, medium, low |
| `mastery_level` | 0, 1, 2, 3, 4, 5 |
| `confidence` | unassessed, provisional, supported, strong |
| `review_status` | not_scheduled, scheduled, due, completed, postponed |
| `project_status` | active, paused, completed, archived |
| `learning_mode` | Explore, Deep Dive, Learn, Decompose, Build, Diagnose |
| `learning_intent` | understand, use, research, build, solve, master, exam |
| `assessment_type` | recall, explanation, application, derivation, debugging, prediction, counterexample, reverse_teaching, cross_domain_transfer, changed_condition_transfer |
| `atomic_gate_status` | passed, failed, not_applicable |
| `quality_dimension` | completeness, independence, dependency_correctness, explanatory_depth, verifiability, boundary_clarity |
| `evidence_result` | pass, partial, fail |
| `project_event` | project_created, classification_confirmed, map_generated, graph_changed, lesson_completed, assessment_completed, mastery_updated, misconception_found, roadmap_changed, review_completed |

`mastery_level` 语义：0 未评估 / 1 认得 / 2 能解释 / 3 常规独立应用 / 4 变更或陌生情境迁移 / 5 从原理重建、推导与稳健迁移。只做对原题最高记 3。

## 6. ID、去重与规范节点

- ID 格式 `NODE-\d{3,}` 与 `PROJECT-\d{3,}`，创建后稳定，不因改名、重排或版本变化而复用。
- `aliases` 收集别名与缩写；跨分支出现同一概念时，保留一个规范节点，其余用 `canonical_id` 指向它，并在 `related_nodes` 中登记引用关系。
- **不得仅因名称相近就合并**概念；同名不同义必须拆成两个节点并各自写明 `description` 与 `limitations`。
- 去重判定顺序：ID → 规范名/别名 → `description` 与 `mechanism` 语义 → 人工确认（不确定时新建并标注 `canonical_id: null`，不自动合并）。

## 7. 校验契约（确定性，不靠模型判断）

| 脚本 | 校验对象 |
|---|---|
| `scripts/validate_schema.py` | 必填字段、类型、枚举、ID 格式、父子引用、边一致性、掌握度引用 |
| `scripts/validate_map.py` | 重复 ID、缺失节点、非法边方向、自环、环、重复边、非法依赖类型、断连组件 |
| `scripts/validate_references.py` | 所有 Markdown 内部链接、脚本与模板存在性 |
| `scripts/validate_state.py` | 项目 ID、节点引用、证据结构、版本信息、历史未被覆盖 |
| `scripts/check_consistency.py` | 跨文件枚举一致性、重复规则、模块路由表有效性 |

所有脚本：零第三方依赖、退出码 `0` 通过 / `1` 校验失败 / `2` 参数或解析错误、支持 `--json` 机器可读输出、可读错误信息指向具体字段或文件行。

## 8. 版本与变更

节点 `version`、三图版本、进度历史由 [memory/version-control.md](../memory/version-control.md) 管理。图变更不得自动清空已证明的掌握度；仅当变更影响已证明的能力时定向重评。

## 9. 模板与样本

- 合法示例：[templates/knowledge-node.json](../templates/knowledge-node.json)、[templates/learner-progress.json](../templates/learner-progress.json)
- 测试样本：`tests/fixtures/`（正常与各类失败样本）
- 人类可读输出骨架仍用 `assets/`，不改变 V1 路径约定
