# Engine 1 · 教学策略自适应

## 1. 输入

`LearnerProfile` 的偏好权重、当前节点的 `knowledge_state`、最近三次评估结果、误解画像、可用表征清单、环境能力探测结果。

## 2. 决策表

| 学习者状态 | 优先表征 | 练习类型 |
|---|---|---|
| `unexposed` | 直觉解释 + 图形 | 概念理解题 |
| `exposed_not_able` | 换表征 + 反例 | 原理推导题 / Debug |
| `understands` | 苏格拉底式提问 | 计算题 / 代码编写题 |
| `independent_application` | 代码实践 / 实验验证 | 实验任务 / 仿真任务 |
| `transfer_capable` | 反向教学 | 跨领域迁移任务 / 项目任务 |
| 前置缺口 | 回退前置节点 | 定向补救题 |

数学 → 逐步推导；空间/结构 → 图；编程 → 可跑最小代码；工程 → 实验/仿真；抽象 → 类比 + 反例；流程 → 时序图；状态系统 → 状态表。

## 3. 权重更新（确定性规则）

```
同一表征连续 3 次 objective_assessment=pass → weight += 1（上限 5）
同一表征连续 2 次 fail → weight -= 1（下限 0）
单次 fail → 仅记 weak_signal，不改 weight
每 10 次评估 → 所有 weight 向基线 2 收敛 1 步
```

规则由 `intelligence/decision-engine.md` 调用；不得因模型「感觉」学习者适合某种方式而调整。

## 4. 降级

环境不支持图片/代码执行时，按 `multimodal/capability-fallback.md` 切换为文本描述与理论推演，并标注 `execution_status`。
