# Engine 4 · 实验与仿真

## 1. 优先领域

物理、电子、控制、计算机等可观测领域，优先设计可执行实验。

| 领域 | 实验骨架 |
|---|---|
| 电容器 | 改变 R/C → 观察充放电曲线 → 验证时间常数 → 对比理论与实测 |
| PID | 改变 Kp/Ki/Kd → 观察超调量 → 比较稳定时间 → 分析稳定性 |
| 嵌入式 | 写 GPIO 程序 → 观察输入输出 → 串口打印调试 → 分析中断/定时器 |

## 2. 真实性分级（强制）

`execution_status` 四值：`executed`（确实运行）、`theoretical`（理论推演）、`simulated`（模拟示例）、`not_run`。

**没有执行实验时不得声称实验成功**；输出必须标注分级。`PracticeEvidence` 中 `execution_status != executed` 的记录不能支撑能力 C4/C5。

## 3. 环境能力探测

先读 `multimodal/capability-fallback.md`：无代码执行/仿真环境时降级为理论推演 + 数据表分析，并明确告知用户「本任务未实际运行」。

## 4. 验收

实验任务必须写 `expected_output` 与 `evaluation_criteria`（含「观察什么」「什么结果算支持」「理论值与实测如何比较」）。
