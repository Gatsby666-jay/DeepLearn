# 学习状态模板

双花括号 `{{...}}` 为待填字段。每个学习项目一个文件，建议放在 `deeplearn-state/<project>.md`，与 Skill 包分离。

```markdown
---
project: {{稳定标识}}
objective: {{用户原始目标文本}}
classification: {{主类 + 辅类}}
mode: {{Explore / Deep Dive / Learn / Decompose / Build / Diagnose}}
assumptions: {{采用的默认假设}}
updated: {{YYYY-MM-DD}}
---

## 三图版本
- 结构图：{{版本 / 更新时间}}
- 依赖图：{{版本 / 校验结果：无环}}
- 路线图：{{A/B/C / 当前阶段}}

## 节点进度
| id | name | mastery(0-5) | 证据摘要 | 薄弱前置 |
|---|---|---|---|---|
| {{L3-01}} | {{名称}} | {{0}} | {{无}} | {{无}} |

## 当前位置
- 当前节点：{{ID}}
- 下一推荐任务：{{一句可执行的动作}}
- 薄弱点：{{ID 列表}}

## 用户偏好
- 深度 / 语言 / 每周时长 / 是否需要迁移任务：{{…}}
```

## 写入规则

- 追加新行，不覆盖已有证据摘要。
- `mastery` 只在有作答、推理或实践产出时更新（见 assessment.md）。
- 用户手工编辑过的内容一律保留。
- workspace 不可写时声明「本次进度未持久化」，不报错中断。
