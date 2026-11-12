# V3 · 学习记忆与隐私

## 1. 新增历史（在 V2 事件驱动状态之上）

学习事件历史、能力成长历史、知识图谱变更历史、复习历史、评估历史、学习计划版本。全部写入 `LearningEvent`（`event_type` 枚举见 `scripts/v3_rules.py`），只追加不覆盖。

## 2. 必须支持

- 跨会话恢复：读 `state.json` 的 `current_stage` + 最新 `LearningPlan.version`
- 历史证据追踪：`evidence_id` 全局唯一，可回溯到来源
- 数据迁移/回滚/重要状态备份：`scripts/migrate_v2_v3.py`
- 用户主动修改画像、查看与纠正错误记录：写 `correction` 事件，保留原记录

## 3. 隐私与真实性

- 只保存对长期学习有价值的信息，不无必要保存私人信息。
- `evidence_source` 强制区分 `self_report` / `model_inference` / `objective_assessment`；自我评价与模型推断**不得**直接提升掌握度或能力等级。
- V2 的 `evidence`、`learning_history`、`history` 字段在迁移中只读不写。
