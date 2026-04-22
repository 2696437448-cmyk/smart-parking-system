# 安全与配置硬化说明（Step35）

## 1. 适用边界

1. 当前仓库仍保留“本地演示 / 答辩优先”的 demo 默认值。
2. `Step35` 的目标不是把项目变成生产级安全基线，而是把“demo 默认值”和“可发布/可交付配置”明确分层。
3. 默认原则：
   - `.env.example`：仅用于本地 demo / acceptance 默认值
   - `.env.secure.example`：用于非 demo 场景的安全起点
   - `.env` / `apps/frontend/.env.local`：本机私有覆盖，禁止提交

## 2. 推荐配置分层

1. 本地演示：
   - 复制 `.env.example` 为 `.env`
   - 复制 `apps/frontend/.env.example` 为 `apps/frontend/.env.local`

2. 非 demo / 交付前：
   - 从 `.env.secure.example` 复制为 `.env`
   - 替换所有 `CHANGE_ME_*`
   - 保持 `RABBIT_USER/RABBIT_PASS` 与 `RABBITMQ_DEFAULT_USER/RABBITMQ_DEFAULT_PASS` 一致

## 3. 凭证轮换

1. 修改 `.env` 中以下项：
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_PASSWORD`
   - `RABBIT_PASS`
   - `RABBITMQ_DEFAULT_PASS`
   - `GF_ADMIN_PASSWORD`
2. 如同时更换用户名，需同步修改：
   - `MYSQL_USER`
   - `RABBIT_USER`
   - `RABBITMQ_DEFAULT_USER`
   - `GF_ADMIN_USER`
3. 修改后重启：

```bash
./scripts/defense_demo.sh stop
./scripts/defense_demo.sh preflight
./scripts/defense_demo.sh start
```

## 4. 安全扫描

1. 本地扫描命令：

```bash
python3 scripts/security_scan.py
python3 scripts/test_step35_security_config.py
```

2. 重点检查：
   - 私钥头
   - GitHub token
   - OpenAI key
   - AWS Access Key
   - 被误追踪的 `.env` / `.env.local`

## 5. 恢复建议

1. 若修改 `.env` 后无法登录 RabbitMQ / Grafana：
   - 先检查 `.env` 是否把 `RABBIT_USER` 与 `RABBITMQ_DEFAULT_USER` 配成不同值
   - 检查 `GF_ADMIN_USER` / `GF_ADMIN_PASSWORD` 是否和预期一致
2. 若只是答辩环境临时异常，可回退到 `.env.example` 作为本地 demo 恢复基线。
3. 若是非 demo 环境，不应直接回退到 demo 默认值，应从 `.env.secure.example` 重新生成 `.env`。
4. 每次恢复后都建议执行：

```bash
make preflight-static
python3 scripts/test_step35_security_config.py
```

## 6. 当前边界

1. Step35 完成后，仓库已经具备：
   - demo 默认值与 secure 模板分层
   - 敏感项扫描脚本
   - 安全恢复文档
2. 但这仍不等价于生产级安全审计，后续若进入真实部署，需要继续补：
   - 密钥管理
   - TLS / HTTPS
   - 最小权限账户
   - 容器镜像漏洞扫描

## 7. Step43 认证补充说明

1. 当前系统已补入统一登录页与 gateway 级轻量 JWT 鉴权。
2. 演示账号默认值：
   - `owner_demo / demo123`
   - `admin_demo / admin123`
3. 这些账号仅用于本地 demo、验收与答辩演示，不应作为真实交付环境默认凭据继续保留。
4. `gateway-service` 中的 JWT secret 与演示账号配置应在非 demo 场景通过环境变量或独立配置覆盖。
5. owner 业务身份已开始优先依赖 `X-Auth-User-Id` 认证头，而不是前端自由提交的 `user_id`，这是当前版本最重要的身份收口点。

## 8. 非 demo 环境建议

1. 替换所有演示账号用户名与密码。
2. 替换 JWT secret，避免继续使用仓库内 demo 默认值。
3. 若进入正式部署，应继续补充：
   - refresh token 或服务端会话失效策略
   - 登录失败次数限制
   - 审计日志
   - HTTPS 终止与反向代理安全配置
