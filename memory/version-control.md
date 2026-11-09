# 版本与变更管理

职责：管理知识图、路线图与学习进度的版本，保证图变化时**不丢失已证明的掌握度**。字段遵循 [core/data-schema.md](../core/data-schema.md)，状态写入流程见 [references/state-management.md](../references/state-management.md)。

## 1. 版本化对象

| 对象 | 版本字段 | 变更触发 |
|---|---|---|
| 知识结构图 | `versions.knowledge_map` | 增删节点、改父子关系 |
| 知识依赖图 | `versions.dependency_graph` | 增删边、改 `necessity` / `dependency_type`、破环 |
| 学习路线图 | `versions.roadmap` | 重排阶段、插入复习节点、切换路径 |
| 节点数据 | `KnowledgeNode.version` | 修改 `mechanism` / `principles` / `limitations` |
| 状态文件 | `versions.state` | 任意一次持久化写入 |

版本号为从 1 起的整数，每次实际变更 +1；仅读取或展示不增加版本。

## 2. 触发快照的事件

`project_created`、`classification_confirmed`、`map_generated`、`graph_changed`、`roadmap_changed`、`lesson_completed`、`assessment_completed`、`mastery_updated`、`misconception_found`、`review_completed`（枚举定义在 `scripts/deeplearn_rules.py`）。

其中 `graph_changed` 与 `roadmap_changed` **必须**在 `history/` 下留一份快照；其余事件写入 `changelog.md` 即可。

## 3. 节点变更三步

1. 保留该节点已有的 `evidence` 与 `learning_history`，一条不删。
2. 判断变更是否影响已证明的能力：
   - 仅改 `name` / `aliases` / `description` → 不影响，保留掌握度；
   - 改 `mechanism` / `principles` / `verification_methods` → 可能影响，标记 `confidence: provisional` 并安排一次定向重评；
   - 新增必需前置 → 后继节点的 L4/L5 需重评，L1–L3 保留。
3. 只给受影响的节点安排重评任务，不重置整个项目。

**禁止「图一变就清空全部进度」**。图版本变化不等于学习者能力变化。

## 4. changelog.md 记录格式

```
## v3 | 2026-11-09 | graph_changed
- 影响节点：NODE-004, NODE-007
- 变更：新增 required 边 NODE-002 -> NODE-004
- 是否触发重评：是（NODE-004 的 L4 证据需复核）
- 快照：history/snapshot-003.json
```

每条记录必须写清「是否触发重评」及理由；无重评时写「否，仅元数据变更」。

## 5. 状态完整性写入流程

1. 读取现有 state，校验结构（`scripts/validate_state.py`）。
2. 识别人工编辑：与上次快照不一致且无对应事件的字段，先报告再决定，不自动覆盖。
3. 只写必要变更，追加 `events` 与 `history` 条目。
4. 保留所有 `evidence` 与历史版本引用。
5. 写回后再次校验；失败则回滚到写前内容并报错。
6. 持久化不可用时显式声明「本次更新仅在当前会话内生效」，不假装已保存。

**禁止覆盖无关用户文件**，项目之间目录独立。

## 6. 建议的项目目录

```text
deeplearn-state/
└── embedded-systems/
    ├── state.json
    ├── knowledge-map.md
    ├── dependency-graph.md
    ├── roadmap.md
    ├── progress.json
    ├── review-schedule.json
    ├── changelog.md
    └── history/
        └── snapshot-001.json
```

沿用 `assets/progress-tracker.md` 的字段命名，不另立一套 schema。校验入口：[scripts/validate_state.py](../scripts/validate_state.py)、[scripts/check_consistency.py](../scripts/check_consistency.py)。

## 7. 模块接口

- 闭环位置：`core/orchestrator.md` 的 `PERSIST` 阶段
- 复习排程：[learning/spaced-review.md](../learning/spaced-review.md)
- 事件枚举：[scripts/deeplearn_rules.py](../scripts/deeplearn_rules.py)
