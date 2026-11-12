# V2 → V3 迁移与回滚

## 1. 原则

**V3 不需要改动 V2 数据即可运行**：所有 V3 字段都是新增或可选，旧 `state.json` 按缺失字段补默认值，已有 `evidence` / `learning_history` / `history` 只读不写。

## 2. 迁移脚本

`scripts/migrate_v2_v3.py`，四个子命令：

```bash
python scripts/migrate_v2_v3.py backup   --source <state.json> --backup-dir <dir>
python scripts/migrate_v2_v3.py migrate  --source <state.json> --output <v3-state.json>
python scripts/migrate_v2_v3.py verify   --source <state.json> --migrated <v3-state.json>
python scripts/migrate_v2_v3.py rollback --backup <backup-file> --target <state.json>
```

## 3. 字段映射（只增不改）

| V2 | V3 | 动作 |
|---|---|---|
| `state.json` 根字段 | 原样保留 | 不改 |
| 无 | `schema_version: 3` | 新增 |
| 无 | `learner_profile{}` | 新增空画像（不推断能力） |
| 无 | `competency_progress[]` | 新增空数组 |
| 无 | `learning_events[]` | 由现有 `events[]` 逐条映射，原 `events[]` **保留** |
| 无 | `learning_plan` | null |
| 无 | `practice_evidence[]` | 空数组 |
| `versions.*` | 原样保留 | 不改 |

**不推断**：迁移不得凭空生成 mastery、能力等级或偏好权重；全部置空并标注 `requires_assessment: true`。

## 4. 备份与回滚

- `backup` 生成带时间戳的只读副本（`v2_backup_<utc>.json`）与 `.sha256` 校验文件。
- `migrate` 前自动检查备份存在；无备份则拒绝执行。
- `verify` 逐字段比对：V2 所有原字段值必须完全一致，新增字段必须合法。
- `rollback` 用备份覆盖目标，并校验 sha256；**只在用户确认后执行**。

## 5. 迁移报告

`verify` 输出 `MigrationReport`：`source, migrated, preserved_fields, added_fields, evidence_count_before/after, history_count_before/after, verdict, timestamp`。任何 V2 字段被改动即 `verdict=fail`。

## 6. 兼容性测试

`tests/v3_cases.json` 含 M1（迁移后 V2 字段逐字一致）、M2（无备份拒绝迁移）、M3（回滚恢复 sha256）、M4（V2 47 用例回归）。
