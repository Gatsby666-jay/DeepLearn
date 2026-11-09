# 间隔复习引擎

职责：按证据与遗忘风险安排复习，让薄弱且重要的知识获得更高频次。复习不是重读讲解，而是重新验证理解。字段遵循 [core/data-schema.md](../core/data-schema.md)。

## 1. 复习时机的六个因素

| 因素 | 字段 | 影响方向 |
|---|---|---|
| 掌握度 | `mastery_level` | 越低越早复习 |
| 近期表现 | `evidence[-1].result` | fail / partial 提前 |
| 错误频率 | `misconceptions` 数量 | 越多越频繁 |
| 知识难度 | `difficulty` | 越高越频繁 |
| 距上次评估 | `last_assessed` → 今天 | 越久越该复习 |
| 知识重要性 | `importance` | essential 优先于 optional / extension |

## 2. 四类复习

| 类型 | 触发条件 | 建议间隔区间 | 任务形态 |
|---|---|---|---|
| 首次复习 | 节点刚达到 L2–L3 | 1–3 天 | 不看材料复述 + 一道最小应用题 |
| 短期复习 | 首次复习通过、证据仍为 provisional | 3–7 天 | 变式题 + 一个反例 |
| 延迟复习 | 短期通过、confidence 达 supported | 1–3 周 | 迁移任务或反向教学 |
| 长期维护 | 迁移通过、confidence 为 strong | 1–3 个月 | 跨领域同构或边界反事实 |

间隔是**估算区间**，不是精确承诺；按 `next_review` 记录 ISO 日期，允许推迟。

## 3. 优先级打分（可执行）

按以下顺序排序，同级再按 `difficulty` 降序：

1. `review_status = due` 且 `mastery_level <= 2`
2. 近一次 `result = fail`，或 `misconceptions` 非空
3. `importance = essential` 且 `confidence != strong`
4. `evidence[-1].result = partial`
5. 其它到期项
6. 未到期项不进入本次会话

**禁止给所有节点安排相同间隔**；`optional` / `extension` 节点可降频或直接跳过。

## 4. 复习任务要求

- 考理解而非背诵：至少含一个「说明理由」「举反例」「换个条件会怎样」类任务。
- 复习后按 [references/assessment.md](../references/assessment.md) 写一条新 `evidence`，不覆盖旧记录。
- 通过则提高 `confidence` 并安排下一档复习；失败则回 `REMEDIATE`，不自动降低已由强证据支撑的掌握度之外的其它节点。

## 5. 用户可执行的四个动作

```
查看到期复习   → 列出 due 节点、优先级、建议任务
开始复习会话   → 一次只做一个节点，出题 → 收作答 → 给反馈
跳过 / 推迟    → 写 review_status=postponed 与新 next_review，记录原因
复习后更新     → 写 evidence、更新 mastery_level / confidence / review_status
```

## 6. review_schedule.json 最小结构

```json
{
  "project_id": "PROJECT-001",
  "entries": [
    {"node_id": "NODE-001", "review_status": "due",
     "next_review": "2026-11-16", "review_type": "short_term",
     "priority": 2, "last_result": "pass"}
  ]
}
```

`review_type` 取 `initial` / `short_term` / `delayed` / `maintenance`；`priority` 为 1–6 的整数，越小越优先。由 [scripts/validate_state.py](../scripts/validate_state.py) 校验结构。

## 7. 模块接口

- 状态与事件持久化：[references/state-management.md](../references/state-management.md)、[memory/version-control.md](../memory/version-control.md)
- 闭环位置：`core/orchestrator.md` 的 `CONTINUE` 分支可在复习到期时转入本模块
- 门禁：复习通过与否必须写证据，见 [references/quality-gates.md](../references/quality-gates.md) 的 G5
