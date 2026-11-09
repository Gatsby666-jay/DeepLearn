# 误解诊断引擎

职责：从学习者的一次作答里定位**错误信念的来源**，而不是只判对错。诊断结果驱动 `core/orchestrator.md` 的 `REMEDIATE → REPLAN` 分支。数据字段遵循 [core/data-schema.md](../core/data-schema.md)。

## 1. 十类错误

| 类型 | 识别信号 | 常见根因 | 节点定位方式 |
|---|---|---|---|
| 术语误解 | 定义说反、把 A 的名字套到 B 上 | 前置概念未建立 | 查该术语所在 `NODE-*` 的 `description` |
| 前置缺失 | 推理中途断裂、跳不过某一步 | `prerequisites` 中有节点 mastery < 2 | 沿 `dependency_edges` 回溯到最早的未达标节点 |
| 心智模型错误 | 结论自洽但整体机制错（如认为指针存的是值） | 类比误导、直觉未校正 | 定位 `mechanism` 与 `trace_chain` 对应节点 |
| 推理跳步 | 直接给结论、缺中间依据 | 教学时跳过了必要推导 | 定位 `trace_chain` 中缺失的那一段 |
| 类比误导 | 把类比当机制、把近似当定律 | 未标注类比失效边界 | 定位 `limitations` 未读的节点 |
| 公式误用 | 套错公式、符号含义错 | 未理解推导条件 | 定位 `principles` 与 `decomposition_level` 更深的节点 |
| 流程操作错误 | 步骤顺序错、命令参数错 | 缺少可观察产出 | 定位 `objectives` / `applications` 节点 |
| 边界条件误解 | 在失效条件下仍套用结论 | `limitations` 未掌握 | 定位 `limitations` 字段所在节点 |
| 题意误读 | 答非所问、解决了另一个问题 | 问题表述或目标理解偏差 | 回 `INTAKE` 复核目标，不判为知识缺口 |
| 偶然猜对 | 答案对但理由空或矛盾 | 无有效证据 | 不给掌握度，补 `verification_methods` |

**必须区分**：「缺少前置知识」与「迁移能力不足」不是同一种失败。前者回补 `prerequisites`，后者给迁移任务；把两者混为一谈会导致无效补课。

## 2. 诊断六步

1. 记录原始作答，标出**错误信念的原句**。
2. 对照正确机制，写清「它为什么不对」，不写「答错了」。
3. 用上表定位根因类型；根因不明时补一道更小的诊断题，不猜。
4. 列出受影响的 `node_id` 及后继节点（沿 `dependency_edges` 正向查）。
5. 设计**只针对根因**的补救：前置缺失补前置，心智模型错误换表征重讲，边界误解补反例。
6. 给一道**新的**验证任务（不复用原题），写明完成判据。

## 3. 证据门槛

- 不得仅凭一次含糊回答就下诊断；至少要有「作答 + 一句理由」或两次一致的错误信号。
- 证据不足时输出「暂不诊断」+ 一道澄清题，并保留原进度。
- `confidence` 按证据强度取 `unassessed` / `provisional` / `supported` / `strong`；低于 `supported` 不得触发路线重排。
- 诊断结果写入 `LearnerProgress.misconceptions` 与 `learning_history`，只追加不覆盖。

## 4. 输出格式

```
诊断节点：<NODE-xxx>
错误类型：<十类之一>
错误信念：「<引用原句>」
为何不对：<一句机制对照>
根因：<术语/前置/模型/跳步/类比/公式/流程/边界/题意/猜对>
受影响节点：<NODE-... 列表>
补救任务：<单一可执行动作 + 完成判据>
新验证任务：<题目 + 完成判据>
confidence：<四值之一>
下一步：① 开始补救 ② 补一道诊断题 ③ 返回学习路线
```

## 5. 模块接口

- 输入来自 [references/assessment.md](../references/assessment.md) 的证据记录。
- 补救教学走 [references/teaching.md](../references/teaching.md)，换表征而非重复原文。
- 路线重排走 [references/learning-paths.md](../references/learning-paths.md)，状态写回见 [references/state-management.md](../references/state-management.md)。
- 门禁判定见 [references/quality-gates.md](../references/quality-gates.md) 的 G5。
