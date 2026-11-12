# Engine 4 · 项目驱动学习

## 1. 反向生成链

```
项目目标 → 子系统 → 技术能力 → 知识节点 → 前置任务 → 实施步骤 → 测试 → 验收
```

以 STM32 智能小车为例，子系统：STM32 基础、GPIO、PWM、定时器、电机驱动、传感器、PID 控制、电源管理、系统集成、故障调试。

## 2. 硬规则

- 根据目标**自动识别必要知识**，不要求所有知识学完才开始项目。
- 允许理论学习与项目实践**交替**进行（阶段表里标 `theory` / `practice` / `mixed`）。
- 每个阶段有可验收产出与失败回退（回补对应知识节点）。
- 项目完成情况写入 `CompetencyProgress.evidence`，并触发能力等级复评。

## 3. 与 V2 的关系

复用 `references/learning-paths.md` 的「目标导向路径」与 `scripts/validate_roadmap.py` 的阶段/工期校验；V3 只追加 `target_competencies[]` 与 `practice_type` 字段，不改 V2 路线结构。
