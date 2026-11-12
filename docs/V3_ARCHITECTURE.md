# V3 架构说明

## 1. 定位

V1 知识拆解与第一性原理 → V2 分类/三图/路径/教学/评估/补救/持久化闭环 → **V3 从 Knowledge-Centered 升级为 Learner-Centered Competency Development**：理解学习者、围绕能力成长、通过实践验证、长期追踪、按证据动态演进。

## 2. 六大引擎

| 引擎 | 目录 | 核心产物 |
|---|---|---|
| 1 Learner Intelligence | `intelligence/` | LearnerProfile、动态偏好、效率分析、统一决策 |
| 2 Knowledge Evolution | `knowledge/` | 变更提案、七种关系、来源可信度 |
| 3 Competency | `competency/` | C0–C5 能力模型、评分标准、能力证据 |
| 4 Practice | `practice/` | 十类练习、三级提示、实验/仿真/项目、七维评价 |
| 5 Multimodal | `multimodal/` | 输入适配、图片/代码工作流、能力降级 |
| 6 Evaluation | `evaluation/` | 学习效果/教学质量评价、12 领域 Benchmark |

## 3. 分层与兼容

```
SKILL.md（入口）
  ├─ core/           V2 Orchestrator + V2 schema（不改） + v3-schema + v3-integration
  ├─ references/     V2 11 份方法论（不改）
  ├─ learning/       V2 误解诊断 + 间隔复习（不改）
  ├─ memory/         V2 版本控制 + V3 learner-history（新增）
  ├─ intelligence/    V3
  ├─ knowledge/       V3
  ├─ competency/      V3
  ├─ practice/        V3
  ├─ multimodal/      V3
  ├─ evaluation/      V3
  ├─ scripts/         V2 8 个 + V3 新增（互不覆盖）
  ├─ templates/       V2 2 个 + V3 10 个
  ├─ tests/           V2 47 用例 + V3 用例（V2 不删）
  └─ benchmarks/      V3 12 领域
```

V2 的 12 阶段闭环仍是主干；V3 在 `core/v3-integration.md` 定义的接入点注入，不重写 Orchestrator。

## 4. 三条不可混淆的轴（V3 扩展为五条）

| 轴 | 结构 | 说明 |
|---|---|---|
| 知识组织 | `KnowledgeNode.parent_id` | 包含关系 |
| 学习依赖 | `prerequisites` | 只有 required 前置阻断 |
| 知识掌握 | `LearnerProgress.mastery_level` (L0–L5) | 学习者对知识 |
| 能力水平 | `CompetencyProgress.proficiency_level` (C0–C5) | 学习者做事的能力，**独立** |
| 证据可信度 | `evidence_source` + `confidence` | 自评/推断/客观测评分离 |

## 5. 确定性 vs 规则级

Python 负责：schema、枚举、ID、引用完整性、迁移/回滚、决策优先级计算、能力等级判定、Benchmark 断言、图谱提案校验。
执行 Agent 负责：解释、题目内容生成、图片理解、教学互动、图谱实际修改。所有规则级能力在文档中明确标注，不伪装成已实现代码。
