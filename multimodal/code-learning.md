# Engine 5 · 代码分析工作流

## 1. 七项能力

解释代码结构、追踪执行流程、分析变量变化、发现逻辑错误、解释错误原因、提供调试任务、根据代码表现评价能力。

## 2. 真实性约束

**不得声称已经运行代码，除非确实使用了可用的执行环境。** 静态分析结果标注 `execution_status=theoretical` 或 `simulated`；真实运行后才可写 `executed` 并附输出。

## 3. 输出结构

```
结构说明 → 执行流程（按顺序列出状态变化）→ 变量表 → 问题定位 → 原因解释
→ 调试任务（含 expected_output 与 hints）→ 能力评价建议
```

调试任务生成 `PracticeTask`（practice_type=`debug`），评价写入 `CompetencyProgress`。
