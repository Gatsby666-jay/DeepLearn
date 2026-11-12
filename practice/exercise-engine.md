# Engine 4 · 练习生成

## 1. 十类练习

概念理解题、原理推导题、计算题、代码编写题、Debug 任务、实验任务、仿真任务、工程设计任务、项目任务、跨领域迁移任务。

按学习目标与知识类型自动选（映射见 `intelligence/adaptive-engine.md`），并把结果写入 `PracticeTask.practice_type`。

## 2. PracticeTask 字段

`exercise_id, target_node_ids[], target_competencies[], difficulty, prerequisites[], task, expected_output, hints[3], evaluation_criteria[], common_misconceptions[], solution_visibility, schema_version, created_at, source`。

## 3. 渐进提示（强制三级）

| 级别 | 内容 | 不得 |
|---|---|---|
| Hint 1 | 方向提示：指出该用哪类原理/工具 | 不点出关键机制 |
| Hint 2 | 关键机制提示：点明核心关系 | 不给具体步骤 |
| Hint 3 | 局部步骤提示：给第一步或局部推导 | 不给完整解答 |

`hints` 必须恰好 3 条；`solution_visibility` 取 `hidden` / `on_request` / `after_attempt` / `teaching_only`。完整解答仅在合适的教学场景提供，默认 `after_attempt`。

## 4. 可执行部分

`scripts/practice_engine.py` 校验任务结构、三级提示、目标节点/能力引用、评估标准完整性，并按 `difficulty` 与 `knowledge_state` 选择练习类型；**生成题目内容本身属规则级**，由执行 Agent 完成。
