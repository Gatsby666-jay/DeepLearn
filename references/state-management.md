# 学习状态管理

每次会话开始（读取）与结束（更新）时载入。

## 原则

- 每个学习项目一个独立 state 文件，项目之间状态不互通。
- state 是学习进度，不是内容讲义；不把教学内容抄进 state。
- 更新前先读取现有文件；**不覆盖用户自建笔记、不改写其它项目文件、不删除历史记录**。
- workspace 只读或不可写时，退化为会话内记忆，并在输出中声明「本次进度未持久化」。

## 文件位置

建议 `deeplearn-state/<project>.md`，与 Skill 包分开，避免污染 Skill 目录。`project` 用简短稳定标识（如 `embedded-systems`、`taylor-expansion`），不用时间戳。初始化骨架见 `assets/progress-tracker.md`。

## state schema

```markdown
---
project: <标识>
objective: <原始目标文本>
classification: <主类 + 辅类>
mode: <当前 Mode>
assumptions: <采用的默认假设>
updated: <日期>
---

## 三图版本
- 结构图：<版本 / 最后更新时间>
- 依赖图：<版本 / 校验结果：无环>
- 路线图：<路径 A/B/C / 当前阶段>

## 节点进度
| id | name | mastery(0-5) | 证据摘要 | 薄弱前置 |
|---|---|---|---|---|

## 当前位置
- 当前节点：<id>
- 下一推荐任务：<…>
- 薄弱点：<id 列表>

## 用户偏好
- 深度 / 语言 / 时长 / 是否需要迁移任务：<…>
```

## 读写流程

1. 会话开始：按项目标识查找 state；存在则读取，不存在则从模板初始化并声明假设。
2. 分类、三图、路线与当前节点以 state 为准；用户未要求重拆时不重建图。
3. 教学结束：按 assessment.md 的证据规则更新 `mastery`，写一句证据摘要。
4. 切换 Mode：保留三图与进度，只改 `mode` 与「下一推荐任务」。
5. 发现新前置或破环：更新依赖图版本，重新运行校验，再更新路线图版本。
6. 会话结束：写回 state，保留既有表格行，不覆盖历史证据摘要。

## 冲突处理

- 用户目标与 state 中的 `objective` 不一致 → 先说明差异并询问是「新项目」还是「同一项目改目标」，不自动覆盖。
- 用户手工编辑过 state 或知识图文件 → 保留其改动，只在追加区域写入新信息；必要时请求确认。
- 同一项目存在多个 state 文件 → 列出并请用户选择，不自行合并或删除。

## 闭环更新（G5）

每轮教学或诊断结束后，一次写回以下内容，缺一不可：

- 各节点 `mastery` 与**证据摘要**（引用用户作答要点，不写「表现良好」）；
- 薄弱点列表及其影响的后继节点；
- 三图版本号（结构图 / 依赖图 / 路线图）；
- 路线图重排结果（新增复习节点、后移的阶段）；
- 当前位置与新的「下一推荐任务」。

未执行重排就推进下一节点，视为 G5 门禁失败。写入时追加新行，不覆盖历史证据摘要。

## 不持久化的内容

- 完整讲解文本、练习答案全文、资源清单、临时澄清问题。
- 其它学习项目的任何字段。
- 用户未确认的推测性掌握度。


## V2 增补：事件驱动持久化

不依赖「会话结束统一保存」。每个重要事件立即写回：project_created / classification_confirmed / map_generated / graph_changed / lesson_completed / assessment_completed / mastery_updated / misconception_found / roadmap_changed / review_completed。

`state.json` 必填：`project_id, status, current_stage, versions, progress[], events[], history[]`；可选 `current_node, next_task, weak_nodes, review_schedule`。结构由 `scripts/validate_state.py` 校验，`current_stage` 取 `core/orchestrator.md` 的 12 阶段之一。

项目目录独立：`deeplearn-state/<project>/{state.json, knowledge-map.md, dependency-graph.md, roadmap.md, progress.json, review-schedule.json, changelog.md, history/}`。版本与快照见 `memory/version-control.md`。

写入六步：读现有 → 校验结构 → 识别人工编辑 → 只写必要变更 → 保留 `evidence` 与 `history` → 再校验。不可写时声明「本次仅会话内生效」。中断恢复按 `current_stage` 继续，不重建未变化的图。
