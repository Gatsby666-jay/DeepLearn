# Engine 1 · 学习者智能：动态画像

V2 记录进度，V3 建立**可随证据更新的学习者模型**。字段定义见 `core/v3-schema.md`，可执行枚举见 `scripts/v3_rules.py`。

## 1. 知识画像（每个 NODE 一条）

字段：`node_id, current_mastery, confidence, evidence_count, evidence_history, last_assessed, retention_status, common_errors, prerequisite_gaps, learning_difficulty, recommended_next_action`。

**六种状态必须区分**（`knowledge_state` 枚举）：

| 状态 | 判据 |
|---|---|
| `unexposed` | 无任何 evidence |
| `exposed_not_able` | 有接触记录但评估 fail |
| `understands` | 能解释机制，L2 |
| `independent_application` | 独立完成常规任务，L3 |
| `transfer_capable` | 迁移/变更条件通过，L4 |
| `stable_long_term` | 延迟复习仍通过且 confidence=strong |

禁止用学习者自我评价直接判定掌握；`evidence_source=self_report` 只能作为线索，须由 `objective_assessment` 复核。

## 2. 偏好建模（非固定标签）

八种教学表征：直觉解释、数学推导、图形解释、代码实践、实验验证、案例教学、苏格拉底式提问、反向教学。

更新规则：
- 记录每次「表征 → 评估结果」对；
- **连续三次**同一表征下通过且另一表征失败，才提高该表征权重；
- 单次失败不得写入稳定偏好，只记 `weak_signal`；
- 权重每 N 次评估衰减一次，允许偏好随能力变化。

## 3. 学习效率分析

仅在可靠数据可得时记录：任务耗时、正确率、独立完成度、提示依赖度、错误重复率、遗忘情况、迁移成功率。

输出为**区间与趋势**（如「近期提示依赖下降」），不得编造精确测量值或伪科学指标。缺失数据写 `null` 并标注「数据不足」。

## 4. 与 V2 的关系

`LearnerProgress.mastery_level` 仍是唯一掌握度真值；本模块的 `current_mastery` 是它的**投影**，由事件重建，不另立一套 mastery。用户可查看并纠正画像中的错误记录（写 `correction` 事件，保留原记录）。
