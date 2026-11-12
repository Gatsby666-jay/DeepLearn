# V3 统一数据模型（单一事实来源）

**规则：V2 的 `KnowledgeNode` / `LearnerProgress` / `DependencyEdge` 与 15 组枚举保持原样，本文件只定义 V3 新增结构。** 可执行定义见 `scripts/v3_rules.py`；字段校验见 `scripts/validate_v3_schema.py`。

## 0. 通用规则（所有 V3 结构）

| 规则 | 要求 |
|---|---|
| 唯一 ID | `NODE-*` 知识、`COMP-*` 能力、`PROFILE-*` 画像、`EVENT-*` 事件、`TASK-*` 练习、`PEV-*` 实践证据、`PLAN-*` 计划、`CHG-*` 变更、`RES-*` 资源、`ARES-*` 评价结论 |
| `schema_version` | 必填，整数，当前 `3` |
| 时间 | `created_at` 必填（ISO 日期）；`updated_at` / `last_assessed` 可空 |
| 来源/证据 | 至少含 `source` 或 `evidence_refs[]` 之一；不得为空对象冒充证据 |
| 枚举 | 全部取自 `scripts/v3_rules.py`，不得自创 |
| 空值 | 未知写 `null` 并附 `reason`；**不得用 0 或空字符串冒充已测量值** |
| 跨模块引用 | 由 `validate_v3_schema.py` 校验存在性 |

## 1. KnowledgeNode（V2 保留 + V3 可选扩展）

V2 必填字段不变。V3 追加可选：`relations[]`（七种关系，见 `knowledge/relationship-engine.md`）、`provenance{}`（见 `knowledge/provenance.md`）、`schema_version: 2`（V2 节点保持 2，迁移不改）。

## 2. LearnerProgress（V2 保留）

`project_id, node_id, mastery_level(L0–L5), confidence, evidence[], misconceptions[], last_assessed, review_status, next_review, learning_history[]`。V3 追加可选 `knowledge_state`（六态枚举），由 `LearnerProfile` 投影生成，不覆盖 mastery_level。

## 3. LearnerProfile（新增）

`profile_id, project_id, schema_version, created_at, updated_at, prior_knowledge[], learning_preferences{}, cognitive_load{}, misconception_profile[], learning_behavior{}, learner_confidence, knowledge_states[], retention_summary, source`。

- `learning_preferences`：`{modality: weight(0–5), evidence_count, last_updated}`，权重更新规则见 `intelligence/adaptive-engine.md`
- `learner_confidence`：与 `confidence`（证据置信度）不同轴，表示学习者自评信心，仅作信号
- `knowledge_states[]`：`{node_id, state, evidence_count, last_assessed}`

## 4. Competency（新增）

`competency_id, name, description, required_knowledge[], observable_behaviors[], performance_criteria[], assessment_methods[], proficiency_levels[C0..C5], evidence_refs[], schema_version, created_at, source`。

## 5. CompetencyProgress（新增）

`project_id, competency_id, proficiency_level(C0–C5), confidence, evidence[], last_assessed, growth_history[], next_action, schema_version, created_at`。

## 6. LearningEvent（新增）

`event_id, project_id, event_type, occurred_at, node_ids[], competency_ids[], payload{}, evidence_refs[], source, schema_version`。`event_type` 枚举见 `v3_rules.py`（含 V2 十类事件的超集）。**只追加，不覆盖、不删除。**

## 7. PracticeTask（新增）

`exercise_id, target_node_ids[], target_competencies[], practice_type, difficulty(1–5), prerequisites[], task, expected_output, hints[3], evaluation_criteria[], common_misconceptions[], solution_visibility, schema_version, created_at, source`。

## 8. PracticeEvidence（新增）

`evidence_id, project_id, exercise_id, node_ids[], competency_ids[], scores{}（七维 0–2）, hint_level_used(0–3), execution_status, independence, anomaly_handling, result, reasoning, evidence_source, occurred_at, schema_version`。

## 9. LearningPlan（新增）

`plan_id, project_id, version, created_at, goal, decision{}, stages[], next_action, reason, unchanged_from_previous[], schema_version`。`decision{}` 结构 = 决策引擎九项输出。

## 10. KnowledgeGraphChange（新增）

`change_id, affected_node_ids[], change_type, old_value, new_value, reason, evidence[], confidence, impact_scope[], requires_reassessment, status, schema_version, created_at, source`。

## 11. Resource（新增）

`resource_id, title, source, url|null, resource_type, difficulty, language, relevant_node_ids[], prerequisites[], intended_use, last_verified|null, verification_status, schema_version, created_at`。未验证不得写 `verified`。

## 12. AssessmentResult（新增）

`assessment_id, project_id, subject_type(knowledge|competency), subject_id, level, confidence, evidence_ids[], reason, reviewer, scores{}, schema_version, created_at`。`reviewer` 区分 `deterministic_check` / `model_self_review` / `human_review`。

## 13. 关系图

```
KnowledgeNode ──required_knowledge──> Competency
LearnerProgress ──node_id──> KnowledgeNode
CompetencyProgress ──competency_id──> Competency
PracticeTask ──target_node_ids──> KnowledgeNode
PracticeTask ──target_competencies──> Competency
PracticeEvidence ──exercise_id──> PracticeTask
AssessmentResult ──evidence_ids──> PracticeEvidence / LearnerProgress.evidence
LearningEvent ──evidence_refs──> 上述证据
LearningPlan ──decision──> 决策引擎输出
KnowledgeGraphChange ──affected_node_ids──> KnowledgeNode
```

所有箭头由 `validate_v3_schema.py` 校验；悬空引用报 `missing_reference`。

## 14. 与 V2 的边界

| 不变 | 新增 |
|---|---|
| V2 schema、15 组枚举、8 个脚本行为、47 用例 | V3 结构、`v3_rules.py` 枚举、`validate_v3_schema.py`、`migrate_v2_v3.py` |
| `mastery_level` L0–L5 | `proficiency_level` C0–C5（独立） |
| `evidence` 八字段 | `PracticeEvidence` 七维评分（独立） |
