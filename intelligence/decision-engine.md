# 统一自适应决策引擎

**权威实现：`scripts/decision_engine.py`（可执行、可测试）**。本文件只定义契约。

## 1. 输入 / 输出

输入：学习目标、知识掌握度、能力水平、前置缺口、错误历史、近期表现、复习需求、时间约束、学习者偏好。

输出九项：`current_problem`、`next_node_id`、`needs_review`、`needs_prerequisite_repair`、`teaching_modality`、`practice_type`、`enter_project_practice`、`allow_advance`、`reason`（简短理由，必须给出）。

## 2. 决策优先级（严格顺序）

1. 修复**阻塞性前置缺口**（`prerequisite_gaps` 含 required 前置且 mastery < 2）
2. 处理**反复出现的核心误解**（`common_errors` 同一错误 ≥2 次）
3. 复习**重要且有遗忘风险**的知识（`review_status=due` 且 importance=essential）
4. 推进当前目标所需的**关键知识**
5. 通过**实践**建立能力（知识 L3 以上但对应能力 < C3）
6. 扩展选修与探索知识

## 3. 硬规则

- **不得只根据一个 mastery 数字做决定**：至少综合 mastery、confidence、evidence_count、recent_errors、review、competency 六类信号。
- 任何 `allow_advance=true` 必须有 `evidence` 支撑，且 `VALIDATE` 已通过。
- 关键决策必须输出 `reason`，让学习者知道为什么做这件事。
- 时间约束冲突时保留目标，输出「最小可达子集」并标注未覆盖范围，不劝退。

## 4. 与 V2 闭环的接口

由 `core/orchestrator.md` 的 `PLAN` / `REPLAN` / `CONTINUE` 阶段调用；输出写入 `LearningPlan` 与 `LearningEvent`，`PERSIST` 后生效。V2 的 `VALIDATE` 失败阻塞优先于本引擎。
