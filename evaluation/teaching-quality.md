# Engine 6 · 教学质量评价

## 1. 七项评分（每次教学 0–2 分）

解释是否正确、是否符合学习者水平、是否覆盖必要前置、是否存在逻辑跳跃、是否有有效验证、是否及时发现误解、是否帮助学习者独立完成任务。

## 2. 结果结构

`TeachingQualityRecord`：`session_id, scores{}, total, blocking_issues[], evidence_refs[], reviewer, schema_version, created_at`。

`reviewer` 必须区分 `model_self_review` / `human_review` / `deterministic_check`。**模型自评不得单独作为系统成功的依据**；结构性项目（前置覆盖、验证任务存在、逻辑跳跃标记）由 `scripts/run_benchmark.py` 做确定性检查。

## 3. 阻塞规则

「解释正确性」或「前置覆盖」为 0 时，本次教学判定为需返工，不得推进到下一节点。
