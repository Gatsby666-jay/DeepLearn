# Engine 6 · Benchmark 回归集

## 1. 覆盖领域（12 个，长期回归）

数学基础、微积分、物理原理、电路基础、C 语言、数据结构、操作系统、Git、Python、STM32、PID、工程项目。

## 2. 每个用例字段

`benchmark_id, domain, input, expected_classification, expected_knowledge_structure, expected_prerequisites, expected_teaching_strategy, expected_assessment, failure_conditions`。

数据：`benchmarks/cases.json`；执行器：`scripts/run_benchmark.py`（确定性断言，可重复执行）。

## 3. 断言内容

- 分类枚举合法性（对照 `v3_rules.ENUMS`）
- 预期前置是否在知识结构中被声明
- 教学策略是否属于八种合法表征
- 评估方式是否属于 V2 十类或 V3 七类能力证据
- failure_conditions 是否非空且可机读

**不判定解释文本质量**（主观项由 `teaching-quality.md` 人工复核），只做结构/枚举/引用的确定性检查。
