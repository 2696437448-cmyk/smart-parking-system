# 第 3 周：请求流与网关

## 本周目标

- 弄清一次请求从前端到后端是怎么走的
- 看懂前端统一请求封装
- 理解网关为什么不仅仅是“转发器”

## 你会先看哪些文件

- `apps/frontend/src/services/http.ts`
- `apps/frontend/src/services/owner.ts`
- `apps/frontend/src/services/admin.ts`
- `apps/frontend/src/services/runtime.ts`
- `services/gateway-service/src/main/java/com/smartparking/gateway/GatewayRoutesConfig.java`
- `services/gateway-service/src/main/java/com/smartparking/gateway/TraceIdGlobalFilter.java`
- `services/gateway-service/src/main/java/com/smartparking/gateway/ModelFallbackController.java`

## 这部分代码到底在做什么

这部分代码解决的问题是：`浏览器的请求该怎么稳定地进入后端系统`。

你可以把它拆成前后两段来看：

### 前端请求段

前端不会每个页面都自己直接 `fetch()`，而是统一走：

- `http.ts`：负责统一拼 URL、带请求头、处理错误
- `owner.ts` / `admin.ts`：按业务域封装具体接口
- `runtime.ts`：统一读取网关地址和实时通道地址

这样做的好处是：

- 改网关地址时不用全项目手改
- 错误处理方式统一
- 请求头里的 trace 信息统一

### 网关段

网关的作用不只是“把请求送过去”，还负责：

- 统一入口
- trace 透传
- 模型服务熔断与 fallback
- CORS 放行

所以它是“系统入口层”，不是单纯的转发脚本。

## 一条必须跟读的调用链

这周建议你跟 `admin dashboard` 的一条请求链：

1. `useAdminDashboardView.ts` 调用 `fetchAdminDashboard()`
2. `fetchAdminDashboard()` 调用 `requestJson()`
3. `requestJson()` 用 `gatewayUrl()` 拼出网关 URL
4. 浏览器请求打到 `gateway-service`
5. `TraceIdGlobalFilter` 给请求补上 `X-Trace-Id`
6. `GatewayRoutesConfig` 根据路径把请求转发到 `parking-service`
7. 如果模型相关路径后端挂掉，`ModelFallbackController` 会返回降级结果

## 给新手的概念解释

### 什么是 Trace ID

可以把它理解成“这一次请求的编号”。  
前端发起请求时带上它，网关和后端再继续透传，这样出了问题就能一路追踪。

### 什么是 fallback

fallback 就是“兜底返回”。  
比如模型服务挂了，系统不一定直接报错崩掉，而是先给一个降级结果，让页面还能继续工作。

### 什么是 CORS

浏览器默认会限制不同来源之间的请求。  
网关配置 CORS，就是告诉浏览器“前端这个地址可以访问我”。

## 本周可直接运行的命令

```bash
# 启动整套演示环境
./scripts/defense_demo.sh start

# 验证网关健康状态
curl http://localhost:8080/actuator/health

# 查看一个典型 owner dashboard 请求
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
```

## 本周小练习

1. 在 `http.ts` 中找出错误是怎么被统一包装成 `HttpRequestError` 的。
2. 在 `GatewayRoutesConfig.java` 中找出哪些路径会被转发到 `parking-service`。
3. 写一句话解释：为什么模型服务的 fallback 放在网关做，而不是放在前端做。

## 本周完成标准

- 你能完整说出一次请求从页面到网关再到后端的路径
- 你知道前端为什么要统一请求封装
- 你能说明网关除了转发之外还做了哪些工作

## 可选加深阅读

- `services/gateway-service/src/main/resources/application.yml`
- `reports/step15_execution.md`
- `reports/step39_execution.md`

## 继续深入

请求流和 gateway 的详细代码路径请继续：

- `../chains/chain-01-owner-dashboard-request.md`
- `../labs/lab-01-owner-dashboard.md`

