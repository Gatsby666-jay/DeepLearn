# Engine 4 · 实践评价

## 1. 七维评价（不只判答案）

结果正确性、推理过程、方法合理性、独立完成度、异常处理、约束满足情况、可解释性。每维 0–2 分，写入 `PracticeEvidence.scores`。

## 2. 判定规则

- 总分不替代关键维度：**独立完成度或推理过程为 0 时，不得判能力 C3 以上**。
- 提示依赖度记录为 `hint_level_used`（0–3）；`hint_level_used=3` 最高只能判 C2。
- 错误重复率与异常表现写入 `LearnerProfile.common_errors`，供决策引擎使用。
- 评价结论写入 `AssessmentResult`，含 `reason`、`evidence_ids[]`、`confidence`。

## 3. 可执行部分

`scripts/validate_v3_schema.py` 校验 `PracticeEvidence` 结构与分数范围；`scripts/competency_engine.py` 依据分数与证据类型给出能力等级建议（确定性）。
