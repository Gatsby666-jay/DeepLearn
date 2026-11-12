# Engine 2 · 知识关系丰富化

## 1. 七种关系

| 关系 | 语义 | 是否阻断路线 |
|---|---|---|
| `prerequisite` | 必须先掌握 | **是** |
| `conceptual_similarity` | 概念相似、易混 | 否 |
| `mathematical_relation` | 数学结构关联 | 否 |
| `causal_relation` | 因果机制 | 否 |
| `implementation_relation` | 实现依赖 | 否（除非同时标 required 前置） |
| `application_relation` | 应用场景 | 否 |
| `contrast_relation` | 对照/反例 | 否 |

只有 `prerequisite` 且 `necessity=required` 才进入 `KnowledgeNode.prerequisites`，才阻止学习路线前进。其余关系写入 `related_nodes`，仅用于教学关联、易混辨析与迁移任务生成。

## 2. 与 V2 的兼容

V2 的 `dependency_type` 五值枚举保持不变（conceptual/mathematical/physical/operational/implementation dependency）。V3 七种关系写入新字段 `relations[]`，**不改动** V2 的 `dependency_edges`。`scripts/v3_rules.py` 校验两者不得混用。

## 3. 易混辨析

`conceptual_similarity` 与 `contrast_relation` 必须配套生成一个反例任务，写入 `PracticeTask.common_misconceptions`。
