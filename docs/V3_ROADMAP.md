# V3 已知问题与 V4 方向

## 1. V3 实现状态分级

| 能力 | 状态 |
|---|---|
| V3 统一 schema、枚举、引用校验 | 已实现并测试（`validate_v3_schema.py`） |
| V2→V3 迁移/备份/回滚/报告 | 已实现并测试（`migrate_v2_v3.py`） |
| 统一决策引擎（九项输出 + 优先级 + 理由） | 已实现并测试（`decision_engine.py`） |
| 能力等级判定（七维评分 → C0–C5） | 已实现并测试（`competency_engine.py`） |
| 练习结构/三级提示/类型选择校验 | 已实现并测试（`practice_engine.py`） |
| 图谱变更提案校验 | 已实现并测试（`knowledge_evolution.py`） |
| 12 领域 Benchmark 回归 | 已实现并测试（`run_benchmark.py`） |
| 场景 A–H | 契约 + 脚本串联测试，**非真实 Agent 端到端** |
| 学习者偏好动态学习、认知负荷建模 | 规则文档 + 数据结构，权重更新由确定性规则约束，运行时由 Agent 执行 |
| 图片理解 / 代码执行 / 仿真 | **可选能力**，依赖宿主环境；本 Skill 不自带执行器，降级路径见 `multimodal/capability-fallback.md` |
| 教学质量主观评价、真迁移题质量 | 未自动化，需人工复核 |

## 2. 已知限制

- Orchestrator、state 读写/快照、replan、复习调度、资源验证仍为 V2 的规则级设计；V3 未引入运行时状态机。
- 多模态能力完全依赖宿主；本包不提供图片识别或代码执行实现。
- Benchmark 只断言结构/枚举/引用，不判定解释文本质量。
- 学习者画像的「偏好」由确定性权重规则约束，但教学表征的实际效果由 Agent 记录，脚本无法验证记录真实性。

## 3. v3.0.1 已完成（2026-11-13）

LICENSE（MIT）、GitHub Actions CI、README / 测试报告 / CHANGELOG 的事实订正、默会知识边界声明、`decision_engine.py` 五处缺陷修复与 6 条回归、`SKILL.md` 首轮自检清单、发布改单提交均已落地。这些属于工程卫生与局部代码修复，**不改变本节列举的运行时缺失**：Orchestrator 状态机、state 读写快照、replan、复习调度、资源验证器仍无执行代码。

## 4. V4 建议

1. 引入可选的 `state_engine.py`：真正读写 state.json / 快照 / 跨会话恢复，把 V2/V3 规则级状态变成可执行。
2. 接入代码沙盒：让 `execution_status=executed` 有真实输出支撑，自动判题并回写能力证据。
3. 端到端回归：固定学习目标 → 完整闭环 → 断言 LearningEvent 序列与能力成长曲线。
4. 图谱提案自动应用 + 影响范围重评（需用户确认闸门）。
5. Benchmark 扩充为可评分的多轮对话集，引入人工复核抽样。
