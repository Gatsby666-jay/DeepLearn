# Engine 2 · 知识网络进化

V2 三图系统保持不变；V3 只增加**有证据、可回滚的变更提案**。

## 1. 触发条件

遗漏前置、依赖方向错误、重复节点、节点划分不合理、新知识加入、学习者在同一基础节点反复出错（≥2 次）。

## 2. 变更记录（KnowledgeGraphChange）

字段：`change_id, affected_node_ids, change_type, old_value, new_value, reason, evidence, confidence, impact_scope, requires_reassessment`，另含 `schema_version, created_at, source`。

## 3. 硬规则

- **不得因一个错误答案自动重构整张图**：`evidence` 至少 2 条独立记录且 `confidence >= supported` 才生成提案。
- 提案默认 `status=proposed`；由用户或后续证据确认后才 `applied`。
- 应用后只重评 `impact_scope` 内的节点，保留其它历史证据。
- 每次应用写快照与 changelog，见 `memory/version-control.md`（V2 保留）。

## 4. 可执行部分

`scripts/knowledge_evolution.py` 校验提案结构、证据条数、置信度、影响范围引用；`scripts/decision_engine.py` 在 REMEDIATE 阶段决定是否提交提案。**图谱修改本身仍由执行 Agent 完成**（规则级），脚本只做确定性校验。
