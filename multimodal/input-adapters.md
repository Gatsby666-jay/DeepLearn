# Engine 5 · 输入能力适配

## 1. 支持的输入类型

文本、图片、代码、数据表格、数学公式、图表、PDF/文档（**仅在当前环境支持时**）。

## 2. 强制能力探测

处理任何非文本输入前，先判定当前会话是否具备：图片读取工具、代码执行环境、文件解析能力、外部 API。结果写入 `CapabilityProbe`（`capability, available, fallback`）。

**不得假设 Skill 一定具备图片识别、代码执行或外部 API 能力。** 探测失败即走 `capability-fallback.md`。

## 3. 统一接入流程

```
输入 → 能力探测 → 适配器选择 → 信息抽取 → 关联 NODE-* / COMP-* → 缺口识别 → 教学/练习
```

抽取结果必须标注 `source_modality` 与 `extraction_confidence`；低置信时要求补充清晰材料，不猜测图中数值或代码语义。
