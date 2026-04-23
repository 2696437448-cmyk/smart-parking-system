# Step43 执行报告（轻量登录与身份收口）

## 执行范围

1. 目标：为 `smart-parking-thesis` 增加统一登录入口、gateway 级角色鉴权与 owner 身份收口能力。
2. 范围：
   - `gateway-service` 轻量 JWT 认证
   - 前端登录页、登录态、Bearer 注入与路由守卫
   - `parking-service` 对认证头的最小适配
   - 文档与 gate 补充
3. 不包含：
   - 注册、验证码、第三方 OAuth
   - refresh token、多设备会话和黑名单
   - 独立用户中心服务

## 实际改动

1. Gateway 认证能力
   - 新增 `JwtService`、`AuthProperties`、`DemoUserRecord`
   - 新增 `AuthController`、`AuthRouteValidator`、`AuthGatewayFilterFactory`
   - `gateway-service` 支持演示账号登录、JWT 校验和 owner/admin 接口角色隔离

2. 前端登录能力
   - 新增统一登录页 `apps/frontend/src/pages/LoginPage.vue`
   - 新增 `apps/frontend/src/services/auth.ts`
   - 新增 `apps/frontend/src/stores/auth.ts`
   - `router.ts` 增加 `/login`、`guestOnly`、`requiresAuth` 和按角色跳转逻辑
   - `http.ts` 新增 Bearer token 自动注入

3. Owner 身份收口
   - 业主首页不再允许手工输入 `userId`
   - owner 业务请求不再显式提交可编辑 `user_id`
   - `parking-service` 优先读取 `X-Auth-User-Id`

4. 文档与 gate
   - 更新 `README.md`
   - 更新 `docs/defense_demo_runbook.md`
   - 新增 `scripts/test_step43_login_auth.py`
   - 新增 `scripts/test_step44_authenticated_owner_identity.py`

## 核心结果

1. 系统默认入口从“直接进入业务页”调整为“先登录，再按角色进入首页”。
2. `OWNER` 与 `ADMIN` 页面和接口都具备了统一的认证边界。
3. owner 身份不再由前端页面自由填写，业务身份开始由 gateway 透传的认证头驱动。
4. 改造保持在现有微服务骨架内完成，没有引入独立用户中心，适合答辩展示与论文表述。

## 演示账号

1. 业主演示账号：`owner_demo / demo123`
2. 物业演示账号：`admin_demo / admin123`

## 执行命令与结果

```bash
python3 scripts/test_step21_frontend_pages.py
python3 scripts/test_step43_login_auth.py
python3 scripts/test_step44_authenticated_owner_identity.py
cd apps/frontend && npm run typecheck
cd apps/frontend && npm run build
cd services/gateway-service && /opt/homebrew/bin/mvn -q -Dmaven.repo.local=/tmp/smart-parking-m2 -Dtest=AuthControllerTest test
cd services/parking-service && /opt/homebrew/bin/mvn -q -Dmaven.repo.local=/tmp/smart-parking-m2 -DskipTests package
```

结果：全部通过。

## 当前边界

1. 这是“轻量登录 + 角色隔离”的 demo/答辩级实现，不等价于生产级 IAM。
2. JWT secret 和演示账号仍需在非 demo 环境外置化。
3. 若后续继续扩展，可在当前 gateway 方案上逐步增加 refresh token、审计日志和更细粒度权限控制。
