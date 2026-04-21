# Smart Parking 轻量登录方案设计

- 日期：2026-04-21
- 项目：`smart-parking-thesis`
- 设计状态：已确认方向，待用户审阅书面 spec 后进入实现计划
- 方案选择：方案 B，网关发放轻量 token，前后端都做角色校验

## 1. 背景

当前 `smart-parking-thesis` 已完成业主端与物业端双角色页面、网关入口、停车主业务服务、模型服务和实时服务等核心能力，系统业务链路可以从推荐、预约、订单、导航一直闭环到物业经营监控。但从身份认证视角看，当前系统仍然采用“默认直达业务页面”的演示模式：前端访问根路径后直接进入 `/owner/dashboard`，物业端也可以直接访问 `/admin/monitor`，没有独立登录页、路由守卫、用户会话或后端鉴权。

这一现状对于功能演示是够用的，但对于毕业设计最终交付、论文表达和答辩完整性来说仍然欠缺一个关键环节，即系统缺少基础身份认证与角色隔离能力。尤其是在当前系统已经明确区分业主端用户和物业端用户两类角色的前提下，如果两类页面和接口都可以无门槛访问，那么“角色边界”只存在于页面命名层，而没有真正落实到系统入口与接口访问控制层。

因此，本轮设计的目标不是引入一套完整的生产级账号体系，而是在不破坏现有停车主链、不额外拆分用户中心服务的前提下，为系统补上一套真实可用、易于答辩说明、并且与现有微服务结构兼容的轻量登录方案。

## 2. 现状判断

当前系统没有真正的用户登录能力，主要依据如下。

1. 前端路由直接将 `/` 重定向到 `/owner/dashboard`，不存在 `/login` 页面，也没有路由守卫。
2. 业主端页面中的 `userId` 目前作为业务输入项手工填写，而不是作为已认证身份自动注入。
3. 前端统一请求封装没有 Bearer token 注入逻辑，也不存在前端登录态恢复机制。
4. `gateway-service` 当前只承担路由转发、熔断和降级职责，没有认证控制器、JWT 校验、角色校验或会话管理逻辑。
5. `parking-service` 提供 `/api/v1/owner/**` 与 `/api/v1/admin/**` 等业务接口，但未引入 Spring Security 或其他用户鉴权机制。

这说明当前系统的 owner/admin 区分主要停留在信息架构和页面组织层，还没有形成受保护的系统访问边界。

## 3. 目标

本轮设计目标如下。

1. 让系统访问路径从“直接进入业务页”调整为“先登录，再按角色进入对应端页面”。
2. 为系统补齐基础身份认证、角色隔离和受保护接口访问能力。
3. 把认证入口统一放在 `gateway-service`，避免破坏当前“前端统一通过 gateway 进入后端”的架构主线。
4. 在不重写 `parking-service` 主业务逻辑的前提下，为 owner/admin 接口增加统一前置鉴权。
5. 保持实现轻量、说明清晰、适合毕业设计答辩，不额外扩展到完整用户中心工程。

## 4. 非目标

以下内容不属于本轮范围。

1. 不做注册、找回密码、短信验证码、邮箱验证或第三方 OAuth 登录。
2. 不做细粒度权限点控制，仅保留 `OWNER` 和 `ADMIN` 两类角色。
3. 不引入 refresh token、多设备会话管理、黑名单服务或单点登录。
4. 不新建独立用户服务，不把本轮扩展为正式生产级 IAM 系统。
5. 不大幅改写 `parking-service` 的预约、订单、导航和物业监控主链。

## 5. 方案比较与结论

本轮讨论过三种轻量登录思路。

1. 纯前端演示登录：改动最小，但后端接口不受保护，只能算“页面层伪登录”。
2. gateway 发放轻量 token，并在 gateway 做前后端统一角色校验：既保留统一入口，又能真正保护 owner/admin 接口。
3. 由 `parking-service` 自己完成登录与 JWT：实现可行，但会削弱 gateway 作为统一入口的治理角色，也不利于后续扩展。

最终采用方案二，即在 `gateway-service` 中新增轻量认证模块，由 gateway 负责：

1. 登录凭据校验。
2. JWT access token 签发。
3. owner/admin 角色鉴权。
4. 将认证身份透传给后端业务服务。

这是当前项目结构下最稳妥的方案，因为它最大限度沿用了现有统一入口设计，同时避免将身份逻辑散落到多个服务中。

## 6. 总体架构

本轮登录方案采用“前端登录页 + gateway 认证模块 + parking-service 认证头适配”的三段式结构。

### 6.1 前端职责

前端负责：

1. 提供 `/login` 登录页。
2. 保存和恢复本地登录态。
3. 在路由层阻止未登录用户进入 `/owner/**` 与 `/admin/**`。
4. 在 HTTP 请求层自动注入 Bearer token。
5. 在 token 失效时清理本地状态并跳回登录页。

### 6.2 gateway 职责

`gateway-service` 负责：

1. 提供认证接口，如登录、当前用户信息查询、登出。
2. 校验演示账号配置与密码。
3. 签发与校验 JWT。
4. 对 `/api/v1/owner/**` 和 `/api/v1/admin/**` 做统一角色校验。
5. 将认证用户的 `user_id` 与 `role` 以请求头形式透传给后端服务。

### 6.3 parking-service 职责

`parking-service` 不承担登录入口职责，只做轻量适配：

1. owner 场景优先从 gateway 透传的认证头中读取权威用户身份。
2. 保持原有接口合同兼容，不立即大改 owner/admin 业务参数结构。
3. 避免让前端显式传入的 `user_id` 成为权威身份来源。

这种分工可以在不推翻现有业务主链的情况下，为系统增加真正的身份边界。

## 7. 登录流程

### 7.1 页面访问流程

页面访问流程调整如下。

1. 用户访问 `/`。
2. 若前端本地不存在有效登录态，则重定向到 `/login`。
3. 用户在登录页输入用户名和密码。
4. 登录成功后：
   - `OWNER` 跳转到 `/owner/dashboard`
   - `ADMIN` 跳转到 `/admin/monitor`
5. 若已登录用户再次访问 `/login`，则直接跳转到其角色首页。
6. 用户点击退出登录后，前端清空本地认证状态并回到 `/login`。

### 7.2 接口调用流程

认证相关接口调用流程如下。

1. 前端调用 `POST /api/v1/auth/login`。
2. gateway 校验用户名与密码是否匹配演示账号配置。
3. gateway 签发 JWT access token，并返回用户摘要。
4. 前端保存 token 与用户摘要。
5. 前端后续访问 owner/admin 业务接口时自动携带 `Authorization: Bearer <token>`。
6. gateway 在转发业务请求前先校验 token 和角色。
7. 校验通过后，gateway 增加认证头并继续转发。
8. 校验失败时，gateway 直接返回 `401` 或 `403`。

## 8. Token 设计

本轮采用单 access token 的轻量 JWT 方案，不引入 refresh token。

### 8.1 签名与有效期

1. 签名算法：`HS256`
2. 有效期：建议 8 小时
3. 密钥来源：gateway 环境变量或配置文件中的认证密钥

8 小时的原因在于，该时长足以覆盖演示、验收和答辩过程，同时不会把会话机制做得过于复杂。

### 8.2 Claims 设计

JWT claims 建议至少包含以下字段。

```json
{
  "sub": "owner_demo",
  "user_id": "owner-app-001",
  "role": "OWNER",
  "display_name": "业主演示账号",
  "iat": 1710000000,
  "exp": 1710028800
}
```

其中：

1. `sub` 表示登录账号名。
2. `user_id` 表示业务主链里使用的业主身份标识。
3. `role` 用于 gateway 的角色校验。
4. `display_name` 用于前端顶部展示和答辩演示。
5. `iat` 与 `exp` 用于控制 token 生命周期。

## 9. 接口设计

### 9.1 `POST /api/v1/auth/login`

请求体示例：

```json
{
  "username": "owner_demo",
  "password": "demo123"
}
```

响应体示例：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9.demo.payload",
  "token_type": "Bearer",
  "expires_in": 28800,
  "user": {
    "user_id": "owner-app-001",
    "username": "owner_demo",
    "display_name": "业主演示账号",
    "role": "OWNER"
  }
}
```

登录失败时返回 `401`，并给出统一错误消息。

### 9.2 `GET /api/v1/auth/me`

该接口用于前端刷新页面后恢复登录态，并验证本地 token 是否仍然有效。

如果 token 合法，则返回当前用户摘要；如果 token 无效或已过期，则返回 `401`。

### 9.3 `POST /api/v1/auth/logout`

轻量版登出不需要服务端维护复杂会话状态，因此该接口可以作为可选能力存在：

1. 前端最基本的登出动作是本地清空 token。
2. gateway 可额外返回统一登出响应，便于接口语义完整。
3. 若后续需要增加审计日志，可在此接口补充行为记录。

## 10. 角色与访问控制策略

角色控制规则如下。

### 10.1 `OWNER`

1. 允许访问 `/owner/**`
2. 允许调用 `/api/v1/owner/**`
3. 不允许访问 `/admin/**`
4. 不允许调用 `/api/v1/admin/**`

### 10.2 `ADMIN`

1. 允许访问 `/admin/**`
2. 允许调用 `/api/v1/admin/**`
3. 不允许访问 `/owner/**`
4. 不允许调用 `/api/v1/owner/**`

### 10.3 错误语义

1. 未登录：`401 Unauthorized`
2. token 无效或过期：`401 Unauthorized`
3. 已登录但角色不匹配：`403 Forbidden`

这种区分可以让前端和论文说明都更清楚，即“未认证”和“已认证但无权限”是两类不同问题。

## 11. `user_id` 权威来源设计

这是本轮方案里最关键的安全收口点。

当前 owner 业务接口显式接收 `user_id` 参数。如果登录后仍然允许前端自由填写这个参数，那么虽然页面体验看上去有登录，但接口身份仍可能被伪造。因此本轮必须把“页面展示身份”和“后端权威身份”统一起来。

### 11.1 前端层

1. 登录成功后，owner 页面不再让用户手工输入 `userId`。
2. 原有“用户 ID”输入项应改为只读展示，或者从界面中移除。
3. owner 相关请求里的 `user_id` 统一由登录态自动注入。

### 11.2 gateway 层

gateway 在 token 校验通过后，应向下游请求增加认证头，例如：

1. `X-Auth-User-Id`
2. `X-Auth-Role`
3. `X-Auth-Username`

### 11.3 parking-service 层

`parking-service` 在 owner 场景中优先信任 gateway 透传的 `X-Auth-User-Id`，并将其作为权威身份来源。原有 `user_id` 请求参数可以暂时保留用于兼容，但不再作为最终认证身份依据。

这种设计能在保持现有接口合同基本稳定的前提下，真正解决“前端 user_id 可伪造”的问题。

## 12. 前端设计

### 12.1 登录页

前端新增 `/login` 页面，负责承载登录入口。登录页不需要复杂的注册或找回密码能力，只需聚焦以下信息：

1. 系统标题与身份说明。
2. 用户名输入框。
3. 密码输入框。
4. 登录按钮。
5. 登录失败提示。
6. 演示账号提示区（可选，用于答辩演示）。

页面风格应与当前科技风 UI 保持一致，但不需要做成独立营销页，重点是建立清晰可信的系统入口。

### 12.2 认证状态管理

前端新增 auth store，用于统一管理：

1. access token
2. 当前用户摘要
3. 是否已登录
4. 登录恢复状态
5. 登出动作

建议使用现有 Pinia 体系实现，而不是新引入额外状态库。

### 12.3 路由守卫

路由层增加以下行为。

1. 未登录访问 `/owner/**` 或 `/admin/**` 时跳转到 `/login`。
2. 已登录访问 `/login` 时跳转到角色首页。
3. `OWNER` 访问 `/admin/**` 时拦截并重定向。
4. `ADMIN` 访问 `/owner/**` 时拦截并重定向。

### 12.4 HTTP 统一注入

当前前端已具备统一请求入口，因此应在统一请求封装中自动追加 Bearer token，而不是在每个业务请求里重复写认证头。

这样可以把认证改动收敛到一处，并降低后续维护成本。

### 12.5 现有 owner 页面调整

业主端页面中当前作为输入项暴露的 `userId` 应做如下调整。

1. 不再允许自由编辑。
2. 若仍需展示，则改为只读身份展示。
3. 业务请求中的 `userId` 来自 auth store。
4. `location` 与 `preferredWindow` 仍由用户输入，不影响现有业务链路表达。

### 12.6 Layout 顶部身份展示

`OwnerLayout` 与 `AdminLayout` 应新增当前登录用户摘要与退出按钮，使系统在视觉上也具备“已认证使用中”的状态感。

## 13. Gateway 设计

### 13.1 演示账号配置

本轮不引入数据库用户表，而是在 gateway 中维护轻量演示账号配置。每个账号至少包含：

1. `username`
2. `password_hash` 或固定演示密码
3. `role`
4. `user_id`
5. `display_name`
6. `enabled`

为了避免把明文密码直接写入代码，建议至少通过环境变量或配置文件注入，并保留后续切换为 hash 校验的能力。

### 13.2 JWT 服务

gateway 新增 `JwtService`，负责：

1. token 签发
2. token 解析
3. token 过期校验
4. claims 读取

### 13.3 认证过滤器

gateway 在转发 `/api/v1/owner/**` 与 `/api/v1/admin/**` 之前执行认证过滤器。过滤器职责如下。

1. 解析 `Authorization` 请求头。
2. 校验 token 有效性。
3. 提取 `role` 与 `user_id`。
4. 判断当前目标路径是否与角色匹配。
5. 向下游请求注入认证头。
6. 在失败时直接返回 `401/403`。

### 13.4 路由保护范围

gateway 需要放行：

1. `/api/v1/auth/**`

gateway 需要保护：

1. `/api/v1/owner/**`
2. `/api/v1/admin/**`

`/internal/v1/ingest/**` 等内部接口是否纳入本轮保护，可暂时维持现状，不作为此次登录方案重点。

## 14. Parking Service 适配策略

`parking-service` 的目标不是接管认证，而是接收 gateway 的认证结果并完成身份收口。

建议做法如下。

1. 对 owner 查询与预约入口增加认证头读取。
2. 优先使用 `X-Auth-User-Id` 作为业务上下文中的用户身份。
3. 仅在无认证头的兼容场景下保留原有 `user_id` 参数逻辑。
4. 避免让业务服务自己再次解析 JWT，从而保持 gateway 作为统一认证入口。

这样既能提升身份一致性，又不会把业务服务改造成第二套认证入口。

## 15. 文件落点建议

### 15.1 前端

建议新增或修改如下文件。

1. 新增 `apps/frontend/src/pages/LoginPage.vue`
2. 新增 `apps/frontend/src/services/auth.ts`
3. 新增 `apps/frontend/src/stores/auth.ts`
4. 修改 `apps/frontend/src/router.ts`
5. 修改 `apps/frontend/src/services/http.ts`
6. 修改 `apps/frontend/src/composables/useOwnerDashboardView.ts`
7. 修改 `apps/frontend/src/pages/OwnerDashboard.vue`
8. 修改 `apps/frontend/src/layouts/OwnerLayout.vue`
9. 修改 `apps/frontend/src/layouts/AdminLayout.vue`

### 15.2 Gateway

建议新增或修改如下文件。

1. 修改 `services/gateway-service/pom.xml`
2. 新增 `AuthController.java`
3. 新增 `AuthProperties.java`
4. 新增 `JwtService.java`
5. 新增认证过滤器实现
6. 修改 `services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`

### 15.3 Parking Service

建议在 owner 入口附近增加认证头读取适配，使权威身份来源由 gateway 收口。

## 16. 验证方案

本轮至少需要覆盖以下验收场景。

1. 未登录访问 `/owner/dashboard`，跳转到 `/login`
2. 未登录访问 `/admin/monitor`，跳转到 `/login`
3. `OWNER` 登录成功后进入 `/owner/dashboard`
4. `OWNER` 访问 `/admin/monitor`，被拒绝或重定向
5. `ADMIN` 登录成功后进入 `/admin/monitor`
6. `ADMIN` 访问 `/owner/dashboard`，被拒绝或重定向
7. 登录成功后 owner 推荐、预约、订单、导航主链保持可用
8. 登录成功后 admin dashboard、图表与实时状态保持可用
9. token 失效后，接口返回 `401`，前端清理登录态并回到 `/login`
10. 退出登录后刷新受保护页面，需要重新登录

## 17. 论文与答辩表达建议

本方案在论文和答辩中可以概括为以下几个点。

1. 系统在网关层增加统一认证入口，而不是让认证逻辑散落到各业务服务中。
2. 采用轻量 JWT 令牌机制承载用户会话，降低了系统实现复杂度。
3. 通过 `OWNER` 与 `ADMIN` 两类角色实现业主端与物业端访问边界控制。
4. 前端通过路由守卫与统一请求封装完成页面访问控制与登录态透传。
5. 后端通过 gateway 认证过滤器与认证头透传完成接口前置鉴权。
6. 系统在不破坏既有停车主链的前提下补齐了基础身份认证与角色隔离能力。

## 18. 风险与取舍

本轮方案的主要优点是轻量、集中、易讲清楚，但也有明确取舍。

1. 由于不引入 refresh token 和完整用户中心，本方案更适合毕业设计与演示环境，而不应直接视为生产级安全体系。
2. 演示账号配置位于 gateway，后续若要扩展多用户管理，仍需演进到数据库化用户存储。
3. 如果 `parking-service` 仍长期兼容可自由传入的 `user_id` 参数，则后续需要继续推进接口语义收口。

这些取舍是有意为之，因为本轮目标是补齐系统完成度，而不是在当前阶段把认证体系扩展为另一个独立项目。

## 19. 下一步

本设计确认后，下一步应进入实现计划阶段，重点包括：

1. 前端登录页、auth store 与路由守卫。
2. gateway 认证接口、JWT 服务与角色过滤器。
3. owner 业务身份从前端输入迁移为登录态注入。
4. `parking-service` 对认证头的最小适配。
5. 登录与角色隔离相关验收脚本。
