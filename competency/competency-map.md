# Engine 3 · 知识与能力映射

## 1. 映射结构

`required_knowledge[]` 是**必要但不充分**条件；能力还需 `observable_behaviors[]` 与实践证据。一个能力可依赖多个知识节点，一个知识节点可支撑多个能力。

| 知识 | 掌握度 | 能力 | 等级 |
|---|---|---|---|
| PID 原理 | L4 | 控制器设计与调参 | C2 |
| C 指针 | L4 | 内存错误排查 | C3 |
| 电路基础 | L3 | 电路设计 | C1 |

上表说明：知识 L4 **不推出**能力 C4，两者独立记录。

## 2. 反向规划（项目驱动）

`practice/project-engine.md` 从项目目标反推：目标 → 子系统 → 所需能力 → 支撑知识 → 前置任务 → 实施步骤 → 测试 → 验收。**不要求所有知识学完才开始项目**，允许理论与实践交替。

## 3. 校验

`scripts/validate_v3_schema.py` 检查：`required_knowledge` 引用存在的 `NODE-*`；能力进度引用的 `COMP-*` 存在；`proficiency_level` 与 `evidence` 类型匹配（C4/C5 需迁移或异常类证据）。
