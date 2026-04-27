# 算潮 (Suanchao)

[English](./README.md) | [中文](./README_CN.md)

算潮是一个面向中文用户的在线编程训练平台，支持在线判题、AI 出题、AI 导师、题目广场分享、错题复习与中英文切换。

## 功能概览

- 在线判题：支持提交判题与自定义输入运行。
- AI 出题：可按刷题进度估计难度，或自定义难度生成私有题。
- AI 私有题库：AI 生成题目仅用户个人可见，并与公共题库区分展示。
- 题目广场：可分享已通过题目、导入他人题目、Star 排序。
- 讨论系统：题目讨论、评论与楼主删除评论。
- 错题本：按标签与到期节奏复习，支持二刷提醒。
- 多语言界面：中文/英文切换。

## 技术栈

- 前端：Vue 3 + Vite + Pinia + Vue Router + Monaco Editor
- 后端：FastAPI + SQLAlchemy (async) + Alembic
- 数据库：PostgreSQL
- 队列/缓存：Redis

## 项目结构

```text
.
├── app/                 # FastAPI 后端
├── frontend/            # Vue 前端
├── alembic/             # 数据库迁移
├── scripts/             # 运维/迁移脚本
├── deploy/              # Docker/Podman 构建与 Nginx 配置
├── docker-compose.yml   # 容器编排
└── DEPLOY_DOCKER.md     # 云端部署说明
```

## 本地开发

### 1) 后端

```bash
cd /path/to/suanchao
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

按需编辑 `.env`（数据库、AI、SMTP 等）。

### 2) 准备数据库并迁移

```bash
python scripts/migrate.py upgrade head
```

### 3) 启动后端

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 30881
```

### 4) 启动前端

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 30880
```

访问：

- 前端：`http://127.0.0.1:30880`
- 后端健康检查：`http://127.0.0.1:30881/health`

## 容器部署（推荐云端）

本项目已提供 Docker / Podman Compose 配置：

```bash
cp .env.cloud.example .env
podman compose up -d --build
```

或：

```bash
docker compose up -d --build
```

完整说明见 [DEPLOY_DOCKER.md](./DEPLOY_DOCKER.md)。

## 数据库迁移

常用命令：

```bash
python scripts/migrate.py upgrade head
python scripts/migrate.py current
python scripts/migrate.py history
python scripts/migrate.py downgrade -1
```

迁移体系详见 [MIGRATIONS.md](./MIGRATIONS.md)。

## 安全说明

- 请勿提交 `.env`、数据库备份、日志文件到仓库。
- 上线前请替换所有密钥（`SECRET_KEY`、`OPENAI_API_KEY`、`SMTP_PASSWORD` 等）。
