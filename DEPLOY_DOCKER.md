# Docker / Podman 云端部署（不使用 FRP）

## 1. 准备环境

在云服务器安装 Docker 或 Podman（支持 Compose）。

## 2. 配置环境变量

在项目根目录执行：

```bash
cp .env.cloud.example .env
```

然后编辑 `.env`，至少修改这些值：

- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `OPENAI_API_KEY`（如果要使用 AI 功能）
- `SMTP_USER` / `SMTP_PASSWORD`（如果要邮箱验证码与找回密码）

## 3. 启动服务

```bash
docker compose up -d --build
```

如果你使用 Podman：

```bash
podman compose up -d --build
```

服务说明：

- `frontend`：对外端口 `APP_PORT`（默认 80）
- `backend`：仅容器内可访问（由 Nginx 反代 `/api`）
- `postgres`：持久化卷 `postgres_data`
- `redis`：持久化卷 `redis_data`

## 4. 常用运维命令

查看状态：

```bash
docker compose ps
curl http://127.0.0.1/health
```

Podman 对应命令：

```bash
podman compose ps
curl http://127.0.0.1/health
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Podman 对应命令：

```bash
podman compose logs -f backend
podman compose logs -f frontend
```

停止服务：

```bash
docker compose down
```

Podman 对应命令：

```bash
podman compose down
```

停止并删除卷（会清空数据库）：

```bash
docker compose down -v
```

Podman 对应命令：

```bash
podman compose down -v
```

## 5. 更新发布

拉取新代码后执行：

```bash
docker compose up -d --build
```

Podman 对应命令：

```bash
podman compose up -d --build
```

后端容器启动时会自动执行：

```bash
alembic upgrade head
```

## 6. 域名与 HTTPS（生产建议）

- DNS 将域名 A 记录指向云服务器 IP。
- 80/443 端口放行。
- 建议在服务器最外层再挂一层 Nginx/Caddy 做 HTTPS 证书与反向代理。
