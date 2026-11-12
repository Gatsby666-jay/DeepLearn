# V2 / V3 集成契约

职责：定义 V3 六大引擎如何接入 V2 的 12 阶段闭环，**不重写 Orchestrator**。

## 1. 接入点

| V2 阶段 | V3 附加动作 | 权威文件 |
|---|---|---|
| INTAKE | 读取或初始化 `LearnerProfile` | `intelligence/learner-model.md` |
| CLASSIFY | 追加 learning_intent 与能力目标 | `references/classification.md`（V2 保留） |
| MAP | 补充能力映射与知识关系类型 | `competency/competency-map.md`、`knowledge/relationship-engine.md` |
| VALIDATE | 追加 V3 schema 与迁移校验 | `scripts/validate_v3_schema.py` |
| PLAN | 调用统一决策引擎，产出带理由的下一步 | `intelligence/decision-engine.md` |
| DIAGNOSE | 更新误解画像与前置缺口 | `intelligence/learner-model.md` |
| TEACH | 按偏好选表征；生成练习/实验/项目任务 | `intelligence/adaptive-engine.md`、`practice/*` |
| ASSESS | 分离记录 Knowledge Mastery 与 Competency Proficiency | `competency/competency-assessment.md` |
| REMEDIATE | 生成图谱变更提案（不自动改图） | `knowledge/knowledge-evolution.md` |
| REPLAN | 依据决策优先级重排 | `intelligence/decision-engine.md` |
| PERSIST | 追加 LearningEvent、能力/图谱/复习/评估历史 | `memory/learner-history.md` |
| CONTINUE | 回到 TEACH / MAP / PLAN，输出决策理由 | `core/orchestrator.md` |

## 2. 兼容规则

- V2 的 `KnowledgeNode`、`LearnerProgress`、`DependencyEdge` 与 15 组枚举**保持原样**；V3 结构使用新 ID 空间与 `schema_version: 3`。
- V2 的 47 个测试用例、24 个 fixture、`scripts/*` 行为不得改变；V3 只新增脚本与用例。
- 旧状态文件缺 V3 字段时由 `migrate_v2_v3.py` 补默认值；**不覆盖** `evidence`、`learning_history`、`history`。
- V3 决策不得绕过 V2 的 `VALIDATE` 失败阻塞与「无证据不前进」硬规则。

## 3. 能力探测

多模态与外部工具是**可选能力**。运行时先读 `multimodal/capability-fallback.md` 的探测清单；不支持则走文本/理论推演降级，并在输出中标注 `execution_status`，**不得声称已运行图片识别或代码执行**。

## 4. 单一事实来源

V3 字段与枚举的可执行定义只在 `scripts/v3_rules.py`；规范说明在 `core/v3-schema.md`；两者由 `scripts/check_consistency.py` 与 `scripts/validate_v3_schema.py` 双向校验。规则只在权威文件定义一次。
