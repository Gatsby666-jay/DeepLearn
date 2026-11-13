# V3 测试报告（实测，2026-11-12）

所有结果来自本次会话实际执行的命令输出，未使用文档描述代替实现。

## 1. Phase 0 基线（升级前）

| 命令 | 输出 |
|---|---|
| `quick_validate.py` | 通过 |
| `run_tests.py` | 合计 47 \| 通过 44 \| 失败 0 \| 未自动化 3 |
| `validate_references.py` | checked 93，内部引用全部有效 |
| `check_consistency.py` | enums 15、scripts_compiled 8、markdown_headings 181，通过 |
| 文件数 / git | 64 文件 / `142f913` |

完整审计见 `V3_BASELINE.md`。

## 2. Phase 6 全量回归（升级后）

```
quick_validate.py                 → 通过
validate_references.py            → checked 127，内部引用全部有效
check_consistency.py              → enums 15、scripts_compiled 18、markdown_headings 303，一致性通过
package_skill.py                  → Skill is valid!
run_tests.py        (V2)          → 合计 47 | 通过 44 | 失败 0 | 未自动化 3
run_v3_tests.py     (V3)          → 合计 53 | 通过 50 | 失败 0 | 未自动化 3
run_benchmark.py    (Benchmark)   → 合计 12 | 通过 12 | 失败 0
```

合计可执行用例 **112**（47 V2 + 53 V3 + 12 Benchmark），通过 106、失败 0、未自动化 6。

## 3. V3 套件覆盖明细

| 组 | 数量 | 内容 |
|---|---|---|
| V01–V02 | 2 | V3 全结构容器与跨引用、悬空引用被拒 |
| V03–V12 | 10 | 10 个 V3 模板逐一通过 schema |
| SA–SH | 8 | 场景 A–H 的 **`trace.priority` 精确值断言**（`expect_json` 逐条比对具体优先级，非字符串非空检查） |
| V13 | 1 | 空上下文拒绝决策 |
| V14–V17 | 4 | 能力 C4 / 未执行 C3 / 提示依赖 C2 / 推理为 0 C1 |
| V18–V20 | 3 | 练习推荐、合法任务、三级提示缺失 |
| V21–V22 | 2 | 图谱提案通过 / 单次错误被拒 |
| V23–V26 | 4 | Benchmark、迁移全流程、V2 47 用例回归、V2 引用一致性 |
| V27–V32 | 6 | 决策引擎退出码 1/2 分流、preferences 类型、时间约束分支、created_at 非硬编码、P1 不被时间跳过 |
| C01–C08 | 8 | 文档契约检查（明确标注为契约，非场景执行） |
| E01–E02 | 2 | 多脚本串联端到端数据流 |
| N01–N03 | 3 | 主观能力，`SKIP_NOT_AUTOMATED` |

## 4. 场景 A–H 实测映射

| 场景 | 断言 | 结果 |
|---|---|---|
| A 零基础嵌入式 | `P4_key_knowledge_for_goal` | PASS |
| B 有基础但不会指针 | `P1_blocking_prerequisite_gap` | PASS |
| C 能力与知识不一致 | `P5_practice_for_competency` | PASS |
| D STM32 智能小车 | `P5_practice_for_competency` | PASS |
| E 指针错误认知 | `P2_recurring_misconception` | PASS |
| F 长期学习 | `P3_important_review_due` | PASS |
| G 知识图谱修改 | 提案校验 + 迁移 + Benchmark 串联 | PASS |
| H 多模态输入 | 决策 + 能力降级契约 | PASS |

场景验证的是**确定性决策输出与结构契约**，不是真实 Agent 端到端对话；后者仍未自动化。

## 5. 迁移测试（test_migration.py，8 项断言）

无备份拒绝迁移 ✓ / 备份生成 ✓ / 带备份迁移成功 ✓ / V2 字段零改动 ✓ / 证据与历史数量不变 ✓ / V3 字段只增不推断 ✓ / 回滚恢复原始字节 ✓ / 回滚后无 V3 字段 ✓。

## 6. 修复记录

首轮 V3 套件 2 个失败（V23、E02）同源于 benchmark 数据把 `practice_type` 值（`simulation`、`project`）误填入 `teaching_modality`；另 1 个为微积分前置「函数」未列入知识结构。修正 3 处数据后重跑，12 领域全通过、V3 套件 0 失败。**未通过修改校验器来「修绿」**。

v3.0.1 新增 6 条决策引擎回归（V27–V32），并把 V13 期望退出码由 2 改为 1 —— 这是 docstring 声明的「1 = blocking validation」首次真正落地，属于语义归位而非放宽断言；`run_v3_tests.py` 同步支持 `expect_json_ne`。

## 7. 未自动化与已知问题

N01 图片识别质量、N02 代码执行与实验真实性、N03 教学质量与真迁移题主观质量，均标 `SKIP_NOT_AUTOMATED`。规则级设计（Orchestrator 运行时、state 读写快照、replan、复习调度、资源验证器、Lesson 生成）仍未变成执行代码；多模态依赖宿主能力。详见 `V3_ROADMAP.md`。

## 8. 结论

**CONDITIONAL PASS**：V2 兼容性零退化、V3 六大引擎的数据结构与确定性逻辑均有可执行实现与测试证据、12 领域 Benchmark 可重复执行、迁移可备份回滚；但闭环运行时执行层与主观教学质量仍未自动化，不宣称 PASS。
