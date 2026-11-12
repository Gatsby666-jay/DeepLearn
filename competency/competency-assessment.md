# Engine 3 · 能力评估

## 1. 允许的证据类型

`independent_project`、`design_decision_explanation`、`anomaly_resolution`、`parameter_tuning_verified`、`debugging`、`cross_scenario_transfer`、`constrained_task_completion`。

## 2. 升级条件

| 等级 | 最低证据 |
|---|---|
| C1 | 能解释基础概念（objective_assessment） |
| C2 | 在提示/指导下完成标准任务 |
| C3 | 独立完成标准任务，无提示 |
| C4 | 独立处理异常或复杂约束任务 |
| C5 | 跨场景迁移 + 优化/创造新方法 |

证据须含 `execution_status`；`theoretical` / `simulated` / `not_run` 不能支撑 C4/C5。

## 3. 与 V2 评估的关系

V2 的 `assessment_type` 十值枚举保留（知识侧）；V3 能力侧使用 `competency_evidence_type` 七值枚举，两者分别写入 `LearnerProgress.evidence` 与 `CompetencyProgress.evidence`。`scripts/competency_engine.py` 做确定性等级判定。
