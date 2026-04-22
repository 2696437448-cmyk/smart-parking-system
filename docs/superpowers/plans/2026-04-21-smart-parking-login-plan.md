# Smart Parking 轻量登录实现计划

- 日期：2026-04-21
- 项目：`smart-parking-thesis`
- 对应 spec：`docs/superpowers/specs/2026-04-21-smart-parking-login-design.md`
- 实现方向：方案 B，`gateway-service` 发放轻量 JWT，并对 owner/admin 路径做角色校验

## 1. 目标

1. 为系统增加统一登录入口 `/login`。
2. 让未登录用户无法直接访问 `/owner/**` 与 `/admin/**` 页面。
3. 让 `gateway-service` 为 owner/admin 业务接口提供真实的认证与角色隔离。
4. 将 owner 身份从“前端可编辑 user_id”收口为“登录态驱动的权威身份”。

## 2. 实施步骤

### Step 1：Gateway JWT 基础能力

1. 在 `services/gateway-service` 中新增认证配置类。
2. 增加演示账号配置：
   - `owner_demo / demo123`
   - `admin_demo / admin123`
3. 新增 JWT 签发与解析服务。
4. 为 JWT 能力补充最小单元测试。

交付物：

1. `AuthProperties`
2. `DemoUserRecord`
3. `JwtService`
4. `JwtServiceTest`

### Step 2：Gateway 登录接口与统一鉴权过滤

1. 增加：
   - `POST /api/v1/auth/login`
   - `GET /api/v1/auth/me`
   - `POST /api/v1/auth/logout`
2. 在 gateway 内为 `/api/v1/owner/**` 与 `/api/v1/admin/**` 增加统一过滤器。
3. 校验 token、角色与路径匹配关系。
4. 透传认证头：
   - `X-Auth-User-Id`
   - `X-Auth-Role`
   - `X-Auth-Username`

交付物：

1. `AuthController`
2. `AuthResponses`
3. `AuthRouteValidator`
4. `AuthGatewayFilterFactory`
5. `AuthControllerTest`

### Step 3：前端登录页、登录态与路由守卫

1. 新增 `/login` 页面。
2. 新增 Pinia 鉴权 store，负责：
   - 登录
   - 登出
   - 登录态恢复
3. 在请求封装中自动注入 `Authorization: Bearer <token>`。
4. 在 Vue Router 中增加：
   - `guestOnly`
   - `requiresAuth`
   - role-based redirect

交付物：

1. `apps/frontend/src/pages/LoginPage.vue`
2. `apps/frontend/src/services/auth.ts`
3. `apps/frontend/src/stores/auth.ts`
4. `apps/frontend/src/router.ts`
5. `apps/frontend/src/services/http.ts`

### Step 4：收口 owner 身份来源

1. 删除业主首页中手工输入 `userId` 的交互。
2. 前端 owner 业务请求不再把 `user_id` 作为可编辑字段发送。
3. `parking-service` 优先使用 gateway 透传的 `X-Auth-User-Id`。
4. 保持现有 owner/admin 业务合同兼容，不重写预约、订单和导航主链。

交付物：

1. `apps/frontend/src/composables/useOwnerDashboardView.ts`
2. `apps/frontend/src/pages/OwnerDashboard.vue`
3. `apps/frontend/src/services/owner.ts`
4. `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
5. `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`

### Step 5：文档与验证

1. 更新 README 与答辩演示文档中的默认入口。
2. 增加静态 gate，固定登录流与身份收口要求。
3. 完成前端 typecheck / build、gateway 测试、parking-service 编译验证。

## 3. 验证清单

```bash
python3 scripts/test_step21_frontend_pages.py
python3 scripts/test_step43_login_auth.py
python3 scripts/test_step44_authenticated_owner_identity.py
cd apps/frontend && npm run typecheck
cd apps/frontend && npm run build
cd services/gateway-service && /opt/homebrew/bin/mvn -q -Dmaven.repo.local=/tmp/smart-parking-m2 -Dtest=AuthControllerTest test
cd services/parking-service && /opt/homebrew/bin/mvn -q -Dmaven.repo.local=/tmp/smart-parking-m2 -DskipTests package
```

## 4. 风险与边界

1. 当前仅为演示级轻量登录，不包含注册、找回密码、refresh token 和黑名单。
2. 演示账号与 JWT secret 仍然属于 demo 默认值，后续如进入交付环境需要外置化和替换。
3. 当前角色只有 `OWNER` 与 `ADMIN` 两类，不扩展到细粒度权限点。
