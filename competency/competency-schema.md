# Engine 3 · 能力数据模型

## 1. 核心区分

| 对象 | ID 空间 | 含义 |
|---|---|---|
| `KnowledgeNode` | `NODE-*` | 知识本身 |
| `LearnerProgress` | `PROJECT-* + NODE-*` | 学习者对知识的掌握 |
| `Competency` | `COMP-*` | 需要培养的能力（**领域无关定义**） |
| `CompetencyProgress` | `PROJECT-* + COMP-*` | 学习者的能力水平 |

**知识掌握度（L0–L5）与能力等级（C0–C5）永不互相替代**；`scripts/v3_rules.py` 用不同枚举与 ID 前缀强制区分。

## 2. Competency 字段

`competency_id, name, description, required_knowledge[], observable_behaviors[], performance_criteria[], assessment_methods[], proficiency_levels[], evidence[], schema_version, created_at`。

## 3. CompetencyProgress 字段

`project_id, competency_id, proficiency_level(C0–C5), confidence, evidence[], last_assessed, growth_history[], next_action, schema_version`。

## 4. 能力等级（可观察标准见 competency-rubrics.md）

C0 不了解 / C1 能解释基础概念 / C2 指导下完成任务 / C3 独立完成标准任务 / C4 处理复杂与异常 / C5 迁移、优化并创造新方法。

**不得因使用了专业术语就升级**；升级必须有 `PracticeEvidence` 且 `evidence_source=objective_assessment`。
