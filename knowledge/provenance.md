# Engine 2 · 知识来源与可信度

## 1. 记录字段

重要节点可记录：`source, source_type, evidence, confidence, verification_status, last_verified`。

## 2. 六类知识类型（必须区分）

| 类型 | 说明 | 可否当机制 |
|---|---|---|
| `established_definition` | 公认定义 | 是（但仍需机制解释） |
| `mathematical_theorem` | 数学定理 | 是，需给推导条件 |
| `experimental_fact` | 实验事实 | 是，需标注观测条件 |
| `engineering_practice` | 工程经验 | 仅作实践参考 |
| `model_assumption` | 模型假设 | 否，必须标注假设 |
| `teaching_analogy` | 教学类比 | **否**，不得当成真实机制 |

`teaching_analogy` 必须成对标注「类比失效之处」。

## 3. 可信度规则

- `verification_status`：`verified` / `unverified` / `disputed` / `needs_review`。
- 无检索能力或链接未验证时写 `unverified` 并给检索关键词，**不编造 URL 或权威出处**。
- `confidence` 取 V3 四值枚举；低于 `supported` 的知识不得作为阻断性前置。
