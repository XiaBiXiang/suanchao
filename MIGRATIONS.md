# 数据库迁移体系（Alembic）

项目已接入 Alembic，迁移入口文件：

- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/`
- `scripts/migrate.py`

## 一、常用命令

### 1) 升级到最新版本

```bash
python scripts/migrate.py upgrade head
```

### 2) 查看当前版本

```bash
python scripts/migrate.py current
```

### 3) 查看历史迁移

```bash
python scripts/migrate.py history
```

### 4) 回滚一步

```bash
python scripts/migrate.py downgrade -1
```

## 二、已有数据库如何接入迁移

如果数据库是以前用 `app/db/init_db.py` 或手工建表创建的，且没有 `alembic_version`：

1. 先标记到旧基线（不执行 DDL）：

```bash
python scripts/migrate.py stamp 20260309_0001
```

2. 再升级到最新：

```bash
python scripts/migrate.py upgrade head
```

这样会执行 `20260309_0002`，补上 `problems.source_type` 和 `problems.owner_id`。

## 三、当前迁移说明

- `20260309_0001`：初始表结构（users / problems / test_cases / submissions / posts / comments）
- `20260309_0002`：新增题目来源与归属字段：
  - `problems.source_type`
  - `problems.owner_id`
- `20260309_0003`：新增广场分享与导入表：
  - `shared_problems`
  - `shared_problem_imports`
- `20260310_0004`：新增题目标记字段：
  - `problems.is_square_imported`
- `20260310_0005`：新增广场 Star 体系：
  - `shared_problems.star_count`
  - `shared_problem_stars`（同一用户同一分享仅一次）
- `20260310_0006`：新增异步判题与学习增强体系：
  - `problems`：`knowledge_tags` / `title_hash` / `description_hash` / `ai_feedback_score`
  - `submissions`：`run_mode` / `custom_input` / `total_time_ms` / `max_memory_mb` / `result_data`
  - `judge_jobs`（Redis 队列任务状态表）
  - `wrong_problem_notes`（错题本 + 二刷提醒）
  - `ai_problem_feedbacks`（AI 题目有用/无用反馈）

## 四、部署建议（Vercel）

Vercel 适合托管前端与 Serverless API。数据库迁移建议在部署前或部署流水线里单独执行：

```bash
python scripts/migrate.py upgrade head
```

不要在请求路径中执行迁移；应在 CI/CD 或发布脚本中执行一次。

## 五、Redis 验证码存储（可选）

项目验证码存储已支持 Redis，默认行为如下：

- 配置了 `REDIS_URL` 且 Redis 可用：验证码写入 Redis（带 5 分钟过期）
- 未配置或 Redis 不可用：自动回退到内存存储

建议在生产环境（包括 Vercel）配置环境变量：

```bash
REDIS_URL=redis://<user>:<password>@<host>:<port>/<db>
```

启动后若看到日志 `验证码存储已切换到 Redis`，说明启用成功。
